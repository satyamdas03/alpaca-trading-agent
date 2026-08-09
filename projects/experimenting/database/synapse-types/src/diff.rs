//! Differential updates.
//!
//! `Diff` is the atomic unit of change in SynapseDB. A fact is added with
//! `Diff::Added` (+1) and later retracted with `Diff::Retracted` (-1). Summing
//! the multiplicities for a given entity-attribute-value tuple yields its
//! current count in the temporal view.

use serde::{Deserialize, Serialize};
use std::fmt;

/// A single differential change to an entity-attribute-value fact.
#[derive(Copy, Clone, Debug, PartialEq, Eq, Hash, Serialize, Deserialize)]
#[serde(rename_all = "snake_case")]
pub enum Diff {
    /// Fact was inserted; multiplicity +1.
    Added,
    /// Fact was removed; multiplicity -1.
    Retracted,
}

impl Diff {
    /// Return the integer multiplicity: `+1` for `Added`, `-1` for `Retracted`.
    pub const fn value(&self) -> i64 {
        match self {
            Self::Added => 1,
            Self::Retracted => -1,
        }
    }

    /// Return the sign as `isize`.
    pub const fn sign(&self) -> i64 {
        self.value()
    }

    /// `true` if this diff adds a fact.
    pub const fn is_added(&self) -> bool {
        matches!(self, Self::Added)
    }

    /// `true` if this diff retracts a fact.
    pub const fn is_retracted(&self) -> bool {
        matches!(self, Self::Retracted)
    }
}

impl fmt::Display for Diff {
    fn fmt(&self, f: &mut fmt::Formatter<'_>) -> fmt::Result {
        match self {
            Self::Added => f.write_str("+1"),
            Self::Retracted => f.write_str("-1"),
        }
    }
}

#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn values_match_semantics() {
        assert_eq!(Diff::Added.value(), 1);
        assert_eq!(Diff::Retracted.value(), -1);
        assert!(Diff::Added.is_added());
        assert!(Diff::Retracted.is_retracted());
    }

    #[test]
    fn serde_round_trip() {
        let json = serde_json::to_string(&Diff::Added).unwrap();
        assert_eq!(json, "\"added\"");
        let back: Diff = serde_json::from_str(&json).unwrap();
        assert_eq!(back, Diff::Added);
    }
}
