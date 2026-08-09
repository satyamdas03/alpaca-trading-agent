//! Attribute values.
//!
//! `Value` is a serialisable sum type for the concrete values stored in
//! SynapseDB. It deliberately avoids `f32` and keeps byte payloads as a
//! distinct variant so that callers can round-trip binary data without loss.

use serde::{Deserialize, Serialize};
use std::fmt;

/// A concrete value attached to an entity attribute at a point in time.
#[derive(Clone, Debug, PartialEq, Serialize, Deserialize)]
#[serde(rename_all = "snake_case")]
pub enum Value {
    Null,
    Bool(bool),
    I64(i64),
    F64(f64),
    String(String),
    Bytes(Vec<u8>),
}

impl Value {
    /// Construct a `Value::Null`.
    pub fn null() -> Self {
        Self::Null
    }

    /// Construct a `Value::Bool`.
    pub fn bool(value: bool) -> Self {
        Self::Bool(value)
    }

    /// Construct a `Value::I64`.
    pub fn i64(value: i64) -> Self {
        Self::I64(value)
    }

    /// Construct a `Value::F64`.
    pub fn f64(value: f64) -> Self {
        Self::F64(value)
    }

    /// Construct a `Value::String`.
    pub fn string(s: impl Into<String>) -> Self {
        Self::String(s.into())
    }

    /// Construct a `Value::Bytes`.
    pub fn bytes(b: impl Into<Vec<u8>>) -> Self {
        Self::Bytes(b.into())
    }

    /// Returns `true` for `Value::Null`.
    pub fn is_null(&self) -> bool {
        matches!(self, Self::Null)
    }

    /// Try to interpret the value as `i64`.
    pub fn as_i64(&self) -> Option<i64> {
        match self {
            Self::I64(v) => Some(*v),
            _ => None,
        }
    }

    /// Try to interpret the value as `f64`.
    pub fn as_f64(&self) -> Option<f64> {
        match self {
            Self::F64(v) => Some(*v),
            _ => None,
        }
    }

    /// Try to interpret the value as `&str`.
    pub fn as_str(&self) -> Option<&str> {
        match self {
            Self::String(s) => Some(s.as_str()),
            _ => None,
        }
    }
}

impl fmt::Display for Value {
    fn fmt(&self, f: &mut fmt::Formatter<'_>) -> fmt::Result {
        match self {
            Self::Null => f.write_str("null"),
            Self::Bool(b) => write!(f, "{}", b),
            Self::I64(i) => write!(f, "{}", i),
            Self::F64(v) => write!(f, "{}", v),
            Self::String(s) => write!(f, "\"{}\"", s),
            Self::Bytes(b) => write!(f, "bytes({})", b.len()),
        }
    }
}

impl From<bool> for Value {
    fn from(v: bool) -> Self {
        Self::Bool(v)
    }
}

impl From<i64> for Value {
    fn from(v: i64) -> Self {
        Self::I64(v)
    }
}

impl From<i32> for Value {
    fn from(v: i32) -> Self {
        Self::I64(i64::from(v))
    }
}

impl From<f64> for Value {
    fn from(v: f64) -> Self {
        Self::F64(v)
    }
}

impl From<String> for Value {
    fn from(v: String) -> Self {
        Self::String(v)
    }
}

impl From<&str> for Value {
    fn from(v: &str) -> Self {
        Self::String(v.to_string())
    }
}

impl From<Vec<u8>> for Value {
    fn from(v: Vec<u8>) -> Self {
        Self::Bytes(v)
    }
}

#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn round_trip_json() {
        let value = Value::String("hello".to_string());
        let json = serde_json::to_string(&value).unwrap();
        assert_eq!(json, "{\"string\":\"hello\"}");
        let back: Value = serde_json::from_str(&json).unwrap();
        assert_eq!(back, value);
    }

    #[test]
    fn all_variants_serialize() {
        let values = vec![
            Value::null(),
            Value::bool(true),
            Value::i64(-42),
            Value::f64(std::f64::consts::PI),
            Value::string("synapse"),
            Value::bytes(vec![0xde, 0xad, 0xbe, 0xef]),
        ];
        for v in values {
            let json = serde_json::to_string(&v).unwrap();
            let back: Value = serde_json::from_str(&json).unwrap();
            assert_eq!(back, v);
        }
    }
}
