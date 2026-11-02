# Sources pour la France (et leurs pièges)

Les URL et noms de bases changent : si un lien ne répond plus, cherche le nom de la base sur le web plutôt que de conclure que la source n'existe pas.

## Notices et personnes notables
- **data.bnf.fr / catalogue.bnf.fr** : notices d'autorité de toute personne ayant publié (même une brochure, une monographie, un rapport de société savante). La **notice complète** donne naissance et mort avec **lieu et jour** (par exemple « Mort : Paris, 8e arrondissement, 08-05-1936 ») : ne t'arrête pas au titre « (1866-1936) », lis les champs. La page de recherche et la page de notice sont rendues en JavaScript, donc illisibles par un simple fetch, mais :
  - **Dans un navigateur** : `https://data.bnf.fr/fr/search?term=<Prénom+Nom>` puis cliquer le résultat (attendre 2-3 s).
  - **Sans navigateur (fetch seul, marche partout)** : le point d'accès SPARQL répond en JSON. Modèle, à adapter (nom, prénom) :
    `https://data.bnf.fr/sparql?query=<requête encodée>&format=application%2Fsparql-results%2Bjson`
    avec la requête
    `SELECT ?p ?b ?d ?pd WHERE { ?p <http://xmlns.com/foaf/0.1/familyName> "Silvestre"; <http://xmlns.com/foaf/0.1/givenName> "Claude"; <http://rdvocab.info/ElementsGr2/dateOfBirth> ?b; <http://rdvocab.info/ElementsGr2/dateOfDeath> ?d. OPTIONAL { ?p <http://rdvocab.info/ElementsGr2/placeOfDeath> ?pd } } LIMIT 20`
    Les dates reviennent sous forme d'année (`/date/1936/`), le lieu de mort en texte. L'URI `ark:/12148/cb…` du résultat est l'identifiant à citer. Pour le jour exact, ouvrir la notice dans le navigateur.
  - Une notice d'autorité est de niveau B : sa source (acte, nécrologie) n'est pas toujours citée. Elle est excellente comme pivot, puis à confirmer par l'acte. Vérifie l'**identité** (naissance, profession, œuvres) avant de la rattacher à la personne cherchée.
