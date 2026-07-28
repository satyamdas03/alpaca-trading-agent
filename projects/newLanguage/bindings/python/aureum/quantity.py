"""Dimensional quantities for financial computations (MVP pure-Python)."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Dict


class Dimension:
    """A physical or financial dimension, e.g. USD, shares, return."""

    def __init__(self, name: str) -> None:
        self.name = name

    def __eq__(self, other: object) -> bool:
        return isinstance(other, Dimension) and self.name == other.name

    def __hash__(self) -> int:
        return hash(self.name)

    def __repr__(self) -> str:
        return f"Dimension({self.name!r})"

    def __str__(self) -> str:
        return self.name


class Unit:
    """A unit expressed as a dimension raised to an integer power."""

    def __init__(self, dims: Dict[Dimension, int] | None = None) -> None:
        self.dims: Dict[Dimension, int] = {}
        if dims:
            for dim, power in dims.items():
                if power != 0:
                    self.dims[dim] = self.dims.get(dim, 0) + power
            self.dims = {d: p for d, p in self.dims.items() if p != 0}

    @classmethod
    def dimensionless(cls) -> "Unit":
        return cls({})

    @classmethod
    def base(cls, dim: Dimension) -> "Unit":
        return cls({dim: 1})

    def multiply(self, other: "Unit") -> "Unit":
        merged = dict(self.dims)
        for dim, power in other.dims.items():
            merged[dim] = merged.get(dim, 0) + power
        return Unit(merged)

    def divide(self, other: "Unit") -> "Unit":
        merged = dict(self.dims)
        for dim, power in other.dims.items():
            merged[dim] = merged.get(dim, 0) - power
        return Unit(merged)

    def is_compatible(self, other: "Unit") -> bool:
        return self.dims == other.dims

    def __eq__(self, other: object) -> bool:
        return isinstance(other, Unit) and self.dims == other.dims

    def __hash__(self) -> int:
        return hash(tuple(sorted((d.name, p) for d, p in self.dims.items())))

    def __repr__(self) -> str:
        return f"Unit({self.dims!r})"

    def __str__(self) -> str:
        if not self.dims:
            return "1"
        num = []
        den = []
        for dim, power in sorted(self.dims.items(), key=lambda x: x[0].name):
            if power > 0:
                num.append(f"{dim}^{power}" if power != 1 else str(dim))
            else:
                p = -power
                den.append(f"{dim}^{p}" if p != 1 else str(dim))
        if den and num:
            return " / ".join([" * ".join(num), " * ".join(den)])
        if den:
            return "1 / " + " * ".join(den)
        return " * ".join(num)


@dataclass(frozen=True)
class Quantity:
    """A numeric value carrying a unit and provenance."""

    value: float
    unit: Unit
    source: str

    @classmethod
    def dimensionless(cls, value: float, source: str = "") -> "Quantity":
        return cls(value, Unit.dimensionless(), source)

    def add(self, other: "Quantity") -> "Quantity":
        if not self.unit.is_compatible(other.unit):
            raise ValueError(
                f"dimension mismatch: cannot add {self.unit} to {other.unit}"
            )
        return Quantity(
            self.value + other.value,
            self.unit,
            f"({self.source} + {other.source})",
        )

    def multiply(self, other: "Quantity") -> "Quantity":
        return Quantity(
            self.value * other.value,
            self.unit.multiply(other.unit),
            f"({self.source} * {other.source})",
        )

    def divide(self, other: "Quantity") -> "Quantity":
        if other.value == 0:
            raise ZeroDivisionError("division by zero quantity")
        return Quantity(
            self.value / other.value,
            self.unit.divide(other.unit),
            f"({self.source} / {other.source})",
        )

    def __repr__(self) -> str:
        return f"Quantity({self.value}, {self.unit}, source={self.source!r})"
