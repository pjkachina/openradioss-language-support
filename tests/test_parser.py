"""Tests for the OpenRadioss parser."""

from pathlib import Path

import pytest

from decklens.parsers.openradioss import parse_deck, parse_text

FIXTURES = Path(__file__).parent / "fixtures"


def test_parse_mat_elast():
    text = """
/MAT/ELAST/1
STEEL
  7.85E-9
  210000.0  0.3
"""
    cards = parse_text(text)
    assert len(cards) == 1
    c = cards[0]
    assert c.keyword == "MAT/ELAST"
    assert c.card_id == "1"
    assert c.title == "STEEL"
    assert c.fields["E"] == pytest.approx(210000.0)
    assert c.fields["nu"] == pytest.approx(0.3)
    assert c.fields["Rho_Init"] == pytest.approx(7.85e-9)


def test_parse_prop_shell():
    text = """
/PROP/SHELL/1
OUTER_PANEL
  0  0  0  0
  1.2  0.0  0.0  0  0  0  0  0
"""
    cards = parse_text(text)
    assert len(cards) == 1
    c = cards[0]
    assert c.keyword == "PROP/SHELL"
    assert c.fields["Thick"] == pytest.approx(1.2)
    assert c.fields["Ishell"] == 0


def test_parse_part():
    text = """
/PART/1
PANEL_PART
  1  2  0  0  0
"""
    cards = parse_text(text)
    assert len(cards) == 1
    c = cards[0]
    assert c.keyword == "PART"
    assert c.fields["mat_ID"] == 1
    assert c.fields["prop_ID"] == 2


def test_parse_bcs():
    text = """
/BCS/1
FIXED_SUPPORT
  0  0
  1  1  1  0  0  0
"""
    cards = parse_text(text)
    assert len(cards) == 1
    c = cards[0]
    assert c.keyword == "BCS"
    assert c.fields["Tx"] == 1
    assert c.fields["Ty"] == 1
    assert c.fields["Tz"] == 1
    assert c.fields["Rx"] == 0
    assert c.fields["Rz"] == 0


def test_parse_cload():
    text = """
/CLOAD/1
APPLIED_FORCE
  1  Z  1.0  1000.0  0.0  1.0E+30
"""
    cards = parse_text(text)
    assert len(cards) == 1
    c = cards[0]
    assert c.keyword == "CLOAD"
    assert c.fields["Dir"] == "Z"
    assert c.fields["Fscale_y"] == pytest.approx(1000.0)


def test_fortran_d_notation():
    text = """
/MAT/ELAST/5
DENSE
  7.85D-9
  210000.0  0.3
"""
    cards = parse_text(text)
    c = cards[0]
    assert c.fields["Rho_Init"] == pytest.approx(7.85e-9)


def test_comment_lines_skipped():
    text = """
# Header comment
/MAT/ELAST/1
# inline comment
STEEL
  7.85E-9
  210000.0  0.3
"""
    cards = parse_text(text)
    assert len(cards) == 1
    assert cards[0].title == "STEEL"


def test_node_count():
    text = """
/NODE
  1  0.0  0.0  0.0
  2  1.0  0.0  0.0
  3  2.0  0.0  0.0
"""
    cards = parse_text(text)
    node_card = next(c for c in cards if c.keyword == "NODE")
    assert node_card.data_line_count == 3


def test_shell_count():
    text = """
/SHELL/1
  1  1  1  2  3  4
  2  1  2  3  4  5
"""
    cards = parse_text(text)
    shell_card = next(c for c in cards if c.keyword == "SHELL")
    assert shell_card.data_line_count == 2


def test_parse_deck_v1():
    deck = parse_deck(FIXTURES / "sample_v1.rad")
    assert 1 in deck.materials
    mat = deck.materials[1]
    assert mat.law == "ELAST"
    assert mat.E == pytest.approx(210000.0)

    assert 1 in deck.shell_props
    prop = deck.shell_props[1]
    assert prop.thickness == pytest.approx(1.2)

    assert 1 in deck.parts
    assert deck.parts[1].mat_id == 1
    assert deck.parts[1].prop_id == 1

    assert 1 in deck.bcs
    bc = deck.bcs[1]
    assert bc.tx is True
    assert bc.rx is False

    assert 1 in deck.loads
    assert deck.loads[1].load_type == "CLOAD"

    assert deck.node_count == 6
    assert deck.shell_count == 2


def test_parse_deck_v2():
    deck = parse_deck(FIXTURES / "sample_v2.rad")
    assert deck.materials[1].E == pytest.approx(206000.0)
    assert deck.shell_props[1].thickness == pytest.approx(1.6)
    bc = deck.bcs[1]
    assert bc.rx is True
    assert bc.ry is True
    assert bc.rz is True
