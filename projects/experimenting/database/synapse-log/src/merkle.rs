//! Merkle Mountain Range (MMR) integrity layer.
//!
//! This module provides `MerkleMountainRange`, a tamper-evident structure over
//! an append-only sequence of records. It supports:
//!
//! - Incremental appending with peak bagging.
//! - SHA-256 hashing of records and internal nodes.
//! - Inclusion proofs for any leaf by index.
//! - Independent verification of proofs against a root.

use sha2::{Digest, Sha256};
use synapse_types::Record;

/// A 32-byte SHA-256 digest.
pub type Hash = [u8; 32];

/// A node in the explicit MMR forest.
#[derive(Clone, Copy, Debug)]
struct Node {
    hash: Hash,
    left: Option<u64>,
    right: Option<u64>,
    parent: Option<u64>,
    height: u32,
}

/// Inclusion proof for a single leaf.
///
/// The verifier walks from the leaf up to its peak, combining `siblings` in
/// order. `directions[i]` is `true` when the sibling at level `i` is on the
/// right (i.e. the current node is the left child). After reconstructing the
/// peak, the verifier bags it with `other_peaks`.
#[derive(Clone, Debug, PartialEq, Eq)]
pub struct Proof {
    /// Sibling hashes on the path from the leaf to its peak.
    pub siblings: Vec<Hash>,
    /// `directions[i]` is `true` when the sibling is to the right of the
    /// current node at level `i`.
    pub directions: Vec<bool>,
    /// All remaining peaks (left and right of the reconstructed peak), in
    /// left-to-right order.
    pub other_peaks: Vec<Hash>,
}

/// A Merkle Mountain Range providing tamper-evident integrity for the append-only log.
#[derive(Clone, Debug, Default)]
pub struct MerkleMountainRange {
    /// All nodes, indexed by stable id.
    nodes: Vec<Node>,
    /// Peak node ids, ordered left-to-right.
    peaks: Vec<u64>,
    /// Maps leaf index -> leaf node id.
    leaf_nodes: Vec<u64>,
    /// Number of leaves appended so far.
    leaf_count: u64,
}

impl MerkleMountainRange {
    /// Create an empty MMR.
    pub fn new() -> Self {
        Self::default()
    }

    /// Number of leaves currently in the MMR.
    pub fn len(&self) -> u64 {
        self.leaf_count
    }

    /// `true` if no leaves have been appended.
    pub fn is_empty(&self) -> bool {
        self.leaf_count == 0
    }

    /// Compute the SHA-256 leaf hash of a serialised record.
    pub fn hash_record(record: &Record) -> Hash {
        let bytes = bincode::serialize(record).expect("record serialisation is infallible");
        let mut hasher = Sha256::new();
        hasher.update(&bytes);
        hasher.finalize().into()
    }

    /// Append the hash of a record and return its leaf index.
    pub fn append_record(&mut self, record: &Record) -> u64 {
        self.append(Self::hash_record(record))
    }

    /// Append a leaf hash and return its leaf index.
    pub fn append(&mut self, leaf_hash: Hash) -> u64 {
        let leaf_index = self.leaf_count;

        let leaf_id = self.nodes.len() as u64;
        self.nodes.push(Node {
            hash: leaf_hash,
            left: None,
            right: None,
            parent: None,
            height: 0,
        });
        self.leaf_nodes.push(leaf_id);

        let mut current_id = leaf_id;
        let mut n = leaf_index;

        // Merge while the current right-hand mountain has a same-height
        // neighbour to its left. The number of merges equals the number of
        // trailing 1-bits in `leaf_index`.
        while n & 1 == 1 {
            let left_id = self
                .peaks
                .pop()
                .expect("MMR invariant: a left peak must exist when n & 1 == 1");
            let left_hash = self.nodes[left_id as usize].hash;
            let right_hash = self.nodes[current_id as usize].hash;
            let parent_hash = hash_pair(&left_hash, &right_hash);
            let parent_height = self.nodes[current_id as usize].height + 1;

            let parent_id = self.nodes.len() as u64;
            self.nodes.push(Node {
                hash: parent_hash,
                left: Some(left_id),
                right: Some(current_id),
                parent: None,
                height: parent_height,
            });
            self.nodes[left_id as usize].parent = Some(parent_id);
            self.nodes[current_id as usize].parent = Some(parent_id);

            current_id = parent_id;
            n >>= 1;
        }

        self.peaks.push(current_id);
        self.leaf_count += 1;
        leaf_index
    }

