# Assisted genealogy research (`recherche-genealogique`)

A method and a toolkit for genealogy research **with or without an AI assistant**: named sources, levels of certainty (A = record read, B = notice or tree, C = deduction), a local evidence database, fast validation of proofs, PDF reports, tree backup and republication (Geneanet, GEDCOM, Geneweb), and help with **heir research**.

Français : [README.fr.md](README.fr.md) · Deutsch: [README.de.md](README.de.md)

> **Language.** Assistants should **answer in the user's language**, whatever the language of these files. The guide itself is written in French (the author's family research is French); the page [`references/sources-international.md`](references/sources-international.md) is in English and lists entry points for many countries. Records stay in their original language: quote them as written and translate for the user. The **tools** (messages, help, validation interface, report) speak **French, English and German**; see [TRANSLATING.md](TRANSLATING.md) to add another language.

## What it does

- **Evidence discipline.** Every fact carries a named source and a level: **A** record read (by the assistant or the human), **B** notice, online tree or transcription with no record seen, **C** deduction or uncertain reading. Copy dates and places from the source, never reconstruct them. Mirrored sources (Wikipedia/Wikidata, copied trees) count as one.
- **Human in the loop.** The assistant goes as far as it can, then asks for a precise favour: read a handwritten line, log in to a paid account, open a database that can only be browsed by hand.
- **Research method.** Identify the person first; pivots when someone "disappears" (spouse by maiden name, children and in-laws, property, employer, press, census, spelling variants); how to read an archive record; where to look, by country.
- **Tools** (Python standard library, no mandatory install): local SQLite evidence database, GEDCOM import and export, analysis (task of the day, kinship, anomalies, missing people, correlations), a local validation interface, a PDF report that hides living people, and an indicative legal **devolution** for French successions.
- **Tree backup.** The official Geneanet export step by step (GEDCOM and Geneweb formats), import into the local database, safe republication.
- **Heir research.** Guardrails (legitimate purpose, GDPR), method, sources by accessibility, a sober letter template, inheritance scams. **French law only.**

## Use it with an AI assistant

| Your tool | How |
|---|---|
| An assistant that reads the `SKILL.md` format (Claude Code and other coding assistants) | Copy this folder into the tool's skills folder (see its documentation for the location) |
| An assistant that reads `AGENTS.md` | Keep this folder in the project: `AGENTS.md` points to the other files |
| ChatGPT, Gemini, Mistral, Copilot, a local model (chat only) | Paste one of the prompts of [`PROMPT-UNIVERSAL.en.md`](PROMPT-UNIVERSAL.en.md) (or [`.de.md`](PROMPT-UNIVERSAL.de.md), or the French `PROMPT-UNIVERSEL.md`), full or short, into custom instructions, a GPT, a Gem or the system message |
| Claude.ai | Import the `.skill` package (Settings, capabilities) |

What the assistant can do depends on its abilities (text only, shared document, or a workstation that runs commands). It adapts: see [`references/environnements.md`](references/environnements.md). Nothing requires a script.

## Use it without AI: the scripts

Python 3.8 or later (tested with 3.13). PDF reports need `pip install reportlab`; everything else is standard library.

```
python scripts/genealogie.py init tree.db                         # create the database
python scripts/genealogie.py importer my_tree.ged tree.db         # load a GEDCOM export
python scripts/genealogie.py analyse tree.db stats                # state of the tree
python scripts/genealogie.py analyse tree.db tache --racine "First LAST"      # task of the day
python scripts/genealogie.py analyse tree.db parente "A" "B"      # kinship between two people
python scripts/genealogie.py valider tree.db --racine "First LAST" --lecteur "Your name"   # validate proofs in the browser
python scripts/genealogie.py rapport tree.db report.pdf           # proofs and open questions (living people hidden)
python scripts/genealogie.py devolution tree.db "Deceased"        # possible heirs by order (French law, indicative)
python scripts/genealogie.py exporter tree.db tree_out.ged
```

The validation interface only listens on your machine (local address protected by a token); nothing is sent online. Choose the language with `--lang fr|en|de` (or the `GENEALOGIE_LANG` variable); otherwise the system language is used, then French. Command and option names are French identifiers with English aliases (`import`, `export`, `analyze`, `validate`, `report`, `inheritance`; `--root`, `--reader`, `--death-year`, `--all`, `--title`).

## Privacy

Trees contain living people. Keep the files local. The report hides everyone who is probably alive (born less than 100 years ago with no recorded death, or undated and linked to such a person) and removes every line that names them. This is deliberately cautious and works on names: review a report before sharing it. The repository's `.gitignore` keeps backups, databases and reports out of version control; keep it that way.

## Contents

- `SKILL.md`, `AGENTS.md`, `PROMPT-UNIVERSAL.en.md`, `PROMPT-UNIVERSAL.de.md`, `PROMPT-UNIVERSEL.md`: instructions for an assistant.
- `references/`: method, sources (France and international), useful sites, asking the human for help, trees, task of the day, heir research.
- `scripts/`: the Python tools; `scripts/locales/`: the translations (one JSON file per language).
- `TRANSLATING.md`: how to add a language.

## Limits

- **Language.** The tools speak French, English and German. The guide (`SKILL.md` and `references/`) is in French: an assistant reads it and answers in the user's language. Values stored in the database (event kinds such as "naissance", "décès") stay French identifiers and are shown translated on screen, so a database can be shared between people who use different languages. The German and English texts were written by the maintainer's assistant, not by native-speaking reviewers: corrections are welcome.
- **Tested only on French research** (a French family tree, Geneanet, French and Cantal archives). Entry points for other countries are collected from other open projects and **not verified**.
- Heir research is a method guide and an indicative tool, **not legal advice**: a notary validates any devolution. Points marked "à vérifier" in the guide were written from memory.
- No tool replaces reading the records: level A is only reached by reading the document.
- Websites change. If a link fails, search the site's name.

## Related open projects

Independent projects found while building this one (no code copied). Some of their sources are listed in [`references/sources-international.md`](references/sources-international.md).

- [autoresearch-genealogy](https://github.com/mattprusak/autoresearch-genealogy) (MIT): prompts and 24 country guides.
- [Genealogy Research Agent](https://gist.github.com/peas/ee5b0bcdb54a809b6ddee83caff51ca6): a Claude Code skill with a Brazilian focus (no licence stated).
- [gramps-evidence-mcp](https://github.com/ianderso/gramps-evidence-mcp) (MIT): an MCP server on Gramps Web with mandatory citations and confidence levels.
- GEDCOM MCP servers such as [gedcom-mcp](https://glama.ai/mcp/servers/ggoosen/gedcom-mcp/tree) and Gramps tools.

## Licence

MIT (see [LICENSE](LICENSE)): use, copy, modify and redistribute, including commercially, keeping the copyright notice. Provided without warranty.
