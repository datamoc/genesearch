#!/usr/bin/env python3
"""Rapport de preuves et de questions ouvertes, en PDF (ou HTML sans dépendance).

Usage : python rapport_preuves.py <base.db> <sortie.pdf> [--titre "…"] [--tout] [--html]

Contenu : preuves (niveau A), faits incertains (C et douteux), pistes encore non prouvées (journal
de recherche), questions ouvertes (aides demandées, incohérences), légende des niveaux.

Vie privée : par défaut, les personnes probablement vivantes (née il y a moins de 100 ans, sans décès connu)
sont remplacées par « [personne vivante] » dans tout le document. `--tout` désactive ce masquage
(document à garder en local). PDF : bibliothèque `reportlab` (pip install reportlab) ; sans elle, ou avec
`--html`, le script écrit une page HTML imprimable en PDF depuis un navigateur.
"""
import html
import re
import sys
from datetime import date
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))
from analyse_arbre import Tree, cmd_anomalies, quiet  # noqa: E402

LEVELS = [("A", "acte lu (par la personne indiquée)"), ("B", "notice, arbre ou transcription : pas d'acte vu"),
          ("C", "déduction ou lecture incertaine"), ("B−", "extrait de moteur, page non lue")]


def collect(db_path, mask):
    tree = Tree(db_path)
    db = tree.db
    today = date.today().year
    living = set()
    if mask:
        for pid in tree.people:
            by = tree.birth_year(pid)
            if by and today - by < 100 and not tree.death_year(pid):
                living.add(pid)
    names = sorted({tree.name(p) for p in living if len(tree.name(p)) > 4}, key=len, reverse=True)
    pattern = re.compile("|".join(re.escape(n) for n in names)) if names else None

    def m(text):
        return pattern.sub("[personne vivante]", text) if (pattern and text) else (text or "")

    ev = db.execute("""SELECT v.certainty, v.claim, v.reader, v.notes, s.label sl, s.reference sr, s.url su
                       FROM evidence v LEFT JOIN sources s ON s.id=v.source_id
                       WHERE v.certainty IN ('A','C') OR v.notes LIKE '[revu%'
                       ORDER BY v.certainty, v.id""").fetchall()
    # Un fait qui nomme une personne vivante est retiré (date et lieu suffiraient à la reconnaître) et compté.
    hidden = [r for r in ev if pattern and (pattern.search(r["claim"] or "") or pattern.search(r["notes"] or ""))]
    ev = [r for r in ev if r not in hidden]
    log = db.execute("SELECT * FROM research_log ORDER BY id").fetchall()
    helps = db.execute("SELECT * FROM help_requests ORDER BY status DESC, id").fetchall()
    anomalies = quiet(cmd_anomalies, tree)
    anom = [f"{tree.label(pid)} : {msg}" for _, pid, msg in anomalies[:12]]
    return {
        "preuves": [dict(certainty=r["certainty"], claim=m(r["claim"]), reader=m(r["reader"] or ""),
                         notes=m(r["notes"] or ""), source=m(r["sl"] or ""), ref=r["sr"] or "", url=r["su"] or "")
                    for r in ev],
        "journal": [dict(base=r["base"], query=m(r["query"]), period=r["period"] or "", result=m(r["result"]),
                         next=m(r["next_step"] or ""), on=r["searched_on"] or "") for r in log],
        "aides": [dict(request=m(r["request"]), status=r["status"], answer=m(r["answer"] or "")) for r in helps],
        "anomalies": [m(a) for a in anom],
        "n_personnes": len(tree.people), "n_masquees": len(living), "n_faits_masques": len(hidden),
        "niveaux": dict(db.execute("SELECT certainty, COUNT(*) FROM evidence GROUP BY certainty").fetchall()),
    }


