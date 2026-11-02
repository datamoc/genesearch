#!/usr/bin/env python3
"""Export the investigation database as GEDCOM 5.5.1 (UTF-8), importable into Geneanet, Heredis, Ancestris.

Usage: python gedcom_export.py investigation.db tree_out.ged. Certainty levels A/B/C stay in the
database; the GEDCOM does not carry them.
"""
import sqlite3
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))
import i18n  # noqa: E402
from i18n import tr  # noqa: E402

TAGS = {
    "naissance": "BIRT", "baptême": "CHR", "décès": "DEAT", "inhumation": "BURI",
    "profession": "OCCU", "résidence": "RESI", "émigration": "EMIG", "immigration": "IMMI",
    "recensement": "CENS",
}


def clean(text) -> str:
    return " ".join(str(text).split()) if text else ""


def build_families(conn):
    """Regroupe en familles : un couple (époux) + enfants communs, ou parent(s) seul(s) + enfants."""
    parents_of = {}
    for r in conn.execute("SELECT person_a, person_b FROM relations WHERE kind='parent'"):
        parents_of.setdefault(r["person_b"], set()).add(r["person_a"])
    fams, used = [], set()
    for r in conn.execute("SELECT person_a, person_b FROM relations WHERE kind='époux'"):
        pair = frozenset((r["person_a"], r["person_b"]))
        children = sorted(c for c, ps in parents_of.items() if pair <= ps)
        used.update(children)
        fams.append((sorted(pair), children))
    singles = {}
    for c, ps in parents_of.items():
        if c not in used:
            singles.setdefault(frozenset(ps), []).append(c)
    fams += [(sorted(ps), sorted(children)) for ps, children in singles.items()]
    return fams


def main() -> int:
    args = i18n.init(sys.argv[1:])
    if len(args) != 2:
        print(tr("exp.help"), file=sys.stderr)
        return 2
    db_path, out_path = Path(args[0]), Path(args[1])
    conn = sqlite3.connect(db_path)
    conn.row_factory = sqlite3.Row

    persons = conn.execute("SELECT * FROM persons ORDER BY id").fetchall()
    sex = {p["id"]: p["sex"] for p in persons}
    fams = build_families(conn)
    fams_of, famc_of = {}, {}
    for i, (members, children) in enumerate(fams, 1):
        for m in members:
            fams_of.setdefault(m, []).append(i)
        for c in children:
            famc_of.setdefault(c, []).append(i)

    lines = ["0 HEAD", "1 SOUR recherche-genealogique", "1 GEDC", "2 VERS 5.5.1", "2 FORM LINEAGE-LINKED",
             "1 CHAR UTF-8"]

    for p in persons:
        given, surname = clean(p["given_names"]), clean(p["surname"])
        if not (given or surname):
            given = clean(p["full_name"])
        lines += [f"0 @I{p['id']}@ INDI", f"1 NAME {given} /{surname}/"]
        if p["sex"]:
            lines.append(f"1 SEX {p['sex']}")
        for e in conn.execute("SELECT * FROM events WHERE person_id=? ORDER BY id", (p["id"],)):
            tag = TAGS.get(e["kind"])
            if not tag:
                continue  # le mariage est exporté dans la famille (FAM)
            lines.append(f"1 {tag}" + (f" {clean(e['details'])}" if tag == "OCCU" and e["details"] else ""))
            if e["date"]:
                lines.append(f"2 DATE {clean(e['date'])}")
            if e["place"]:
                lines.append(f"2 PLAC {clean(e['place'])}")
        for f in fams_of.get(p["id"], []):
            lines.append(f"1 FAMS @F{f}@")
        for f in famc_of.get(p["id"], []):
            lines.append(f"1 FAMC @F{f}@")
        if p["notes"]:
            lines.append(f"1 NOTE {clean(p['notes'])}")

    for i, (members, children) in enumerate(fams, 1):
        lines.append(f"0 @F{i}@ FAM")
        for m in members:
            lines.append(f"1 {'WIFE' if sex.get(m) == 'F' else 'HUSB'} @I{m}@")
        for c in children:
            lines.append(f"1 CHIL @I{c}@")
        if len(members) == 2:
            marr = conn.execute(
                "SELECT date, place FROM events WHERE kind='mariage' AND person_id IN (?,?) ORDER BY id LIMIT 1",
                members).fetchone()
            if marr:
                lines.append("1 MARR")
                if marr["date"]:
                    lines.append(f"2 DATE {clean(marr['date'])}")
                if marr["place"]:
                    lines.append(f"2 PLAC {clean(marr['place'])}")

    lines.append("0 TRLR")
    out_path.write_text("\n".join(lines) + "\n", encoding="utf-8")
    print(tr("exp.done", persons=len(persons), fams=len(fams), out=out_path))
    return 0


if __name__ == "__main__":
    sys.exit(main())
