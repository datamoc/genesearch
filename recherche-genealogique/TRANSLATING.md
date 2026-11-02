# Translating the tools into another language

The tools speak **French (default), English and German**. A new language needs no code change: it is one JSON file.

## What is translated, and what is not

| Translated | Not translated |
|---|---|
| Messages, help texts, table headings, task of the day, devolution tables and report text (`scripts/locales/*.json`) | **Command and option names** (French identifiers; English aliases exist: `analyze`, `--root`, ...) |
| The validation interface in the browser (all texts, the page language) | **Values stored in the database**: event kinds (`naissance`, `décès`...), the markers `[revu`, `[DOUTEUX]`, the source label `Validation locale (interface)`, help-request statuses (`ouverte`, `faite`). The code looks them up, so they stay the same in every language, and a database can be shared between people who use different languages. They are shown translated on screen |
| The `README` files and the universal prompts | The guide in `SKILL.md` and `references/` (French; an assistant answers in the user's language). `references/sources-international.md` is in English |

## Add a language (example: Spanish, code `es`)

1. Copy `scripts/locales/en.json` to `scripts/locales/es.json`.
2. Translate the **values**. Never change the keys (left side).
3. Keep every `{placeholder}` exactly as in the original (`{n}`, `{person}`, `{g:>2}`...): they are replaced by numbers and names. Keep the line breaks (`\n`) and the Markdown marks (`**`, `|`, `#`) in the same places.
4. Check your file: `python scripts/check_locales.py es` (same keys, same placeholders as `fr.json`).
5. Try it: `python scripts/genealogie.py --lang es analyse tree.db stats`, or set `GENEALOGIE_LANG=es`. The system language is used when neither is set.
6. Optional: translate `README.md` into `README.es.md` and the prompts in `PROMPT-UNIVERSAL.en.md` into `PROMPT-UNIVERSAL.es.md`.

If a key is missing in your file, the French text is shown instead, so a partial translation still works.

## Tips

- Most texts are short messages: keep them short.
- `ui.js.*` are the buttons and labels of the browser interface. Check their length on screen.
- The help texts (`*.help`) are shown with `--help`; keep the command names (`stats`, `tache`, ...) unchanged and explain them.
- Some messages mention French law (devolution of an estate: `dev.*`): translate the words, do not adapt the legal content to another country.
- Open a pull request or send your file to the maintainer; say which language variant you used (for example Spanish of Spain or of Mexico).
