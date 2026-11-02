#!/usr/bin/env python3
"""Dévolution légale simplifiée (droit français, Code civil art. 731 et suivants) à partir de l'arbre local.

Usage : python devolution.py <base.db> <défunt> [--deces ANNEE] [--tous] [--md fichier.md]

  <défunt>      identifiant de la base ou morceau du nom
  --deces ANNEE année du décès si l'arbre ne la donne pas
  --tous        affiche aussi les ordres suivants (par défaut : l'ordre applicable seulement)
  --md fichier  écrit le tableau en Markdown (document sensible : contient des personnes vivantes)

CE QUE FAIT L'OUTIL : repère, dans l'arbre, les héritiers possibles par ordre (descendants ; père, mère,
frères et sœurs ; ascendants ordinaires ; collatéraux ordinaires jusqu'au 6e degré), applique la représentation
et la fente, et indique pour chacun ce qu'il faut prouver.
CE QUE L'OUTIL NE FAIT PAS : il ne remplace ni un notaire ni un généalogiste successoral. Il ignore les droits
du conjoint, le testament, les donations, la renonciation, l'indignité, l'adoption, le droit étranger. Les
parts affichées sont indicatives ; l'ordre applicable dépend de la preuve qu'un héritier est vivant au décès.
Un statut « présumé vivant » ne vaut pas preuve : il faut l'acte de naissance avec ses mentions.
"""
import sys
from fractions import Fraction
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))
from analyse_arbre import Tree  # noqa: E402

ALIVE_LIKE = ("vivant", "presume_vivant", "a_verifier", "inconnu")


class Devolution:
    def __init__(self, tree, defunt, deces):
        self.t, self.d, self.year = tree, defunt, deces
        self.cache = {}

    def status(self, pid):
        if pid in self.cache:
            return self.cache[pid]
        dy, by = self.t.death_year(pid), self.t.birth_year(pid)
        if dy is not None:
            if dy < self.year:
                r = ("predecede", f"décédé en {dy}")
            elif dy == self.year:
                r = ("a_verifier", f"décédé la même année ({dy}) : établir l'ordre des décès")
            else:
                r = ("vivant", f"vivant au décès (mort en {dy} : sa part passe à ses propres héritiers)")
        elif by is None:
            r = ("inconnu", "dates inconnues : à documenter")
        elif self.year - by > 110:
            r = ("predecede", f"présumé décédé (né en {by})")
        else:
            r = ("presume_vivant", f"né en {by}, aucun décès connu : à prouver vivant")
        self.cache[pid] = r
        return r

    def is_alive(self, pid):
        return self.status(pid)[0] in ALIVE_LIKE

    def has_heir(self, pid):
        """Vrai si la personne, ou par représentation un de ses descendants, peut hériter."""
        return self.is_alive(pid) or any(self.has_heir(c) for c in self.t.children[pid])

    def allocate(self, pid, share, via):
        """Répartit `share` entre les héritiers qui prennent la place de `pid` (représentation par souches)."""
        if self.is_alive(pid):
            return [(pid, share, via)]
        kids = [c for c in sorted(self.t.children[pid]) if self.has_heir(c)]
        out = []
        for c in kids:
            out += self.allocate(c, share / len(kids), via + [pid])
        return out

    def order1(self):
        top = [c for c in sorted(self.t.children[self.d]) if self.has_heir(c)]
        out = []
        for c in top:
            out += [(h, sh, v if v else ["enfant"]) for h, sh, v in self.allocate(c, Fraction(1, len(top)), [])]
        return out

    def parents(self):
        return sorted(self.t.parents[self.d])

    def order2(self):
        parents = self.parents()
        out = []
        for p in parents:
            if self.is_alive(p):
                out.append((p, None, ["père" if self.t.people[p]["sex"] == "M" else "mère"]))
        sib = set()
        for p in parents:
            sib |= self.t.children[p]
        sib.discard(self.d)
        for s in sorted(sib):
            if self.has_heir(s):
                out += [(h, None, v if v else ["frère ou sœur"]) for h, _, v in self.allocate(s, Fraction(1), [])]
        return out

    def line_roots(self):
        """Les deux lignes : père et mère du défunt (sexe M puis F, sinon ordre de l'identifiant)."""
        ps = self.parents()
        ps.sort(key=lambda p: {"M": 0, "F": 1}.get(self.t.people[p]["sex"], 2))
        return ps

    def ancestors_levels(self, root):
        """Niveaux d'ascendants à partir de `root` (niveau 1 = root, 2 = ses parents, …)."""
        levels, cur = [], {root}
        while cur:
            levels.append(sorted(cur))
            cur = {q for p in cur for q in self.t.parents[p]}
        return levels

    def order3(self):
        lines = []
        for root in self.line_roots():
            for k, level in enumerate(self.ancestors_levels(root)[1:], start=2):  # grands-parents et au-delà
                alive = [p for p in level if self.is_alive(p)]
                if alive:
                    lines.append((root, k, alive))
                    break
        out = []
        for _, k, alive in lines:
            for p in alive:
                out.append((p, Fraction(1, len(lines) * len(alive)), [f"ascendant de degré {k + 1}"]))
        return out

    def descendants_depth(self, pid):
        out, frontier, h = {}, [pid], 0
        while frontier:
            h += 1
            frontier = [c for p in frontier for c in self.t.children[p]]
            for c in frontier:
                out.setdefault(c, h)
        return out

    def order4(self):
        own_ancestors = set(self.t.ancestors(self.d))
        privileged = set()
        for p in self.parents():
            privileged |= set(self.descendants_depth(p)) | {p}
        found = {}
        for root in self.line_roots():
            for g, level in enumerate(self.ancestors_levels(root), start=1):
                if g < 2:
                    continue
                for a in level:
                    for x, h in self.descendants_depth(a).items():
                        deg = g + h
                        if x in own_ancestors or x in privileged or x == self.d or deg > 6 or not self.is_alive(x):
                            continue
                        found.setdefault(root, []).append((deg, x, a))
        out = []
        for candidates in found.values():
            closest = min(deg for deg, _, _ in candidates)
            nearest = sorted({x for deg, x, _ in candidates if deg == closest})
            for x in nearest:
                out.append((x, Fraction(1, len(found) * len(nearest)), [f"collatéral au {closest}e degré"]))
        return out


