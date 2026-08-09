//! Local append-only log.
//!
//! `LocalLog` owns a directory of immutable segment files.  It provides:
//!
//! - batch append with a returned `LogPosition` (absolute global offset);
//! - random read by `LogPosition`;
//! - time-travel snapshot (`snapshot_as_of`) over all records up to a timestamp;
//! - a live `MerkleMountainRange` root over every appended record.

use crate::merkle::{Hash, MerkleMountainRange};
use crate::segment::{Segment, SegmentResult, SegmentWriter};
use std::fs;
use std::path::{Path, PathBuf};
use std::sync::Mutex;
use synapse_types::{LogPosition, Record, Timestamp};

/// Default number of records per on-disk segment.
pub const DEFAULT_MAX_RECORDS_PER_SEGMENT: usize = 1_000;

#[derive(Debug)]
struct LogState {
    segments: Vec<Segment>,
    mmr: MerkleMountainRange,
    current: Option<SegmentWriter>,
    next_segment_id: u64,
    total_records: u64,
}

impl LogState {
    fn rotate(&mut self, directory: &Path) -> SegmentResult<()> {
        if let Some(writer) = self.current.take() {
            if !writer.records().is_empty() {
                let records_in_writer = writer.len() as u64;
                let start_offset = self.total_records - records_in_writer;
                let mut segment = writer.finalize()?;
                segment.set_start_offset(start_offset);
                self.segments.push(segment);
            }
        }

        let id = self.next_segment_id;
        self.next_segment_id += 1;
        self.current = Some(SegmentWriter::create(directory, id)?);
        Ok(())
    }
}

/// A durable, local temporal differential log.
#[derive(Debug)]
pub struct LocalLog {
    directory: PathBuf,
    max_records_per_segment: usize,
    state: Mutex<LogState>,
}

impl LocalLog {
    /// Create or open a log in `directory`.
    pub fn create(
        directory: impl AsRef<Path>,
        max_records_per_segment: usize,
    ) -> SegmentResult<Self> {
        let directory = directory.as_ref().to_path_buf();
        fs::create_dir_all(&directory)?;
        let log = Self {
            directory,
            max_records_per_segment,
            state: Mutex::new(LogState {
                segments: Vec::new(),
                mmr: MerkleMountainRange::new(),
                current: None,
                next_segment_id: 0,
                total_records: 0,
            }),
        };
        log.state.lock().unwrap().rotate(&log.directory)?;
        Ok(log)
    }

    pub(crate) fn from_recovered(
        directory: impl AsRef<Path>,
        max_records_per_segment: usize,
        segments: Vec<Segment>,
        mmr: MerkleMountainRange,
        next_segment_id: u64,
    ) -> SegmentResult<Self> {
        let directory = directory.as_ref().to_path_buf();
        fs::create_dir_all(&directory)?;
        let total_records = segments.iter().map(|s| s.len()).sum();
        let log = Self {
            directory,
            max_records_per_segment,
            state: Mutex::new(LogState {
                segments,
                mmr,
                current: None,
                next_segment_id,
                total_records,
            }),
        };
        log.state.lock().unwrap().rotate(&log.directory)?;
        Ok(log)
    }

    /// Append a batch of records and return the `LogPosition` of the first
    /// record in the batch.
    pub fn append(&self,
        records: &[Record],
    ) -> SegmentResult<LogPosition> {
        if records.is_empty() {
            return Ok(LogPosition::from_offset(self.total_records()));
        }

        let mut state = self.state.lock().unwrap();

        let need_rotation = state
            .current
            .as_ref()
            .map_or(true, |w| w.len() > 0 && w.len() + records.len() > self.max_records_per_segment);
        if need_rotation {
            state.rotate(&self.directory)?;
        }

        let position = LogPosition::from_offset(state.total_records);
        {
            let current = state.current.as_mut().unwrap();
            for record in records {
                current.append(record)?;
            }
            current.flush()?;
        }
        for record in records {
            state.mmr.append_record(record);
        }
        state.total_records += records.len() as u64;

        Ok(position)
    }

    /// Read the record at a global `LogPosition`, if it exists.
    pub fn read(&self,
        position: LogPosition,
    ) -> Option<Record> {
        let state = self.state.lock().unwrap();
        let offset = position.as_offset();
        if offset >= state.total_records {
            return None;
        }

        for segment in &state.segments {
            let end = segment.start_offset() + segment.len();
            if offset < end {
                let local = (offset - segment.start_offset()) as usize;
                return Some(segment.records()[local].clone());
            }
        }

        // The record lives in the currently open writer.
        if let Some(current) = &state.current {
            let start = state.total_records - current.len() as u64;
            let local = (offset - start) as usize;
            return current.records().get(local).cloned();
        }

        None
    }

