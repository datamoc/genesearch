#!/usr/bin/env python3
"""Crée (ou complète) la base SQLite d'une enquête généalogique.

Usage : python init_db.py enquete.db
Aucune dépendance : bibliothèque standard uniquement.
"""
import sqlite3
import sys
from pathlib import Path


def main() -> int:
    if len(sys.argv) != 2:
        print("Usage : python init_db.py <chemin.db>", file=sys.stderr)
        return 2
    db_path = Path(sys.argv[1])
    schema = (Path(__file__).parent / "schema.sql").read_text(encoding="utf-8")
    with sqlite3.connect(db_path) as conn:
        conn.executescript(schema)
        tables = [r[0] for r in conn.execute(
            "SELECT name FROM sqlite_master WHERE type='table' ORDER BY name")]
    print(f"Base prête : {db_path} ({len(tables)} tables : {', '.join(tables)})")
    return 0


if __name__ == "__main__":
    sys.exit(main())