def fmt(fr):
    return "à fixer avec un notaire" if fr is None else f"{fr.numerator}/{fr.denominator}"


def lien(d, via):
    if not via:
        return "en son nom propre"
    if isinstance(via[0], str):
        return via[0]
    return "par représentation de " + " puis ".join(d.t.name(v) for v in via)


def main():
    args = sys.argv[1:]
    if len(args) < 2 or args[0] in ("-h", "--help"):
        print(__doc__)
        return 0 if args else 2
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8")

    def opt(name, flag=False):
        if name in args:
            i = args.index(name)
            if flag:
                del args[i]
                return True
            v = args[i + 1]
            del args[i:i + 2]
            return v
        return None

    deces, tous, md = opt("--deces"), opt("--tous", True), opt("--md")
    t = Tree(args[0])
    defunt = t.one(args[1])
    year = int(deces) if deces else t.death_year(defunt)
    if not year:
        sys.exit("Année du décès inconnue : renseigne-la avec --deces ANNEE.")
    d = Devolution(t, defunt, year)

    out = [f"# Dévolution légale indicative : {t.label(defunt)}", "",
           f"Décès retenu : **{year}**. Hypothèses : droit français, aucun testament ni donation, aucune renonciation, "
           "aucune adoption ; droits du conjoint non calculés. À valider par un notaire.", ""]
    spouses = sorted(t.spouses[defunt])
    if spouses:
        out += ["**Conjoint(s) dans l'arbre** : " + ", ".join(t.label(s) for s in spouses) +
                ". Vérifier le mariage non dissous au décès ; ses droits dépendent des autres héritiers "
                "(art. 756 et suivants) et ne sont pas calculés ici.", ""]
    orders = [("1er ordre : descendants (art. 734, 735, 751)", d.order1),
              ("2e ordre : père, mère, frères et sœurs et leurs descendants (art. 734, 736, 738, 751)", d.order2),
              ("3e ordre : ascendants ordinaires, fente par moitié entre les deux lignes (art. 734, 746)", d.order3),
              ("4e ordre : collatéraux ordinaires jusqu'au 6e degré, le plus proche dans chaque ligne (art. 734, 753, 755)",
               d.order4)]
    applicable = None
    for title, fn in orders:
        heirs = fn()
        marker = ""
        if heirs and applicable is None:
            applicable, marker = title, " ← **ordre applicable** si les héritiers sont prouvés vivants"
        if applicable is not None and title != applicable and not tous:
            out.append("*(ordres suivants non examinés : `--tous` pour les afficher)*")
            break
        out += [f"## {title}{marker}", ""]
        if not heirs:
            out += ["Aucun héritier possible dans l'arbre.", ""]
            continue
        out += ["| Héritier | Lien | Statut à la date du décès | Part indicative | À prouver |", "|---|---|---|---|---|"]
        for pid, share, via in heirs:
            out.append(f"| {t.label(pid)} | {lien(d, via)} | {d.status(pid)[1]} | {fmt(share)} | "
                       "acte de naissance (filiation, mentions) de l'héritier et de chaque maillon jusqu'au défunt ; "
                       "actes de décès des prédécédés ; preuve qu'il est vivant |")
        out.append("")
    if applicable is None:
        out += ["**Aucun héritier trouvé jusqu'au 6e degré dans cet arbre.** Soit l'arbre est incomplet, soit la "
                "succession est en déshérence ; consulter un notaire (succession vacante, curateur).", ""]
    out += ["## Étapes suivantes", "",
            "1. Prouver chaque lien par un acte (niveau A) : voir `references/recherche-heritiers.md`.",
            "2. Prouver que chaque héritier est vivant ou décédé (mentions marginales, fichier des décès depuis 1970).",
            "3. Compléter l'arbre des branches manquantes (demi-frères et sœurs, enfants hors mariage, adoptions).",
            "4. Passer par le notaire chargé de la succession pour les contacts, la dévolution et l'acte de notoriété."]
    text = "\n".join(out)
    print(text)
    if md:
        Path(md).write_text(text + "\n", encoding="utf-8")
        print(f"\n(écrit dans {md} : document sensible, à garder en local)")
    return 0


if __name__ == "__main__":
    sys.exit(main())
