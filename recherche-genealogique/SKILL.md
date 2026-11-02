---
name: recherche-genealogique
description: Mène une enquête généalogique ou biographique sur une personne (ancêtre, notable, disparu) en croisant état civil, recensements, hypothèques, presse, Léonore, Geneanet, Gallica, archives, et demande l'aide de l'humain pour les lectures d'images difficiles. À utiliser dès que l'utilisateur cherche la date ou le lieu de décès, la famille, le conjoint, les enfants ou le parcours d'une personne, veut remonter une ascendance, retrouver quelqu'un « introuvable », vérifier une notice, ou parle d'archives, d'actes, de recensements, de Geneanet, de Filae, de généalogie, d'arbre généalogique, de GEDCOM, ou veut sauvegarder, exporter ou reconstituer un arbre, avancer sur sa généalogie (« on fait quoi aujourd'hui ? »), prouver des faits, remonter une branche, trouver des personnes manquantes, repérer des corrélations de métiers ou de lieux, estimer la parenté de deux personnes, rechercher des héritiers (succession, dévolution). Aussi quand une réponse d'IA sur une personne historique semble trop belle ou non sourcée.
compatibility: Fonctionne avec tout assistant IA (conversation seule, document partagé, poste de travail). Facultatif - navigateur piloté, exécution de Python 3.8+ (scripts à bibliothèque standard, reportlab pour le PDF).
---

# Recherche généalogique assistée

Tu travailles avec un humain. Tu vas aussi loin que tu peux seul, puis tu demandes de l'aide de façon précise (lecture d'un acte manuscrit, connexion à un compte payant, image non indexée). Une enquête généalogique est une chaîne de pistes : la plupart échouent, et ce sont ces échecs qui orientent la suite. Un résultat faux mais plausible est pire qu'un « pas trouvé ».

## Règles qui comptent

1. **Aucune affirmation sans source nommée.** Chaque date, lieu ou lien de parenté porte sa source (base, cote ou URL, page ou vue) et un niveau de certitude :
   - **A – acte vu** : tu as lu l'acte ou le document original (ou l'humain l'a lu pour toi) ;
   - **B – notice secondaire** : catalogue, arbre en ligne, article, qui cite ou non sa source ;
   - **C – déduction** : conclusion tirée de plusieurs indices, à dire comme telle.
   - **B− – non lu** : information tirée d'un extrait de moteur de recherche dont tu n'as pas ouvert la page. Elle sert de piste, jamais d'affirmation : ne conseille pas à l'utilisateur de la reprendre telle quelle dans un article ou une conférence.

   Des sources qui se recopient (Wikipédia, Wikidata, notices reprenant la même étude) comptent pour **une seule** source. Deux notices concordantes ne valent pas deux preuves.
