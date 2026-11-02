# Unterstützte Genealogie-Recherche (`recherche-genealogique`)

Eine Methode und ein Werkzeugkasten für die Ahnenforschung **mit oder ohne KI-Assistent**: benannte Quellen, Sicherheitsstufen (A = Urkunde gelesen, B = Eintrag oder Baum, C = Schlussfolgerung), eine lokale Beleg-Datenbank, schnelles Prüfen von Belegen, PDF-Berichte, Sicherung und erneute Veröffentlichung von Stammbäumen (Geneanet, GEDCOM, Geneweb) und Hilfe bei der **Erbenermittlung**.

English: [README.md](README.md) · Français : [README.fr.md](README.fr.md)

> **Sprache.** Assistenten sollen **in der Sprache der Nutzerin oder des Nutzers antworten**, unabhängig von der Sprache dieser Dateien. Der Leitfaden (`SKILL.md` und `references/`) ist französisch geschrieben (die Familienforschung des Autors ist französisch); `references/sources-international.md` ist englisch und nennt Einstiegspunkte für viele Länder. Urkunden bleiben in ihrer Originalsprache: wörtlich zitieren und für die Nutzer übersetzen. Die **Werkzeuge** (Meldungen, Hilfetexte, Prüfoberfläche, Bericht) sprechen **Französisch, Englisch und Deutsch**; weitere Sprachen: siehe [TRANSLATING.md](TRANSLATING.md).

## Was es leistet

- **Beleg-Disziplin.** Jeder Fakt hat eine benannte Quelle und eine Stufe: **A** Urkunde gelesen (vom Assistenten oder vom Menschen), **B** Eintrag, Online-Baum oder Abschrift ohne gesehene Urkunde, **C** Schlussfolgerung oder unsichere Lesung. Daten und Orte werden aus der Quelle übernommen, nie rekonstruiert. Quellen, die sich gegenseitig abschreiben (Wikipedia/Wikidata, kopierte Bäume), zählen als eine.
- **Der Mensch bleibt im Spiel.** Der Assistent geht so weit er kann, dann bittet er gezielt um Hilfe: eine handgeschriebene Zeile lesen, sich in ein bezahltes Konto einloggen, eine Datenbank von Hand durchsuchen.
- **Recherchemethode.** Zuerst die Person identifizieren; Ansatzpunkte, wenn jemand „verschwindet“ (Ehegatte über den Mädchennamen, Kinder und angeheiratete Verwandte, Besitz, Arbeitgeber, Presse, Volkszählung, Schreibvarianten); wie man eine Archivurkunde liest; wo man je nach Land sucht.
- **Werkzeuge** (Python-Standardbibliothek, keine Pflichtinstallation): lokale SQLite-Beleg-Datenbank, GEDCOM-Import und -Export, Analyse (Aufgabe des Tages, Verwandtschaft, Unstimmigkeiten, fehlende Personen, Korrelationen), eine lokale Prüfoberfläche, ein PDF-Bericht, der lebende Personen ausblendet, und eine unverbindliche gesetzliche **Erbfolge** für französische Nachlässe.
- **Baumsicherung.** Der offizielle Geneanet-Export Schritt für Schritt (GEDCOM- und Geneweb-Format), Import in die lokale Datenbank, sichere erneute Veröffentlichung.
- **Erbenermittlung.** Leitplanken (berechtigter Zweck, Datenschutz), Methode, Quellen nach Zugänglichkeit, ein nüchterner Briefentwurf, Erbschaftsbetrug. **Nur französisches Recht.**

## Mit einem KI-Assistenten nutzen

| Ihr Werkzeug | So |
|---|---|
| Ein Assistent, der das Format `SKILL.md` liest (Claude Code und andere Programmier-Assistenten) | Diesen Ordner in den Skills-Ordner des Werkzeugs kopieren (Speicherort in dessen Dokumentation) |
| Ein Assistent, der `AGENTS.md` liest | Den Ordner im Projekt behalten: `AGENTS.md` verweist auf die übrigen Dateien |
| ChatGPT, Gemini, Mistral, Copilot, ein lokales Modell (nur Chat) | Einen der Prompts aus [`PROMPT-UNIVERSAL.de.md`](PROMPT-UNIVERSAL.de.md) (lang oder kurz) in die benutzerdefinierten Anweisungen, einen GPT, einen Gem oder die Systemnachricht einfügen |
| Claude.ai | Das `.skill`-Paket importieren (Einstellungen, Fähigkeiten) |

Was der Assistent tun kann, hängt von seinen Fähigkeiten ab (nur Text, gemeinsames Dokument oder ein Arbeitsplatz, der Befehle ausführt). Er passt sich an: siehe [`references/environnements.md`](references/environnements.md). Nichts erfordert ein Skript.

## Ohne KI nutzen: die Skripte

Python 3.8 oder neuer (getestet mit 3.13). PDF-Berichte brauchen `pip install reportlab`; alles andere ist Standardbibliothek.

