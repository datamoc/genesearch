# Tâche du jour et analyses de l'arbre

Table des matières : 1. Quand proposer · 2. Les six types de tâches · 3. Déroulé d'une tâche · 4. Analyses (correlations, parenté) · 5. Sans script

## 1. Quand proposer

Propose une tâche du jour quand l'utilisateur ouvre une session sur son arbre sans question précise (« on avance ? », « qu'est-ce qu'on fait aujourd'hui ? »), ou termine une tâche. Une seule tâche à la fois, courte, avec un résultat vérifiable : une personne prouvée, une incohérence tranchée, une génération remontée. Dis pourquoi tu la choisis et ce qu'elle peut débloquer. Si l'utilisateur veut autre chose, change.

Avec la base locale (poste de travail, scripts Python) : `python scripts/analyse_arbre.py arbre.db tache --racine "<personne de départ>"`. `--type` force un type. La tâche change chaque jour et évite ce qui figure déjà dans `research_log`. La racine est la personne dont on veut l'ascendance (par exemple l'enfant dont l'arbre est tenu) ; sans racine, tout l'arbre est considéré.

## 2. Les six types de tâches

| Type | Ce que ça fait | Commande de repérage |
|---|---|---|
| **preuve** | Passer un fait de B (arbre) à A (acte lu). On cible les ancêtres proches dont la naissance a plus de 75 ans (délai de communicabilité). | `tache --type preuve` |
| **remonter** | Trouver les parents d'un ancêtre qui n'en a pas. On classe par facilité : naissance entre 1792 et 1920 (état civil), lieu connu, proximité de la racine. | `frontiere` |
| **valider** | Trancher une incohérence : décès avant la naissance, parent de 13 ans, enfant né après la mort de sa mère, marié à 14 ans, âge de 106 ans. | `anomalies` |
| **manquant** | Retrouver un parent absent (un seul des deux connu), un enfant probable (écart de 6 ans ou plus entre deux frères et sœurs), un décès inconnu pour un ancêtre né avant 1925. | `manquants` |
| **correlation** | Repérer des régularités : métiers par nom de famille et par zone, transmission du métier de parent à enfant, migrations naissance → décès. | `correlations` |
| **parente** | Mesurer le lien entre deux personnes (ancêtres communs, degré, proximité génétique estimée). | `parente A B` |

## 3. Déroulé d'une tâche

