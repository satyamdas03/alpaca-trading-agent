//! Temporal differential log for SynapseDB.
//!
//! This crate provides the append-only storage engine: fixed-size segment
//! files, an in-memory or on-disk Merkle Mountain Range (MMR) for
//! tamper-evident integrity, and crash recovery. It consumes `Diff` records
//! from `synapse-types` and emits queryable `LogPosition`s.

pub mod segment;
pub mod storage;
pub mod merkle;
pub mod recovery;
pub mod log;
pub mod compaction;

pub use segment::{Segment, SegmentError, SegmentReader, SegmentWriter};
pub use storage::LogStorage;
pub use merkle::{Hash, MerkleMountainRange, Mmr};
pub use recovery::recover;
pub use log::{LocalLog, DEFAULT_MAX_RECORDS_PER_SEGMENT};
pub use compaction::compact_segment;
