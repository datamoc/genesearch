#!/usr/bin/env python3
"""Single entry point of the genealogy tools (tested with Python 3.13, designed for 3.8 or later).

Usage: python genealogie.py [--lang fr|en|de] <command> [arguments]. Run with --help for the commands, in the
chosen language. No mandatory dependency.
"""
import os
import runpy
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))
import i18n  # noqa: E402
from i18n import tr  # noqa: E402

COMMANDS = {
    "init": "init_db.py",
    "importer": "gedcom_import.py",
    "exporter": "gedcom_export.py",
    "analyse": "analyse_arbre.py",
    "valider": "validation_ui.py",
    "rapport": "rapport_preuves.py",
    "devolution": "devolution.py",
}


def main():
    argv = i18n.init(sys.argv[1:])  # chooses the language of the help text and removes --lang
    command = i18n.command(argv[0]) if argv else None
    if command not in COMMANDS:
        print(tr("gen.help"))
        return 0 if argv and argv[0] in ("-h", "--help") else 2
    os.environ["GENEALOGIE_LANG"] = i18n.current()  # the tool run below keeps the same language
    script = Path(__file__).parent / COMMANDS[command]
    sys.argv = [str(script)] + argv[1:]
    try:
        runpy.run_path(str(script), run_name="__main__")
    except SystemExit as e:
        if isinstance(e.code, str):  # error message of the tool: show it, do not swallow it
            print(e.code, file=sys.stderr)
            return 1
        return e.code if isinstance(e.code, int) else 0
    return 0


if __name__ == "__main__":
    sys.exit(main())
