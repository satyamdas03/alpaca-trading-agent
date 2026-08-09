//! Immutable records.
//!
//! A `Record` is the atomic, immutable fact stored in the SynapseDB log. It
//! combines an entity, attribute, value, timestamp and a differential sign,
//! and is the input to both the append-only log and the temporal query engine.

use crate::{Attribute, Diff, EntityId, Timestamp, Value};
use serde::{Deserialize, Serialize};
use std::fmt;

/// A committed log record containing one differential fact.
#[derive(Clone, Debug, PartialEq, Serialize, Deserialize)]
pub struct Record {
    pub entity_id: EntityId,
    pub attribute: Attribute,
    pub value: Value,
    pub timestamp: Timestamp,
    pub diff: Diff,
}

impl Record {
    /// Construct a new record.
    pub fn new(
        entity_id: EntityId,
        attribute: impl Into<Attribute>,
        value: impl Into<Value>,
        timestamp: impl Into<Timestamp>,
        diff: Diff,
    ) -> Self {
        Self {
            entity_id,
            attribute: attribute.into(),
            value: value.into(),
            timestamp: timestamp.into(),
            diff,
        }
    }

    /// Convenience constructor for an `Added` fact.
    pub fn add(
        entity_id: EntityId,
        attribute: impl Into<Attribute>,
        value: impl Into<Value>,
        timestamp: impl Into<Timestamp>,
    ) -> Self {
        Self::new(entity_id, attribute, value, timestamp, Diff::Added)
    }

    /// Convenience constructor for a `Retracted` fact.
    pub fn retract(
        entity_id: EntityId,
        attribute: impl Into<Attribute>,
        value: impl Into<Value>,
        timestamp: impl Into<Timestamp>,
    ) -> Self {
        Self::new(entity_id, attribute, value, timestamp, Diff::Retracted)
    }
}

impl fmt::Display for Record {
    fn fmt(&self, f: &mut fmt::Formatter<'_>) -> fmt::Result {
        write!(
            f,
            "{} {} {} @ {} {}",
            self.entity_id, self.attribute, self.value, self.timestamp, self.diff
        )
    }
}

#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn construct_and_serialize() {
        let record = Record::add(
            EntityId::from_u128(1),
            "price",
            Value::f64(150.25),
            Timestamp::from_nanos(1_000_000),
        );
        assert_eq!(record.diff, Diff::Added);
        assert_eq!(record.value.as_f64(), Some(150.25));

        let json = serde_json::to_string(&record).unwrap();
        let back: Record = serde_json::from_str(&json).unwrap();
        assert_eq!(back, record);
    }

    #[test]
    fn display_record() {
        let record = Record::new(
            EntityId::from_u128(1),
            "price",
            Value::i64(100),
            Timestamp::from_nanos(1_000_000),
            Diff::Added,
        );
        let text = format!("{}", record);
        assert!(text.contains("price"));
        assert!(text.contains("100"));
        assert!(text.contains("+1"));
    }
}
