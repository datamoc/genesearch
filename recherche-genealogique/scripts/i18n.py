"""Translations for the genealogy tools: one JSON catalogue per language in locales/.

Language choice, in order: `--lang xx` on the command line, the GENEALOGIE_LANG variable, the system language
(LC_ALL, LC_MESSAGES, LANG, then the OS locale), then French. To add a language, copy locales/en.json to
locales/<code>.json and translate the values (see TRANSLATING.md); no code change is needed.

Command words and options keep their canonical French identifiers; English aliases are accepted (see below).
"""
import json
import locale
import os
from pathlib import Path

LOCALES = Path(__file__).parent / "locales"
DEFAULT = "fr"

COMMAND_ALIASES = {
    "task": "tache", "frontier": "frontiere", "missing": "manquants", "kinship": "parente", "find": "trouver",
    "import": "importer", "export": "exporter", "analyze": "analyse", "validate": "valider", "report": "rapport",
    "inheritance": "devolution",
}
TASK_ALIASES = {
    "proof": "preuve", "climb": "remonter", "validate": "valider", "missing": "manquant",
    "correlation": "correlation", "kinship": "parente",
}
OPTION_ALIASES = {
    "--root": "--racine", "--reader": "--lecteur", "--death-year": "--deces", "--all": "--tous",
    "--title": "--titre", "--everything": "--tout",
}
_LANGUAGE_NAMES = {"french": "fr", "english": "en", "german": "de", "deutsch": "de", "francais": "fr"}

_catalogs = {}
_current = DEFAULT


def available():
    return sorted(p.stem for p in LOCALES.glob("*.json"))


def _catalog(code):
    if code not in _catalogs:
        path = LOCALES / f"{code}.json"
        _catalogs[code] = json.loads(path.read_text(encoding="utf-8")) if path.exists() else {}
    return _catalogs[code]


def _code_from(raw):
    raw = (raw or "").strip().lower()
    if not raw:
        return None
    languages = available()
    if raw[:2] in languages:
        return raw[:2]
    for name, code in _LANGUAGE_NAMES.items():
        if raw.startswith(name) and code in languages:
            return code
    return None


def _system_language():
    for variable in ("GENEALOGIE_LANG", "LC_ALL", "LC_MESSAGES", "LANG"):
        code = _code_from(os.environ.get(variable))
        if code:
            return code
    try:
        return _code_from(locale.getlocale()[0])
    except (ValueError, TypeError):
        return None


def current():
    return _current


def set_language(code):
    global _current
    _current = _code_from(code) or DEFAULT
    return _current


def tr(key, **values):
    """Message for `key` in the current language, with `values` inserted ; falls back to French, then to the key."""
    for code in (_current, DEFAULT):
        message = _catalog(code).get(key)
        if message is None:
            continue
        try:
            return message.format(**values) if values else message
        except (KeyError, IndexError, ValueError):
            continue  # translation with a wrong placeholder: use the French text instead
    return key


def command(word):
    return COMMAND_ALIASES.get(word, word)


def task_type(word):
    return TASK_ALIASES.get(word, word)


def init(argv):
    """Pick the language and normalise option aliases. Returns the argument list without `--lang xx`."""
    argv = list(argv)
    chosen = None
    if "--lang" in argv:
        i = argv.index("--lang")
        chosen = argv[i + 1] if i + 1 < len(argv) else None
        del argv[i:i + 2]
    set_language(chosen if _code_from(chosen) else (_system_language() or DEFAULT))
    return [OPTION_ALIASES.get(a, a) for a in argv]
