#!/usr/bin/env python3
"""Create (or complete) the SQLite database of a genealogy investigation.

Usage: python init_db.py investigation.db
Standard library only.
"""
import sqlite3
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))
import i18n  # noqa: E402
from i18n import tr  # noqa: E402


def main() -> int:
    args = i18n.init(sys.argv[1:])
    if args and args[0] in ("-h", "--help"):
        print(tr("init.usage"))
        return 0
    if len(args) != 1:
        print(tr("init.usage"), file=sys.stderr)
        return 2
    db_path = Path(args[0])
    schema = (Path(__file__).parent / "schema.sql").read_text(encoding="utf-8")
    with sqlite3.connect(db_path) as conn:
        conn.executescript(schema)
        tables = [r[0] for r in conn.execute(
            "SELECT name FROM sqlite_master WHERE type='table' ORDER BY name")]
    print(tr("init.ready", db=db_path, n=len(tables), names=", ".join(tables)))
    return 0


if __name__ == "__main__":
    sys.exit(main())