def sections(d):
    """Liste neutre (titre, [blocs]) partagée par le PDF et le HTML. Un bloc = ('p', texte) ou ('t', lignes)."""
    A = [p for p in d["preuves"] if p["certainty"] == "A"]
    C = [p for p in d["preuves"] if p["certainty"] == "C"]
    out = []
    out.append(("Légende des niveaux de certitude", [("t", [["Niveau", "Signification"]] + [[k, v] for k, v in LEVELS])]))
    hidden_note = ([("p", f"{d['n_faits_masques']} fait(s) concernant des personnes vivantes ne sont pas détaillés dans ce document.")]
                   if d["n_faits_masques"] else [])
    out.append(("Preuves : faits établis par un acte (niveau A)", ([(
        "t", [["Fait", "Source", "Lecteur et notes"]] +
        [[p["claim"], " ".join(x for x in (p["source"], p["ref"]) if x),
          " ".join(x for x in (p["reader"], p["notes"]) if x)] for p in A])] if A else [("p", "Aucune preuve de niveau A pour l'instant.")])
        + hidden_note))
    out.append(("Faits incertains (niveau C, lectures douteuses)", [(
        "t", [["Fait", "Source", "Pourquoi incertain"]] +
        [[p["claim"], p["source"], p["notes"]] for p in C])] if C else [("p", "Aucun.")]))
    out.append(("Pistes trouvées, non encore prouvées (journal de recherche)",
                [("t", [["Recherche", "Résultat", "Suite à donner"]] +
                  [[f"{j['on']} · {j['base']} · {j['query']}", j["result"], j["next"]] for j in d["journal"]])]
                if d["journal"] else [("p", "Journal vide.")]))
    open_help = [a for a in d["aides"] if a["status"] == "ouverte"]
    qs = [["Question ou demande d'aide", "Statut"]] + [[a["request"], a["status"]] for a in d["aides"]]
    blocks = [("t", qs)] if d["aides"] else [("p", "Aucune demande d'aide enregistrée.")]
    if d["anomalies"]:
        blocks += [("p", "Incohérences repérées dans l'arbre, à vérifier dans les actes :"),
                   ("t", [["Incohérence"]] + [[a] for a in d["anomalies"]])]
    out.append((f"Questions ouvertes ({len(open_help)} demande(s) d'aide en attente)", blocks))
    return out


def write_html(d, path, titre):
    esc = html.escape
    body = []
    for title, blocks in sections(d):
        body.append(f"<h2>{esc(title)}</h2>")
        for kind, val in blocks:
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
        f"<h1>{esc(titre)}</h1><p>{date.today().isoformat()} · {d['n_personnes']} personnes dans la base"
        f"{' · ' + str(d['n_masquees']) + ' personnes vivantes masquées' if d['n_masquees'] else ''}</p>" + "".join(body),
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
        canvas.drawString(18 * mm, 10 * mm, f"{titre} · généré le {date.today().isoformat()} · données personnelles, à garder en local")
        canvas.drawRightString(A4[0] - 18 * mm, 10 * mm, f"page {doc.page}")
        canvas.restoreState()

    doc = SimpleDocTemplate(str(path), pagesize=A4, leftMargin=18 * mm, rightMargin=18 * mm,
                            topMargin=16 * mm, bottomMargin=18 * mm, title=titre)
    flow = [Paragraph(esc(titre), ss["Title"]),
            Paragraph(f"{date.today().isoformat()} · {d['n_personnes']} personnes dans la base · preuves par niveau : "
                      f"{', '.join(f'{k} {v}' for k, v in sorted(d['niveaux'].items()))}"
                      + (f" · {d['n_masquees']} personnes vivantes masquées" if d["n_masquees"] else ""), ss["BodyText"]),
            Spacer(1, 6)]
    for title, blocks in sections(d):
        flow.append(Paragraph(esc(title), ss["Heading2"]))
        for kind, val in blocks:
            if kind == "p":
                flow.append(Paragraph(esc(val), ss["BodyText"]))
                continue
            header, *rows = val
            ncol = len(header)
            data = [[Paragraph(esc(h), head) for h in header]] + \
                   [[Paragraph(esc(c), cell) for c in r] for r in rows]
            width = A4[0] - 36 * mm
            widths = {1: [width], 2: [width * .22, width * .78], 3: [width * .38, width * .34, width * .28]}[ncol]
            if ncol == 3 and header[0].startswith("Recherche"):
                widths = [width * .28, width * .45, width * .27]
            if ncol == 2 and header[0].startswith("Question"):
                widths = [width * .84, width * .16]
            if ncol == 2 and header[0] == "Niveau":
                widths = [width * .12, width * .88]
            t = Table(data, colWidths=widths, repeatRows=1)
            t.setStyle(TableStyle([("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#2f5d50")),
                                   ("GRID", (0, 0), (-1, -1), 0.3, colors.HexColor("#bbbbbb")),
                                   ("VALIGN", (0, 0), (-1, -1), "TOP"),
                                   ("ROWBACKGROUNDS", (0, 1), (-1, -1), [colors.white, colors.HexColor("#f4f4f0")])]))
            flow += [t, Spacer(1, 6)]
    doc.build(flow, onFirstPage=footer, onLaterPages=footer)


def main():
    args = sys.argv[1:]
    if len(args) < 2 or args[0] in ("-h", "--help"):
        print(__doc__)
        return 0 if args else 2
    titre = "Rapport de preuves et de questions ouvertes"
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
            print(f"PDF écrit : {out} ({d['n_masquees']} personnes vivantes masquées)" if mask else f"PDF écrit : {out} (sans masquage)")
            return 0
        except ImportError:
            print("reportlab absent : `pip install reportlab`, ou relancer avec --html (page à imprimer en PDF).", file=sys.stderr)
            want_html = True
            out = out.with_suffix(".html")
    write_html(d, out, titre)
    print(f"HTML écrit : {out}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
