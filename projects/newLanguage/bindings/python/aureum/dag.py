"""Deterministic, content-addressed DAG evaluator (MVP pure-Python)."""

from __future__ import annotations

import hashlib
from dataclasses import dataclass
from typing import Any, Dict, List, Set

from .quantity import Quantity


class NodeId:
    """Content-addressed node identifier."""

    def __init__(self, value: str) -> None:
        self.value = value

    @classmethod
    def from_content(cls, content: str) -> "NodeId":
        digest = hashlib.sha256(content.encode()).hexdigest()[:16]
        return cls(f"node_{digest}")

    def __eq__(self, other: object) -> bool:
        return isinstance(other, NodeId) and self.value == other.value

    def __hash__(self) -> int:
        return hash(self.value)

    def __repr__(self) -> str:
        return f"NodeId({self.value!r})"


@dataclass(frozen=True)
class Node:
    """A node in the computation DAG."""

    kind: str
    payload: Any

    def node_id(self) -> NodeId:
        import json

        content = json.dumps(
            {"kind": self.kind, "payload": str(self.payload)}, sort_keys=True
        )
        return NodeId.from_content(content)


class Dag:
    """A deterministic computation DAG."""

    def __init__(self) -> None:
        self._nodes: Dict[NodeId, Node] = {}
        self._edges: Dict[NodeId, Set[NodeId]] = {}

    def insert(self, node: Node) -> NodeId:
        node_id = node.node_id()
        if node_id in self._nodes and self._nodes[node_id] != node:
            raise RuntimeError("content-address collision detected")
        self._nodes[node_id] = node
        self._edges.setdefault(node_id, set())
        return node_id

    def connect(self, from_id: NodeId, to_id: NodeId) -> None:
        if from_id not in self._nodes:
            raise KeyError(f"unknown node {from_id}")
        if to_id not in self._nodes:
            raise KeyError(f"unknown node {to_id}")
        self._edges[from_id].add(to_id)
        if self._has_cycle(to_id):
            self._edges[from_id].remove(to_id)
            raise ValueError("cyclic dependency detected")

    def _has_cycle(self, start: NodeId) -> bool:
        visited: Set[NodeId] = set()
        stack: Set[NodeId] = set()

        def visit(node: NodeId) -> bool:
            if node in stack:
                return True
            if node in visited:
                return False
            visited.add(node)
            stack.add(node)
            for child in self._edges.get(node, set()):
                if visit(child):
                    return True
            stack.remove(node)
            return False

        return visit(start)

    def node(self, node_id: NodeId) -> Node | None:
        return self._nodes.get(node_id)

    def nodes(self) -> List[tuple[NodeId, Node]]:
        return list(self._nodes.items())

    def __repr__(self) -> str:
        return f"Dag(nodes={len(self._nodes)}, edges={sum(len(v) for v in self._edges.values())})"