```
python scripts/genealogie.py --lang de init baum.db                       # Datenbank anlegen
python scripts/genealogie.py --lang de importer mein_baum.ged baum.db     # GEDCOM-Export laden
python scripts/genealogie.py --lang de analyse baum.db stats              # Zustand des Baums
python scripts/genealogie.py --lang de analyse baum.db tache --racine "Vorname NAME"   # Aufgabe des Tages
python scripts/genealogie.py --lang de analyse baum.db parente "A" "B"    # Verwandtschaft zweier Personen
python scripts/genealogie.py --lang de valider baum.db --racine "Vorname NAME" --lecteur "Ihr Name"   # Belege im Browser prüfen
python scripts/genealogie.py --lang de rapport baum.db bericht.pdf        # Belege und offene Fragen (Lebende ausgeblendet)
python scripts/genealogie.py --lang de devolution baum.db "Erblasser"     # mögliche Erben nach Ordnung (französisches Recht, unverbindlich)
python scripts/genealogie.py exporter baum.db baum_aus.ged
```

Die Sprache wählt `--lang fr|en|de`, sonst die Variable `GENEALOGIE_LANG`, sonst die Systemsprache (Standard: Französisch). Befehls- und Optionsnamen bleiben französische Bezeichner; englische Aliasnamen werden akzeptiert (`import`, `export`, `analyze`, `validate`, `report`, `inheritance`; `--root`, `--reader`, `--death-year`, `--all`, `--title`).

Die Prüfoberfläche lauscht nur auf Ihrem Rechner (lokale Adresse, durch ein Token geschützt); nichts wird online gesendet.

## Datenschutz

Stammbäume enthalten lebende Personen. Halten Sie die Dateien lokal. Der Bericht blendet alle aus, die wahrscheinlich noch leben (vor weniger als 100 Jahren geboren ohne erfassten Tod, oder ohne Datum, aber mit einer solchen Person verbunden), und entfernt jede Zeile, die sie nennt. Das ist bewusst vorsichtig und arbeitet mit Namen: Prüfen Sie einen Bericht, bevor Sie ihn weitergeben. Die `.gitignore` des Repositorys hält Sicherungen, Datenbanken und Berichte aus der Versionsverwaltung heraus; lassen Sie das so.

## Inhalt

- `SKILL.md`, `AGENTS.md`, `PROMPT-UNIVERSAL.de.md`, `PROMPT-UNIVERSAL.en.md`, `PROMPT-UNIVERSEL.md`: Anweisungen für einen Assistenten.
- `references/`: Methode, Quellen (Frankreich und international), nützliche Seiten, Hilfe vom Menschen erbitten, Bäume, Aufgabe des Tages, Erbenermittlung.
- `scripts/`: die Python-Werkzeuge; `scripts/locales/`: Übersetzungen (eine JSON-Datei je Sprache).
- `TRANSLATING.md`: eine Sprache hinzufügen.

## Grenzen

- **Sprache des Leitfadens.** `SKILL.md` und die Dateien in `references/` sind französisch; ein Assistent liest sie und antwortet in Ihrer Sprache. Die Werkzeuge sind dreisprachig (fr, en, de). In der Datenbank gespeicherte Werte (Ereignisarten wie „naissance“, „décès“) bleiben französische Kennungen und werden auf dem Bildschirm übersetzt.
- **Nur an französischer Forschung getestet** (ein französischer Stammbaum, Geneanet, französische und Cantal-Archive). Einstiegspunkte für andere Länder stammen aus anderen offenen Projekten und sind **nicht überprüft**.
- Die Erbenermittlung ist ein Methodenleitfaden und ein unverbindliches Werkzeug, **keine Rechtsberatung**: ein Notar bestätigt jede Erbfolge. Mit „à vérifier“ markierte Punkte im Leitfaden wurden aus dem Gedächtnis geschrieben.
- Kein Werkzeug ersetzt das Lesen der Urkunden: Stufe A erreicht man nur, indem man das Dokument liest.
- Webseiten ändern sich. Funktioniert ein Link nicht, den Namen der Seite suchen.

## Verwandte offene Projekte

Unabhängige Projekte, die beim Bau dieses Projekts gefunden wurden (kein Code übernommen). Einige ihrer Quellen stehen in [`references/sources-international.md`](references/sources-international.md).

- [autoresearch-genealogy](https://github.com/mattprusak/autoresearch-genealogy) (MIT): Prompts und 24 Länderführer.
- [Genealogy Research Agent](https://gist.github.com/peas/ee5b0bcdb54a809b6ddee83caff51ca6): ein Claude-Code-Skill mit brasilianischem Schwerpunkt (keine Lizenz angegeben).
- [gramps-evidence-mcp](https://github.com/ianderso/gramps-evidence-mcp) (MIT): ein MCP-Server für Gramps Web mit Pflichtzitaten und Vertrauensstufen.
- GEDCOM-MCP-Server wie [gedcom-mcp](https://glama.ai/mcp/servers/ggoosen/gedcom-mcp/tree) und Gramps-Werkzeuge.

## Lizenz

MIT (siehe [LICENSE](LICENSE)): nutzen, kopieren, ändern und weitergeben, auch kommerziell, unter Beibehaltung des Copyright-Vermerks. Ohne Gewähr.
