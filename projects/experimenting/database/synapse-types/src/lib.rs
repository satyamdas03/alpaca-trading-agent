//! Shared core types for the SynapseDB temporal differential database.
//!
//! This crate defines the cross-cutting data model used by both the log layer
//! and the CLI: entity identifiers, attributed values, timestamps, differential
//! updates, immutable records, and logical log positions.

pub mod entity;
pub mod attribute;
pub mod value;
pub mod timestamp;
pub mod diff;
pub mod record;
pub mod log_position;

pub use entity::EntityId;
pub use attribute::Attribute;
pub use value::Value;
pub use timestamp::Timestamp;
pub use diff::Diff;
pub use record::Record;
pub use log_position::LogPosition;