    /// Return the current root hash, or `None` if the MMR is empty.
    pub fn root(&self) -> Option<Hash> {
        if self.peaks.is_empty() {
            return None;
        }
        let peak_hashes: Vec<_> = self
            .peaks
            .iter()
            .map(|&id| self.nodes[id as usize].hash)
            .collect();
        Some(bag_peaks(&peak_hashes))
    }

    /// Produce an inclusion proof for the leaf at `leaf_index`.
    pub fn proof(&self, leaf_index: u64) -> Option<Proof> {
        if leaf_index >= self.leaf_count {
            return None;
        }

        let mut node_id = self.leaf_nodes[leaf_index as usize];
        let mut siblings = Vec::new();
        let mut directions = Vec::new();

        while let Some(parent_id) = self.nodes[node_id as usize].parent {
            let parent = &self.nodes[parent_id as usize];
            let is_left = parent.left == Some(node_id);
            let sibling_id = if is_left { parent.right.unwrap() } else { parent.left.unwrap() };
            siblings.push(self.nodes[sibling_id as usize].hash);
            directions.push(is_left); // sibling is right when current is left
            node_id = parent_id;
        }

        let peak_index = peak_index_for_leaf(leaf_index, self.leaf_count);
        let other_peaks: Vec<_> = self
            .peaks
            .iter()
            .enumerate()
            .filter(|(i, _)| *i != peak_index)
            .map(|(_, &id)| self.nodes[id as usize].hash)
            .collect();

        Some(Proof {
            siblings,
            directions,
            other_peaks,
        })
    }

    /// Verify that `leaf_hash` at `leaf_index` is included under `root`.
    pub fn verify(
        root: Hash,
        leaf_index: u64,
        leaf_count: u64,
        leaf_hash: Hash,
        proof: &Proof,
    ) -> bool {
        if leaf_index >= leaf_count {
            return false;
        }
        if proof.siblings.len() != proof.directions.len() {
            return false;
        }

        let mut current = leaf_hash;
        for (&sibling, &is_left) in proof.siblings.iter().zip(&proof.directions) {
            current = if is_left {
                hash_pair(&current, &sibling)
            } else {
                hash_pair(&sibling, &current)
            };
        }

        let peak_index = match peak_index_for_leaf(leaf_index, leaf_count) {
            idx if idx <= proof.other_peaks.len() => idx,
            _ => return false,
        };

        let mut peaks = proof.other_peaks.clone();
        peaks.insert(peak_index, current);

        bag_peaks(&peaks) == root
    }
}

/// Type alias kept for callers that prefer the shorter name.
pub type Mmr = MerkleMountainRange;

fn hash_pair(left: &Hash, right: &Hash) -> Hash {
    let mut hasher = Sha256::new();
    hasher.update(left);
    hasher.update(right);
    hasher.finalize().into()
}

fn bag_peaks(peaks: &[Hash]) -> Hash {
    if peaks.is_empty() {
        return [0u8; 32];
    }
    let mut root = peaks[0];
    for &peak in &peaks[1..] {
        root = hash_pair(&root, &peak);
    }
    root
}

