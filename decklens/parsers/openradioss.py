"""OpenRadioss (.rad) input file parser.

Reads keyword blocks (/TYPE[/SUBTYPE]/ID) into a list of Card objects.
Each Card holds the parsed numeric/string fields for that block.
Use cards_to_deck() to convert the raw Card list into a structured Deck.
"""

from __future__ import annotations

import re
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

from .base import (
    BoundaryCondition,
    Contact,
    Deck,
    Load,
    Material,
    Part,
    ShellProperty,
    SolidProperty,
)


@dataclass
class Card:
    keyword: str            # e.g. "PROP/SHELL"
    card_id: str            # e.g. "101"
    title: str
    fields: dict[str, Any] = field(default_factory=dict)
    data_line_count: int = 0  # raw non-comment data lines (used for NODE/SHELL counts)


# ---------------------------------------------------------------------------
# Card schemas: ordered list of data-line specs per keyword
# Each spec maps positional field names to parse types ("int" | "float" | "str")
# ---------------------------------------------------------------------------

_F = "float"
_I = "int"

CARD_SCHEMAS: dict[str, list[dict]] = {
    "PROP/SHELL": [
        {"names": ["Ishell", "Ismstr", "Ish3n", "Idrill"],                   "types": [_I, _I, _I, _I]},
        {"names": ["Thick", "T_min", "T_max", "Fun_Id", "Istrain", "Igeo",
                   "Ithick", "Iplas"],                                        "types": [_F, _F, _F, _I, _I, _I, _I, _I]},
    ],
    "PROP/SOLID": [
        {"names": ["Isolid", "Ismstr", "Icpre", "Ivis", "Iframe"],            "types": [_I, _I, _I, _I, _I]},
    ],
    "MAT/ELAST": [
        {"names": ["Rho_Init"],                                               "types": [_F]},
        {"names": ["E", "nu"],                                                "types": [_F, _F]},
    ],
    "MAT/PLAS_JOHNS": [
        {"names": ["Rho_Init"],                                               "types": [_F]},
        {"names": ["E", "nu"],                                                "types": [_F, _F]},
        {"names": ["a", "b", "n", "eps_max_p", "sigma_max"],                 "types": [_F, _F, _F, _F, _F]},
        {"names": ["c", "eps_dot_0", "F_smooth", "Ifloc", "Ifail"],          "types": [_F, _F, _F, _I, _I]},
    ],
    "MAT/PLAS_ZERIL": [
        {"names": ["Rho_Init"],                                               "types": [_F]},
        {"names": ["E", "nu"],                                                "types": [_F, _F]},
        {"names": ["a", "b", "n", "c", "m", "T_melt", "T_ref", "eps_dot_0"], "types": [_F] * 8},
    ],
    "MAT/VOID": [],
    "PART": [
        {"names": ["mat_ID", "prop_ID", "subset_ID", "skew_ID", "frame_ID"], "types": [_I, _I, _I, _I, _I]},
    ],
    "BCS": [
        {"names": ["Skew_Id", "Grnod_Id"],                                    "types": [_I, _I]},
        {"names": ["Tx", "Ty", "Tz", "Rx", "Ry", "Rz"],                      "types": [_I, _I, _I, _I, _I, _I]},
    ],
    "LOAD/PRESSURE": [
        {"names": ["Surf_Id", "Fscale_T", "Fscale_P", "Sens_Id"],            "types": [_I, _F, _F, _I]},
    ],
    "GRAV": [
        {"names": ["Skew_Id", "Sens_Id"],                                     "types": [_I, _I]},
        {"names": ["gx", "gy", "gz"],                                         "types": [_F, _F, _F]},
    ],
    "CLOAD": [
        {"names": ["Fct_Id", "Dir", "Ascale_x", "Fscale_y", "Tstart", "Tstop"],
         "types": [_I, "str", _F, _F, _F, _F]},
    ],
    "INTER/TYPE7": [
        {"names": ["slave_ID", "master_ID", "istf", "igap", "igpad", "isym"], "types": [_I, _I, _I, _I, _I, _I]},
        {"names": ["Stfac", "Fric", "gap_min", "gap_max", "Tstart", "Tstop"], "types": [_F, _F, _F, _F, _F, _F]},
    ],
    "INTER/TYPE11": [
        {"names": ["slave_ID", "master_ID", "Spotflag", "Ibag"],              "types": [_I, _I, _I, _I]},
        {"names": ["Stfac", "Fric", "gap_min"],                               "types": [_F, _F, _F]},
    ],
}


