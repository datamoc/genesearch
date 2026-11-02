# Selon ce que l'assistant peut faire

Table des matières : 1. Reconnaître le mode · 2. Mode conversation seule · 3. Mode document partagé · 4. Mode poste de travail · 5. Mode poste de travail dans le cloud · 6. Sans assistant : l'humain seul · 7. Points communs

## 1. Reconnaître le mode

Ce qui compte, c'est la capacité, pas le nom de l'outil. Demande-toi ce que tu peux réellement faire :

| Tu peux… | Mode |
|---|---|
| seulement échanger du texte (et lire des images envoyées) | **Conversation seule** |
| écrire dans un document ou un tableur partagé | **Document partagé** |
| lire et écrire des fichiers locaux et exécuter des commandes (Python) | **Poste de travail** |
| faire de même, mais sur une machine distante (sandbox, cloud) | **Poste de travail dans le cloud** |

Ces modes se combinent : un assistant de conversation avec recherche web et un navigateur piloté reste en mode « conversation seule » pour les fichiers. Ne suppose jamais qu'un script s'exécutera ni qu'un navigateur est disponible : vérifie, et dis à l'utilisateur ce que tu ne peux pas faire.

Cela vaut pour tous les assistants (Claude, ChatGPT, Gemini, Copilot, Mistral, modèles locaux, agents de code).

## 2. Mode conversation seule

- Tiens un **journal d'enquête** dans la conversation, remis à jour à la fin de chaque étape, avec les blocs : Question · Faits établis (source, niveau A/B/C) · Hypothèses · Recherches faites (y compris négatives) · Aide demandée.
- Demande à l'utilisateur d'envoyer les images d'actes ; lis-les toi-même d'abord (zoom, recadrage si tu peux).
- Utilise la recherche web et le navigateur si l'application les offre. Sinon, indique l'adresse exacte à ouvrir et ce qu'il faut recopier.
- Les calculs (parenté, tâche du jour) se font à la main sur le tableau du journal : voir `tache-du-jour.md`, § « Sans script ».

## 3. Mode document partagé

- Le document est le journal. Sections fixes : Question · Faits établis · Hypothèses · Recherches faites · Arbre / relations · Aide demandée · Prochaines pistes.
- Un tableau « Faits établis » : fait · valeur · source · niveau · date de consultation. Garde chaque recherche négative dans « Recherches faites ».
- Mets à jour le document à chaque étape plutôt qu'à la fin.

## 4. Mode poste de travail

Propose, sans rien installer avant accord de l'utilisateur :
- **Base locale** : `python scripts/genealogie.py init arbre.db` (ou `scripts/init_db.py`) crée une base SQLite (aucune installation) avec personnes, événements, relations, sources, preuves et journal de recherche. DuckDB est possible pour l'analyse (`pip install duckdb`) et peut lire la même base.
- **OCR et images** : Tesseract (avec le paquet de langue français) pour l'imprimé, `pillow` et `opencv-python` pour redresser, recadrer, augmenter le contraste avant lecture ; `pymupdf` pour extraire les pages de PDF. Pour le manuscrit, un service dédié comme Transkribus est plus adapté (voir § 5).
- **Analyse et tâche du jour** : `python scripts/genealogie.py analyse arbre.db tache --racine "<personne>"` (aussi `stats`, `frontiere`, `anomalies`, `manquants`, `correlations`, `parente A B`, `trouver`). Voir `tache-du-jour.md`.
- **Validation rapide des preuves** : `python scripts/genealogie.py valider arbre.db --racine "<personne>" --lecteur "<prénom>"` ouvre une page locale (jeton, 127.0.0.1) pour marquer chaque fait A, B, C ou douteux. Voir `tache-du-jour.md`, § 3 bis.
- **Rapport PDF** : `python scripts/genealogie.py rapport arbre.db rapport.pdf` (preuves, pistes, questions ouvertes ; personnes vivantes masquées par défaut). Voir `tache-du-jour.md`, § 3 ter.
- **Dévolution et héritiers** : `python scripts/genealogie.py devolution arbre.db "<défunt>"` (héritiers possibles par ordre, preuves à réunir). Voir `recherche-heritiers.md`.
- **Arbres** : `genealogie.py importer` charge un export GEDCOM dans la base (niveau B) et `genealogie.py exporter` en produit un, importable dans Geneanet ou un logiciel. Procédure complète, sauvegarde et republication dans `arbres.md`.

Pendant l'enquête :
1. Initialise la base au démarrage si elle n'existe pas ; enregistre chaque fait avec sa source et son niveau, chaque recherche dans `research_log` (y compris négative).
2. Stocke les images utiles dans un dossier `sources/` avec leur cote en nom de fichier.
3. Interroge la base pour voir ce qui reste incertain (`SELECT … WHERE certainty != 'A'`).

## 5. Mode poste de travail dans le cloud

L'installation locale d'outils est limitée. Pour les images, tu peux les envoyer à un service de reconnaissance en ligne (par exemple Transkribus pour le manuscrit), mais **demande d'abord l'accord de l'utilisateur** : un document envoyé à un tiers quitte le contexte de la conversation. N'envoie rien de sensible (documents de personnes vivantes) sans accord explicite. Rapatrie la base et les rapports vers le poste de l'utilisateur en fin de séance.

## 6. Sans assistant : l'humain seul

Tous les scripts se lancent à la main, sans IA (`README.md`). L'interface de validation (`genealogie.py valider`) est faite pour une personne qui a lu les actes ; le rapport PDF et l'analyse (`parente`, `anomalies`, `correlations`) servent à décider quoi chercher ensuite.

## 7. Points communs

- Aucune étape ne dépend d'un script : la base et l'OCR sont des plus, pas des prérequis.
- Les comptes payants ne sont utilisés que dans la session de navigateur déjà connectée de l'utilisateur.
- Réponds dans la langue de l'utilisateur ; les sources et les règles de ce guide sont rédigées pour la France et l'Europe francophone, adapte les sites pour un autre pays (`sites-utiles.md`).
