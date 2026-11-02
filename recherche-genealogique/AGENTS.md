# Recherche généalogique assistée : consignes pour un assistant IA

Ce dossier contient une méthode de recherche généalogique et des outils. Il fonctionne avec n'importe quel assistant IA (Claude, ChatGPT, Gemini, Copilot, Mistral, modèle local, agent de code) ; il suffit de lire les fichiers ci-dessous. Si ton outil lit un fichier `AGENTS.md`, `CLAUDE.md`, `GEMINI.md` ou le format `SKILL.md`, ce dossier est déjà au bon format ; sinon, copie le contenu de `PROMPT-UNIVERSEL.md` (français), `PROMPT-UNIVERSAL.en.md` (anglais) ou `PROMPT-UNIVERSAL.de.md` (allemand) dans les instructions de l'assistant.

**Language:** always answer in the user's language. The references are in French except `references/sources-international.md` (English: entry points for other countries). Quote records in their original language and translate them. The scripts speak French, English and German: pass `--lang fr|en|de` (or set `GENEALOGIE_LANG`) to match the user's language; `TRANSLATING.md` explains how to add another one.

## Lis dans cet ordre

1. `SKILL.md` : les règles (sources et niveaux de certitude A/B/C, recopier sans recomposer, accord avant d'agir), le démarrage de session, la boucle de travail, la tâche du jour.
2. `references/environnements.md` : ce que tu peux faire selon tes capacités (conversation seule, document partagé, poste de travail, cloud).
3. À la demande : `references/methode.md` (pivots quand une personne « disparaît »), `references/sources-france.md` et `references/sites-utiles.md` (où chercher), `references/demande-aide.md` (demander une lecture à l'humain), `references/arbres.md` (sauvegarder, importer, republier un arbre), `references/tache-du-jour.md` (analyses, validation, rapport), `references/recherche-heritiers.md` (recherche d'héritiers : cadre, méthode, dévolution, garde-fous ; droit français), `references/sources-international.md` (hors de France).

## Règles non négociables

- Aucune affirmation sans source nommée et niveau de certitude. Un lieu ou une date se recopie de la source, ne se recompose jamais.
- Demande l'accord de l'utilisateur avant de télécharger, d'accepter des conditions d'un site, d'envoyer un document à un tiers, ou de modifier un arbre en ligne.
- N'utilise les comptes payants que dans la session déjà connectée de l'utilisateur. Ne demande ni ne saisis jamais de mot de passe ; ne contourne ni captcha ni blocage.
- Recherche d'héritiers : uniquement dans une démarche successorale légitime ; ne cherche pas les coordonnées d'une personne vivante en dehors de ce cadre, et passe par le notaire pour les contacts.
- Les arbres contiennent des personnes vivantes : garde les fichiers en local et masque-les dans tout document partagé.

## Outils

Les scripts de `scripts/` n'utilisent que la bibliothèque standard de Python (PDF : `reportlab`, facultatif). Point d'entrée : `python scripts/genealogie.py --help`. Rien n'est obligatoire : sans exécution de commandes, tiens le journal d'enquête dans la conversation ou dans un document.
