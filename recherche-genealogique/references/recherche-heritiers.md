# Recherche d'héritiers

Table des matières : 1. Cadre et garde-fous · 2. Les principes restent les mêmes · 3. Méthode · 4. Dévolution légale, résumé · 5. Sources selon leur accessibilité · 6. Contacter un héritier · 7. Arnaques et vérifications · 8. Cas particuliers · 9. Livrables et outils

Ce guide décrit une démarche et ne constitue pas un conseil juridique. Les règles (état civil, RGPD, profession de généalogiste successoral, droit des successions) changent et dépendent de la date du décès et du pays : à faire confirmer par le notaire chargé de la succession. Les points marqués « à vérifier » le sont particulièrement.

## 1. Cadre et garde-fous

**Usage légitime** : une succession est ouverte (un décès est établi) et la personne qui demande agit pour elle (héritier, famille, notaire, généalogiste mandaté), ou cherche les cousins d'une famille pour une succession, ou vérifie une dévolution déjà établie.

**Ce que tu fais** : reconstituer la parenté par des actes, appliquer la dévolution légale à l'arbre, préparer un dossier de preuves pour le notaire, rédiger un courrier sobre.

**Ce que tu ne fais pas** :
- retrouver l'adresse, le téléphone, l'employeur ou la vie privée d'une personne vivante en dehors d'une démarche successorale légitime ;
- constituer des fiches sur des personnes vivantes, ou en conserver plus que nécessaire ;
- interroger des fichiers réservés (fiscaux, sociaux, bancaires, police) ou contourner un accès ;
- collecter des profils de réseaux sociaux en série, ni démarcher.

Si la demande ressemble à la recherche d'une personne vivante sans lien avec une succession (ancien conjoint, voisin, débiteur, personne qui a coupé les ponts), ne cherche pas ses coordonnées : explique pourquoi et oriente vers les voies officielles (notaire, mairie qui transmet un courrier, avocat, commissaire de justice, tribunal).

**Au début d'un dossier**, demande : qui est le défunt, y a-t-il un acte de décès, qui mandate la recherche (notaire, héritier, famille), et dans quel but. Sans succession ouverte ni mandat identifiable, reste à de la généalogie familiale ordinaire sur des personnes décédées.