- **Léonore** (base des Archives nationales, Légion d'honneur) : dossier numérisé, état civil, parfois adresse. Ligne de décès vide = à ne pas interpréter sans autre indice.
- **Wikipédia, Wikidata, Geneawiki** : pistes. Geneawiki liste les personnalités d'une commune avec leurs sources. Wikidata expose souvent des identifiants (Léonore, BnF, cimetière) qui mènent droit à la pièce primaire, et indique pour chaque valeur si elle est référencée : un lieu de décès sans référence reste B−. Wikipédia et Wikidata se recopient souvent : une seule source, pas deux.
- **Dictionnaires biographiques locaux** (académies, sociétés savantes) : bonnes nécrologies de notables.

## État civil et recensements
- **Archives départementales** : état civil (naissances, mariages, décès, tables décennales), recensements, hypothèques, enregistrement. La plupart des moteurs sont rendus en JavaScript et se parcourent à la main : utilise le navigateur, puis demande de l'aide pour les lectures manuscrites.
- **Mentions marginales** sur les actes de naissance : mariage et décès rapportés après coup, selon l'époque et la commune.
- **Tables décennales** : décès de la commune sur dix ans, par ordre alphabétique. Elles n'existent pas partout pour toutes les périodes.
- **Paris** : archives de Paris. Pour une période sans table décennale, il faut chercher par année et par arrondissement dans les tables annuelles. Les listes nominatives de recensement 1926-1936 ont été numérisées et indexées par noms ; l'index est imparfait (noms mal lus, personnes absentes). Si un nom n'est pas indexé, essaie les proches : conjoint, nom de jeune fille, enfants.
- **Convois funèbres** (archives municipales, par ex. Lyon) : tables annuelles, utile si le décès est local.

## Décès récents
- **MatchID / fichier INSEE des décès** : décès depuis 1970. Au-delà de cette date, ne cherche pas ici.

## Presse
- **Gallica** (BnF) : presse et livres, recherche plein texte ; l'OCR est approximatif, essaie plusieurs graphies.
- **RetroNews** : presse, abonnement pour la lecture complète.
- Presse régionale numérisée par les départements.

## Bases collaboratives et payantes
- **Geneanet** : arbres des membres, relevés, registres numérisés, cimetières. Les arbres sont des sources B : lis leur source ou remonte à l'acte. Certaines fonctions exigent un compte ; utilise la session déjà ouverte de l'utilisateur.
- **Filae** : arbres et actes. Même règle.
- **Cimetières et sépultures** : Geneanet, sites de relevés municipaux. Une tombe donne dates, parfois famille.

## Geneanet par le navigateur (testé)

Un fetch direct reçoit un 403 ; la même URL s'ouvre dans le navigateur de l'utilisateur. Index nominatif, sans saisir de formulaire :
`https://www.geneanet.org/fonds/individus/?nom=<NOM>&prenom=<Prénom+Prénom>&place__0__=<Lieu>&go=1`
Ouvre l'URL, ferme la fenêtre d'alerte « Trouvez sans chercher » (refuse l'offre), puis lis le texte de la page. Chaque ligne donne les noms, le conjoint, l'année, le lieu et le type de fonds (Archives, Arbres en ligne, Presse). Cette recherche ne s'interroge que sur les index : la lecture de l'acte lui-même (image) reste à l'humain.

Pour un décès : sur la page de résultats, cocher le filtre **Décès** (bouton radio dans « Événements ») fait remonter les registres indexés avec lieu et date, y compris à Paris. Cliquer le résultat ouvre le **registre numérisé** (`/registres/view/<id>/<vue>`) et, dans le volet de droite, l'**index collaboratif** de la page : nom, prénoms, profession, conjoint, parents, lieu et date de naissance, date de l'événement, et l'identifiant de l'indexeur. Cet index est de niveau B (transcription d'un contributeur) tant que l'acte n'a pas été lu sur l'image. Retiens aussi la **date de l'événement indexée**, qui est celle de l'acte ou de l'inhumation, pas forcément celle du décès : la date de décès exacte se lit dans l'acte.

Quand la connexion change (utilisateur déconnecté puis connecté), **rejoue la même recherche** : des lignes et des filtres apparaissent qui manquaient avant.

Enseignements :
- **Chercher aussi le conjoint** sous son nom de jeune fille : l'index donne souvent le même couple des deux côtés et confirme l'identité (mariage, naissance de l'épouse).
- **Plusieurs lignes identiques** (relevés de mariages dupliqués) comptent pour une seule source.
- Le mariage et la naissance sont bien couverts pour la période 1800-1900 en Rhône ; les **décès postérieurs à 1900** et les **décès hors du département** y sont rares : pour eux, passer aux archives de la ville du dernier domicile (Paris, etc.).
- Les données Premium sont masquées si le compte n'a pas l'abonnement ; l'absence d'une ligne ne prouve rien. Note les champs masqués dans le journal.

## Lire un acte sur le site d'archives départementales (testé : Cantal)

1. **Pars de la source citée par l'arbre.** Une fiche d'arbre qui cite les archives (`archives.cantal.fr/ark:…`) donne le lien direct vers la vue du registre : c'est plus rapide que le moteur de recherche du site.
2. **Conditions de réutilisation.** Le visualiseur affiche d'abord une licence (réutilisation libre, gratuite, mentionner la source) et un bouton « J'ai pris connaissance… et j'accepte les conditions ». Accepter des conditions demande l'accord explicite de l'utilisateur dans la conversation ; ne clique jamais sans.
3. **Un acte s'étend sur plusieurs vues** : le début peut être au bas de la page précédente (« Aujourd'hui quatorze… ») et la suite sur la page d'après. Lis les deux.
4. **Lire une écriture ancienne** : capture la page, puis zoome par blocs (moitié haute, moitié basse de chaque page) ; une capture entière ne suffit pas. Recopie les noms tels que tu les lis, marque les mots incertains (« Falat ? »), et recoupe avec les dates de l'arbre (jour et mois lus, pas déduits).
5. **Calendrier républicain** (1793 à 1805) : convertis la date (14 pluviôse an IV = 3 février 1796) et vérifie qu'elle correspond à celle de l'arbre.
6. **Ce qu'un acte de mariage apporte** : âges, professions, parents des deux époux (avec leurs professions), témoins (souvent des frères et sœurs), et les dates des actes de naissance qu'on a produits : excellent pour passer des faits en niveau A et remonter d'une génération.
7. **Consigne tout de suite** : source (cote et vues), faits en A avec « lecteur : l'assistant IA, à confirmer par un humain » ; les mots douteux en C ou en demande d'aide.

## Pièges
- Les graphies varient (accents, traits d'union, « Bois-d'Oingt » / « Bois d'Oingt » / « Val d'Oingt » après fusion de communes en 2017).
- Les noms de lieux et les arrondissements changent.
- Les dates de numérisation évoluent : une source absente aujourd'hui peut être en ligne demain, et l'inverse.
- Les moteurs rendus en JavaScript renvoient une page « vide » à un simple fetch : ce n'est pas un résultat négatif.
