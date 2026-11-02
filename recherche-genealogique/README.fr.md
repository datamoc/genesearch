# Recherche généalogique assistée

English: [README.md](README.md) (version pour GitHub) · Deutsch : [README.de.md](README.de.md)

Méthode et outils pour mener une enquête généalogique **avec ou sans IA** : sources nommées, niveaux de certitude (A acte lu · B notice ou arbre · C déduction), base locale, validation rapide des preuves, rapport PDF, sauvegarde et republication d'arbres (Geneanet et logiciels via GEDCOM).

*Method and tools for genealogy research, with or without an AI assistant. The guide is written in French for French and Alsace-Moselle sources; the scripts and the evidence model work for any country.*

## Avec un assistant IA

| Votre outil | Comment l'utiliser |
|---|---|
| Un assistant qui lit le format `SKILL.md` (par exemple Claude Code et d'autres assistants de code) | Copier ce dossier dans le dossier des skills de l'outil (voir sa documentation pour l'emplacement) |
| Un assistant qui lit `AGENTS.md` | Garder ce dossier dans le projet : `AGENTS.md` renvoie vers les autres fichiers |
| ChatGPT, Gemini, Mistral, Copilot ou un modèle local, en conversation | Coller `PROMPT-UNIVERSEL.md` (version complète ou version courte) dans les instructions personnalisées, un GPT, un Gem ou le message système |
| Claude.ai | Importer le paquet `.skill` (Paramètres, capacités) |

Ce que l'assistant peut faire dépend de ses capacités : conversation seule, document partagé, ou poste de travail avec exécution de commandes. Il s'adapte (`references/environnements.md`).

## Sans IA : les scripts seuls

Prérequis : Python 3.8 ou plus récent (testé avec 3.13). Aucune installation, sauf `pip install reportlab` si vous voulez le PDF.

```
python scripts/genealogie.py init arbre.db                      # crée la base
python scripts/genealogie.py importer mon_arbre.ged arbre.db    # charge un export GEDCOM
python scripts/genealogie.py analyse arbre.db stats             # état de l'arbre
python scripts/genealogie.py analyse arbre.db tache --racine "Prénom NOM"   # tâche du jour
python scripts/genealogie.py analyse arbre.db parente "A" "B"   # lien de parenté entre deux personnes
python scripts/genealogie.py valider arbre.db --racine "Prénom NOM" --lecteur "Votre prénom"   # validation des preuves dans le navigateur
python scripts/genealogie.py rapport arbre.db rapport.pdf       # PDF des preuves et des questions ouvertes
python scripts/genealogie.py devolution arbre.db "Défunt" # héritiers possibles par ordre (droit français, indicatif)
python scripts/genealogie.py exporter arbre.db arbre_exporte.ged
```

Langue des outils : `--lang fr|en|de`, ou la variable `GENEALOGIE_LANG`, ou la langue du système (français par défaut). Les noms de commandes et d'options restent des identifiants français, avec des alias anglais (`import`, `export`, `analyze`, `validate`, `report`, `inheritance` ; `--root`, `--reader`, `--death-year`, `--all`, `--title`).

L'interface de validation s'ouvre sur votre poste uniquement (adresse locale protégée par un jeton) ; rien n'est envoyé en ligne. Le rapport PDF masque par défaut les personnes probablement vivantes.

## Sauvegarder un arbre Geneanet

La méthode officielle, pas à pas, est dans `references/arbres.md` : page « Exports et sauvegardes » de l'arbre, formats GEDCOM (échange) et Geneweb (le plus fidèle, garde les sources). Le GEDCOM ne contient pas les photos.

## Contenu

- `SKILL.md`, `AGENTS.md`, `PROMPT-UNIVERSEL.md` (français), `PROMPT-UNIVERSAL.en.md` (anglais), `PROMPT-UNIVERSAL.de.md` (allemand) : consignes pour un assistant.
- `references/` : méthode, sources (France et international), sites utiles, demandes d'aide, arbres, tâche du jour, recherche d'héritiers.
- `scripts/` : outils Python (bibliothèque standard) ; `scripts/locales/` : traductions (un fichier JSON par langue).
- `TRANSLATING.md` : ajouter une langue.

## Licence

MIT (voir `LICENSE`) : vous pouvez utiliser, copier, modifier et redistribuer ce dossier, y compris à titre commercial, en conservant la mention de copyright. Le logiciel est fourni sans garantie. Les guides juridiques (recherche d'héritiers) ne sont pas un avis juridique.

## Limites

- Les sources et exemples concernent surtout la France ; pour un autre pays, le modèle de preuves et les scripts restent valables, les sites sont à remplacer (`references/sources-international.md` donne des points d'entrée, non vérifiés). Les outils (messages, aide, interface de validation, rapport) parlent français, anglais et allemand (`--lang fr|en|de`, voir `TRANSLATING.md` pour en ajouter une) ; le guide (`SKILL.md` et `references/`) est en français et l'assistant répond dans la langue de l'utilisateur. Les valeurs stockées dans la base (types d'événements comme « naissance ») restent des identifiants français, affichés traduits à l'écran. Les textes anglais et allemands n'ont pas été relus par des locuteurs natifs : les corrections sont bienvenues.
- La recherche d'héritiers est un guide de méthode et un outil indicatif, pas un avis juridique : un notaire valide la dévolution.
- Aucun outil ne remplace la lecture des actes : les niveaux A ne s'obtiennent qu'en lisant le document.
- Les adresses de sites changent ; chercher le nom du site si un lien ne répond plus.
