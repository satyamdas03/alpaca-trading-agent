//! Strategy DSL model for the Aureum Quant Kernel.

use serde::{Deserialize, Serialize};

/// Top-level strategy document.
#[derive(Clone, Debug, Serialize, Deserialize)]
pub struct Strategy {
    pub api_version: String,
    pub kind: String,
    pub metadata: Metadata,
    pub spec: Spec,
}

#[derive(Clone, Debug, Serialize, Deserialize)]
pub struct Metadata {
    pub name: String,
    #[serde(default)]
    pub description: String,
    #[serde(default)]
    pub tags: Vec<String>,
}

#[derive(Clone, Debug, Serialize, Deserialize)]
pub struct Spec {
    pub universe: Universe,
    pub schedule: Schedule,
    #[serde(default)]
    pub signals: Vec<Signal>,
    pub ranking: Ranking,
    pub weights: Weights,
    #[serde(default)]
    pub risk: Risk,
    pub execution: Execution,
    #[serde(default)]
    pub audit: Audit,
}

#[derive(Clone, Debug, Serialize, Deserialize)]
pub struct Universe {
    pub source: String,
    #[serde(default)]
    pub filter: UniverseFilter,
}

#[derive(Clone, Debug, Default, Serialize, Deserialize)]
pub struct UniverseFilter {
    #[serde(default)]
    pub sector: Option<String>,
    #[serde(default)]
    pub min_price: Option<f64>,
    #[serde(default)]
    pub min_adv20: Option<f64>,
}

#[derive(Clone, Debug, Serialize, Deserialize)]
pub struct Schedule {
    pub rebalance: String,
    pub lookback: String,
}

#[derive(Clone, Debug, Serialize, Deserialize)]
pub struct Signal {
    pub name: String,
    pub expr: String,
    #[serde(default)]
    pub r#type: String,
    #[serde(default)]
    pub description: String,
}

#[derive(Clone, Debug, Serialize, Deserialize)]
pub struct Ranking {
    pub by: String,
    #[serde(default)]
    pub ascending: bool,
}

#[derive(Clone, Debug, Serialize, Deserialize)]
#[serde(tag = "kind")]
pub enum Weights {
    Equal { top_n: f64 },
    RankScale { top_n: f64 },
    Custom { expr: String },
}

#[derive(Clone, Debug, Default, Serialize, Deserialize)]
pub struct Risk {
    #[serde(default)]
    pub max_drawdown: Option<ConstraintSpec>,
    #[serde(default)]
    pub max_leverage: Option<ConstraintSpec>,
    #[serde(default)]
    pub max_turnover_annual: Option<ConstraintSpec>,
}

#[derive(Clone, Debug, Serialize, Deserialize)]
pub struct ConstraintSpec {
    pub value: f64,
    #[serde(default)]
    pub hard: bool,
}

#[derive(Clone, Debug, Serialize, Deserialize)]
pub struct Execution {
    pub open: String,
    #[serde(default)]
    pub slippage: f64,
}

#[derive(Clone, Debug, Default, Serialize, Deserialize)]
pub struct Audit {
    #[serde(default)]
    pub lineage: String,
    #[serde(default)]
    pub deterministic: bool,
    #[serde(default)]
    pub deterministic_seed: Option<u64>,
}

impl Strategy {
    pub fn from_yaml(yaml: &str) -> anyhow::Result<Self> {
        let mut doc: Strategy = serde_yaml::from_str(yaml)?;
        // Normalize defaults after parsing.
        if doc.audit.lineage.is_empty() {
            doc.audit.lineage = "full".to_string();
        }
        Ok(doc)
    }
}

#[cfg(test)]
mod tests {
    use super::*;

    const SAMPLE: &str = include_str!("../../../examples/strategies/momentum.yaml");

    #[test]
    fn test_parse_sample_strategy() {
        let strategy = Strategy::from_yaml(SAMPLE).expect("failed to parse sample strategy");
        assert_eq!(strategy.metadata.name, "tech-momentum-sector-neutral");
        assert_eq!(strategy.spec.schedule.rebalance, "1M");
        assert_eq!(strategy.spec.signals.len(), 1);
    }
}
