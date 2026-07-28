//! Dimensional quantities for financial computations.

use serde::{Deserialize, Serialize};
use std::fmt;

/// A physical or financial dimension, e.g. `USD`, `shares`, `return`.
#[derive(Clone, Debug, PartialEq, Eq, Hash, Serialize, Deserialize)]
pub struct Dimension(String);

impl Dimension {
    pub fn new(name: impl Into<String>) -> Self {
        Self(name.into())
    }

    pub fn as_str(&self) -> &str {
        &self.0
    }
}

impl fmt::Display for Dimension {
    fn fmt(&self, f: &mut fmt::Formatter<'_>) -> fmt::Result {
        write!(f, "{}", self.0)
    }
}

/// A unit expressed as a dimension raised to an integer power.
#[derive(Clone, Debug, PartialEq, Eq, Hash, Serialize, Deserialize)]
pub struct Unit {
    dims: Vec<(Dimension, i32)>,
}

impl Unit {
    pub fn dimensionless() -> Self {
        Self { dims: vec![] }
    }

    pub fn base(dim: Dimension) -> Self {
        Self { dims: vec![(dim, 1)] }
    }

    pub fn multiply(&self, other: &Self) -> Self {
        let mut dims = self.dims.clone();
        for (dim, pow) in &other.dims {
            if let Some(existing) = dims.iter_mut().find(|(d, _)| d == dim) {
                existing.1 += pow;
            } else {
                dims.push((dim.clone(), *pow));
            }
        }
        dims.retain(|(_, pow)| *pow != 0);
        dims.sort_by(|a, b| a.0.as_str().cmp(b.0.as_str()));
        Self { dims }
    }

    pub fn divide(&self, other: &Self) -> Self {
        let mut dims = self.dims.clone();
        for (dim, pow) in &other.dims {
            if let Some(existing) = dims.iter_mut().find(|(d, _)| d == dim) {
                existing.1 -= pow;
            } else {
                dims.push((dim.clone(), -*pow));
            }
        }
        dims.retain(|(_, pow)| *pow != 0);
        dims.sort_by(|a, b| a.0.as_str().cmp(b.0.as_str()));
        Self { dims }
    }

    pub fn is_compatible(&self, other: &Self) -> bool {
        self.dims == other.dims
    }
}

impl fmt::Display for Unit {
    fn fmt(&self, f: &mut fmt::Formatter<'_>) -> fmt::Result {
        if self.dims.is_empty() {
            return write!(f, "1");
        }
        let num: Vec<_> = self
            .dims
            .iter()
            .filter(|(_, p)| *p > 0)
            .map(|(d, p)| {
                if *p == 1 {
                    d.to_string()
                } else {
                    format!("{}^{}", d, p)
                }
            })
            .collect();
        let den: Vec<_> = self
            .dims
            .iter()
            .filter(|(_, p)| *p < 0)
            .map(|(d, p)| {
                let abs = p.abs();
                if abs == 1 {
                    d.to_string()
                } else {
                    format!("{}^{}", d, abs)
                }
            })
            .collect();
        if den.is_empty() {
            write!(f, "{}", num.join(" * "))
        } else if num.is_empty() {
            write!(f, "1 / {}", den.join(" * "))
        } else {
            write!(f, "{} / {}", num.join(" * "), den.join(" * "))
        }
    }
}

/// A numeric value carrying a unit and provenance.
#[derive(Clone, Debug, PartialEq, Serialize, Deserialize)]
pub struct Quantity {
    pub value: f64,
    pub unit: Unit,
    pub source: String,
}

impl Quantity {
    pub fn new(value: f64, unit: Unit, source: impl Into<String>) -> Self {
        Self {
            value,
            unit,
            source: source.into(),
        }
    }

    pub fn dimensionless(value: f64, source: impl Into<String>) -> Self {
        Self::new(value, Unit::dimensionless(), source)
    }

    /// Adds two quantities only if their units match.
    pub fn add(&self, other: &Self) -> crate::Result<Self> {
        if !self.unit.is_compatible(&other.unit) {
            return Err(crate::AureumError::DimensionMismatch {
                expected: self.unit.to_string(),
                actual: other.unit.to_string(),
            });
        }
        Ok(Self {
            value: self.value + other.value,
            unit: self.unit.clone(),
            source: format!("{} + {}", self.source, other.source),
        })
    }

    /// Multiplies two quantities, combining their units.
    pub fn multiply(&self, other: &Self) -> Self {
        Self {
            value: self.value * other.value,
            unit: self.unit.multiply(&other.unit),
            source: format!("{} * {}", self.source, other.source),
        }
    }

    /// Divides two quantities, combining their units.
    pub fn divide(&self, other: &Self) -> Self {
        Self {
            value: self.value / other.value,
            unit: self.unit.divide(&other.unit),
            source: format!("{} / {}", self.source, other.source),
        }
    }
}

#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn test_unit_multiply_divide() {
        let usd = Unit::base(Dimension::new("USD"));
        let share = Unit::base(Dimension::new("share"));
        let position = usd.multiply(&share);
        assert_eq!(position.to_string(), "USD * share");

        let price = usd.divide(&share);
        assert_eq!(price.to_string(), "USD / share");
    }

    #[test]
    fn test_quantity_add_compatible() {
        let a = Quantity::new(100.0, Unit::base(Dimension::new("USD")), "a");
        let b = Quantity::new(50.0, Unit::base(Dimension::new("USD")), "b");
        let c = a.add(&b).unwrap();
        assert_eq!(c.value, 150.0);
    }

    #[test]
    fn test_quantity_add_incompatible_fails() {
        let a = Quantity::new(100.0, Unit::base(Dimension::new("USD")), "a");
        let b = Quantity::new(50.0, Unit::base(Dimension::new("EUR")), "b");
        assert!(a.add(&b).is_err());
    }
}
