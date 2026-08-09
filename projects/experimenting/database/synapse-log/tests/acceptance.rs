//! Phase 0 acceptance test: 1M writes, crash, recover, read snapshot.

use std::time::Instant;
use synapse_log::{recover, LocalLog};
use synapse_types::{Attribute, EntityId, Record, Timestamp, Value};
use tempfile::TempDir;

fn make_record(idx: u64) -> Record {
    Record::add(
        EntityId::from_u128(idx as u128),
        Attribute::new("value"),
        Value::i64(idx as i64),
        Timestamp::from_nanos(idx),
    )
}

#[test]
#[ignore = "slow 1M-write acceptance test — run with `cargo test --test acceptance --release -- --ignored --nocapture`"]
fn one_million_writes_recover_and_snapshot() {
    let dir = TempDir::new().unwrap();
    let log = LocalLog::create(dir.path(), 100_000).unwrap();

    let n: u64 = 1_000_000;
    let batch_size: usize = 10_000;
    let start = Instant::now();
    for batch_start in (0..n).step_by(batch_size) {
        let batch_end = (batch_start + batch_size as u64).min(n);
        let batch: Vec<Record> = (batch_start..batch_end).map(make_record).collect();
        log.append(&batch).unwrap();
    }
    let write_elapsed = start.elapsed();
    let write_per_sec = n as f64 / write_elapsed.as_secs_f64();

    assert_eq!(log.total_records(), n);
    let root_before = log.latest_root().expect("root after writes");

    // Crash the log by flushing and dropping it.
    log.flush().unwrap();
    drop(log);

    // Recover and verify everything is still there.
    let recovered = recover(dir.path()).unwrap();
    assert_eq!(recovered.total_records(), n);
    assert_eq!(recovered.latest_root(), Some(root_before));

    // Read a few random offsets.
    for offset in [0, n / 2, n - 1] {
        let record = recovered
            .read(synapse_types::LogPosition::from_offset(offset))
            .unwrap_or_else(|| panic!("missing record at offset {}", offset));
        assert_eq!(record.entity_id, EntityId::from_u128(offset as u128));
    }

    // Snapshot as_of n/2 should contain exactly n/2 records.
    let snapshot = recovered.snapshot_as_of(Timestamp::from_nanos(n / 2));
    assert_eq!(snapshot.len() as u64, n / 2 + 1);
    assert_eq!(snapshot.first().unwrap().entity_id, EntityId::from_u128(0));
    assert_eq!(
        snapshot.last().unwrap().entity_id,
        EntityId::from_u128((n / 2) as u128)
    );

    // Append a small record after recovery to prove the log is writable again.
    let tail = make_record(n);
    let tail_pos = recovered.append(std::slice::from_ref(&tail)).unwrap();
    assert_eq!(tail_pos.as_offset(), n);
    assert_eq!(recovered.read(tail_pos), Some(tail));

    eprintln!(
        "1M writes: {:.3}s ({:.0} records/s), segments: {}",
        write_elapsed.as_secs_f64(),
        write_per_sec,
        recovered.segment_count()
    );
}
