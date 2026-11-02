#!/usr/bin/env python3
"""Analysis of a family tree stored in the investigation database (SQLite).

Usage: python analyse_arbre.py <db> <command> [options]. Run with --help for the commands, in the chosen
language (see i18n.py). Standard library only.
"""
import contextlib
import io
import re
import sqlite3
import sys
from collections import Counter, defaultdict, deque
from datetime import date

import i18n
from i18n import tr

YEAR = re.compile(r"\b(\d{4})\b")


def year(text):
    m = YEAR.search(text or "")
    return int(m.group(1)) if m else None


def commune(place):
    return (place or "").split(",")[0].strip().replace("_", " ") or None


def departement(place):
    parts = [p.strip() for p in (place or "").split(",")]
    return parts[1] if len(parts) > 1 else (parts[0] if parts and parts[0] else None)


class Tree:
    def __init__(self, path):
        self.db = sqlite3.connect(path)
        self.db.row_factory = sqlite3.Row
        self.people = {r["id"]: r for r in self.db.execute("SELECT * FROM persons")}
        self.events = defaultdict(list)
        for r in self.db.execute("SELECT * FROM events"):
            self.events[r["person_id"]].append(r)
        self.parents, self.children, self.spouses = defaultdict(set), defaultdict(set), defaultdict(set)
        for r in self.db.execute("SELECT person_a, person_b, kind FROM relations"):
            if r["kind"] == "parent":
                self.parents[r["person_b"]].add(r["person_a"])
                self.children[r["person_a"]].add(r["person_b"])
            elif r["kind"] == "époux":
                self.spouses[r["person_a"]].add(r["person_b"])
                self.spouses[r["person_b"]].add(r["person_a"])
        self.logged = " ".join(
            (r["query"] or "").lower() for r in self.db.execute("SELECT query FROM research_log"))

    def name(self, pid):
        return self.people[pid]["full_name"]

    def ev(self, pid, *kinds):
        return [e for e in self.events[pid] if e["kind"] in kinds]

    def birth_year(self, pid):
        ys = [year(e["date"]) for e in self.ev(pid, "naissance", "baptême") if year(e["date"])]
        return min(ys) if ys else None

    def death_year(self, pid):
        ys = [year(e["date"]) for e in self.ev(pid, "décès", "inhumation") if year(e["date"])]
        return min(ys) if ys else None

    def birth_place(self, pid):
        for e in self.ev(pid, "naissance", "baptême"):
            if e["place"]:
                return e["place"]
        return None

    def label(self, pid):
        return tr("tree.label", name=self.name(pid), pid=pid,
                  birth=self.birth_year(pid) or "?", death=self.death_year(pid) or "?")

    def find(self, motif):
        if str(motif).isdigit() and int(motif) in self.people:
            return [int(motif)]
        words = [w.lower() for w in str(motif).split()]
        return [pid for pid, p in self.people.items()
                if all(w in (p["full_name"] or "").lower() for w in words)]

    def one(self, motif):
        found = self.find(motif)
        if not found:
            sys.exit(tr("tree.not_found", motif=motif))
        if len(found) > 1:
            print(tr("tree.several", motif=motif), file=sys.stderr)
            for pid in found[:10]:
                print(f"  {self.label(pid)}", file=sys.stderr)
            sys.exit(1)
        return found[0]

    def ancestors(self, root):
        """{ancestor: minimal generation}, with the root at 0."""
        gen, queue = {root: 0}, deque([root])
        while queue:
            p = queue.popleft()
            for par in self.parents[p]:
                if par not in gen:
                    gen[par] = gen[p] + 1
                    queue.append(par)
        return gen

    def paths_up(self, start):
        """{ancestor: {length: number of paths}}."""
        result = defaultdict(lambda: defaultdict(int))
        level = {start: 1}
        n = 0
        while level:
            nxt = defaultdict(int)
            for p, count in level.items():
                result[p][n] += count
                for par in self.parents[p]:
                    nxt[par] += count
            level, n = nxt, n + 1
        return result

    def root_set(self, racine):
        if racine is None:
            return {pid: 0 for pid in self.people}
        return self.ancestors(self.one(racine))


