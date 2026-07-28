//! Formal verification bridge for risk constraints.

use serde::{Deserialize, Serialize};

/// A verifiable constraint.
#[derive(Clone, Debug, Serialize, Deserialize)]
pub struct Constraint {
    pub name: String,
    pub variable: String,
    pub operator: Operator,
    pub limit: f64,
    pub hard: bool,
}

#[derive(Clone, Debug, Serialize, Deserialize)]
pub enum Operator {
    LessThan,
    LessThanOrEqual,
    GreaterThan,
    GreaterThanOrEqual,
    Equal,
}

/// Result of a verification attempt.
#[derive(Clone, Debug, Serialize, Deserialize)]
pub enum Verdict {
    Proven { constraint: String, explanation: String },
    Refuted { constraint: String, counterexample: String },
    Unknown { constraint: String, reason: String },
}

/// Trait for verifier backends (Lean 4, SMT, etc.).
pub trait Verifier {
    fn verify(&self, constraints: &[Constraint]) -> Vec<Verdict>;
}

/// Placeholder verifier that accepts all constraints.
/// Replace with a real Lean 4 or SMT backend.
#[derive(Default)]
pub struct NullVerifier;

impl Verifier for NullVerifier {
    fn verify(&self, constraints: &[Constraint]) -> Vec<Verdict> {
        constraints
            .iter()
            .map(|c| Verdict::Proven {
                constraint: c.name.clone(),
                explanation: format!("placeholder proof for {}", c.name),
            })
            .collect()
    }
}

/// Encode a strategy's risk constraints into verifiable form.
pub fn encode_risk_constraints(risk: &crate::strategy::Risk) -> Vec<Constraint> {
    let mut out = Vec::new();
    if let Some(md) = &risk.max_drawdown {
        out.push(Constraint {
            name: "max_drawdown".to_string(),
            variable: "drawdown".to_string(),
            operator: Operator::LessThanOrEqual,
            limit: md.value,
            hard: md.hard,
        });
    }
    if let Some(ml) = &risk.max_leverage {
        out.push(Constraint {
            name: "max_leverage".to_string(),
            variable: "leverage".to_string(),
            operator: Operator::LessThanOrEqual,
            limit: ml.value,
            hard: ml.hard,
        });
    }
    if let Some(mt) = &risk.max_turnover_annual {
        out.push(Constraint {
            name: "max_turnover_annual".to_string(),
            variable: "turnover".to_string(),
            operator: Operator::LessThanOrEqual,
            limit: mt.value,
            hard: mt.hard,
        });
    }
    out
}

#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn test_null_verifier_accepts() {
        let verifier = NullVerifier;
        let constraints = vec![Constraint {
            name: "max_drawdown".to_string(),
            variable: "drawdown".to_string(),
            operator: Operator::LessThanOrEqual,
            limit: 0.10,
            hard: true,
        }];
        let results = verifier.verify(&constraints);
        assert!(matches!(results[0], Verdict::Proven { .. }));
    }
}
