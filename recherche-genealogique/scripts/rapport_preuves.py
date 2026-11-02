#!/usr/bin/env python3
"""Report of proofs and open questions, as PDF (or dependency-free HTML).

Usage: python rapport_preuves.py <db> <output.pdf> [--titre "..."] [--tout] [--html]. Run with --help for the full
text in the chosen language. Living people are excluded by default; see the help text.
"""
import html
import re
import sys
import unicodedata
from datetime import date
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))
import i18n  # noqa: E402
from analyse_arbre import Tree, cmd_anomalies, quiet  # noqa: E402
from i18n import tr  # noqa: E402



def levels():
    return [("A", tr("rep.level.A")), ("B", tr("rep.level.B")), ("C", tr("rep.level.C")), ("B−", tr("rep.level.Bm"))]


def status_label(status):
    """Translate the stored status of a help request (stored in French: ouverte, faite)."""
    label = tr(f"rep.status.{status}")
    return status if label == f"rep.status.{status}" else label


def fold(text):
    """Minuscules sans accents, pour comparer des noms sans tenir compte de la casse ni des accents."""
    decomposed = unicodedata.normalize("NFD", text or "")
    return "".join(c for c in decomposed if unicodedata.category(c) != "Mn").lower()


def living_people(tree, current_year):
    """Personnes probablement vivantes : voir la docstring du module."""
    living = {pid for pid in tree.people
              if tree.birth_year(pid) and current_year - tree.birth_year(pid) < 100 and not tree.death_year(pid)}
    undated = {pid for pid in tree.people
               if not tree.birth_year(pid) and not tree.death_year(pid)
               and (tree.parents[pid] | tree.children[pid] | tree.spouses[pid]) & living}
    return living | undated


def name_pattern(tree, people):
    """Expression qui reconnaît les noms de `people` : « Prénom NOM » et « NOM Prénom », sans casse ni accents."""
    forms = set()
    for pid in people:
        person = tree.people[pid]
        given, surname = (person["given_names"] or "").strip(), (person["surname"] or "").strip()
        forms.add(person["full_name"])
        if given and surname:
            forms |= {f"{given} {surname}", f"{surname} {given}"}
    forms = sorted({fold(f) for f in forms if len(f) > 4}, key=len, reverse=True)
    return re.compile("|".join(re.escape(f) for f in forms)) if forms else None


def collect(db_path, mask):
    tree = Tree(db_path)
    db = tree.db
    living = living_people(tree, date.today().year) if mask else set()
    pattern = name_pattern(tree, living)

    def mentions_living(*texts):
        return bool(pattern) and any(pattern.search(fold(t)) for t in texts if t)

    def visible(rows, *fields):
        """Sépare les lignes qui nomment une personne vivante des autres."""
        shown = [r for r in rows if not mentions_living(*(r[f] for f in fields))]
        return shown, len(rows) - len(shown)

    evidence = db.execute("""SELECT v.certainty, v.claim, v.reader, v.notes, s.label sl, s.reference sr, s.url su
                             FROM evidence v LEFT JOIN sources s ON s.id=v.source_id
                             WHERE v.certainty IN ('A','C') OR v.notes LIKE '[revu%'
                             ORDER BY v.certainty, v.id""").fetchall()
    log = db.execute("SELECT * FROM research_log ORDER BY id").fetchall()
    helps = db.execute("SELECT * FROM help_requests ORDER BY status DESC, id").fetchall()
    evidence, hidden_evidence = visible(evidence, "claim", "notes", "reader", "sl", "sr", "su")
    log, hidden_log = visible(log, "base", "query", "period", "result", "next_step", "searched_on")
    helps, hidden_helps = visible(helps, "request", "answer", "status")
    anomalies = [f"{tree.label(pid)} : {msg}" for _, pid, msg in quiet(cmd_anomalies, tree)[:12]]
    shown_anomalies = [a for a in anomalies if not mentions_living(a)]
    return {
        "preuves": [dict(certainty=r["certainty"], claim=r["claim"], reader=r["reader"] or "",
                         notes=r["notes"] or "", source=r["sl"] or "", ref=r["sr"] or "", url=r["su"] or "")
                    for r in evidence],
        "journal": [dict(base=r["base"], query=r["query"], period=r["period"] or "", result=r["result"],
                         next=r["next_step"] or "", on=r["searched_on"] or "") for r in log],
        "aides": [dict(request=r["request"], status=r["status"], answer=r["answer"] or "") for r in helps],
        "anomalies": shown_anomalies,
        "masques": {"preuves": hidden_evidence, "journal": hidden_log, "aides": hidden_helps,
                    "anomalies": len(anomalies) - len(shown_anomalies)},
        "n_personnes": len(tree.people), "n_masquees": len(living),
        "niveaux": dict(db.execute("SELECT certainty, COUNT(*) FROM evidence GROUP BY certainty").fetchall()),
    }


