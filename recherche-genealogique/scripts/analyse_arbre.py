#!/usr/bin/env python3
"""Analyse d'un arbre généalogique stocké dans la base d'enquête (SQLite).

Usage : python analyse_arbre.py <base.db> <commande> [options]

Commandes
  stats                      couverture : dates, lieux, sources, niveau de certitude
  tache [--racine X] [--type T]  propose la tâche du jour (change chaque jour, évite ce qui est déjà dans research_log) ;
                             T = preuve | remonter | valider | manquant | correlation | parente
  frontiere [--racine X]     ancêtres sans parents connus, classés par facilité de recherche
  anomalies                  incohérences à valider (dates impossibles, âges aberrants)
  manquants [--racine X]     parent absent, écarts anormaux entre frères et sœurs, décès inconnus
  correlations               métiers et lieux : qui, où, quand
  parente A B                lien de parenté et proximité génétique estimée entre deux personnes
  trouver MOTIF              retrouve une personne par nom (renvoie l'identifiant)

X, A, B : identifiant numérique de la base ou morceau du nom (« Marie MARTIN »). Stdlib uniquement.
"""
import contextlib
import io
import re
import sqlite3
import sys
from collections import Counter, defaultdict, deque
from datetime import date

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
        b, d = self.birth_year(pid), self.death_year(pid)
        return f"{self.name(pid)} (n°{pid}, {b or '?'}–{d or '?'})"

    def find(self, motif):
        if str(motif).isdigit() and int(motif) in self.people:
            return [int(motif)]
        words = [w.lower() for w in str(motif).split()]
        return [pid for pid, p in self.people.items()
                if all(w in (p["full_name"] or "").lower() for w in words)]

    def one(self, motif):
        found = self.find(motif)
        if not found:
            sys.exit(f"Personne introuvable : {motif}")
        if len(found) > 1:
            print(f"Plusieurs personnes pour « {motif} » ; précise avec l'identifiant :", file=sys.stderr)
            for pid in found[:10]:
                print(f"  {self.label(pid)}", file=sys.stderr)
            sys.exit(1)
        return found[0]

    def ancestors(self, root):
        """{ancêtre: génération minimale} avec la racine à 0."""
        gen, queue = {root: 0}, deque([root])
        while queue:
            p = queue.popleft()
            for par in self.parents[p]:
                if par not in gen:
                    gen[par] = gen[p] + 1
                    queue.append(par)
        return gen

    def paths_up(self, start):
        """{ancêtre: {longueur: nombre de chemins}}."""
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
        print("La base est vide. Importe un arbre (`gedcom_import.py`) ou ajoute des personnes, puis relance.")
        return
    with_birth = sum(1 for p in t.people if t.birth_year(p))
    with_death = sum(1 for p in t.people if t.death_year(p))
    no_parents = sum(1 for p in t.people if not t.parents[p])
    certainty = Counter(r[0] for r in t.db.execute("SELECT certainty FROM evidence"))
    years = [t.birth_year(p) for p in t.people if t.birth_year(p)]
    print(f"Personnes : {n}")
    print(f"Avec année de naissance : {with_birth} ({100*with_birth//n} %) ; de décès : {with_death} ({100*with_death//n} %)")
    print(f"Sans parents connus : {no_parents} ({100*no_parents//n} %)")
    if years:
        print(f"Naissances de {min(years)} à {max(years)} ; médiane {sorted(years)[len(years)//2]}")
    print("Niveaux de certitude des preuves :", dict(certainty) or "aucune")
    print("→ Tant que tout est B, rien n'est prouvé par un acte : voir `tache`.")


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
    print(f"Ancêtres sans parents connus : {len(rows)} (les plus faciles à remonter d'abord)")
    for score, g, pid, by, bp in rows[:15]:
        print(f"  gén.{g:>2}  {t.label(pid)}  {commune(bp) or 'lieu inconnu'}")
    return rows


def cmd_anomalies(t):
    out = []
    for pid in t.people:
        b, d = t.birth_year(pid), t.death_year(pid)
        if b and d and d < b:
            out.append((3, pid, f"décès ({d}) avant la naissance ({b})"))
        if b and d and d - b > 105:
            out.append((2, pid, f"âge au décès {d-b} ans"))
        for m in t.ev(pid, "mariage"):
            my = year(m["date"])
            if b and my and my - b < 15:
                out.append((3, pid, f"marié à {my-b} ans ({my})"))
        for par in t.parents[pid]:
            pb, pd = t.birth_year(par), t.death_year(par)
            sex = t.people[par]["sex"]
            if b and pb:
                lo, hi = (15, 50) if sex == "F" else (15, 75)
                if not lo <= b - pb <= hi:
                    out.append((3 if b - pb < lo else 2, pid,
                                f"né {b-pb} ans après {'sa mère' if sex=='F' else 'son père'} {t.name(par)} (n°{par})"))
            if b and pd and ((sex == "F" and b > pd) or (sex != "F" and b > pd + 1)):
                out.append((3, pid, f"né en {b}, après le décès ({pd}) de {t.name(par)} (n°{par})"))
    out.sort(key=lambda x: -x[0])
    print(f"{len(out)} incohérences à valider (la source peut être fausse, ou la date mal lue)")
    for sev, pid, msg in out[:25]:
        print(f"  [{'!!' if sev==3 else '! '}] {t.label(pid)} : {msg}")
    return out