    /// Return all records with `timestamp <= ts`, in append order.
    pub fn snapshot_as_of(&self,
        ts: Timestamp,
    ) -> Vec<Record> {
        let state = self.state.lock().unwrap();
        let mut out = Vec::new();
        for segment in &state.segments {
            for record in segment.records() {
                if record.timestamp <= ts {
                    out.push(record.clone());
                }
            }
        }
        if let Some(current) = &state.current {
            for record in current.records() {
                if record.timestamp <= ts {
                    out.push(record.clone());
                }
            }
        }
        out
    }

    /// The current Merkle Mountain Range root, or `None` if the log is empty.
    pub fn latest_root(&self) -> Option<Hash> {
        let state = self.state.lock().unwrap();
        state.mmr.root()
    }

    /// Total number of records currently in the log.
    pub fn total_records(&self) -> u64 {
        self.state.lock().unwrap().total_records
    }

    /// Number of closed segment files.
    pub fn segment_count(&self) -> usize {
        self.state.lock().unwrap().segments.len()
    }

    /// Flush the currently open segment to disk and fsync it.
    ///
    /// This is useful before simulating a crash or handing the log directory
    /// over to recovery.  Closed segments are already durable.
    pub fn flush(&self) -> SegmentResult<()> {
        let mut state = self.state.lock().unwrap();
        if let Some(current) = state.current.as_mut() {
            current.flush()?;
        }
        Ok(())
    }
}

#[cfg(test)]
mod tests {
    use super::*;
    use synapse_types::{Attribute, Diff, EntityId, Record, Timestamp, Value};
    use tempfile::TempDir;

    fn make_record(idx: u64, ts: u64, diff: Diff) -> Record {
        Record::new(
            EntityId::from_u128(idx as u128),
            Attribute::new("price"),
            Value::i64(idx as i64),
            Timestamp::from_nanos(ts),
            diff,
        )
    }

    #[test]
    fn append_read_round_trip() {
        let dir = TempDir::new().unwrap();
        let log = LocalLog::create(dir.path(), 100).unwrap();

        let a = make_record(1, 100, Diff::Added);
        let b = make_record(2, 200, Diff::Added);
        let c = make_record(1, 300, Diff::Retracted);

        let pos_a = log.append(&[a.clone(), b.clone()]).unwrap();
        let pos_b = pos_a.add(1);
        let pos_c = log.append(std::slice::from_ref(&c)).unwrap();

        assert_eq!(log.read(pos_a), Some(a));
        assert_eq!(log.read(pos_b), Some(b));
        assert_eq!(log.read(pos_c), Some(c));
        assert_eq!(log.read(LogPosition::from_offset(999)), None);
    }

    #[test]
    fn snapshot_as_of_prefix() {
        let dir = TempDir::new().unwrap();
        let log = LocalLog::create(dir.path(), 100).unwrap();

        let records = vec![
            make_record(1, 100, Diff::Added),
            make_record(2, 200, Diff::Added),
            make_record(3, 300, Diff::Retracted),
            make_record(4, 400, Diff::Added),
        ];
        log.append(&records).unwrap();

        assert_eq!(log.snapshot_as_of(Timestamp::from_nanos(0)), vec![]);
        assert_eq!(
            log.snapshot_as_of(Timestamp::from_nanos(200)),
            records[..2].to_vec()
        );
        assert_eq!(
            log.snapshot_as_of(Timestamp::from_nanos(350)),
            records[..3].to_vec()
        );
        assert_eq!(
            log.snapshot_as_of(Timestamp::from_nanos(500)),
            records
        );
    }

    #[test]
    fn latest_root_exists() {
        let dir = TempDir::new().unwrap();
        let log = LocalLog::create(dir.path(), 100).unwrap();
        assert!(log.latest_root().is_none());

        let records = vec![
            make_record(1, 100, Diff::Added),
            make_record(2, 200, Diff::Added),
        ];
        log.append(&records).unwrap();
        let root = log.latest_root();
        assert!(root.is_some());

        let mut mmr = MerkleMountainRange::new();
        for r in &records {
            mmr.append_record(r);
        }
        assert_eq!(root, mmr.root());
    }

    #[test]
    fn segment_rotation() {
        let dir = TempDir::new().unwrap();
        let log = LocalLog::create(dir.path(), 2).unwrap();

        let r1 = make_record(1, 10, Diff::Added);
        let r2 = make_record(2, 20, Diff::Added);
        let r3 = make_record(3, 30, Diff::Added);

        log.append(std::slice::from_ref(&r1)).unwrap();
        log.append(std::slice::from_ref(&r2)).unwrap();
        log.append(std::slice::from_ref(&r3)).unwrap();

        assert_eq!(log.segment_count(), 1);
        assert_eq!(log.read(LogPosition::from_offset(0)), Some(r1));
        assert_eq!(log.read(LogPosition::from_offset(1)), Some(r2));
        assert_eq!(log.read(LogPosition::from_offset(2)), Some(r3));
    }
}
