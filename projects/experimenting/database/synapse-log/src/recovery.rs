//! Crash recovery.
//!
//! `recover` brings a `LocalLog` back to a consistent state after an unclean
//! shutdown by:
//!
//! - Scanning segment files in identifier order.
//! - Rebuilding the in-memory `MerkleMountainRange` from on-disk records.
//! - Detecting a partially-written tail frame and truncating the file to the
//!   last complete frame.
//! - Re-opening a fresh writable segment so appends can continue.

use crate::log::LocalLog;
use crate::merkle::MerkleMountainRange;
use crate::segment::{Segment, SegmentError, SegmentReader};
use std::fs;
use std::path::Path;

/// Recover a `LocalLog` from the segment files in `directory`.
///
/// Any torn or corrupt trailing bytes in the highest-numbered segment are
/// discarded.  If the last segment file is unreadable, it is removed.
pub fn recover(directory: impl AsRef<Path>) -> Result<LocalLog, SegmentError> {
    let directory = directory.as_ref();
    fs::create_dir_all(directory)?;

    let mut entries: Vec<(u64, std::path::PathBuf)> = fs::read_dir(directory)?
        .filter_map(|entry| {
            let entry = entry.ok()?;
            let path = entry.path();
            let name = path.file_name().and_then(|n| n.to_str())?;
            let id_str = name.strip_prefix("segment_")?.strip_suffix(".segment")?;
            let id = id_str.parse::<u64>().ok()?;
            Some((id, path))
        })
        .collect();
    entries.sort_by_key(|e| e.0);

    let mut segments = Vec::new();
    let mut mmr = MerkleMountainRange::new();
    let mut total_records: u64 = 0;
    let mut next_segment_id: u64 = 0;

    if entries.is_empty() {
        return LocalLog::from_recovered(directory, crate::log::DEFAULT_MAX_RECORDS_PER_SEGMENT, segments, mmr, next_segment_id);
    }

    for (idx, (id, path)) in entries.iter().enumerate() {
        let is_last = idx == entries.len() - 1;

        let (records, truncate_to) = if is_last {
            match SegmentReader::read_valid_prefix(path) {
                Ok((records, valid_offset)) => {
                    let file_len = fs::metadata(path)?.len();
                    if valid_offset < file_len {
                        // Truncate a partially-written tail back to the last
                        // complete frame.  An empty-but-valid header is kept as
                        // the previous active writer.
                        let file = fs::OpenOptions::new().write(true).open(path)?;
                        file.set_len(valid_offset)?;
                        file.sync_all()?;
                    }
                    (records, Some(valid_offset))
                }
                Err(_) => {
                    // Unreadable last file: discard it.
                    let _ = fs::remove_file(path);
                    continue;
                }
            }
        } else {
            let records = SegmentReader::read_all(path)?;
            (records, None)
        };

        let _ = truncate_to; // non-last segments are not truncated

        for record in &records {
            mmr.append_record(record);
        }

        let start_offset = total_records;
        total_records += records.len() as u64;
        let segment = Segment::from_parts(*id, start_offset, records, path.clone());
        segments.push(segment);
        next_segment_id = id + 1;
    }

    LocalLog::from_recovered(directory, crate::log::DEFAULT_MAX_RECORDS_PER_SEGMENT, segments, mmr, next_segment_id)
}

#[cfg(test)]
mod tests {
    use super::*;
    use crate::log::LocalLog;
    use crate::segment::SegmentReader;
    use synapse_types::{Attribute, Diff, EntityId, Record, Timestamp, Value};
    use std::io::Write;
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
    fn recovery_after_simulated_crash() {
        let dir = TempDir::new().unwrap();

        // Build a log: with max 2 records per segment, after 4 appends segment 0
        // is closed and the current writer is segment 1 (records 2 and 3).
        let records: Vec<Record> = (0..5)
            .map(|i| make_record(i, (i + 1) * 10, Diff::Added))
            .collect();
        {
            let log = LocalLog::create(dir.path(), 2).unwrap();
            for record in records.iter().take(4) {
                log.append(std::slice::from_ref(record)).unwrap();
            }
            assert_eq!(log.segment_count(), 1);
            log.flush().unwrap();
            // `log` is dropped here, closing the BufWriter.
        }

        // Append a few garbage bytes to the current open segment to simulate a
        // crash mid-frame.
        let current_path = dir.path().join("segment_0000000001.segment");
        let mut file = std::fs::OpenOptions::new()
            
            .append(true)
            .open(&current_path)
            .unwrap();
        file.write_all(&[0u8; 3]).unwrap();
        file.sync_all().unwrap();
        drop(file);

        // Recover: the trailing 3 bytes should be truncated and the log should
        // still contain all 4 records.
        let recovered = recover(dir.path()).unwrap();
        assert_eq!(recovered.total_records(), 4);
        for (i, record) in records.iter().take(4).enumerate() {
            assert_eq!(
                recovered.read(synapse_types::LogPosition::from_offset(i as u64)),
                Some(record.clone())
            );
        }

        // The recovered root should match the MMR built from the first 4
        // records.
        let mut mmr = crate::merkle::MerkleMountainRange::new();
        for r in records.iter().take(4) {
            mmr.append_record(r);
        }
        assert_eq!(recovered.latest_root(), mmr.root());

        // The tail segment file should be readable in full after truncation.
        let tail_records = SegmentReader::read_all(&current_path).unwrap();
        assert_eq!(tail_records, records[2..4].to_vec());
    }

    #[test]
    fn recovery_keeps_appending() {
        let dir = TempDir::new().unwrap();
        let a = make_record(1, 10, Diff::Added);
        {
            let log = LocalLog::create(dir.path(), 100).unwrap();
            log.append(std::slice::from_ref(&a)).unwrap();
            log.flush().unwrap();
            // Drop `log` so the segment is fully closed and recoverable.
        }

        let recovered = recover(dir.path()).unwrap();
        assert_eq!(recovered.total_records(), 1);
        let b = make_record(2, 20, Diff::Added);
        let pos = recovered.append(std::slice::from_ref(&b)).unwrap();
        assert_eq!(pos.as_offset(), 1);
        assert_eq!(recovered.read(pos), Some(b));
    }

    #[test]
    fn recover_empty_directory() {
        let dir = TempDir::new().unwrap();
        let log = recover(dir.path()).unwrap();
        assert_eq!(log.total_records(), 0);
        assert!(log.latest_root().is_none());
    }
}
