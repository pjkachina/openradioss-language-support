"""Core data models representing a parsed CAE deck."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any


@dataclass
class Material:
    id: int
    name: str
    law: str  # ELAST, PLAS_JOHNS, PLAS_ZERIL, VOID, etc.
    rho: float | None = None
    E: float | None = None        # Young's modulus
    nu: float | None = None       # Poisson's ratio
    yield_stress: float | None = None
    raw_fields: dict[str, Any] = field(default_factory=dict)


@dataclass
class ShellProperty:
    id: int
    name: str
    thickness: float | None = None
    ishell: int | None = None     # element formulation
    raw_fields: dict[str, Any] = field(default_factory=dict)


@dataclass
class SolidProperty:
    id: int
    name: str
    isolid: int | None = None
    raw_fields: dict[str, Any] = field(default_factory=dict)


@dataclass
class Part:
    id: int
    name: str
    mat_id: int | None = None
    prop_id: int | None = None


@dataclass
class BoundaryCondition:
    id: int
    name: str
    tx: bool = False  # translation X constrained
    ty: bool = False
    tz: bool = False
    rx: bool = False  # rotation X constrained
    ry: bool = False
    rz: bool = False


@dataclass
class Load:
    id: int
    name: str
    load_type: str  # GRAV, CLOAD, PRESSURE
    raw_fields: dict[str, Any] = field(default_factory=dict)


@dataclass
class Contact:
    id: int
    name: str
    contact_type: str  # TYPE7, TYPE11, etc.
    raw_fields: dict[str, Any] = field(default_factory=dict)


@dataclass
class Deck:
    filename: str
    materials: dict[int, Material] = field(default_factory=dict)
    shell_props: dict[int, ShellProperty] = field(default_factory=dict)
    solid_props: dict[int, SolidProperty] = field(default_factory=dict)
    parts: dict[int, Part] = field(default_factory=dict)
    bcs: dict[int, BoundaryCondition] = field(default_factory=dict)
    loads: dict[int, Load] = field(default_factory=dict)
    contacts: dict[int, Contact] = field(default_factory=dict)
    node_count: int = 0
    shell_count: int = 0
    solid_count: int = 0
    parameters: dict[str, str] = field(default_factory=dict)
