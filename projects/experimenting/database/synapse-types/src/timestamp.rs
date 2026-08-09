//! Logical timestamps.
//!
//! `Timestamp` is a monotonic, comparable 64-bit value. It may represent
//! wall-clock nanoseconds since the Unix epoch or a logical Lamport-style
//! counter, depending on the deployment mode.

use serde::{Deserialize, Serialize};
use std::fmt;
use std::time::{SystemTime, UNIX_EPOCH};

/// A logical point in time used to order observations.
#[derive(
    Copy, Clone, Debug, Default, PartialEq, Eq, PartialOrd, Ord, Hash, Serialize, Deserialize,
)]
#[serde(transparent)]
pub struct Timestamp(pub u64);

impl Timestamp {
    /// Construct a `Timestamp` from a raw nanosecond or logical-clock value.
    pub const fn from_nanos(nanos: u64) -> Self {
        Self(nanos)
    }

    /// Return the underlying raw value.
    pub const fn as_nanos(&self) -> u64 {
        self.0
    }

    /// Construct a timestamp from the current system clock.
    ///
    /// Returns `None` if the system time is before the Unix epoch.
    pub fn now() -> Option<Self> {
        let elapsed = SystemTime::now().duration_since(UNIX_EPOCH).ok()?;
        Some(Self(elapsed.as_nanos() as u64))
    }
}

impl fmt::Display for Timestamp {
    fn fmt(&self, f: &mut fmt::Formatter<'_>) -> fmt::Result {
        write!(f, "{}", self.0)
    }
}

impl From<u64> for Timestamp {
    fn from(nanos: u64) -> Self {
        Self(nanos)
    }
}

impl From<Timestamp> for u64 {
    fn from(ts: Timestamp) -> Self {
        ts.0
    }
}

#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn ordering() {
        assert!(Timestamp::from_nanos(100) < Timestamp::from_nanos(200));
        assert_eq!(Timestamp::from_nanos(100), Timestamp::from_nanos(100));
    }

    #[test]
    fn serde_round_trip() {
        let ts = Timestamp::from_nanos(1_234_567_890);
        let json = serde_json::to_string(&ts).unwrap();
        assert_eq!(json, "1234567890");
        let back: Timestamp = serde_json::from_str(&json).unwrap();
        assert_eq!(back, ts);
    }
}
