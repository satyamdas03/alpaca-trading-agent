//! Deterministic, content-addressed directed acyclic graph evaluator.

use petgraph::graph::{DiGraph, NodeIndex};
use serde::{Deserialize, Serialize};
use sha2::{Digest, Sha256};
use std::collections::HashMap;

use crate::{AureumError, Quantity, Result};

/// Unique identifier for a DAG node.
#[derive(Clone, Debug, PartialEq, Eq, Hash, Serialize, Deserialize)]
pub struct NodeId(pub String);

impl NodeId {
    pub fn new(id: impl Into<String>) -> Self {
        Self(id.into())
    }

    pub fn from_content(content: &str) -> Self {
        let mut hasher = Sha256::new();
        hasher.update(content.as_bytes());
        let result = hasher.finalize();
        Self(format!("node_{:016x}", u128::from_be_bytes(result[..16].try_into().unwrap())))
    }
}

/// A node in the computation DAG.
#[derive(Clone, Debug, Serialize, Deserialize)]
pub enum Node {
    /// A constant value with provenance.
    Constant(Quantity),
    /// A pure transform over input nodes.
    Transform {
        name: String,
        inputs: Vec<NodeId>,
        /// Serialized expression body used for hashing.
        body: String,
    },
}

impl Node {
    pub fn id(&self) -> NodeId {
        match self {
            Node::Constant(q) => NodeId::from_content(&format!("const:{}", serde_json::to_string(q).unwrap())),
            Node::Transform { name, inputs, body } => {
                let mut content = name.clone();
                for input in inputs {
                    content.push_str(&input.0);
                }
                content.push_str(body);
                NodeId::from_content(&content)
            }
        }
    }
}

/// A deterministic computation DAG.
pub struct Dag {
    graph: DiGraph<Node, ()>,
    index: HashMap<NodeId, NodeIndex>,
}

impl Default for Dag {
    fn default() -> Self {
        Self::new()
    }
}

impl Dag {
    pub fn new() -> Self {
        Self {
            graph: DiGraph::new(),
            index: HashMap::new(),
        }
    }

    /// Insert a node and return its canonical id.
    pub fn insert(&mut self, node: Node) -> NodeId {
        let id = node.id();
        if let Some(existing) = self.index.get(&id) {
            // Content-addressed: same content = same node.
            if &self.graph[*existing] != &node {
                // Should be impossible if id is a true hash.
                panic!("content-address collision detected");
            }
            return id;
        }
        let idx = self.graph.add_node(node);
        self.index.insert(id.clone(), idx);
        id
    }

    /// Add a dependency edge from `from` to `to`.
    pub fn connect(&mut self, from: &NodeId, to: &NodeId) -> Result<()> {
        let from_idx = self
            .index
            .get(from)
            .ok_or_else(|| AureumError::UnknownNode(from.0.clone()))?;
        let to_idx = self
            .index
            .get(to)
            .ok_or_else(|| AureumError::UnknownNode(to.0.clone()))?;
        self.graph.add_edge(*from_idx, *to_idx, ());
        if petgraph::algo::is_cyclic_directed(&self.graph) {
            // Remove the edge we just added.
            self.graph
                .find_edge(*from_idx, *to_idx)
                .and_then(|e| {
                    self.graph.remove_edge(e);
                    Some(())
                });
            return Err(AureumError::CyclicDependency);
        }
        Ok(())
    }

    pub fn node(&self, id: &NodeId) -> Option<&Node> {
        self.index.get(id).map(|idx| &self.graph[*idx])
    }

    pub fn nodes(&self) -> Vec<(&NodeId, &Node)> {
        self.index
            .iter()
            .map(|(id, idx)| (id, &self.graph[*idx]))
            .collect()
    }
}

#[cfg(test)]
mod tests {
    use super::*;
    use crate::{Dimension, Quantity, Unit};

    #[test]
    fn test_dag_insert_and_connect() {
        let mut dag = Dag::new();
        let a = dag.insert(Node::Constant(Quantity::dimensionless(1.0, "test")));
        let b = dag.insert(Node::Constant(Quantity::dimensionless(2.0, "test")));
        let t = dag.insert(Node::Transform {
            name: "sum".to_string(),
            inputs: vec![a.clone(), b.clone()],
            body: "a + b".to_string(),
        });
        dag.connect(&a, &t).unwrap();
        dag.connect(&b, &t).unwrap();
        assert_eq!(dag.nodes().len(), 3);
    }

    #[test]
    fn test_dag_detects_cycle() {
        let mut dag = Dag::new();
        let a = dag.insert(Node::Constant(Quantity::dimensionless(1.0, "test")));
        let b = dag.insert(Node::Transform {
            name: "id".to_string(),
            inputs: vec![a.clone()],
            body: "x".to_string(),
        });
        dag.connect(&a, &b).unwrap();
        let result = dag.connect(&b, &a);
        assert!(matches!(result, Err(AureumError::CyclicDependency)));
    }
}