def sections(d):
    """Neutral list (title, [blocks]) shared by the PDF and the HTML.
    A block is ('p', text) or ('t', rows, layout) where layout names the PDF column widths."""
    A = [p for p in d["preuves"] if p["certainty"] == "A"]
    C = [p for p in d["preuves"] if p["certainty"] == "C"]

    def hidden_note(kind, label):
        count = d["masques"][kind]
        return [("p", tr("rep.hidden", count=count, label=tr(label)))] if count else []

    out = [(tr("rep.sec.legend"),
            [("t", [[tr("rep.col.level"), tr("rep.col.meaning")]] + [[k, v] for k, v in levels()], "legend")])]
    if A:
        proofs = [("t", [[tr("rep.col.fact"), tr("rep.col.source"), tr("rep.col.reader_notes")]] +
                    [[p["claim"], " ".join(x for x in (p["source"], p["ref"]) if x),
                      " ".join(x for x in (p["reader"], p["notes"]) if x)] for p in A], None)]
    else:
        proofs = [("p", tr("rep.none.proofs"))]
    out.append((tr("rep.sec.proofs"), proofs + hidden_note("preuves", "rep.hidden.facts")))
    if C:
        uncertain = [("t", [[tr("rep.col.fact"), tr("rep.col.source"), tr("rep.col.why_uncertain")]] +
                      [[p["claim"], p["source"], p["notes"]] for p in C], None)]
    else:
        uncertain = [("p", tr("rep.none.generic"))]
    out.append((tr("rep.sec.uncertain"), uncertain))
    if d["journal"]:
        leads = [("t", [[tr("rep.col.search"), tr("rep.col.result"), tr("rep.col.next")]] +
                  [[f"{j['on']} · {j['base']} · {j['query']}", j["result"], j["next"]] for j in d["journal"]],
                  "journal")]
    else:
        leads = [("p", tr("rep.none.log"))]
    out.append((tr("rep.sec.leads"), leads + hidden_note("journal", "rep.hidden.log")))
    open_help = [a for a in d["aides"] if a["status"] == "ouverte"]
    if d["aides"]:
        blocks = [("t", [[tr("rep.col.question"), tr("rep.col.status")]] +
                    [[a["request"], status_label(a["status"])] for a in d["aides"]], "questions")]
    else:
        blocks = [("p", tr("rep.none.help"))]
    blocks += hidden_note("aides", "rep.hidden.questions")
    if d["anomalies"]:
        blocks += [("p", tr("rep.anom.intro")),
                   ("t", [[tr("rep.col.anomaly")]] + [[a] for a in d["anomalies"]], None)]
    blocks += hidden_note("anomalies", "rep.hidden.anomalies")
    out.append((tr("rep.sec.questions", n=len(open_help)), blocks))
    return out


def write_html(d, path, titre):
    esc = html.escape
    body = []
    for title, blocks in sections(d):
        body.append(f"<h2>{esc(title)}</h2>")
        for kind, val, *_layout in blocks:
            if kind == "p":
                body.append(f"<p>{esc(val)}</p>")
            else:
                head, *rows = val
                body.append("<table><tr>" + "".join(f"<th>{esc(h)}</th>" for h in head) + "</tr>" +
                            "".join("<tr>" + "".join(f"<td>{esc(c)}</td>" for c in r) + "</tr>" for r in rows) + "</table>")
    Path(path).write_text(
        f"<!doctype html><meta charset='utf-8'><title>{esc(titre)}</title>"
        "<style>body{font:14px/1.4 sans-serif;max-width:900px;margin:24px auto}table{border-collapse:collapse;width:100%}"
        "td,th{border:1px solid #ccc;padding:5px;vertical-align:top;text-align:left}th{background:#eee}</style>"
        f"<h1>{esc(titre)}</h1><p>{tr('rep.meta', date=date.today().isoformat(), n=d['n_personnes'])}"
        f"{tr('rep.meta.masked', n=d['n_masquees']) if d['n_masquees'] else ''}</p>" + "".join(body),
        encoding="utf-8")


