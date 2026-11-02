#!/usr/bin/env python3
"""Importe un fichier GEDCOM (export Geneanet, Heredis, etc.) dans la base d'enquête.

Usage : python gedcom_import.py arbre.ged enquete.db [--label "Arbre Famille X, export du 2026-11-02"]
Stdlib uniquement. Les personnes, événements (naissance, décès, mariage, etc.) et
relations (époux, parent) sont créés ; chaque événement est rattaché à une source
« import GEDCOM » de niveau B (transcription d'un arbre, pas un acte vu).
"""
import re
import sqlite3
import sys
from pathlib import Path

EVENT_KINDS = {
    "BIRT": "naissance", "CHR": "baptême", "DEAT": "décès", "BURI": "inhumation",
    "MARR": "mariage", "DIV": "divorce", "OCCU": "profession", "RESI": "résidence",
    "EMIG": "émigration", "IMMI": "immigration", "CENS": "recensement",
}


def read_text(path: Path) -> str:
    raw = path.read_bytes()
    for enc in ("utf-8-sig", "cp1252", "latin-1"):
        try:
            return raw.decode(enc)
        except UnicodeDecodeError:
            continue
    return raw.decode("latin-1", errors="replace")


def parse_records(text: str):
    """Retourne la liste des enregistrements de niveau 0 sous forme de nœuds (level, tag, value, children)."""
    root = {"level": -1, "tag": "ROOT", "value": "", "xref": None, "children": []}
    stack = [root]
    line_re = re.compile(r"^\s*(\d+)\s+(@[^@]+@\s+)?(\w+)\s?(.*)$")
    for line in text.splitlines():
        m = line_re.match(line)
        if not m:
            continue
        level, xref, tag, value = int(m[1]), (m[2] or "").strip() or None, m[3], m[4]
        if tag in ("CONC", "CONT") and stack[-1]["level"] < level:
            sep = "" if tag == "CONC" else "\n"
            stack[-1]["value"] += sep + value
            continue
        node = {"level": level, "tag": tag, "value": value, "xref": xref, "children": []}
        while stack[-1]["level"] >= level:
            stack.pop()
        stack[-1]["children"].append(node)
        stack.append(node)
    return root["children"]


def child(node, tag):
    return next((c for c in node["children"] if c["tag"] == tag), None)


def event_row(node):
    date, place = child(node, "DATE"), child(node, "PLAC")
    return (date["value"] if date else None, place["value"] if place else None, node["value"] or None)


def main() -> int:
    args = sys.argv[1:]
    label = "Import GEDCOM"
    if "--label" in args:
        i = args.index("--label")
        label = args[i + 1]
        del args[i:i + 2]
    if len(args) != 2:
        print(__doc__, file=sys.stderr)
        return 2
    ged_path, db_path = Path(args[0]), Path(args[1])
    records = parse_records(read_text(ged_path))

    conn = sqlite3.connect(db_path)
    conn.execute("PRAGMA foreign_keys = ON")
    cur = conn.cursor()
    cur.execute("INSERT INTO sources(label, local_file, consulted) VALUES (?, ?, date('now'))",
                (f"{label} ({ged_path.name})", str(ged_path)))
    source_id = cur.lastrowid

    person_ids = {}
    n_events = n_rel = 0

    for rec in (r for r in records if r["tag"] == "INDI"):
        name_node = child(rec, "NAME")
        raw = name_node["value"] if name_node else ""
        m = re.match(r"^(.*?)\s*/([^/]*)/\s*(.*)$", raw)
        given, surname = (m[1].strip(), m[2].strip()) if m else (raw.strip(), "")
        full = " ".join(p for p in (given, surname.upper() if surname else "") if p) or "(sans nom)"
        sex = child(rec, "SEX")
        note = child(rec, "NOTE")
        cur.execute(
            "INSERT INTO persons(gedcom_id, full_name, given_names, surname, sex, notes) VALUES (?,?,?,?,?,?)",
            (rec["xref"], full, given, surname, sex["value"] if sex else None, note["value"] if note else None))
        pid = person_ids[rec["xref"]] = cur.lastrowid
        for ev in rec["children"]:
            kind = EVENT_KINDS.get(ev["tag"])
            if kind:
                date, place, details = event_row(ev)
                cur.execute("INSERT INTO events(person_id, kind, date, place, details) VALUES (?,?,?,?,?)",
                            (pid, kind, date, place, details))
                eid = cur.lastrowid
                cur.execute("INSERT INTO evidence(claim, event_id, source_id, certainty, reader, notes) "
                            "VALUES (?,?,?,?,?,?)",
                            (f"{full} : {kind} {date or ''} {place or ''}".strip(), eid, source_id, "B", "import", None))
                n_events += 1

    for fam in (r for r in records if r["tag"] == "FAM"):
        husb, wife = child(fam, "HUSB"), child(fam, "WIFE")
        h = person_ids.get(husb["value"]) if husb else None
        w = person_ids.get(wife["value"]) if wife else None
        if h and w:
            cur.execute("INSERT INTO relations(person_a, person_b, kind) VALUES (?,?,'époux')", (h, w))
            n_rel += 1
        marr = child(fam, "MARR")
        if marr:
            date, place, details = event_row(marr)
            for spouse in (h, w):
                if spouse:
                    cur.execute("INSERT INTO events(person_id, kind, date, place, details) VALUES (?,?,?,?,?)",
                                (spouse, "mariage", date, place, details))
                    n_events += 1
        for chil in (c for c in fam["children"] if c["tag"] == "CHIL"):
            cid = person_ids.get(chil["value"])
            for parent in (h, w):
                if parent and cid:
                    cur.execute("INSERT INTO relations(person_a, person_b, kind) VALUES (?,?,'parent')", (parent, cid))
                    n_rel += 1

    conn.commit()
    conn.close()
    print(f"Importé : {len(person_ids)} personnes, {n_events} événements, {n_rel} relations "
          f"depuis {ged_path.name} (source n°{source_id}, niveau B).")
    return 0


if __name__ == "__main__":
    sys.exit(main())
