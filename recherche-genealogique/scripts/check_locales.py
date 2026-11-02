#!/usr/bin/env python3
"""Check the translation catalogues in locales/: same keys and same {placeholders} as the French reference.

Usage: python check_locales.py [code ...]   (default: every language found in locales/)
Exit code 0 if everything is consistent, 1 otherwise. Run it after adding or editing a translation.
Standard library only.
"""
import json
import re
import string
import sys
from pathlib import Path

LOCALES = Path(__file__).parent / "locales"
REFERENCE = "fr"


def placeholders(text):
    """Names of the {fields} of a message, e.g. {n} or {g:>2} -> n, g."""
    return sorted({name for _, name, _, _ in string.Formatter().parse(text) if name})


def check(code, reference):
    problems = []
    path = LOCALES / f"{code}.json"
    try:
        catalogue = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, ValueError) as error:
        return [f"{code}: cannot read {path.name}: {error}"]
    for key in reference:
        if key not in catalogue:
            problems.append(f"{code}: missing key {key}")
            continue
        try:
            if placeholders(catalogue[key]) != placeholders(reference[key]):
                problems.append(f"{code}: placeholders differ in {key}: {placeholders(catalogue[key])} "
                                f"instead of {placeholders(reference[key])}")
        except ValueError as error:
            problems.append(f"{code}: invalid format string in {key}: {error}")
        if re.search(r"\{\s*\}", catalogue[key]):
            problems.append(f"{code}: empty placeholder in {key}")
    for key in catalogue:
        if key not in reference:
            problems.append(f"{code}: unknown key {key} (not in {REFERENCE}.json)")
    return problems


def main():
    reference = json.loads((LOCALES / f"{REFERENCE}.json").read_text(encoding="utf-8"))
    codes = sys.argv[1:] or sorted(p.stem for p in LOCALES.glob("*.json") if p.stem != REFERENCE)
    problems = []
    for code in codes:
        problems += check(code, reference)
    for line in problems:
        print(line)
    print(f"{len(reference)} keys in {REFERENCE}.json; checked: {', '.join(codes) or '-'}; problems: {len(problems)}")
    return 1 if problems else 0


if __name__ == "__main__":
    sys.exit(main())
