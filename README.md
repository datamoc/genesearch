# genesearch

A genealogy-research skill and toolkit that works with **any AI assistant, or none**.

- Evidence discipline: named sources, levels A (record read) / B (notice or tree) / C (deduction), no invented places or dates.
- A human stays in the loop: the assistant goes as far as it can, then asks precisely for help.
- Local tools (Python standard library): SQLite evidence database, GEDCOM import and export, analysis, a local validation interface, a PDF report that hides living people, tree backup (Geneanet export), indicative French heir devolution.
- Assistants should answer **in the user's language**. The tools speak **French, English and German** (one JSON file per language, easy to extend: see [TRANSLATING.md](recherche-genealogique/TRANSLATING.md)). The guide is in French; international entry points are in English.

**Start here:** [`recherche-genealogique/`](recherche-genealogique/) holds the skill, with an [English README](recherche-genealogique/README.md) ([français](recherche-genealogique/README.fr.md), [Deutsch](recherche-genealogique/README.de.md)), instructions for assistants (`SKILL.md`, `AGENTS.md`, [universal prompts](recherche-genealogique/PROMPT-UNIVERSAL.en.md)), references and scripts.

Licence: MIT.

Status: used on one French family tree; other countries' sources are leads collected from other projects, not verified. Personal data (family trees, backups, databases, reports) is kept out of the repository by `.gitignore`.
