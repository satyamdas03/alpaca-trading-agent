//! Attribute names.
//!
//! `Attribute` is a compact, validated newtype around a UTF-8 string.
//! Attributes act as the column dimension in the entity-attribute-value model
//! and support efficient comparison and serialisation.

use serde::{Deserialize, Serialize};
use std::fmt;

/// Names an attribute (property) of an entity.
#[derive(Clone, Debug, Default, PartialEq, Eq, PartialOrd, Ord, Hash, Serialize, Deserialize)]
#[serde(transparent)]
pub struct Attribute(pub String);

impl Attribute {
    /// Construct an `Attribute` from any string-like value.
    pub fn new(s: impl Into<String>) -> Self {
        Self(s.into())
    }

    /// Borrow the underlying string slice.
    pub fn as_str(&self) -> &str {
        &self.0
    }

    /// Consume the wrapper and return the owned string.
    pub fn into_inner(self) -> String {
        self.0
    }
}

impl fmt::Display for Attribute {
    fn fmt(&self, f: &mut fmt::Formatter<'_>) -> fmt::Result {
        f.write_str(&self.0)
    }
}

impl From<String> for Attribute {
    fn from(s: String) -> Self {
        Self(s)
    }
}

impl From<&str> for Attribute {
    fn from(s: &str) -> Self {
        Self(s.to_string())
    }
}

impl From<Attribute> for String {
    fn from(attr: Attribute) -> Self {
        attr.0
    }
}

#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn constructors_and_display() {
        let a1 = Attribute::new("name");
        let a2 = Attribute::from("name".to_string());
        let a3: Attribute = "name".into();
        assert_eq!(a1, a2);
        assert_eq!(a2, a3);
        assert_eq!(a1.as_str(), "name");
        assert_eq!(format!("{}", a1), "name");
    }

    #[test]
    fn serde_round_trip() {
        let attr = Attribute::new("market-cap");
        let json = serde_json::to_string(&attr).unwrap();
        assert_eq!(json, "\"market-cap\"");
        let back: Attribute = serde_json::from_str(&json).unwrap();
        assert_eq!(back, attr);
    }
}
