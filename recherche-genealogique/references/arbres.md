# Arbres : sauvegarder, garder en local, republier

Table des matières : 1. Principe · 2. Sauvegarder un arbre Geneanet (méthode officielle) · 3. Importer dans la base locale · 4. Republier · 5. Site sans export : lecture page à page · 6. Vie privée

## 1. Principe

La base locale est la maison de l'enquête : personnes, événements, relations, et pour chaque fait sa source et son niveau (A/B/C). Le site (Geneanet, etc.) en est un miroir pratique. **GEDCOM** est le format d'échange. Toujours préférer la méthode d'export que le site propose lui-même ; ne lis page à page que s'il n'y en a pas (§5).

Un arbre importé arrive au niveau **B** : c'est la transcription de quelqu'un, pas un acte vu. Les enquêtes qui suivent promeuvent les faits en A quand l'acte est lu.

## 2. Sauvegarder un arbre Geneanet (méthode officielle, testée)

1. **Vérifier le compte et l'arbre.** L'utilisateur est connecté à son compte (ne demande jamais de mot de passe). Sur `https://gw.geneanet.org/my-tree/operations/export`, le bandeau montre le nom de l'arbre (par exemple « Famille X ») et le compte. Si le nom ne correspond pas à l'arbre voulu, demande à l'utilisateur de changer de compte ou d'arbre lui-même.
2. **La page « Exports et sauvegardes »** propose deux choix : « Mon arbre en ligne » (export complet) ou « Une branche de mon arbre en ligne » (ascendante, descendante ou les deux), puis le format : **GEDCOM** (.ged, pour échanger avec d'autres logiciels) ou **Geneweb** (.gw, sauvegarde fidèle du logiciel de Geneanet). Pour une sauvegarde complète, fais les deux.
   **Fais toujours les deux formats** : le `.gw` (Geneweb) est le plus fidèle et garde la **source de chaque fait** (« Livret de famille », « Rédacteur de l'arbre »), que le GEDCOM d'export perd en grande partie. Le `.ged` sert à l'échange et à l'import dans la base locale. Dans la liste déroulante du format, choisis « Format GeneWeb (*.gw) » puis relance « Télécharger ».
3. **Demande l'accord avant de télécharger** : indique le nom du fichier attendu, la source (l'arbre et le compte) et, si connu, la taille. Un téléchargement n'est jamais fait sans accord.
   Options affichées après avoir choisi « Mon arbre en ligne » : format (GEDCOM par défaut), « Liens web vers les photos principales des individus » (n'ajoute que des liens, utile pour récupérer les photos plus tard) et « Images de la chronique familiale » (ajoute des images, peut alourdir beaucoup le fichier). Après « Télécharger », la page affiche un indicateur de chargement puis revient à l'état initial : c'est normal.
   **Vérifier que le fichier est arrivé** : demande d'abord à l'utilisateur dans quel dossier son navigateur enregistre (ce n'est pas toujours « Téléchargements » ; ici un autre lecteur), puis liste ce dossier. S'il n'y a rien de nouveau (les extensions de navigateur ne peuvent pas ouvrir `chrome://downloads`), ne relance pas l'export en boucle : demande à l'utilisateur d'ouvrir ses téléchargements (Ctrl+J dans Chrome) et de dire où le fichier a atterri, ou de le déplacer dans le dossier de sauvegarde.
4. **Range le fichier** dans un dossier daté, hors du dépôt de code (par exemple `sauvegardes/AAAA-MM-JJ_nom-arbre/`), et note sa taille et son empreinte SHA-256 dans le journal.
5. **Limites connues** : le GEDCOM ne contient pas les photos et documents joints ; les notes et sources sont conservées inégalement selon le logiciel. Les abonnés Premium ont des sauvegardes automatiques et une restauration en ligne (« Restauration de l'arbre ») ; sans Premium, l'export manuel régulier est la sauvegarde.
6. **Fréquence** : proposer un rappel périodique (par exemple tous les trois mois, et avant toute grosse modification).

## 3. Importer dans la base locale (poste de travail)

```
python scripts/init_db.py arbre.db
python scripts/gedcom_import.py sauvegardes/…/arbre.ged arbre.db --label "Arbre Famille X, export du AAAA-MM-JJ"
```
Crée personnes, événements (naissance, baptême, décès, inhumation, mariage, profession, résidence…), relations (époux, parent) et une source « import GEDCOM » de niveau B. Pas de script (Chat, Docs) : lis le GEDCOM comme un texte, produis un tableau personnes / événements / relations dans le journal, avec les mêmes niveaux.

**Limite connue de l'export** (mesurée sur un arbre de 3 271 personnes) : `gedcom_export.py` ne recrée pas les familles d'un seul conjoint sans enfant ni relation (5 sur 1 582 dans ce cas, avec leur événement de mariage). Les personnes, elles, sont toutes conservées. Le fichier `.ged` d'origine reste donc la sauvegarde de référence ; l'export depuis la base sert à republier ou à échanger, et son contenu se compare toujours à l'original avant usage.

## 4. Republier vers un site

À faire seulement sur demande explicite, car cela peut **remplacer** l'arbre en ligne.
1. **Sauvegarde d'abord** (§2), toujours, même si l'utilisateur dit qu'il en a une.
2. `python scripts/gedcom_export.py arbre.db arbre_exporte.ged` produit un GEDCOM 5.5.1 UTF-8.
3. Relis le fichier avec l'utilisateur (nombre de personnes, quelques fiches).
4. L'import se fait sur la page « Mise à jour GEDCOM » (`gw.geneanet.org/my-tree/operations/update`), par l'utilisateur ou avec son accord explicite à chaque étape. Ne clique pas sur la confirmation finale sans accord.
5. Rouvre l'arbre ensuite et compare le nombre de personnes avec la base.

## 5. Site sans export : lecture page à page

Seulement si : (a) le site ne propose aucune export, (b) les données sont celles de l'utilisateur ou qu'il a le droit de copier, (c) il a vérifié les conditions du site. Méthode :
- Utilise la **session déjà connectée** du propriétaire, en lecture seule. Aucun mot de passe, aucun contournement de captcha ou de blocage.
- **Une page à la fois, à un rythme lent** (quelques secondes à une dizaine de secondes entre pages, avec un peu de variation), jamais en parallèle : l'objectif est de ne pas charger le site, pas de passer inaperçu.
- **Arrête-toi et préviens l'utilisateur** au premier captcha, code 429, page de blocage ou connexion perdue.
- Enregistre la page brute (texte ou HTML) avant de l'analyser, avec l'URL et l'heure, pour pouvoir reprendre sans tout refaire. Garde une liste des pages faites.
- Dépouille ensuite en local vers la base, au niveau B.
Si le volume est grand (des centaines de pages), propose plutôt à l'utilisateur de demander l'export au support du site.

## 6. Vie privée

Un arbre contient des personnes vivantes. Garde les fichiers en local ; ne les envoie à aucun service tiers (OCR en ligne, assistant en ligne) sans accord explicite. Dans le journal, ne reproduis les données de personnes vivantes que si la question l'exige.
