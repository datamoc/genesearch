# Méthode : pivots quand une personne « disparaît »

Table des matières : 1. Ordre général · 2. Pivots · 3. Cas d'école · 4. Quand s'arrêter

## 0. Identifier la personne avant de la suivre

Quand la question part d'une entreprise, d'un livre ou d'un événement (« le fondateur de… »), ne cherche pas le décès tout de suite : établis d'abord **qui** est la personne, avec nom complet, prénoms, date et lieu de naissance. Sans cela, tout le reste (actes, recensements, tables) est de l'homonymie en puissance. Points d'entrée :
- les notices de personnalités des communes (Geneawiki, Wikipédia de la commune), qui citent souvent Léonore ;
- **data.bnf.fr** pour toute personne qui a publié (brochure, monographie, rapport) : interroge-la dès que tu as un nom et un prénom, par SPARQL si tu n'as qu'un fetch (voir `sources-france.md`). Elle donne souvent naissance et mort avec lieu et jour. C'est le raccourci le plus rentable de cette liste ;
- Wikidata (identifiants Léonore, BnF) ;
- les actes de société (annuaires, Journal officiel, presse financière) qui donnent prénoms, adresse, parfois profession et âge ;
- les études d'historiens sur l'entreprise, dont les notes citent les archives.
Écris l'identité en niveau B tant que l'acte de naissance n'a pas été vu, et garde les homonymes rencontrés dans le journal.

## 0 bis. Graphies et écarts

- **Essaie les variantes d'un nom** avant de conclure à l'absence : une personne introuvable sous « Juhles » apparaissait sous « Julhes » (lettres permutées, aussi accents, tirets, doubles consonnes, Sch/Ch, ä/ae, ou/u, prénoms composés dans l'autre ordre). Dans Geneanet, l'option « ajouter les variantes sur le nom » aide, mais ne remplace pas les essais manuels. Note chaque graphie essayée dans le journal.
- **Écart entre ton arbre et une source** (naissance 1766 contre 1764 ailleurs, « vers 1776 » contre une date exacte) : l'acte prime sur les arbres. Tant que l'acte n'est pas lu, garde les deux valeurs, marque la question ouverte et ne choisis pas la plus plausible.
- **Un acte de mariage est le plus riche des actes** pour remonter : il donne les parents des deux époux (avec professions), l'âge, souvent les dates et lieux de naissance, et les témoins (fréquemment des frères et sœurs).

## 1. Ordre général

Commence par ce qui est peu coûteux et très discriminant, puis élargis. Entre deux pistes équivalentes, prends celle qui se lit en texte avant celle qui exige des images.

1. Notices existantes (BnF, Wikipédia, Léonore, Geneawiki, arbres Geneanet) : elles donnent des pistes, jamais des preuves, tant que leur source n'est pas vue.
2. Acte de naissance : mentions marginales (mariage, décès, reconnaissance, divorce). Leur présence dépend de l'époque et de la commune, et elles manquent souvent : les consulter coûte peu, leur absence ne prouve rien.
3. Recensements de population à la dernière adresse connue, puis aux adresses suivantes.
4. Tables de décès (annuelles et décennales) du lieu de naissance et du dernier domicile connu.
5. Pivots ci-dessous si tout cela échoue.

## 2. Pivots

- **Conjoint et nom de jeune fille.** Trouver l'épouse (acte de mariage, contrat, mention marginale de l'acte de naissance du mari, acte de naissance d'un enfant) ouvre une seconde porte : les index sont parfois lacunaires pour un nom et complets pour l'autre.
- **Enfants, gendres, beaux-parents.** À un âge avancé, la personne vit souvent chez un enfant ou un gendre. Un recensement où elle est « chez » quelqu'un se retrouve en cherchant ce quelqu'un.
- **Biens et hypothèques.** Les registres de conservation des hypothèques et les répertoires de formalités donnent un domicile à chaque mutation, y compris le dernier. Utile quand la personne a hérité ou vendu des terres.
- **Employeur et carrière.** Rachat d'une société, nouvel emploi, retraite, caisse de retraite : la fiche d'un employeur ou d'un annuaire (Didot-Bottin, annuaires professionnels) donne une ville.
- **Presse.** Faire-part, nécrologies, chronique mondaine, annonce de succession : Gallica, RetroNews, presse régionale numérisée, bulletins de sociétés savantes ou professionnelles.
- **Distinctions.** Dossier Léonore (Légion d'honneur) : la ligne de décès vide est elle-même un indice (dossier non clos). Les pièces annexes donnent adresses et état civil.
- **Succession et enregistrement.** Tables de successions et absences, déclarations de mutation par décès au bureau du dernier domicile.
- **Changement de lieu.** Si la dernière adresse connue est ancienne, cherche un déménagement vers la capitale, vers un enfant, ou une retraite en région. Les hypothèques et les recensements postérieurs servent à le repérer.
- **Grandes villes.** Pas de table décennale partout. Quand l'on connaît l'arrondissement ou la période, la table annuelle de l'arrondissement suffit (voir `sources-france.md`).

## 3. Cas d'école (sans en donner la solution)

Un industriel né dans le Rhône en 1866, dont la société est reprise en 1931, a un dossier Léonore à ligne de décès vide, pas de décès dans les tables de sa naissance ni de son ancien domicile, pas d'indication dans sa mention marginale. La résolution passe par plusieurs pivots enchaînés : domicile lors du dernier recensement, famille proche, mutations de biens, puis une base d'index de recensements interrogée par le nom de l'épouse, qui était indexée alors que le mari ne l'était pas. Retiens le schéma : une seule piste directe échoue presque toujours ; c'est l'enchaînement et l'essai du nom d'un proche qui aboutit.

Une réponse « trouvée instantanément » qui donne le lieu de décès sans pouvoir citer un acte ou une table est suspecte : vérifie le lieu par une table ou une presse avant de l'écrire.

## 4. Quand s'arrêter

Arrête et rends compte quand : la prochaine piste exige des images que seul un humain peut consulter, ou un compte que tu n'as pas, ou plus de trois pistes consécutives sont négatives sans nouvelle hypothèse. Présente alors l'état des connaissances, les négatifs, et la demande d'aide la plus rentable.
