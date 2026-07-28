//! PyO3 bindings for the Aureum core engine.

use aureum_core::{quantity::*, strategy::*, Dag, Node, NodeId, Quantity, Strategy};
use pyo3::prelude::*;
use pyo3::types::PyDict;

/// Parse a strategy YAML string into a Python dict representation.
#[pyfunction]
fn parse_strategy_yaml(yaml: String) -> PyResult<String> {
    let strategy = Strategy::from_yaml(&yaml).map_err(|e| {
        PyErr::new::<pyo3::exceptions::PyValueError, _>(format!("failed to parse strategy: {e}"))
    })?;
    serde_json::to_string_pretty(&strategy).map_err(|e| {
        PyErr::new::<pyo3::exceptions::PyRuntimeError, _>(format!("serialization failed: {e}"))
    })
}

/// Create a dimensionless quantity (for testing).
#[pyfunction]
fn make_quantity(value: f64, source: String) -> PyResult<String> {
    let q = Quantity::dimensionless(value, source);
    serde_json::to_string_pretty(&q).map_err(|e| {
        PyErr::new::<pyo3::exceptions::PyRuntimeError, _>(format!("serialization failed: {e}"))
    })
}

/// A Python wrapper around the Rust DAG.
#[pyclass]
struct PyDag {
    dag: Dag,
}

#[pymethods]
impl PyDag {
    #[new]
    fn new() -> Self {
        Self { dag: Dag::new() }
    }

    fn insert_constant(&mut self, value: f64, source: String) -> PyResult<String> {
        let node = Node::Constant(Quantity::dimensionless(value, source));
        let id = self.dag.insert(node);
        Ok(id.0)
    }

    fn insert_transform(&mut self,
        name: String,
        inputs: Vec<String>,
        body: String,
    ) -> PyResult<String> {
        let node = Node::Transform {
            name,
            inputs: inputs.into_iter().map(NodeId::new).collect(),
            body,
        };
        let id = self.dag.insert(node);
        Ok(id.0)
    }

    fn nodes(&self) -> PyResult<Vec<String>> {
        Ok(self.dag.nodes().into_iter().map(|(id, _)| id.0.clone()).collect())
    }
}

/// Python module definition.
#[pymodule]
fn aureum_py(m: &Bound<PyModule>) -> PyResult<()> {
    m.add_function(wrap_pyfunction!(parse_strategy_yaml, m)?)?;
    m.add_function(wrap_pyfunction!(make_quantity, m)?)?;
    m.add_class::<PyDag>()?;
    Ok(())
}