def cmd_manquants(t, racine):
    gens = t.root_set(racine)
    out = []
    for pid, g in gens.items():
        par = t.parents[pid]
        if len(par) == 1:
            known = next(iter(par))
            role = "mère" if t.people[known]["sex"] != "F" else "père"
            out.append((5 - 0.2 * g, f"{role} inconnu(e) de {t.label(pid)} (l'autre parent : {t.name(known)})"))
        d, b = t.death_year(pid), t.birth_year(pid)
        if b and not d and b < 1925 and g > 0:
            out.append((3 - 0.2 * g, f"décès inconnu de {t.label(pid)}"))
    # écarts entre enfants d'un même couple
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
                    out.append((2.5, f"écart de {y2-y1} ans entre {t.name(c1)} ({y1}) et {t.name(c2)} ({y2}) : enfant manquant ?"))
    out.sort(reverse=True)
    print(f"{len(out)} pistes de personnes ou d'informations manquantes")
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
    print("Départements de naissance :", ", ".join(f"{k} {v}" for k, v in by_place.most_common(8)))
    print("\nMétiers les plus fréquents, noms de famille et départements associés :")
    for trade, c in sorted(by_trade.items(), key=lambda x: -sum(x[1].values()))[:10]:
        top_names = ", ".join(f"{n} ({k})" for n, k in c.most_common(3))
        top_dep = ", ".join(f"{n} ({k})" for n, k in trade_place[trade].most_common(2))
        print(f"  {trade} : {sum(c.values())} personnes ; noms : {top_names} ; zones : {top_dep}")
    # transmission du métier père → enfant
    same = total = 0
    for pid in t.people:
        mine = {(e["details"] or "").lower() for e in t.ev(pid, "profession") if e["details"]}
        for par in t.parents[pid]:
            theirs = {(e["details"] or "").lower() for e in t.ev(par, "profession") if e["details"]}
            if mine and theirs:
                total += 1
                same += bool(mine & theirs)
    if total:
        print(f"\nMétier identique à celui d'un parent : {same} cas sur {total} ({100*same//total} %)")
    # mobilité naissance / décès
    moved = Counter()
    for pid in t.people:
        bp = departement(t.birth_place(pid))
        dp = next((departement(e["place"]) for e in t.ev(pid, "décès") if e["place"]), None)
        if bp and dp and bp != dp:
            moved[(bp, dp)] += 1
    if moved:
        print("\nMigrations (département de naissance → de décès) :",
              ", ".join(f"{a}→{b} ({n})" for (a, b), n in moved.most_common(6)))


def label_degree(n1, n2):
    if n1 == 0 or n2 == 0:
        k = max(n1, n2)
        return "même personne" if k == 0 else ("parent/enfant" if k == 1 else f"ancêtre direct à {k} générations")
    if n1 == n2 == 1:
        return "frère/sœur (ou demi-frère/sœur)"
    if min(n1, n2) == 1:
        m = max(n1, n2)
        if m == 2:
            return "oncle/tante – neveu/nièce"
        if m == 3:
            return "grand-oncle/tante – petit-neveu/nièce"
        return f"{m-2}e génération au-dessus de l'oncle/tante (ancêtre commun à {m} générations)"
    k = min(n1, n2)
    degree = "cousins germains" if k == 2 else f"cousins du {k-1}e degré"
    return degree + (f", décalés de {abs(n1-n2)} génération(s)" if n1 != n2 else "")


def cmd_parente(t, a, b):
    ia, ib = t.one(a), t.one(b)
    up_a, up_b = t.paths_up(ia), t.paths_up(ib)
    common = set(up_a) & set(up_b)
    if not common:
        print(f"Aucun ancêtre commun trouvé entre {t.label(ia)} et {t.label(ib)} dans cet arbre.")
        print("(Absence dans l'arbre n'est pas absence de lien : les branches s'arrêtent à la frontière connue.)")
        return
    # ancêtres communs « les plus récents » : on retire ceux qui sont ancêtres d'un autre ancêtre commun
    above = set()
    for x in common:
        above |= (set(t.ancestors(x)) - {x}) & common
    lca = sorted(common - above)
    r = 0.0
    print(f"{t.label(ia)}  ↔  {t.label(ib)}")
    for x in lca:
        for n1, c1 in up_a[x].items():
            for n2, c2 in up_b[x].items():
                r += c1 * c2 * 0.5 ** (n1 + n2)
                print(f"  ancêtre commun : {t.label(x)} — à {n1} gén. de A, {n2} gén. de B "
                      f"({c1*c2} chemin(s)) → {label_degree(n1, n2)}")
    print(f"Proximité génétique estimée (coefficient de parenté de Wright) : {r:.4f} ≈ {100*r:.2f} % d'ADN en commun en moyenne")
    print("Estimation sur l'arbre connu, sans consanguinité des ancêtres : valeur plancher.")