# Keywords whose data starts on the line immediately after the keyword (no title line)
_NO_TITLE_KEYWORDS: frozenset[str] = frozenset([
    "NODE", "SHELL", "SOLID", "BRIC", "QUAD", "TRIA", "BEAM", "TRUSS",
    "SH3N", "PART_MOVE",
])


# ---------------------------------------------------------------------------
# Parser
# ---------------------------------------------------------------------------

def parse_file(path: str | Path) -> list[Card]:
    text = Path(path).read_text(encoding="utf-8", errors="replace")
    return parse_text(text)


def parse_text(text: str) -> list[Card]:
    lines = text.splitlines()
    cards: list[Card] = []
    i = 0

    while i < len(lines):
        raw = lines[i]
        stripped = raw.strip()

        if not stripped or stripped.startswith("#"):
            i += 1
            continue

        if stripped.upper().startswith("/END"):
            i += 1
            continue

        if stripped.startswith("/"):
            keyword, card_id = _split_keyword(stripped)
            if not keyword:
                i += 1
                continue

            i += 1
            # Mesh-data blocks have no title line — data starts immediately
            if keyword in _NO_TITLE_KEYWORDS:
                title = ""
            else:
                title = ""
                while i < len(lines):
                    t = lines[i].strip()
                    if t and not t.startswith("#"):
                        title = t
                        i += 1
                        break
                    i += 1

            # Collect data lines until next keyword block or /END
            data_lines: list[str] = []
            while i < len(lines):
                dl = lines[i]
                ds = dl.strip()
                if not ds or ds.startswith("#"):
                    i += 1
                    continue
                if ds.startswith("/"):
                    break
                data_lines.append(dl)
                i += 1

            fields = _parse_fields(keyword, data_lines)
            cards.append(Card(
                keyword=keyword,
                card_id=card_id,
                title=title,
                fields=fields,
                data_line_count=len(data_lines),
            ))
        else:
            i += 1

    return cards


# ---------------------------------------------------------------------------
# Deck builder
# ---------------------------------------------------------------------------