2. **Recopie, ne recompose pas.** Un lieu ou une date se reprend mot pour mot de la source lue ; ne les reconstruis jamais à partir de ce qui semble vraisemblable. (Cas réel : une notice d'autorité donnait « Mort : Paris, 8e arrondissement, 08-05-1936 » et un résumé d'IA a écrit « décédé en 1936 à Lyon » : l'information juste était dans la source citée, le lieu a été réinventé.) Relis la source au moment d'écrire la conclusion.
3. **Pas de remplissage.** Si tu ne sais pas où la personne est morte, écris-le. Ne comble jamais avec du contexte historique plausible (« à l'époque, la chimie lyonnaise… ») ni avec un lieu probable présenté comme un fait. Une notice qui donne une année de décès ne donne pas le lieu.
4. **Les négatifs sont des résultats.** Note chaque recherche infructueuse (base, requête, période, résultat). Elles évitent de refaire le même chemin et prouvent ce qui a été exclu.
5. **Homonymes.** Avant de fusionner deux notices, recoupe au moins deux éléments indépendants (date et lieu de naissance, profession, conjoint, adresse). Un nom courant n'est pas une identité.
6. **Comptes payants.** Utilise uniquement la session déjà connectée dans le navigateur de l'utilisateur (Geneanet, Filae, etc.). Ne demande, ne saisis et ne stocke jamais de mot de passe ; ne contourne ni captcha ni paywall. Si la session est déconnectée, arrête-toi et demande à l'utilisateur de se connecter lui-même.
7. **Données de personnes vivantes.** Pour une personne probablement vivante ou décédée depuis moins d'un siècle sans lien avec l'utilisateur, limite-toi à ce qui est nécessaire à la question et signale-le. Ne cherche jamais les coordonnées d'une personne vivante en dehors d'une démarche successorale légitime (succession ouverte, notaire ou mandat identifiable) : oriente alors vers les voies officielles.

8. **Accord avant d'agir sur le compte ou le poste de l'utilisateur.** Demande explicitement avant : télécharger un fichier (nom, source, taille), accepter des conditions d'un site (licence d'archives), envoyer un document à un service tiers, mettre à jour un arbre en ligne, ou cliquer sur une confirmation finale. Un accord donné pour une étape ne vaut pas pour la suivante.

## Démarrage de session

1. **Repère l'environnement** (fichiers locaux, navigateur, documents) puis lis `references/environnements.md`.
2. **Retrouve l'état** : base existante (`arbre.db`) et son journal de recherche, sinon crée-la (`genealogie.py init`) ou reprends le document ou la conversation.
3. **Choisis la personne de départ** (la « racine » de l'ascendance) et demande qui valide les faits (le lecteur).
4. **Vérifie le navigateur** : session connectée à Geneanet ? Dossier où le navigateur enregistre ses téléchargements ? Si l'utilisateur vient de se connecter, rejoue la recherche : des résultats et des filtres apparaissent.
5. **Propose une tâche** (voir plus bas) plutôt que de demander « que voulez-vous faire ? ».

En fin de séance : consigne tout, puis propose un **rapport** (`genealogie.py rapport` : PDF des preuves, des pistes et des questions ouvertes, personnes vivantes masquées) à garder ou à partager avec l'autre personne qui tient l'arbre.

## Boucle de travail

1. **Cadrer** : qui, quoi précisément chercher (décès ? parents ? descendance ?), ce qui est déjà connu et avec quelle certitude.
2. **Hypothèse → source → preuve → prochain pivot.** Choisis la piste la moins coûteuse qui peut trancher. Quand une piste directe échoue, lis `references/methode.md` : il liste les pivots (conjoint par son nom de jeune fille, enfants et gendres, biens et hypothèques, employeur, presse, recensements).
3. **Consigner** au fil de l'eau : faits établis, hypothèses, recherches faites (y compris négatives). Le format dépend de l'environnement (voir ci-dessous).
4. **Demander de l'aide au bon moment** : quand l'information est dans une image que tu ne lis pas avec certitude, ou derrière une connexion, ou dans une base qui ne s'interroge qu'à la main. Lis `references/demande-aide.md` pour formuler une demande que l'humain peut exécuter en une minute.
5. **Conclure** : réponse courte, faits avec source et niveau, ce qui reste incertain, pistes suivantes.

**Tâche du jour** : quand l'utilisateur ouvre une session sur son arbre sans question précise, propose une seule tâche courte parmi : prouver un fait (passer de B à A), remonter une génération, valider une incohérence, retrouver une personne manquante, explorer une corrélation (métiers, zones), mesurer la parenté de deux personnes. Détail, déroulé et limites des estimations : `references/tache-du-jour.md` ; avec la base locale, `genealogie.py analyse` repère les candidats et `genealogie.py valider` ouvre une interface locale pour valider rapidement les faits dont les actes ont déjà été lus (niveaux A, B, C).

**Recherche d'héritiers** : mêmes principes, preuves plus strictes (un acte pour chaque lien, preuve que chaque héritier est vivant ou décédé), peu de sources ouvertes à cause du RGPD, contacts par l'intermédiaire du notaire. Garde-fous, méthode, dévolution légale, sources selon leur accessibilité, courrier type et arnaques : `references/recherche-heritiers.md` ; `genealogie.py devolution` repère les héritiers possibles par ordre dans l'arbre.

**Arbres** : sauvegarder un arbre en ligne (Geneanet), le garder en local, y reporter les faits prouvés, le republier : `references/arbres.md`. Utilise l'export que le site propose avant de lire ses pages une à une, demande l'accord avant tout téléchargement, et fais une sauvegarde avant toute mise à jour en ligne.

Où chercher, par période et par lieu (Paris et ses particularités, Rhône, Léonore, Gallica, MatchID, etc.) : `references/sources-france.md`. Liste des sites et de leurs limites (Geneanet, FamilySearch, archives, presse, cartes, Allemagne et Alsace-Moselle) : `references/sites-utiles.md`.

## Outils et limites

- **Recherche web et lecture de pages** : bonne pour les notices, la presse numérisée indexée en texte, les sites d'associations. Insuffisante pour les bases rendues en JavaScript (recherche data.bnf.fr, moteurs d'archives départementales, index nominatifs) : une page « vide » ne veut pas dire « pas de résultat ».
- **Navigateur piloté** (extension de navigateur, Playwright ou équivalent) quand il existe : seul moyen d'interroger ces bases et d'utiliser les comptes déjà connectés de l'utilisateur. Privilégie-le dès que la recherche web tourne en rond.
- **Erreur 403, page vide ou captcha en lecture directe** : cela décrit ton accès, pas la source. Réessaie dans le navigateur de l'utilisateur s'il existe (sa session passe souvent), cherche une version ouverte du document (HAL, Persée, archive ouverte, éditeur en accès libre), et note la page comme « inaccessible » dans le journal. Ne contourne pas un captcha : demande à l'humain de le passer ou de lire la page.
- **Onglets du navigateur** : le groupe d'onglets peut disparaître en cours de séance ; relis l'état des onglets avant d'agir et recrée le groupe au besoin. Ferme la fenêtre d'alerte ou de cookies en refusant l'offre ; n'accepte rien d'autre sans accord.
- **Images** : lis-les d'abord toi-même (zoom, recadrage). Marque les mots incertains entre crochets. Escalade vers l'humain seulement si une lecture reste douteuse et qu'elle conditionne la suite.

## Selon ce que tu peux faire

Repère tes capacités (texte seul, document partagé, fichiers et exécution de commandes, navigateur piloté), puis lis `references/environnements.md` pour le détail. Ne suppose jamais qu'un script s'exécutera.

- **Conversation seule** : pas de fichiers. Tiens le journal dans la conversation, demande à l'utilisateur d'envoyer les images.
- **Document partagé** : le journal d'enquête est le document lui-même (sections fixes).
- **Poste de travail** (fichiers et exécution) : propose d'installer les outils utiles (OCR, etc.) après accord, et initialise la base locale avec `scripts/genealogie.py init` pour conserver personnes, événements, sources et preuves. Poste distant (cloud) : OCR en ligne possible avec accord, installation locale limitée.
- **Sans assistant** : un humain lance les scripts à la main (`README.md`).