/// Return the index (in left-to-right peak order) of the peak containing
/// `leaf_index` for an MMR with `leaf_count` leaves.
fn peak_index_for_leaf(leaf_index: u64, leaf_count: u64) -> usize {
    if leaf_count == 0 {
        return 0;
    }
    let mut remaining = leaf_index;
    let mut peak_size = 1u64 << (63 - leaf_count.leading_zeros());
    let mut index = 0usize;
    while peak_size > 0 {
        if leaf_count & peak_size != 0 {
            if remaining < peak_size {
                return index;
            }
            remaining -= peak_size;
            index += 1;
        }
        peak_size >>= 1;
    }
    index
}

#[cfg(test)]
mod tests {
    use super::*;
    use synapse_types::{Attribute, Diff, EntityId, Record, Timestamp, Value};

    fn dummy_record(idx: u64) -> Record {
        Record::new(
            EntityId::from_u128(idx as u128),
            Attribute::new("test"),
            Value::i64(idx as i64),
            Timestamp::from_nanos(idx),
            if idx & 1 == 0 { Diff::Added } else { Diff::Retracted },
        )
    }

    #[test]
    fn hundred_appends_verify() {
        let mut mmr = MerkleMountainRange::new();
        let mut records = Vec::with_capacity(100);

        for i in 0..100 {
            let record = dummy_record(i);
            let idx = mmr.append_record(&record);
            assert_eq!(idx, i);
            records.push(record);
        }

        let root = mmr.root().expect("root exists after appends");

        for i in 0..100 {
            let proof = mmr.proof(i).expect("proof exists for every leaf");
            assert!(MerkleMountainRange::verify(
                root,
                i,
                mmr.len(),
                MerkleMountainRange::hash_record(&records[i as usize]),
                &proof
            ));
        }
    }

    #[test]
    fn tampered_record_fails() {
        let mut mmr = MerkleMountainRange::new();
        let records: Vec<_> = (0..20).map(dummy_record).collect();
        for r in &records {
            mmr.append_record(r);
        }

        let root = mmr.root().unwrap();
        let proof = mmr.proof(5).unwrap();

        let mut bad_hash = MerkleMountainRange::hash_record(&records[5]);
        bad_hash[0] ^= 0xff;

        assert!(!MerkleMountainRange::verify(root, 5, mmr.len(), bad_hash, &proof));
    }

    #[test]
    fn tampered_root_fails() {
        let mut mmr = MerkleMountainRange::new();
        let records: Vec<_> = (0..20).map(dummy_record).collect();
        for r in &records {
            mmr.append_record(r);
        }

        let mut root = mmr.root().unwrap();
        root[0] ^= 0xff;

        let proof = mmr.proof(5).unwrap();
        let leaf_hash = MerkleMountainRange::hash_record(&records[5]);
        assert!(!MerkleMountainRange::verify(root, 5, mmr.len(), leaf_hash, &proof));
    }

    #[test]
    fn tampered_sibling_fails() {
        let mut mmr = MerkleMountainRange::new();
        let records: Vec<_> = (0..20).map(dummy_record).collect();
        for r in &records {
            mmr.append_record(r);
        }

        let root = mmr.root().unwrap();
        let mut proof = mmr.proof(5).unwrap();
        if !proof.siblings.is_empty() {
            proof.siblings[0][0] ^= 0xff;
            let leaf_hash = MerkleMountainRange::hash_record(&records[5]);
            assert!(!MerkleMountainRange::verify(root, 5, mmr.len(), leaf_hash, &proof));
        }
    }

    #[test]
    fn empty_mmr_has_no_root() {
        let mmr = MerkleMountainRange::new();
        assert!(mmr.root().is_none());
        assert!(mmr.is_empty());
    }

    #[test]
    fn peak_index_for_leaf_cases() {
        // 13 = 8 + 4 + 1: peaks cover [0..8), [8..12), [12..13).
        assert_eq!(peak_index_for_leaf(0, 13), 0);
        assert_eq!(peak_index_for_leaf(7, 13), 0);
        assert_eq!(peak_index_for_leaf(8, 13), 1);
        assert_eq!(peak_index_for_leaf(11, 13), 1);
        assert_eq!(peak_index_for_leaf(12, 13), 2);
    }
}
