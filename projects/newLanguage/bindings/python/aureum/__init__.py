"""Aureum — self-proving semantic kernel for finance.

This is the Python developer API. The performance-critical execution engine
will be backed by the Rust `aureum-core` crate via PyO3; the pure-Python
implementation below is the MVP scaffolding.
"""

from .strategy import Strategy
from .quantity import Quantity, Unit, Dimension
from .dag import Dag, Node

__all__ = ["Strategy", "Quantity", "Unit", "Dimension", "Dag", "Node"]