**RGPD, en pratique** (rappel, pas un avis juridique) : finalité précise ; minimisation (ne garder que ce qui établit la qualité d'héritier) ; durée limitée ; sécurité (fichiers locaux, aucun envoi à un service tiers sans accord) ; information des personnes quand on les contacte ; accès et rectification sur demande ; pas de donnée sensible inutile (santé, religion, opinions). Les documents partagés masquent les personnes vivantes.

## 2. Les principes restent les mêmes

Sources nommées, niveaux A/B/C, recopie sans recomposer, négatifs consignés, homonymes écartés : tout cela s'applique, avec des exigences plus fortes.

- **Chaîne de preuves.** Chaque héritier se prouve par une suite d'actes : acte de décès du défunt (date, lieu, dernier domicile), acte de naissance de l'héritier avec filiation, actes intermédiaires si l'on remonte ou redescend (naissance, mariage, décès de chaque maillon). Niveau **A** pour chaque maillon avant tout courrier ; le niveau B (arbre, notice) sert à s'orienter.
- **Vivant ou décédé** se prouve : mentions marginales de l'acte de naissance (mariage, décès), fichier INSEE des décès depuis 1970, acte de décès. « Aucun décès connu » ne prouve pas qu'une personne est vivante.
- **Les homonymes coûtent plus cher** : écrire à la mauvaise personne divulgue des informations sur une succession. Recoupe au moins deux éléments (naissance, parents, conjoint, ancienne adresse) avant tout contact.
- **Les échecs aussi** : « introuvable à telle date, par tels moyens » se note dans le journal, avec les démarches faites, pour que le notaire ne les refasse pas.

## 3. Méthode

1. **Défunt** : état civil complet (noms, prénoms, naissance, décès, dernier domicile, situation matrimoniale). Copie intégrale de l'acte de décès auprès de la mairie.
2. **Dispositions** : testament, contrat de mariage, donations, assurance-vie. Ce n'est pas du ressort du généalogiste seul : le notaire interroge le fichier central des dispositions de dernières volontés et les assureurs (à vérifier).
3. **Famille proche** : conjoint, enfants, parents, frères et sœurs, à partir du livret de famille et des actes.
4. **Dévolution** : `python scripts/genealogie.py devolution arbre.db "<défunt>"` repère les héritiers possibles par ordre (voir § 4).
5. **Preuves** : un acte pour chaque lien ; compléter l'arbre des branches manquantes (demi-frères et sœurs, enfants nés hors mariage, adoptions, reconnaissances).
6. **Statut de chaque héritier** : vivant ou décédé, avec la preuve (§ 2).
7. **Localisation** : par des voies légitimes seulement (§ 5), de préférence par l'intermédiaire du notaire.
8. **Contact** : courrier sobre (§ 6), une fois l'identité de l'héritier recoupée.
9. **Dossier** : tableau de dévolution, arbre avec pièces, journal des démarches et des contacts, remis au notaire.

## 4. Dévolution légale, résumé (France, Code civil, à vérifier selon la date du décès)

| Ordre | Héritiers | Notes |
|---|---|---|
| 1er | Descendants (enfants, puis petits-enfants…) | Représentation : les descendants d'un enfant prédécédé le remplacent, par souches |
| 2e | Père et mère, frères et sœurs et leurs descendants | Parts à fixer selon qui survit ; demi-frères et sœurs : partage par ligne |
| 3e | Ascendants ordinaires (grands-parents…) | Le plus proche dans chaque ligne ; **fente** : moitié ligne paternelle, moitié ligne maternelle |
| 4e | Collatéraux ordinaires (oncles, tantes, cousins…) jusqu'au **6e degré** | Le plus proche dans chaque ligne ; pas de représentation hors frères et sœurs |

- On s'arrête au premier ordre qui a un héritier prouvé vivant au décès.
- Le **conjoint survivant** a des droits qui dépendent de la configuration (enfants communs ou non, parents, etc.) : ils ne sont pas calculés par l'outil, le notaire les établit.
- Ne sont pas traités : testament, donations, renonciation, indignité, adoption, droit étranger.
- Le degré se compte en additionnant les générations de chaque côté jusqu'à l'ancêtre commun (cousin germain : 4e degré).

## 5. Sources selon leur accessibilité

Moins il y a de sources ouvertes, plus il faut passer par des canaux officiels. Ne cherche pas à contourner une restriction : demande à l'humain ou au notaire.

| Accès | Sources | Remarques |
|---|---|---|
| **Ouvertes** | Actes d'état civil de plus de 75 ans (archives en ligne) ; fichier INSEE des décès depuis 1970 (MatchID) ; avis de décès dans la presse et sur les sites d'avis (ils citent souvent conjoint, enfants, frères et sœurs, petits-enfants) ; arbres en ligne (personnes vivantes en général masquées) ; Gallica, RetroNews ; registre du commerce et annonces légales ; publicités de successions vacantes (à vérifier) | Une source ouverte reste de niveau B tant que l'acte n'est pas lu |
| **Sous conditions** (qualité à justifier, demande motivée) | Actes de moins de 75 ans (naissance, mariage) et copies intégrales : mairie du lieu de l'acte, délivrance limitée à certaines personnes ou avec mandat du notaire (à vérifier) ; livret de famille (détenu par la famille) ; renseignements du fichier immobilier et livre foncier d'Alsace-Moselle (demande précise, souvent payante) ; contrats d'assurance-vie via l'AGIRA ; caisses de retraite | Mentionner la qualité de mandataire du notaire ou d'héritier ; garder la trace de la demande |
| **Réservées** (notaire, administration) | Fichier central des dispositions de dernières volontés ; fichier des comptes bancaires (FICOBA) ; fichiers fiscaux et sociaux ; listes électorales hors usage prévu | Ne les sollicite pas toi-même ; indique au notaire qu'il peut le faire |

**Pour joindre quelqu'un de vivant** : le notaire ; la mairie du dernier domicile connu, qui peut transmettre un courrier sans donner l'adresse ; une famille qui connaît la personne, avec son accord pour transmettre ; une demande de renseignements adressée à des tiers (voisins, employeurs) est à éviter : elle divulgue la démarche.

## 6. Contacter un héritier

- Passe par le **notaire** ou obtiens un mandat écrit. Le courrier part du notaire ou de la personne mandatée, sous son nom, avec des coordonnées vérifiables.
- Contenu : qui écrit et au nom de qui, la succession concernée (nom du défunt, notaire en charge), ce que l'on demande (confirmer son identité, sa filiation, un contact), un délai raisonnable, comment vérifier l'expéditeur. **Pas de montant**, pas de pression, pas de détail familial inutile, pas de relances répétées.
- N'écris pas à une adresse dont tu n'es pas sûr qu'elle est celle de la bonne personne. Ne communique rien à un tiers.
- Héritier mineur ou protégé : le courrier s'adresse à son représentant légal.
- Aucune réponse : consigne la tentative dans le journal et signale-la au notaire ; n'insiste pas par d'autres canaux.

Courrier type (à faire relire par le notaire) :
> Madame, Monsieur, je vous écris au nom de Maître X, notaire à Y, chargé du règlement de la succession de Z. Les recherches généalogiques nous conduisent à penser que vous pourriez être concerné(e) par cette succession. Pouvez-vous prendre contact avec l'étude (coordonnées ci-dessous) avant le (date), afin de confirmer votre identité et votre lien de parenté ? Aucun versement ni document bancaire ne vous est demandé. Vous pouvez vérifier ce courrier en appelant directement l'étude au numéro figurant dans l'annuaire.

## 7. Arnaques et vérifications (si c'est toi qu'on contacte)

- **Signaux d'alerte** : demande d'argent ou de coordonnées bancaires avant tout, urgence, adresse de messagerie gratuite, pas de nom de notaire vérifiable, promesse d'une grosse somme sans détail.
- **Vérifier** : appelle l'étude notariale par un numéro que tu as trouvé toi-même ; demande le nom du défunt et ton lien supposé ; tu peux traiter directement avec le notaire sans passer par un tiers.
- **Contrat de révélation** : un généalogiste peut proposer de te révéler une succession contre un pourcentage. Lis les conditions, la durée d'exclusivité et le taux avant de signer ; compare ; fais relire par un notaire ou un avocat (à vérifier selon le cas).

## 8. Cas particuliers

- **Succession vacante ou non réclamée** : un curateur est nommé ; l'administration des domaines (direction nationale d'interventions domaniales) intervient ; passer par un notaire (à vérifier).
- **Décès ou héritiers à l'étranger** : la loi applicable dépend en général de la dernière résidence habituelle pour les décès après août 2015 (règlement européen sur les successions) ; états civils étrangers à légaliser ou apostiller et à faire traduire (à vérifier).
- **Option des héritiers** : accepter ou renoncer dans un délai de dix ans à compter du décès en principe (à vérifier) ; une renonciation modifie l'ordre et les parts.
- **Filiations complexes** : adoption, reconnaissance tardive, enfant né hors mariage : lire les mentions marginales et demander l'aide du notaire.
- **Succession ancienne** : si le défunt est mort depuis longtemps, il n'y a peut-être plus rien à ouvrir ; cela reste de la généalogie familiale.

## 9. Livrables et outils

- `python scripts/genealogie.py devolution arbre.db "<défunt>" [--deces ANNEE] [--tous] [--md fichier.md]` : tableau des héritiers possibles par ordre, avec statut, part indicative et pièces à prouver. Le fichier Markdown contient des personnes vivantes : le garder en local.
- `python scripts/genealogie.py rapport arbre.db rapport.pdf --tout` : preuves et questions ouvertes pour le notaire (version complète, document confidentiel).
- Journal de recherche (`research_log`) : une ligne par démarche, avec la date, la source, le résultat et la suite, y compris les contacts tentés.
- `python scripts/genealogie.py valider …` : faire passer les faits en niveau A à mesure que les actes sont lus.