def cards_to_deck(cards: list[Card], filename: str = "") -> Deck:
    """Convert a parsed Card list into a structured Deck object."""
    deck = Deck(filename=filename)

    for card in cards:
        try:
            cid = int(card.card_id) if card.card_id else 0
        except ValueError:
            cid = 0

        kw = card.keyword
        f = card.fields

        if kw == "MAT/ELAST":
            deck.materials[cid] = Material(
                id=cid, name=card.title, law="ELAST",
                rho=f.get("Rho_Init"), E=f.get("E"), nu=f.get("nu"),
                raw_fields=f,
            )
        elif kw == "MAT/PLAS_JOHNS":
            deck.materials[cid] = Material(
                id=cid, name=card.title, law="PLAS_JOHNS",
                rho=f.get("Rho_Init"), E=f.get("E"), nu=f.get("nu"),
                yield_stress=f.get("a"),  # a = initial yield stress in J-C
                raw_fields=f,
            )
        elif kw == "MAT/PLAS_ZERIL":
            deck.materials[cid] = Material(
                id=cid, name=card.title, law="PLAS_ZERIL",
                rho=f.get("Rho_Init"), E=f.get("E"), nu=f.get("nu"),
                yield_stress=f.get("a"),
                raw_fields=f,
            )
        elif kw == "MAT/VOID":
            deck.materials[cid] = Material(id=cid, name=card.title, law="VOID")

        elif kw == "PROP/SHELL":
            deck.shell_props[cid] = ShellProperty(
                id=cid, name=card.title,
                thickness=f.get("Thick"),
                ishell=f.get("Ishell"),
                raw_fields=f,
            )
        elif kw == "PROP/SOLID":
            deck.solid_props[cid] = SolidProperty(
                id=cid, name=card.title,
                isolid=f.get("Isolid"),
                raw_fields=f,
            )

        elif kw == "PART":
            deck.parts[cid] = Part(
                id=cid, name=card.title,
                mat_id=f.get("mat_ID"),
                prop_id=f.get("prop_ID"),
            )

        elif kw == "BCS":
            deck.bcs[cid] = BoundaryCondition(
                id=cid, name=card.title,
                tx=bool(f.get("Tx", 0)),
                ty=bool(f.get("Ty", 0)),
                tz=bool(f.get("Tz", 0)),
                rx=bool(f.get("Rx", 0)),
                ry=bool(f.get("Ry", 0)),
                rz=bool(f.get("Rz", 0)),
            )

        elif kw == "GRAV":
            deck.loads[cid] = Load(id=cid, name=card.title, load_type="GRAV", raw_fields=f)
        elif kw == "CLOAD":
            deck.loads[cid] = Load(id=cid, name=card.title, load_type="CLOAD", raw_fields=f)
        elif kw == "LOAD/PRESSURE":
            deck.loads[cid] = Load(id=cid, name=card.title, load_type="PRESSURE", raw_fields=f)

        elif kw.startswith("INTER/"):
            contact_type = kw.split("/", 1)[1]
            deck.contacts[cid] = Contact(
                id=cid, name=card.title, contact_type=contact_type, raw_fields=f,
            )

        elif kw == "NODE":
            deck.node_count += card.data_line_count

        elif kw == "SHELL":
            deck.shell_count += card.data_line_count

        elif kw in {"SOLID", "BRIC"}:
            deck.solid_count += card.data_line_count

    return deck


def parse_deck(path: str | Path) -> Deck:
    """One-shot: parse file → Deck."""
    p = Path(path)
    cards = parse_file(p)
    return cards_to_deck(cards, filename=p.name)


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _split_keyword(line: str) -> tuple[str, str]:
    """'/PROP/SHELL/101' → ('PROP/SHELL', '101')"""
    parts = [p for p in line.strip().split("/") if p]
    if not parts:
        return "", ""

    skip = {"BEGIN", "END", "UNIT", "INCLUDE", "SUBMODEL", "MERGE", "OCTREE"}
    if parts[0].upper() in skip:
        return "", ""

    if parts and _looks_int(parts[-1]):
        return "/".join(parts[:-1]).upper(), parts[-1]
    return "/".join(parts).upper(), ""


def _looks_int(s: str) -> bool:
    return bool(re.fullmatch(r"-?\d+", s.strip()))


def _to_float(raw: str) -> float:
    """Parse float, handling FORTRAN D-notation (7.85D-9 → 7.85e-9)."""
    return float(raw.replace("D", "E").replace("d", "e"))


def _parse_fields(keyword: str, data_lines: list[str]) -> dict[str, Any]:
    schema = CARD_SCHEMAS.get(keyword)
    if schema is None:
        return {}

    fields: dict[str, Any] = {}
    spec_idx = 0

    for line in data_lines:
        stripped = line.strip()
        if not stripped or stripped.startswith("$") or stripped.startswith("#"):
            continue

        if spec_idx >= len(schema):
            break

        spec = schema[spec_idx]
        tokens = stripped.split()
        for j, (name, typ) in enumerate(zip(spec["names"], spec["types"])):
            if j >= len(tokens):
                break
            raw = tokens[j]
            try:
                if typ == "int":
                    fields[name] = int(raw)
                elif typ == "float":
                    fields[name] = _to_float(raw)
                else:
                    fields[name] = raw
            except ValueError:
                fields[name] = raw

        spec_idx += 1

    return fields