def write_pdf(d, path, titre):
    from reportlab.lib import colors
    from reportlab.lib.pagesizes import A4
    from reportlab.lib.styles import ParagraphStyle, getSampleStyleSheet
    from reportlab.lib.units import mm
    from reportlab.platypus import Paragraph, SimpleDocTemplate, Spacer, Table, TableStyle

    ss = getSampleStyleSheet()
    cell = ParagraphStyle("c", parent=ss["BodyText"], fontSize=8.5, leading=10.5)
    head = ParagraphStyle("h", parent=cell, fontName="Helvetica-Bold", textColor=colors.white)
    esc = lambda s: html.escape(str(s))  # noqa: E731

    def footer(canvas, doc):
        canvas.saveState()
        canvas.setFont("Helvetica", 7.5)
        canvas.setFillGray(0.4)
        canvas.drawString(18 * mm, 10 * mm, tr("rep.footer", title=titre, date=date.today().isoformat()))
        canvas.drawRightString(A4[0] - 18 * mm, 10 * mm, tr("rep.page", n=doc.page))
        canvas.restoreState()

    doc = SimpleDocTemplate(str(path), pagesize=A4, leftMargin=18 * mm, rightMargin=18 * mm,
                            topMargin=16 * mm, bottomMargin=18 * mm, title=titre)
    flow = [Paragraph(esc(titre), ss["Title"]),
            Paragraph(tr("rep.pdf.intro", date=date.today().isoformat(), n=d["n_personnes"],
                         levels=", ".join(f"{k} {v}" for k, v in sorted(d["niveaux"].items())))
                      + (tr("rep.meta.masked", n=d["n_masquees"]) if d["n_masquees"] else ""), ss["BodyText"]),
            Spacer(1, 6)]
    for title, blocks in sections(d):
        flow.append(Paragraph(esc(title), ss["Heading2"]))
        for kind, val, *layout in blocks:
            if kind == "p":
                flow.append(Paragraph(esc(val), ss["BodyText"]))
                continue
            header, *rows = val
            ncol = len(header)
            data = [[Paragraph(esc(h), head) for h in header]] + \
                   [[Paragraph(esc(c), cell) for c in r] for r in rows]
            width = A4[0] - 36 * mm
            widths = {1: [width], 2: [width * .22, width * .78], 3: [width * .38, width * .34, width * .28]}[ncol]
            if layout and layout[0] == "journal":
                widths = [width * .28, width * .45, width * .27]
            elif layout and layout[0] == "questions":
                widths = [width * .84, width * .16]
            elif layout and layout[0] == "legend":
                widths = [width * .12, width * .88]
            t = Table(data, colWidths=widths, repeatRows=1)
            t.setStyle(TableStyle([("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#2f5d50")),
                                   ("GRID", (0, 0), (-1, -1), 0.3, colors.HexColor("#bbbbbb")),
                                   ("VALIGN", (0, 0), (-1, -1), "TOP"),
                                   ("ROWBACKGROUNDS", (0, 1), (-1, -1), [colors.white, colors.HexColor("#f4f4f0")])]))
            flow += [t, Spacer(1, 6)]
    doc.build(flow, onFirstPage=footer, onLaterPages=footer)


def main():
    args = i18n.init(sys.argv[1:])
    if len(args) < 2 or args[0] in ("-h", "--help"):
        print(tr("rep.help"))
        return 0 if args else 2
    titre = tr("rep.default_title")
    if "--titre" in args:
        i = args.index("--titre")
        titre = args[i + 1]
        del args[i:i + 2]
    mask = "--tout" not in args
    want_html = "--html" in args
    args = [a for a in args if not a.startswith("--")]
    d = collect(args[0], mask)
    out = Path(args[1])
    if not want_html:
        try:
            write_pdf(d, out, titre)
            print(tr("rep.pdf.written", out=out, n=d["n_masquees"]) if mask else tr("rep.pdf.written_nomask", out=out))
            return 0
        except ImportError:
            print(tr("rep.no_reportlab"), file=sys.stderr)
            want_html = True
            out = out.with_suffix(".html")
    write_html(d, out, titre)
    print(tr("rep.html.written", out=out))
    return 0


if __name__ == "__main__":
    sys.exit(main())
