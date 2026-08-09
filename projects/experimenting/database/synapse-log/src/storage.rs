//! Persistent log storage.
//!
//! This module will implement `LogStorage`, the high-level disk layout that
//! manages a sequence of `Segment` files plus an index. Responsibilities include:
//!
//! - Opening and creating log directories.
//! - Mapping global `LogPosition`s to the correct segment and local offset.
//! - Coordinating append operations across segments under async concurrency.
//! - Flushing data to durable storage and tracking high-water marks.

/// Manages the on-disk layout of segment files and append coordination.
pub struct LogStorage;
