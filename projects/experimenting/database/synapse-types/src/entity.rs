//! Entity identifiers.
//!
//! `EntityId` is an opaque, hashable, serialisable 128-bit identifier for a
//! logical entity. It is intentionally compact (fits in two registers) and
//! stable across time, serving as the primary key for every temporal
//! observation in SynapseDB.

use serde::{Deserialize, Serialize};
use std::fmt;

/// Uniquely identifies an entity in SynapseDB.
#[derive(
    Copy, Clone, Debug, Default, PartialEq, Eq, PartialOrd, Ord, Hash, Serialize, Deserialize,
)]
#[serde(transparent)]
pub struct EntityId(pub u128);

impl EntityId {
    /// Construct an `EntityId` from a raw 128-bit value.
    pub const fn from_u128(value: u128) -> Self {
        Self(value)
    }

    /// Return the underlying 128-bit value.
    pub const fn as_u128(&self) -> u128 {
        self.0
    }
}

impl fmt::Display for EntityId {
    fn fmt(&self, f: &mut fmt::Formatter<'_>) -> fmt::Result {
        write!(f, "{:032x}", self.0)
    }
}

impl From<u128> for EntityId {
    fn from(value: u128) -> Self {
        Self(value)
    }
}

impl From<EntityId> for u128 {
    fn from(id: EntityId) -> Self {
        id.0
    }
}

#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn round_trip_u128() {
        let id = EntityId::from_u128(0x0123_4567_89ab_cdef_0123_4567_89ab_cdef);
        assert_eq!(id.as_u128(), 0x0123_4567_89ab_cdef_0123_4567_89ab_cdef);
        assert_eq!(format!("{}", id), "0123456789abcdef0123456789abcdef");
    }

    #[test]
    fn serde_round_trip() {
        let id = EntityId::from_u128(42);
        let json = serde_json::to_string(&id).unwrap();
        assert_eq!(json, "42");
        let back: EntityId = serde_json::from_str(&json).unwrap();
        assert_eq!(back, id);
    }
}
