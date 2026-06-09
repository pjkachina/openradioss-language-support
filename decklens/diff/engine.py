"""Semantic diff engine: compares two Deck objects and returns engineering-aware Changes."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any

from ..parsers.base import (
    BoundaryCondition,
    Contact,
    Deck,
    Load,
    Material,
    Part,
    ShellProperty,
    SolidProperty,
)

# Thresholds (WARNING%, CRITICAL%) per field name
_THRESHOLDS: dict[str, tuple[float, float]] = {
    "thickness": (5.0, 20.0),
    "Thick":     (5.0, 20.0),
    "E":         (1.5, 10.0),
    "nu":        (5.0, 15.0),
    "yield_stress": (5.0, 15.0),
    "a":         (5.0, 15.0),   # J-C yield stress
    "Rho_Init":  (5.0, 20.0),
    "rho":       (5.0, 20.0),
    "Fscale_y":  (10.0, 50.0),  # load magnitude
    "Stfac":     (10.0, 30.0),  # contact stiffness
    "Fric":      (10.0, 30.0),  # friction coefficient
    "gap_min":   (10.0, 30.0),
}

_SEVERITY_ORDER = ("CRITICAL", "WARNING", "INFO")


@dataclass
class Change:
    category: str       # MATERIAL | PROPERTY | PART | BOUNDARY | LOAD | CONTACT | MESH | TOPOLOGY
    item_type: str      # e.g. "MAT/ELAST", "PROP/SHELL"
    item_id: int | str
    item_name: str
    field: str
    old_value: Any
    new_value: Any
    unit: str | None = None
    percent_change: float | None = None
    severity: str = "INFO"   # INFO | WARNING | CRITICAL


def _pct(old: float, new: float) -> float | None:
    if old == 0.0:
        return None
    return (new - old) / abs(old) * 100.0


def _severity(field: str, pct: float | None) -> str:
    if pct is None:
        return "WARNING"
    warn, crit = _THRESHOLDS.get(field, (5.0, 20.0))
    abs_pct = abs(pct)
    if abs_pct >= crit:
        return "CRITICAL"
    if abs_pct >= warn:
        return "WARNING"
    return "INFO"


def _float_change(
    category: str,
    item_type: str,
    item_id: int,
    item_name: str,
    field: str,
    old: float | None,
    new: float | None,
    unit: str | None = None,
) -> Change | None:
    if old is None and new is None:
        return None
    if old == new:
        return None
    pct = _pct(old, new) if (old is not None and new is not None) else None
    sev = _severity(field, pct)
    return Change(
        category=category,
        item_type=item_type,
        item_id=item_id,
        item_name=item_name,
        field=field,
        old_value=old,
        new_value=new,
        unit=unit,
        percent_change=pct,
        severity=sev,
    )


class DiffEngine:
    def diff(self, before: Deck, after: Deck) -> list[Change]:
        changes: list[Change] = []
        changes.extend(self._diff_materials(before, after))
        changes.extend(self._diff_shell_props(before, after))
        changes.extend(self._diff_solid_props(before, after))
        changes.extend(self._diff_parts(before, after))
        changes.extend(self._diff_bcs(before, after))
        changes.extend(self._diff_loads(before, after))
        changes.extend(self._diff_contacts(before, after))
        changes.extend(self._diff_mesh(before, after))
        # Sort: CRITICAL first, then WARNING, then INFO
        changes.sort(key=lambda c: _SEVERITY_ORDER.index(c.severity))
        return changes

    # ------------------------------------------------------------------
    # Materials
    # ------------------------------------------------------------------

    def _diff_materials(self, before: Deck, after: Deck) -> list[Change]:
        changes: list[Change] = []
        all_ids = set(before.materials) | set(after.materials)

        for mid in sorted(all_ids):
            b = before.materials.get(mid)
            a = after.materials.get(mid)

            if b is None:
                changes.append(Change(
                    category="MATERIAL", item_type=f"MAT/{a.law}",
                    item_id=mid, item_name=a.name,
                    field="[added]", old_value=None, new_value=a.name,
                    severity="WARNING",
                ))
                continue
            if a is None:
                changes.append(Change(
                    category="MATERIAL", item_type=f"MAT/{b.law}",
                    item_id=mid, item_name=b.name,
                    field="[removed]", old_value=b.name, new_value=None,
                    severity="CRITICAL",
                ))
                continue

            item_type = f"MAT/{b.law}"
            name = b.name

            for fld, unit in [("E", "MPa"), ("nu", None), ("rho", "Mg/mm³"), ("yield_stress", "MPa")]:
                bv = getattr(b, fld)
                av = getattr(a, fld)
                c = _float_change("MATERIAL", item_type, mid, name, fld, bv, av, unit)
                if c:
                    changes.append(c)

            # Extra raw fields for plasticity laws
            if b.law in ("PLAS_JOHNS", "PLAS_ZERIL"):
                for fld, unit in [("b", "MPa"), ("n", None), ("c", None)]:
                    bv = b.raw_fields.get(fld)
                    av = a.raw_fields.get(fld)
                    c = _float_change("MATERIAL", item_type, mid, name, fld, bv, av, unit)
                    if c:
                        changes.append(c)

        return changes

    # ------------------------------------------------------------------
    # Shell properties
    # ------------------------------------------------------------------

    def _diff_shell_props(self, before: Deck, after: Deck) -> list[Change]:
        changes: list[Change] = []
        all_ids = set(before.shell_props) | set(after.shell_props)

        for pid in sorted(all_ids):
            b = before.shell_props.get(pid)
            a = after.shell_props.get(pid)

            if b is None:
                changes.append(Change(
                    category="PROPERTY", item_type="PROP/SHELL",
                    item_id=pid, item_name=a.name,
                    field="[added]", old_value=None, new_value=a.name,
                    severity="WARNING",
                ))
                continue
            if a is None:
                changes.append(Change(
                    category="PROPERTY", item_type="PROP/SHELL",
                    item_id=pid, item_name=b.name,
                    field="[removed]", old_value=b.name, new_value=None,
                    severity="CRITICAL",
                ))
                continue

            c = _float_change("PROPERTY", "PROP/SHELL", pid, b.name, "thickness", b.thickness, a.thickness, "mm")
            if c:
                # Annotate bending stiffness impact: EI ∝ t³
                if c.percent_change is not None and b.thickness and a.thickness:
                    ratio = a.thickness / b.thickness
                    stiffness_pct = (ratio ** 3 - 1.0) * 100.0
                    c.field = f"thickness (bend-stiffness {stiffness_pct:+.1f}%)"
                changes.append(c)

            if b.ishell != a.ishell and a.ishell is not None:
                changes.append(Change(
                    category="PROPERTY", item_type="PROP/SHELL",
                    item_id=pid, item_name=b.name,
                    field="Ishell (formulation)",
                    old_value=b.ishell, new_value=a.ishell,
                    severity="WARNING",
                ))

        return changes

    # ------------------------------------------------------------------
    # Solid properties
    # ------------------------------------------------------------------

    def _diff_solid_props(self, before: Deck, after: Deck) -> list[Change]:
        changes: list[Change] = []
        all_ids = set(before.solid_props) | set(after.solid_props)

        for pid in sorted(all_ids):
            b = before.solid_props.get(pid)
            a = after.solid_props.get(pid)

            if b is None:
                changes.append(Change(
                    category="PROPERTY", item_type="PROP/SOLID",
                    item_id=pid, item_name=a.name,
                    field="[added]", old_value=None, new_value=a.name,
                    severity="INFO",
                ))
            elif a is None:
                changes.append(Change(
                    category="PROPERTY", item_type="PROP/SOLID",
                    item_id=pid, item_name=b.name,
                    field="[removed]", old_value=b.name, new_value=None,
                    severity="CRITICAL",
                ))
            elif b.isolid != a.isolid:
                changes.append(Change(
                    category="PROPERTY", item_type="PROP/SOLID",
                    item_id=pid, item_name=b.name,
                    field="Isolid (formulation)",
                    old_value=b.isolid, new_value=a.isolid,
                    severity="WARNING",
                ))

        return changes

    # ------------------------------------------------------------------
    # Parts
    # ------------------------------------------------------------------

    def _diff_parts(self, before: Deck, after: Deck) -> list[Change]:
        changes: list[Change] = []
        all_ids = set(before.parts) | set(after.parts)

        for pid in sorted(all_ids):
            b = before.parts.get(pid)
            a = after.parts.get(pid)

            if b is None:
                changes.append(Change(
                    category="PART", item_type="PART",
                    item_id=pid, item_name=a.name,
                    field="[added]", old_value=None, new_value=a.name,
                    severity="INFO",
                ))
                continue
            if a is None:
                changes.append(Change(
                    category="PART", item_type="PART",
                    item_id=pid, item_name=b.name,
                    field="[removed]", old_value=b.name, new_value=None,
                    severity="CRITICAL",
                ))
                continue

            if b.mat_id != a.mat_id:
                changes.append(Change(
                    category="PART", item_type="PART",
                    item_id=pid, item_name=b.name,
                    field="mat_ID",
                    old_value=b.mat_id, new_value=a.mat_id,
                    severity="CRITICAL",
                ))
            if b.prop_id != a.prop_id:
                changes.append(Change(
                    category="PART", item_type="PART",
                    item_id=pid, item_name=b.name,
                    field="prop_ID",
                    old_value=b.prop_id, new_value=a.prop_id,
                    severity="CRITICAL",
                ))

        return changes

    # ------------------------------------------------------------------
    # Boundary conditions
    # ------------------------------------------------------------------

    def _diff_bcs(self, before: Deck, after: Deck) -> list[Change]:
        changes: list[Change] = []
        all_ids = set(before.bcs) | set(after.bcs)
        dofs = ["tx", "ty", "tz", "rx", "ry", "rz"]

        for bid in sorted(all_ids):
            b = before.bcs.get(bid)
            a = after.bcs.get(bid)

            if b is None:
                changes.append(Change(
                    category="BOUNDARY", item_type="BCS",
                    item_id=bid, item_name=a.name,
                    field="[added]", old_value=None, new_value=a.name,
                    severity="WARNING",
                ))
                continue
            if a is None:
                changes.append(Change(
                    category="BOUNDARY", item_type="BCS",
                    item_id=bid, item_name=b.name,
                    field="[removed]", old_value=b.name, new_value=None,
                    severity="CRITICAL",
                ))
                continue

            for dof in dofs:
                bv = getattr(b, dof)
                av = getattr(a, dof)
                if bv != av:
                    changes.append(Change(
                        category="BOUNDARY", item_type="BCS",
                        item_id=bid, item_name=b.name,
                        field=dof.upper(),
                        old_value="fixed" if bv else "free",
                        new_value="fixed" if av else "free",
                        severity="CRITICAL" if not av else "WARNING",
                    ))

        return changes

    # ------------------------------------------------------------------
    # Loads
    # ------------------------------------------------------------------

    def _diff_loads(self, before: Deck, after: Deck) -> list[Change]:
        changes: list[Change] = []
        all_ids = set(before.loads) | set(after.loads)

        for lid in sorted(all_ids):
            b = before.loads.get(lid)
            a = after.loads.get(lid)

            if b is None:
                changes.append(Change(
                    category="LOAD", item_type=a.load_type,
                    item_id=lid, item_name=a.name,
                    field="[added]", old_value=None, new_value=a.name,
                    severity="WARNING",
                ))
                continue
            if a is None:
                changes.append(Change(
                    category="LOAD", item_type=b.load_type,
                    item_id=lid, item_name=b.name,
                    field="[removed]", old_value=b.name, new_value=None,
                    severity="CRITICAL",
                ))
                continue

            item_type = b.load_type

            # CLOAD: compare direction and magnitude scaling
            if item_type == "CLOAD":
                bdir = b.raw_fields.get("Dir")
                adir = a.raw_fields.get("Dir")
                if bdir != adir:
                    changes.append(Change(
                        category="LOAD", item_type="CLOAD",
                        item_id=lid, item_name=b.name,
                        field="Dir",
                        old_value=bdir, new_value=adir,
                        severity="CRITICAL",
                    ))
                c = _float_change("LOAD", "CLOAD", lid, b.name, "Fscale_y",
                                  b.raw_fields.get("Fscale_y"), a.raw_fields.get("Fscale_y"), "N")
                if c:
                    changes.append(c)

            elif item_type == "GRAV":
                for ax in ("gx", "gy", "gz"):
                    c = _float_change("LOAD", "GRAV", lid, b.name, ax,
                                      b.raw_fields.get(ax), a.raw_fields.get(ax), "mm/s²")
                    if c:
                        changes.append(c)

            elif item_type == "PRESSURE":
                c = _float_change("LOAD", "PRESSURE", lid, b.name, "Fscale_P",
                                  b.raw_fields.get("Fscale_P"), a.raw_fields.get("Fscale_P"), "MPa")
                if c:
                    changes.append(c)

        return changes

    # ------------------------------------------------------------------
    # Contacts
    # ------------------------------------------------------------------

    def _diff_contacts(self, before: Deck, after: Deck) -> list[Change]:
        changes: list[Change] = []
        all_ids = set(before.contacts) | set(after.contacts)

        for cid in sorted(all_ids):
            b = before.contacts.get(cid)
            a = after.contacts.get(cid)

            if b is None:
                changes.append(Change(
                    category="CONTACT", item_type=f"INTER/{a.contact_type}",
                    item_id=cid, item_name=a.name,
                    field="[added]", old_value=None, new_value=a.name,
                    severity="WARNING",
                ))
                continue
            if a is None:
                changes.append(Change(
                    category="CONTACT", item_type=f"INTER/{b.contact_type}",
                    item_id=cid, item_name=b.name,
                    field="[removed]", old_value=b.name, new_value=None,
                    severity="CRITICAL",
                ))
                continue

            item_type = f"INTER/{b.contact_type}"
            for fld, unit in [("Stfac", None), ("Fric", None), ("gap_min", "mm"), ("gap_max", "mm")]:
                c = _float_change("CONTACT", item_type, cid, b.name, fld,
                                  b.raw_fields.get(fld), a.raw_fields.get(fld), unit)
                if c:
                    changes.append(c)

        return changes

    # ------------------------------------------------------------------
    # Mesh topology
    # ------------------------------------------------------------------

    def _diff_mesh(self, before: Deck, after: Deck) -> list[Change]:
        changes: list[Change] = []

        for attr, label, unit in [
            ("node_count", "node_count", "nodes"),
            ("shell_count", "shell_count", "elements"),
            ("solid_count", "solid_count", "elements"),
        ]:
            bv = getattr(before, attr)
            av = getattr(after, attr)
            if bv == av:
                continue
            pct = _pct(bv, av) if bv else None
            changes.append(Change(
                category="MESH", item_type="MESH",
                item_id=0, item_name="mesh",
                field=label,
                old_value=bv, new_value=av,
                unit=unit,
                percent_change=pct,
                severity="WARNING" if pct and abs(pct) >= 10.0 else "INFO",
            ))

        return changes