def cmd_stats(t):
    n = len(t.people)
    if n == 0:
        print(tr("an.stats.empty"))
        return
    with_birth = sum(1 for p in t.people if t.birth_year(p))
    with_death = sum(1 for p in t.people if t.death_year(p))
    no_parents = sum(1 for p in t.people if not t.parents[p])
    certainty = Counter(r[0] for r in t.db.execute("SELECT certainty FROM evidence"))
    years = [t.birth_year(p) for p in t.people if t.birth_year(p)]
    print(tr("an.stats.people", n=n))
    print(tr("an.stats.dates", b=with_birth, bp=100 * with_birth // n, d=with_death, dp=100 * with_death // n))
    print(tr("an.stats.noparents", n=no_parents, p=100 * no_parents // n))
    if years:
        print(tr("an.stats.years", min=min(years), max=max(years), med=sorted(years)[len(years) // 2]))
    print(tr("an.stats.levels"), dict(certainty) or tr("an.none"))
    print(tr("an.stats.hint"))


def cmd_frontiere(t, racine):
    gens = t.root_set(racine)
    rows = []
    for pid, g in gens.items():
        if t.parents[pid]:
            continue
        by, bp = t.birth_year(pid), t.birth_place(pid)
        score = 0
        if by:
            score += 4 if 1792 <= by <= 1920 else (2 if 1600 <= by < 1792 else 1)
        if bp:
            score += 2
        if t.ev(pid, "mariage"):
            score += 1
        score -= 0.3 * g
        rows.append((score, g, pid, by, bp))
    rows.sort(reverse=True)
    print(tr("an.frontier.title", n=len(rows)))
    for score, g, pid, by, bp in rows[:15]:
        print(tr("an.frontier.row", g=g, label=t.label(pid), place=commune(bp) or tr("an.unknown_place")))
    return rows


def cmd_anomalies(t):
    out = []
    for pid in t.people:
        b, d = t.birth_year(pid), t.death_year(pid)
        if b and d and d < b:
            out.append((3, pid, tr("an.anom.death_before_birth", d=d, b=b)))
        if b and d and d - b > 105:
            out.append((2, pid, tr("an.anom.age", age=d - b)))
        for m in t.ev(pid, "mariage"):
            my = year(m["date"])
            if b and my and my - b < 15:
                out.append((3, pid, tr("an.anom.married_young", age=my - b, year=my)))
        for par in t.parents[pid]:
            pb, pd = t.birth_year(par), t.death_year(par)
            sex = t.people[par]["sex"]
            if b and pb:
                lo, hi = (15, 50) if sex == "F" else (15, 75)
                if not lo <= b - pb <= hi:
                    key = "an.anom.born_after_mother" if sex == "F" else "an.anom.born_after_father"
                    out.append((3 if b - pb < lo else 2, pid, tr(key, gap=b - pb, name=t.name(par), pid=par)))
            if b and pd and ((sex == "F" and b > pd) or (sex != "F" and b > pd + 1)):
                out.append((3, pid, tr("an.anom.born_after_death", b=b, pd=pd, name=t.name(par), pid=par)))
    out.sort(key=lambda x: -x[0])
    print(tr("an.anom.title", n=len(out)))
    for sev, pid, msg in out[:25]:
        print(tr("an.anom.row", sev="!!" if sev == 3 else "! ", label=t.label(pid), msg=msg))
    return out


def cmd_manquants(t, racine):
    gens = t.root_set(racine)
    out = []
    for pid, g in gens.items():
        par = t.parents[pid]
        if len(par) == 1:
            known = next(iter(par))
            role = tr("an.role.mother") if t.people[known]["sex"] != "F" else tr("an.role.father")
            out.append((5 - 0.2 * g, tr("an.miss.parent", role=role, person=t.label(pid), other=t.name(known))))
        d, b = t.death_year(pid), t.birth_year(pid)
        if b and not d and b < 1925 and g > 0:
            out.append((3 - 0.2 * g, tr("an.miss.death", person=t.label(pid))))
    # gaps between children of the same couple
    seen_couples = set()
    for pid in gens:
        for sp in t.spouses[pid]:
            couple = frozenset((pid, sp))
            if couple in seen_couples:
                continue
            seen_couples.add(couple)
            kids = sorted(((t.birth_year(c), c) for c in t.children[pid] & t.children[sp] if t.birth_year(c)))
            for (y1, c1), (y2, c2) in zip(kids, kids[1:]):
                if y2 - y1 >= 6:
                    out.append((2.5, tr("an.miss.gap", gap=y2 - y1, n1=t.name(c1), y1=y1, n2=t.name(c2), y2=y2)))
    out.sort(reverse=True)
    print(tr("an.miss.title", n=len(out)))
    for _, msg in out[:25]:
        print("  -", msg)
    return out


def cmd_correlations(t):
    by_trade, by_place, trade_place = defaultdict(Counter), Counter(), defaultdict(Counter)
    for pid in t.people:
        for e in t.ev(pid, "profession"):
            trade = (e["details"] or "").strip().lower()
            if trade:
                by_trade[trade][t.people[pid]["surname"]] += 1
                if t.birth_place(pid):
                    trade_place[trade][departement(t.birth_place(pid))] += 1
        if t.birth_place(pid):
            by_place[departement(t.birth_place(pid))] += 1
    print(tr("an.corr.places"), ", ".join(f"{k} {v}" for k, v in by_place.most_common(8)))
    print(tr("an.corr.trades"))
    for trade, c in sorted(by_trade.items(), key=lambda x: -sum(x[1].values()))[:10]:
        top_names = ", ".join(f"{n} ({k})" for n, k in c.most_common(3))
        top_dep = ", ".join(f"{n} ({k})" for n, k in trade_place[trade].most_common(2))
        print(tr("an.corr.trade_row", trade=trade, n=sum(c.values()), names=top_names, zones=top_dep))
    # does the occupation pass from parent to child?
    same = total = 0
    for pid in t.people:
        mine = {(e["details"] or "").lower() for e in t.ev(pid, "profession") if e["details"]}
        for par in t.parents[pid]:
            theirs = {(e["details"] or "").lower() for e in t.ev(par, "profession") if e["details"]}
            if mine and theirs:
                total += 1
                same += bool(mine & theirs)
    if total:
        print(tr("an.corr.inherit", same=same, total=total, pct=100 * same // total))
    # movement between birth and death
    moved = Counter()
    for pid in t.people:
        bp = departement(t.birth_place(pid))
        dp = next((departement(e["place"]) for e in t.ev(pid, "décès") if e["place"]), None)
        if bp and dp and bp != dp:
            moved[(bp, dp)] += 1
    if moved:
        print(tr("an.corr.moves"), ", ".join(f"{a}→{b} ({n})" for (a, b), n in moved.most_common(6)))


def label_degree(n1, n2):
    if n1 == 0 or n2 == 0:
        k = max(n1, n2)
        if k == 0:
            return tr("an.deg.same")
        return tr("an.deg.parent") if k == 1 else tr("an.deg.ancestor", k=k)
    if n1 == n2 == 1:
        return tr("an.deg.sibling")
    if min(n1, n2) == 1:
        m = max(n1, n2)
        if m == 2:
            return tr("an.deg.uncle")
        if m == 3:
            return tr("an.deg.granduncle")
        return tr("an.deg.uncle_n", up=m - 2, m=m)
    k = min(n1, n2)
    degree = tr("an.deg.cousins1") if k == 2 else tr("an.deg.cousins_n", degree=k - 1)
    return degree + (tr("an.deg.shift", d=abs(n1 - n2)) if n1 != n2 else "")


def cmd_parente(t, a, b):
    ia, ib = t.one(a), t.one(b)
    up_a, up_b = t.paths_up(ia), t.paths_up(ib)
    common = set(up_a) & set(up_b)
    if not common:
        print(tr("an.kin.nocommon", a=t.label(ia), b=t.label(ib)))
        print(tr("an.kin.nocommon2"))
        return
    # most recent common ancestors: drop those who are ancestors of another common ancestor
    above = set()
    for x in common:
        above |= (set(t.ancestors(x)) - {x}) & common
    lca = sorted(common - above)
    r = 0.0
    print(tr("an.kin.head", a=t.label(ia), b=t.label(ib)))
    for x in lca:
        for n1, c1 in up_a[x].items():
            for n2, c2 in up_b[x].items():
                r += c1 * c2 * 0.5 ** (n1 + n2)
                print(tr("an.kin.row", x=t.label(x), n1=n1, n2=n2, paths=c1 * c2, degree=label_degree(n1, n2)))
    print(tr("an.kin.result", r=r, pct=100 * r))
    print(tr("an.kin.floor"))


def cmd_tache(t, racine, forced=None):
    root = t.one(racine) if racine else None
    today = date.today()
    kinds = ["preuve", "remonter", "valider", "manquant", "correlation", "parente"]
    forced = i18n.task_type(forced) if forced else None
    kind = forced if forced in kinds else kinds[today.toordinal() % len(kinds)]
    print(tr("an.task.title", date=today.isoformat()))

    def fresh(pid):
        return t.name(pid).lower() not in t.logged

    chosen = None
    if kind == "preuve":
        gens = t.ancestors(root) if root else {p: 0 for p in t.people}
        cands = sorted(
            (g + (0 if t.birth_place(p) else 3), p) for p, g in gens.items()
            # birth records are only open to the public after 75 years
            if g > 0 and t.birth_year(p) and fresh(p) and 1792 <= t.birth_year(p) <= today.year - 75)
        if cands:
            p = cands[0][1]
            chosen = (tr("an.task.proof.title"),
                      tr("an.task.proof.why", person=t.label(p), year=t.birth_year(p),
                         place=commune(t.birth_place(p)) or tr("an.unknown_place")),
                      tr("an.task.proof.how"))
    elif kind == "remonter":
        rows = cmd_silent_frontier(t, root)
        rows = [r for r in rows if fresh(r[2])]
        if rows:
            p = rows[0][2]
            chosen = (tr("an.task.climb.title"),
                      tr("an.task.climb.why", person=t.label(p), year=t.birth_year(p) or "?",
                         place=commune(t.birth_place(p)) or tr("an.unknown_place")),
                      tr("an.task.climb.how"))
    elif kind == "valider":
        out = [o for o in quiet(cmd_anomalies, t) if fresh(o[1])]
        if out:
            _, p, msg = out[0]
            chosen = (tr("an.task.validate.title"), tr("an.task.validate.why", person=t.label(p), msg=msg),
                      tr("an.task.validate.how"))
    elif kind == "manquant":
        out = quiet(cmd_manquants, t, root)
        if out:
            chosen = (tr("an.task.missing.title"), out[0][1], tr("an.task.missing.how"))
    elif kind == "correlation":
        chosen = (tr("an.task.correlation.title"), tr("an.task.correlation.why"), tr("an.task.correlation.how"))
    else:
        by_name = defaultdict(list)
        for p in t.people:
            sn = (t.people[p]["surname"] or "").strip()
            if sn and sn != "?" and t.birth_year(p):
                by_name[sn].append(p)
        names = sorted(n for n, ps in by_name.items() if len(ps) >= 2)
        if names:
            sn = names[today.toordinal() % len(names)]
            ps = sorted(by_name[sn])
            a, b = ps[today.toordinal() % len(ps)], ps[(today.toordinal() + 1) % len(ps)]
            if a != b:
                chosen = (tr("an.task.kinship.title"),
                          tr("an.task.kinship.why", surname=sn, a=t.label(a), b=t.label(b), ia=a, ib=b),
                          tr("an.task.kinship.how"))
    if not chosen:
        print(tr("an.task.nothing"))
        return
    title, why, how = chosen
    print(tr("an.task.fmt", title=title, why=why, how=how))
    print(tr("an.task.end"))


def cmd_silent_frontier(t, racine):
    gens = t.root_set(racine)
    rows = []
    for pid, g in gens.items():
        if t.parents[pid]:
            continue
        by = t.birth_year(pid)
        score = (4 if by and 1792 <= by <= 1920 else 2 if by and by >= 1600 else 0) + (2 if t.birth_place(pid) else 0) - 0.3 * g
        rows.append((score, g, pid))
    return sorted(rows, reverse=True)


def quiet(command, *args):
    """Run a printing command without output and return its results."""
    with contextlib.redirect_stdout(io.StringIO()):
        return command(*args)


def main():
    argv = i18n.init(sys.argv[1:])
    if len(argv) < 2 or argv[0] in ("-h", "--help"):
        print(tr("an.help"))
        return 0 if argv and argv[0] in ("-h", "--help") else 2
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8")
    racine = forced = None
    if "--racine" in argv:
        i = argv.index("--racine")
        racine = argv[i + 1]
        del argv[i:i + 2]
    if "--type" in argv:
        i = argv.index("--type")
        forced = argv[i + 1]
        del argv[i:i + 2]
    t, cmd, args = Tree(argv[0]), i18n.command(argv[1]), argv[2:]
    if cmd == "stats":
        cmd_stats(t)
    elif cmd == "tache":
        cmd_tache(t, racine, forced)
    elif cmd == "frontiere":
        cmd_frontiere(t, racine)
    elif cmd == "anomalies":
        cmd_anomalies(t)
    elif cmd == "manquants":
        cmd_manquants(t, racine)
    elif cmd == "correlations":
        cmd_correlations(t)
    elif cmd == "parente" and len(args) == 2:
        cmd_parente(t, *args)
    elif cmd == "trouver" and args:
        for pid in t.find(" ".join(args))[:15]:
            print(t.label(pid))
    else:
        print(tr("an.help"), file=sys.stderr)
        return 2
    return 0


if __name__ == "__main__":
    sys.exit(main())
