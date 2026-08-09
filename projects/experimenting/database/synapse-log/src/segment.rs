//! Segment file storage.
//!
//! A `Segment` is an immutable file containing a batch of `Record`s.  The on-disk
//! layout is intentionally simple and self-describing:
//!
//! ```text
//! [magic: 8 bytes "SYNAPSEG"]
//! [version: u16 LE]
//! [segment_id: u64 LE]
//! [frame]*
//!
//! frame = [payload_len: u64 LE] [payload: bincode(Record)] [checksum: 4 bytes]
//! ```
//!
//! The 4-byte checksum is the first four bytes of SHA-256(payload).  A torn or
//! corrupt frame at the end of the last segment is detected during recovery and
//! the file is truncated back to the last complete frame.

use sha2::{Digest, Sha256};
use std::fs::{File, OpenOptions};
use std::io::{BufReader, BufWriter, IntoInnerError, Read, Seek, Write};
use std::path::{Path, PathBuf};
use synapse_types::{Record, Timestamp};
use thiserror::Error;

const MAGIC: &[u8; 8] = b"SYNAPSEG";
const VERSION: u16 = 1;
const HEADER_SIZE: usize = 8 + 2 + 8;
const CHECKSUM_SIZE: usize = 4;

/// Errors that can occur when reading or writing a segment file.
#[derive(Debug, Error)]
pub enum SegmentError {
    /// Underlying I/O failure.
    #[error("io error: {0}")]
    Io(#[from] std::io::Error),

    /// The file header is not a recognised SynapseDB segment.
    #[error("segment corruption: {message}")]
    Corruption { message: String },

    /// Bincode (de)serialization failed.
    #[error("serialization error: {0}")]
    Bincode(#[from] bincode::Error),

    /// A frame was only partially written.
    #[error("torn write detected at offset {0}")]
    TornWrite(u64),
}

impl From<IntoInnerError<BufWriter<File>>> for SegmentError {
    fn from(err: IntoInnerError<BufWriter<File>>) -> Self {
        SegmentError::Io(err.into())
    }
}

/// Result alias for segment operations.
pub type SegmentResult<T> = Result<T, SegmentError>;

/// An immutable, in-memory view of a segment file.
#[derive(Clone, Debug)]
pub struct Segment {
    id: u64,
    start_offset: u64,
    records: Vec<Record>,
    max_timestamp: Timestamp,
    path: PathBuf,
}

impl Segment {
    /// Read an entire segment file, failing if any trailing bytes are not a
    /// complete, valid frame.
    pub fn open(path: impl AsRef<Path>, start_offset: u64) -> SegmentResult<Self> {
        let path = path.as_ref().to_path_buf();
        let records = SegmentReader::read_all(&path)?;
        let max_timestamp = records
            .iter()
            .map(|r| r.timestamp)
            .max()
            .unwrap_or_default();
        let id = read_segment_id(&path)?;
        Ok(Self {
            id,
            start_offset,
            records,
            max_timestamp,
            path,
        })
    }

    pub(crate) fn from_parts(
        id: u64,
        start_offset: u64,
        records: Vec<Record>,
        path: PathBuf,
    ) -> Self {
        let max_timestamp = records
            .iter()
            .map(|r| r.timestamp)
            .max()
            .unwrap_or_default();
        Self {
            id,
            start_offset,
            records,
            max_timestamp,
            path,
        }
    }

    pub(crate) fn set_start_offset(&mut self, offset: u64) {
        self.start_offset = offset;
    }

    /// The records stored in this segment, in append order.
    pub fn records(&self) -> &[Record] {
        &self.records
    }

    /// The segment's stable identifier.
    pub fn id(&self) -> u64 {
        self.id
    }

    /// The global log offset of the first record in this segment.
    pub fn start_offset(&self) -> u64 {
        self.start_offset
    }

    /// Number of records in the segment.
    pub fn len(&self) -> u64 {
        self.records.len() as u64
    }

    /// `true` if the segment contains no records.
    pub fn is_empty(&self) -> bool {
        self.records.is_empty()
    }

    /// The maximum timestamp observed in this segment.
    pub fn max_timestamp(&self) -> Timestamp {
        self.max_timestamp
    }

    /// The path of the backing segment file.
    pub fn path(&self) -> &Path {
        &self.path
    }
}

/// Writes length-prefixed, checksummed records to a new segment file.
pub struct SegmentWriter {
    id: u64,
    path: PathBuf,
    file: BufWriter<File>,
    records: Vec<Record>,
    max_timestamp: Timestamp,
}

impl std::fmt::Debug for SegmentWriter {
    fn fmt(&self, f: &mut std::fmt::Formatter<'_>) -> std::fmt::Result {
        f.debug_struct("SegmentWriter")
            .field("id", &self.id)
            .field("path", &self.path)
            .field("records", &self.records.len())
            .field("max_timestamp", &self.max_timestamp)
            .finish()
    }
}

impl SegmentWriter {
    /// Create a new segment file in `directory` with the given `segment_id`.
    pub fn create(directory: impl AsRef<Path>, segment_id: u64) -> SegmentResult<Self> {
        let path = segment_path(directory.as_ref(), segment_id);
        let file = OpenOptions::new()
            .create_new(true)
            .write(true)
            .open(&path)?;
        let mut file = BufWriter::new(file);
        write_header(&mut file, segment_id)?;
        Ok(Self {
            id: segment_id,
            path,
            file,
            records: Vec::new(),
            max_timestamp: Timestamp::default(),
        })
    }

    /// Append a single record to the segment.
    pub fn append(&mut self, record: &Record) -> SegmentResult<()> {
        let payload = bincode::serialize(record)?;
        let checksum = frame_checksum(&payload);

        self.file.write_all(&(payload.len() as u64).to_le_bytes())?;
        self.file.write_all(&payload)?;
        self.file.write_all(&checksum)?;

        self.max_timestamp = self.max_timestamp.max(record.timestamp);
        self.records.push(record.clone());
        Ok(())
    }

    /// Append a batch of records.
    pub fn append_batch(&mut self, records: &[Record]) -> SegmentResult<()> {
        for record in records {
            self.append(record)?;
        }
        Ok(())
    }

    /// Flush the underlying file buffer and fsync the file.
    pub fn flush(&mut self) -> SegmentResult<()> {
        self.file.flush()?;
        self.file.get_mut().sync_all()?;
        Ok(())
    }

    /// Finalise the segment by syncing it to disk and returning an in-memory
    /// `Segment` view.
    pub fn finalize(mut self) -> SegmentResult<Segment> {
        self.file.flush()?;
        let file = self.file.into_inner()?;
        file.sync_all()?;
        drop(file);
        Ok(Segment::from_parts(
            self.id,
            0,
            self.records,
            self.path,
        ))
    }

    /// Records buffered in the writer but not yet promoted to a closed segment.
    pub(crate) fn records(&self) -> &[Record] {
        &self.records
    }

    pub(crate) fn len(&self) -> usize {
        self.records.len()
    }
}

/// Reads records out of segment files.
pub struct SegmentReader;

impl SegmentReader {
    /// Read every complete record from a segment file.
    ///
    /// Returns `Err(SegmentError::TornWrite)` if the file ends with an
    /// incomplete frame.
    pub fn read_all(path: impl AsRef<Path>) -> SegmentResult<Vec<Record>> {
        let path = path.as_ref();
        let (records, valid_offset) = Self::read_valid_prefix(path)?;
        let file_len = std::fs::metadata(path)?.len();
        if valid_offset < file_len {
            return Err(SegmentError::TornWrite(valid_offset));
        }
        Ok(records)
    }

    /// Read all valid frames from the beginning of the file, stopping at the
    /// first torn or corrupt frame.  Returns the records and the byte offset
    /// immediately after the last valid frame.
    pub fn read_valid_prefix(path: impl AsRef<Path>) -> SegmentResult<(Vec<Record>, u64)> {
        let path = path.as_ref();
        let file = File::open(path)?;
        let mut reader = BufReader::new(file);

        let mut header = [0u8; HEADER_SIZE];
        match read_exact_or_eof(&mut reader, &mut header) {
            Ok(Some(())) => {}
            Ok(None) => return Ok((Vec::new(), 0)),
            Err(e) => return Err(e.into()),
        }
        validate_header(&header)?;

        let mut valid_offset = HEADER_SIZE as u64;
        let mut records = Vec::new();

        loop {
            let mut len_buf = [0u8; 8];
            match read_frame_part(&mut reader, &mut len_buf)? {
                Some(()) => {}
                None => break,
            }
            let payload_len = u64::from_le_bytes(len_buf) as usize;

            let mut payload = vec![0u8; payload_len];
            if read_frame_part(&mut reader, &mut payload)?.is_none() {
                break;
            }

            let mut checksum = [0u8; CHECKSUM_SIZE];
            if read_frame_part(&mut reader, &mut checksum)?.is_none() {
                break;
            }

            if checksum != frame_checksum(&payload) {
                break;
            }

            let record: Record = match bincode::deserialize(&payload) {
                Ok(r) => r,
                Err(_) => break,
            };

            records.push(record);
            valid_offset = reader.stream_position()?;
        }

        Ok((records, valid_offset))
    }
}

fn segment_path(directory: &Path, segment_id: u64) -> PathBuf {
    directory.join(format!("segment_{:010}.segment", segment_id))
}

fn write_header(writer: &mut impl Write, segment_id: u64) -> SegmentResult<()> {
    writer.write_all(MAGIC)?;
    writer.write_all(&VERSION.to_le_bytes())?;
    writer.write_all(&segment_id.to_le_bytes())?;
    Ok(())
}

fn validate_header(header: &[u8; HEADER_SIZE]) -> SegmentResult<()> {
    if &header[..8] != MAGIC {
        return Err(SegmentError::Corruption {
            message: "bad segment magic bytes".to_string(),
        });
    }
    let version = u16::from_le_bytes([header[8], header[9]]);
    if version != VERSION {
        return Err(SegmentError::Corruption {
            message: format!("unsupported segment version {}", version),
        });
    }
    Ok(())
}

fn read_segment_id(path: &Path) -> SegmentResult<u64> {
    let mut file = File::open(path)?;
    let mut header = [0u8; HEADER_SIZE];
    file.read_exact(&mut header)?;
    validate_header(&header)?;
    let id_bytes = &header[10..18];
    Ok(u64::from_le_bytes(id_bytes.try_into().unwrap()))
}

fn frame_checksum(payload: &[u8]) -> [u8; CHECKSUM_SIZE] {
    let hash = Sha256::digest(payload);
    let mut checksum = [0u8; CHECKSUM_SIZE];
    checksum.copy_from_slice(&hash[..CHECKSUM_SIZE]);
    checksum
}

/// Read a frame part, treating a partial trailing read as a torn write
/// rather than a hard error.
fn read_frame_part(reader: &mut impl Read, buf: &mut [u8]) -> SegmentResult<Option<()>> {
    match read_exact_or_eof(reader, buf) {
        Ok(x) => Ok(x),
        Err(e) if e.kind() == std::io::ErrorKind::UnexpectedEof => Ok(None),
        Err(e) => Err(e.into()),
    }
}

/// Read exactly `buf.len()` bytes, returning `Some(())` on success.
///
/// Returns `None` if the reader is already at EOF.  Returns an I/O error if a
/// partial read occurs.
fn read_exact_or_eof(reader: &mut impl Read, buf: &mut [u8]) -> std::io::Result<Option<()>> {
    let mut read = 0;
    while read < buf.len() {
        match reader.read(&mut buf[read..])? {
            0 => {
                if read == 0 {
                    return Ok(None);
                }
                return Err(std::io::Error::new(
                    std::io::ErrorKind::UnexpectedEof,
                    "partial frame read",
                ));
            }
            n => read += n,
        }
    }
    Ok(Some(()))
}

#[cfg(test)]
mod tests {
    use super::*;
    use synapse_types::{Attribute, Diff, EntityId, Record, Timestamp, Value};
    use tempfile::TempDir;

    fn dummy_records(count: u64) -> Vec<Record> {
        (0..count)
            .map(|i| {
                Record::new(
                    EntityId::from_u128(i as u128),
                    Attribute::new("price"),
                    Value::i64(i as i64),
                    Timestamp::from_nanos(i + 1),
                    if i % 2 == 0 { Diff::Added } else { Diff::Retracted },
                )
            })
            .collect()
    }

    #[test]
    fn segment_round_trip() {
        let dir = TempDir::new().unwrap();
        let records = dummy_records(5);

        let mut writer = SegmentWriter::create(dir.path(), 0).unwrap();
        writer.append_batch(&records).unwrap();
        let segment = writer.finalize().unwrap();
        assert_eq!(segment.len(), 5);
        assert_eq!(segment.id(), 0);

        let read = SegmentReader::read_all(segment.path()).unwrap();
        assert_eq!(read, records);
    }

    #[test]
    fn torn_write_detection() {
        let dir = TempDir::new().unwrap();
        let records = dummy_records(3);

        let mut writer = SegmentWriter::create(dir.path(), 0).unwrap();
        writer.append_batch(&records).unwrap();
        writer.flush().unwrap();

        // Corrupt the last byte of the file to simulate a torn final frame.
        let path = segment_path(dir.path(), 0);
        let mut bytes = std::fs::read(&path).unwrap();
        let last = bytes.len() - 1;
        bytes[last] ^= 0xff;
        std::fs::write(&path, &bytes).unwrap();

        // read_valid_prefix should return the first two complete frames.
        let (prefix, valid_offset) = SegmentReader::read_valid_prefix(&path).unwrap();
        assert_eq!(prefix.len(), 2);
        assert!(valid_offset < bytes.len() as u64);

        // read_all should report a torn write.
        assert!(matches!(
            SegmentReader::read_all(&path).unwrap_err(),
            SegmentError::TornWrite(_)
        ));
    }
}