def cmd_tache(t, racine, forced=None):
    root = t.one(racine) if racine else None
    today = date.today()
    kinds = ["preuve", "remonter", "valider", "manquant", "correlation", "parente"]
    kind = forced if forced in kinds else kinds[today.toordinal() % len(kinds)]
    print(f"Tâche du jour — {today.isoformat()}\n")

    def fresh(pid):
        return t.name(pid).lower() not in t.logged

    chosen = None
    if kind == "preuve":
        gens = t.ancestors(root) if root else {p: 0 for p in t.people}
        cands = sorted(
            (g + (0 if t.birth_place(p) else 3), p) for p, g in gens.items()
            # les actes de naissance ne sont communicables qu'après 75 ans
            if g > 0 and t.birth_year(p) and fresh(p) and 1792 <= t.birth_year(p) <= today.year - 75)
        if cands:
            p = cands[0][1]
            chosen = ("Prouver une naissance",
                      f"{t.label(p)} : l'arbre donne la naissance en {t.birth_year(p)} "
                      f"({commune(t.birth_place(p)) or 'lieu inconnu'}), niveau B.",
                      "Archives départementales, état civil de la commune : lire l'acte, relever mentions marginales, "
                      "parents et témoins. Viser le niveau A.")
    elif kind == "remonter":
        rows = cmd_silent_frontier(t, root)
        rows = [r for r in rows if fresh(r[2])]
        if rows:
            p = rows[0][2]
            chosen = ("Remonter d'une génération",
                      f"{t.label(p)} n'a pas de parents connus (naissance {t.birth_year(p) or '?'}, "
                      f"{commune(t.birth_place(p)) or 'lieu inconnu'}).",
                      "Chercher son acte de naissance ou de baptême, puis l'acte de mariage de ses parents "
                      "(souvent dans la commune de l'épouse). Geneanet : index nominatif + registres.")
    elif kind == "valider":
        out = [o for o in quiet(cmd_anomalies, t) if fresh(o[1])]
        if out:
            _, p, msg = out[0]
            chosen = ("Valider une donnée suspecte", f"{t.label(p)} : {msg}.",
                      "Retrouver l'acte ou la source citée ; trancher entre erreur de saisie, homonyme et date mal lue.")
    elif kind == "manquant":
        out = quiet(cmd_manquants, t, root)
        if out:
            chosen = ("Retrouver une personne ou une information manquante", out[0][1],
                      "Actes de naissance des enfants du couple, recensements, tables décennales de décès.")
    elif kind == "correlation":
        chosen = ("Explorer une corrélation", "Lancer `correlations` : métiers, zones et migrations de la famille.",
                  "Choisir un métier ou une zone qui se répète, puis chercher les archives professionnelles ou locales.")
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
                chosen = ("Mesurer une parenté",
                          f"Deux porteurs du nom {sn} : {t.label(a)} et {t.label(b)}. Sont-ils parents ? "
                          f"`parente {a} {b}`.",
                          "Si aucun ancêtre commun n'apparaît, c'est une piste : chercher le lien dans les actes "
                          "(mariages, témoins) ou noter une possible homonymie.")
    if not chosen:
        print("Rien de neuf dans cette catégorie aujourd'hui ; essaie `frontiere`, `anomalies` ou `manquants`.")
        return
    titre, pourquoi, comment = chosen
    print(f"► {titre}\n  Pourquoi : {pourquoi}\n  Comment : {comment}")
    print("\nÀ la fin : consigner la recherche (y compris si elle ne donne rien) dans research_log, "
          "et les faits trouvés dans evidence avec leur niveau.")


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
    """Exécute une commande d'affichage sans rien imprimer et renvoie ses résultats."""
    with contextlib.redirect_stdout(io.StringIO()):
        return command(*args)


def main():
    argv = sys.argv[1:]
    if len(argv) < 2 or argv[0] in ("-h", "--help"):
        print(__doc__)
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
    t, cmd, args = Tree(argv[0]), argv[1], argv[2:]
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
        print(__doc__, file=sys.stderr)
        return 2
    return 0


if __name__ == "__main__":
    sys.exit(main())
