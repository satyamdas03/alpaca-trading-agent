//! Logical log positions.
//!
//! `LogPosition` is an absolute offset into the append-only SynapseDB log. It
//! is used by the log layer to map global sequence numbers to segment files and
//! local byte offsets.

use serde::{Deserialize, Serialize};
use std::fmt;

/// A logical address within the append-only SynapseDB log.
#[derive(
    Copy, Clone, Debug, Default, PartialEq, Eq, PartialOrd, Ord, Hash, Serialize, Deserialize,
)]
#[serde(transparent)]
pub struct LogPosition(pub u64);

impl LogPosition {
    /// Construct a `LogPosition` from a raw offset.
    pub const fn from_offset(offset: u64) -> Self {
        Self(offset)
    }

    /// Return the raw offset.
    pub const fn as_offset(&self) -> u64 {
        self.0
    }

    /// Advance the position by a delta.
    pub const fn add(&self, delta: u64) -> Self {
        Self(self.0 + delta)
    }
}

impl fmt::Display for LogPosition {
    fn fmt(&self, f: &mut fmt::Formatter<'_>) -> fmt::Result {
        write!(f, "{}", self.0)
    }
}

impl From<u64> for LogPosition {
    fn from(offset: u64) -> Self {
        Self(offset)
    }
}

impl From<LogPosition> for u64 {
    fn from(pos: LogPosition) -> Self {
        pos.0
    }
}

#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn offset_arithmetic() {
        let pos = LogPosition::from_offset(100);
        assert_eq!(pos.as_offset(), 100);
        assert_eq!(pos.add(50).as_offset(), 150);
    }

    #[test]
    fn serde_round_trip() {
        let pos = LogPosition::from_offset(4096);
        let json = serde_json::to_string(&pos).unwrap();
        assert_eq!(json, "4096");
        let back: LogPosition = serde_json::from_str(&json).unwrap();
        assert_eq!(back, pos);
    }
}