1. **Annonce la tâche** : la personne, le fait en question, la source actuelle (B) et ce que tu cherches.
2. **Cherche** avec les moyens de `sources-france.md` et `methode.md` : Geneanet (registre numérisé, filtre Décès), data.bnf.fr, archives, presse. Va aussi loin que possible seul ; demande de l'aide pour lire une image douteuse (`demande-aide.md`).
3. **Consigne** dans la base, que la recherche réussisse ou non :
   - `research_log` : base consultée, requête (avec le nom de la personne, pour qu'elle ne soit pas reproposée), résultat, suite ;
   - `evidence` : l'affirmation, sa source, son niveau (A si acte lu, sinon B ou C), qui a lu ;
   - corrige `events` ou `persons` seulement si une source de niveau A le justifie ; garde l'ancienne valeur dans `notes`.
4. **Conclus** en deux lignes : ce qui est établi, ce qui reste, et la suite logique (ou la tâche de demain).

## 3 bis. Valider vite, avec une interface locale (poste de travail)

Quand l'utilisateur ou son entourage a déjà lu beaucoup d'actes, la validation en série passe par `scripts/validation_ui.py` :

```
python scripts/validation_ui.py arbre.db --racine "<personne de départ>" --lecteur "<prénom de celui qui valide>"
```
Elle ouvre une page dans le navigateur (adresse locale à jeton, rien ne sort du poste). Une fiche par personne, des ancêtres proches vers les lointains, avec naissance, mariage et décès ; un clic par fait : **A** acte lu, **B** notice seulement, **C** déduction, **?** douteux, avec une cote ou un lien facultatif. Le niveau et le nom du lecteur sont écrits dans `evidence`, et la fiche n'est plus proposée. Un doute marqué « ? » reste en C avec la mention `[DOUTEUX]` : à reprendre dans une tâche « valider ».

Pourquoi tout est en B au départ : un export d'arbre ne dit pas qui a lu quel acte. L'import classe donc tout en B, sauf indication contraire dans les sources de l'export (seules les mentions « acte », « registre », « livret de famille » y font exception, et elles restent à confirmer). La validation par l'interface, faite par la personne qui a lu les actes, remplace ce classement par défaut. Ne promeus jamais en A à sa place : seule une lecture réelle de l'acte, la tienne ou celle d'un humain, justifie A.

Les dates visiblement fausses (un mariage en 1399 pour une personne née en 1975) se repèrent aussi avec `anomalies`.

## 3 ter. Rapport de séance

`python scripts/rapport_preuves.py arbre.db rapport.pdf --titre "…"` produit un PDF : légende des niveaux, **preuves de niveau A** (fait, source avec cote, lecteur, citation), faits incertains (C), **pistes trouvées non prouvées** (journal), **questions ouvertes** (aides demandées, écarts à trancher) et incohérences repérées. Les personnes probablement vivantes (nées il y a moins de 100 ans, sans décès connu) sont **retirées** : leurs noms, dates et lieux n'apparaissent pas, seul le nombre de faits est donné ; `--tout` désactive ce masquage (document à garder en local). Sans la bibliothèque `reportlab`, `--html` écrit une page à imprimer en PDF depuis un navigateur.

À proposer en fin de séance, pour garder une trace et pour la partager avec la personne qui tient l'arbre en ligne : ce qu'elle doit corriger ou confirmer y figure. Sans scripts (Chat, Docs), le journal d'enquête joue ce rôle ; pour un PDF, utiliser l'outil de création de documents disponible, avec les mêmes sections.

## 4. Analyses

**Corrélations.** Ce sont des pistes, jamais des preuves. Un même nom de famille dans un même village n'est pas une parenté ; un même métier chez deux frères est une tendance, pas une règle. Utilise-les pour choisir où chercher (archives d'un métier, d'une paroisse, d'une corporation), puis vérifie par des actes.

**Proximité génétique.** `parente A B` cherche les ancêtres communs les plus récents et applique le coefficient de parenté de Wright : somme, sur chaque chemin qui relie A et B par un ancêtre commun, de (1/2) puissance (nombre de générations de A + nombre de générations de B). Exemples : parent-enfant 50 %, frères et sœurs 50 % (deux ancêtres communs), grand-parent 25 %, oncle 25 %, cousins germains 12,5 %, grand-oncle 12,5 %. Limites à dire à l'utilisateur :
- c'est une moyenne théorique ; l'ADN réellement partagé varie, surtout au-delà de cousins germains ;
- l'arbre ne contient que les liens connus : « aucun ancêtre commun » signifie « pas dans cet arbre », pas « pas de lien » ;
- la consanguinité des ancêtres communs n'est pas prise en compte : la valeur est un plancher.

**Anomalies.** Une anomalie est un signal, pas une erreur : la date a pu être mal lue, deux homonymes confondus, une source fausse. Cherche toujours l'acte avant de corriger.

## 5. Sans script (Chat, Docs)

Les mêmes questions se posent sur le tableau personnes / événements / relations du journal :
- **preuve** : ancêtres directs dont tous les faits sont en B ;
- **remonter** : lignes qui s'arrêtent, classées par date de naissance (1792-1920 d'abord) ;
- **valider** : écarts d'âge impossibles entre parent et enfant, dates incohérentes ;
- **manquant** : un seul parent connu, intervalle de plus de six ans entre frères et sœurs ;
- **parente** : liste les ancêtres de A et de B avec leur nombre de générations, repère les communs, applique 1/2 puissance (n1 + n2).
Propose une seule tâche, comme avec le script.
