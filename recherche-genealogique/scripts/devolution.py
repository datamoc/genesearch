#!/usr/bin/env python3
"""Simplified legal devolution (French law, Civil Code art. 731 ff.) from the local tree.

Usage: python devolution.py <db> <deceased> [--deces YEAR] [--tous] [--md file.md]. Run with --help for the full
text in the chosen language. Indicative only: a notary validates any devolution.
"""
import sys
from fractions import Fraction
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))
import i18n  # noqa: E402
from analyse_arbre import Tree  # noqa: E402
from i18n import tr  # noqa: E402

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
                r = ("predecede", tr("dev.st.dead", dy=dy))
            elif dy == self.year:
                r = ("a_verifier", tr("dev.st.same_year", dy=dy))
            else:
                r = ("vivant", tr("dev.st.alive", dy=dy))
        elif by is None:
            r = ("inconnu", tr("dev.st.unknown"))
        elif self.year - by > 110:
            r = ("predecede", tr("dev.st.presumed_dead", by=by))
        else:
            r = ("presume_vivant", tr("dev.st.presumed_alive", by=by))
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
            out += [(h, sh, v if v else [tr("dev.rel.child")]) for h, sh, v in self.allocate(c, Fraction(1, len(top)), [])]
        return out

    def parents(self):
        return sorted(self.t.parents[self.d])

    def order2(self):
        parents = self.parents()
        out = []
        for p in parents:
            if self.is_alive(p):
                out.append((p, None, [tr("dev.rel.father") if self.t.people[p]["sex"] == "M" else tr("dev.rel.mother")]))
        sib = set()
        for p in parents:
            sib |= self.t.children[p]
        sib.discard(self.d)
        for s in sorted(sib):
            if self.has_heir(s):
                out += [(h, None, v if v else [tr("dev.rel.sibling")]) for h, _, v in self.allocate(s, Fraction(1), [])]
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
                out.append((p, Fraction(1, len(lines) * len(alive)), [tr("dev.rel.ascendant", degree=k + 1)]))
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
                out.append((x, Fraction(1, len(found) * len(nearest)), [tr("dev.rel.collateral", degree=closest)]))
        return out


def fmt(fr):
    return tr("dev.share.tbd") if fr is None else f"{fr.numerator}/{fr.denominator}"


def lien(d, via):
    if not via:
        return tr("dev.link.self")
    if isinstance(via[0], str):
        return via[0]
    return tr("dev.link.repr", names=tr("dev.then").join(d.t.name(v) for v in via))


def main():
    args = i18n.init(sys.argv[1:])
    if len(args) < 2 or args[0] in ("-h", "--help"):
        print(tr("dev.help"))
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
        sys.exit(tr("dev.noyear"))
    d = Devolution(t, defunt, year)

    out = [tr("dev.title", person=t.label(defunt)), "", tr("dev.assumptions", year=year), ""]
    spouses = sorted(t.spouses[defunt])
    if spouses:
        out += [tr("dev.spouses", names=", ".join(t.label(s) for s in spouses)), ""]
    orders = [(tr("dev.order1"), d.order1), (tr("dev.order2"), d.order2),
              (tr("dev.order3"), d.order3), (tr("dev.order4"), d.order4)]
    applicable = None
    for title, fn in orders:
        heirs = fn()
        marker = ""
        if heirs and applicable is None:
            applicable, marker = title, tr("dev.applicable")
        if applicable is not None and title != applicable and not tous:
            out.append(tr("dev.skipped"))
            break
        out += [f"## {title}{marker}", ""]
        if not heirs:
            out += [tr("dev.none_heirs"), ""]
            continue
        out += [tr("dev.table.head"), "|---|---|---|---|---|"]
        for pid, share, via in heirs:
            out.append(tr("dev.table.row", label=t.label(pid), link=lien(d, via), status=d.status(pid)[1],
                          share=fmt(share)))
        out.append("")
    if applicable is None:
        out += [tr("dev.noheir"), ""]
    out += [tr("dev.next.title"), "", tr("dev.next.1"), tr("dev.next.2"), tr("dev.next.3"), tr("dev.next.4")]
    text = "\n".join(out)
    print(text)
    if md:
        Path(md).write_text(text + "\n", encoding="utf-8")
        print(tr("dev.written", path=md))
    return 0


if __name__ == "__main__":
    sys.exit(main())
