//! Aureum core execution engine.
//!
//! Provides a deterministic, content-addressed DAG evaluator
//! for financial quantities with dimensional types and full lineage.

pub mod dag;
pub mod quantity;
pub mod strategy;
pub mod verifier;

pub use dag::{Dag, Node, NodeId};
pub use quantity::{Dimension, Quantity, Unit};
pub use strategy::Strategy;
pub use verifier::{Constraint, Verdict, Verifier};

/// Re-export common types.
pub mod prelude {
    pub use crate::{Dag, Dimension, NodeId, Quantity, Strategy, Unit};
}

#[derive(Debug, thiserror::Error)]
pub enum AureumError {
    #[error("dimension mismatch: expected {expected}, got {actual}")]
    DimensionMismatch { expected: String, actual: String },
    #[error("cyclic dependency detected in DAG")]
    CyclicDependency,
    #[error("unknown node id: {0}")]
    UnknownNode(String),
    #[error("verification failed: {0}")]
    VerificationFailed(String),
}

pub type Result<T> = std::result::Result<T, AureumError>;
