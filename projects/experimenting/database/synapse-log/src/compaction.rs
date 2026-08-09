//! Segment compaction.
//!
//! Compaction reduces the size of a closed segment by collapsing all
//! adds/retracts for the same `(entity, attribute, value)` triple down to a
//! single net multiplicity at the segment's maximum timestamp.
//!
//! The compacted segment is semantically equivalent for queries at the
//! segment's `max_timestamp` (and later), but it discards intermediate
//! timestamps inside the segment.

use crate::segment::Segment;
use synapse_types::Record;

/// Compact a closed segment, returning a new in-memory segment with the same id
/// and start offset but with records collapsed to net multiplicities.
///
/// For each distinct `(entity, attribute, value)` triple, all `Added` and
/// `Retracted` records are summed.  A positive net count is emitted as that
/// many `Added` records; a negative net count is emitted as retractions.  A zero
/// net count disappears entirely.
pub fn compact_segment(old: &Segment) -> Segment {
    // Value does not implement Hash or Eq, so we group by linear search.
    type Group = ((synapse_types::EntityId, synapse_types::Attribute, synapse_types::Value), (i64, usize));
    let mut groups: Vec<Group> = Vec::new();

    for (idx, record) in old.records().iter().enumerate() {
        let key = (
            record.entity_id,
            record.attribute.clone(),
            record.value.clone(),
        );
        match groups.iter_mut().find(|(k, _)| *k == key) {
            Some((_, (net, _))) => {
                *net += record.diff.value();
            }
            None => {
                groups.push((key, (record.diff.value(), idx)));
            }
        }
    }

    groups.sort_by_key(|a| a.1.1);

    let max_ts = old.max_timestamp();
    let mut compacted = Vec::new();
    for ((entity_id, attribute, value), (net, _)) in groups {
        if net > 0 {
            for _ in 0..net {
                compacted.push(Record::add(entity_id, attribute.clone(), value.clone(), max_ts));
            }
        } else if net < 0 {
            for _ in 0..(-net) {
                compacted.push(Record::retract(
                    entity_id,
                    attribute.clone(),
                    value.clone(),
                    max_ts,
                ));
            }
        }
    }

    Segment::from_parts(old.id(), old.start_offset(), compacted, old.path().to_path_buf())
}

#[cfg(test)]
mod tests {
    use super::*;
    use synapse_types::{Diff, EntityId, Record, Timestamp, Value};

    #[test]
    fn compact_cancels_add_then_retract() {
        let records = vec![
            Record::add(EntityId::from_u128(1), "name", Value::string("alice"), Timestamp::from_nanos(10)),
            Record::retract(EntityId::from_u128(1), "name", Value::string("alice"), Timestamp::from_nanos(20)),
        ];
        let segment = Segment::from_parts(0, 0, records, std::path::PathBuf::from("/tmp/seg"));
        let compacted = compact_segment(&segment);
        assert!(compacted.records().is_empty());
    }

    #[test]
    fn compact_keeps_latest_add() {
        let records = vec![
            Record::add(EntityId::from_u128(1), "name", Value::string("alice"), Timestamp::from_nanos(10)),
            Record::retract(EntityId::from_u128(1), "name", Value::string("alice"), Timestamp::from_nanos(20)),
            Record::add(EntityId::from_u128(1), "name", Value::string("alice"), Timestamp::from_nanos(30)),
        ];
        let segment = Segment::from_parts(0, 0, records, std::path::PathBuf::from("/tmp/seg"));
        let compacted = compact_segment(&segment);
        assert_eq!(compacted.records().len(), 1);
        assert_eq!(compacted.records()[0].diff, Diff::Added);
        assert_eq!(compacted.records()[0].timestamp, Timestamp::from_nanos(30));
    }

    #[test]
    fn compact_preserves_different_values() {
        let records = vec![
            Record::add(EntityId::from_u128(1), "tag", Value::string("a"), Timestamp::from_nanos(10)),
            Record::add(EntityId::from_u128(1), "tag", Value::string("b"), Timestamp::from_nanos(20)),
        ];
        let segment = Segment::from_parts(0, 0, records, std::path::PathBuf::from("/tmp/seg"));
        let compacted = compact_segment(&segment);
        assert_eq!(compacted.records().len(), 2);
    }
}
