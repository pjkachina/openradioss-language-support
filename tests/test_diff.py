"""Tests for the semantic diff engine."""

from pathlib import Path

import pytest

from decklens.diff.engine import Change, DiffEngine
from decklens.parsers.openradioss import parse_deck

FIXTURES = Path(__file__).parent / "fixtures"


@pytest.fixture
def deck_v1():
    return parse_deck(FIXTURES / "sample_v1.rad")


@pytest.fixture
def deck_v2():
    return parse_deck(FIXTURES / "sample_v2.rad")


@pytest.fixture
def changes(deck_v1, deck_v2):
    return DiffEngine().diff(deck_v1, deck_v2)


def _find(changes: list[Change], **kwargs) -> Change | None:
    for ch in changes:
        if all(getattr(ch, k) == v for k, v in kwargs.items()):
            return ch
    return None


def test_thickness_change_detected(changes):
    ch = next((c for c in changes if "thickness" in c.field and c.item_type == "PROP/SHELL"), None)
    assert ch is not None
    assert ch.old_value == pytest.approx(1.2)
    assert ch.new_value == pytest.approx(1.6)
    assert ch.percent_change == pytest.approx(33.333, abs=0.1)
    assert ch.severity == "CRITICAL"


def test_thickness_bending_stiffness_annotation(changes):
    ch = next((c for c in changes if "bend-stiffness" in c.field), None)
    assert ch is not None
    # (1.6/1.2)^3 - 1 ≈ +138%
    assert "+138" in ch.field or "+137" in ch.field


def test_youngs_modulus_change_detected(changes):
    ch = _find(changes, category="MATERIAL", field="E")
    assert ch is not None
    assert ch.old_value == pytest.approx(210000.0)
    assert ch.new_value == pytest.approx(206000.0)
    assert ch.percent_change == pytest.approx(-1.905, abs=0.01)
    assert ch.severity == "WARNING"


def test_bc_rotation_change(changes):
    bc_changes = [c for c in changes if c.category == "BOUNDARY"]
    # v1: rx=False, ry=False, rz=False → v2: all True
    assert len(bc_changes) == 3
    for ch in bc_changes:
        assert ch.old_value == "free"
        assert ch.new_value == "fixed"


def test_load_magnitude_doubled(changes):
    ch = _find(changes, category="LOAD", field="Fscale_y")
    assert ch is not None
    assert ch.percent_change == pytest.approx(100.0)
    assert ch.severity == "CRITICAL"


def test_no_mesh_changes(changes):
    mesh_changes = [c for c in changes if c.category == "MESH"]
    assert len(mesh_changes) == 0


def test_changes_sorted_by_severity(changes):
    ranks = {"CRITICAL": 0, "WARNING": 1, "INFO": 2}
    severities = [ranks[c.severity] for c in changes]
    assert severities == sorted(severities)


def test_no_false_positives_for_unchanged_fields(changes):
    # Density and Poisson's ratio are identical in both fixtures
    rho_changes = [c for c in changes if c.field == "rho"]
    assert len(rho_changes) == 0
    nu_changes = [c for c in changes if c.field == "nu"]
    assert len(nu_changes) == 0
