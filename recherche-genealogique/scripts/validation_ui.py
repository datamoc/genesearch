#!/usr/bin/env python3
"""Local interface to validate proofs (in the browser, on this machine only).

Usage: python validation_ui.py <db> [--racine "Name or no."] [--port 8765] [--lecteur "First name"].
Run with --help for the full text in the chosen language. The server listens on 127.0.0.1 only and
requires a random token (shown at launch); data never leaves the machine. Standard library only.
"""
import html
import json
import secrets
import sqlite3
import sys
import threading
import webbrowser
from datetime import date
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from urllib.parse import parse_qs, urlparse

sys.path.insert(0, str(Path(__file__).parent))
import i18n  # noqa: E402
from analyse_arbre import Tree  # noqa: E402
from i18n import tr  # noqa: E402

KINDS = ("naissance", "baptême", "mariage", "décès", "inhumation")
UI_KEYS = ("title", "loading", "stop", "stop_tip", "stat", "reader_none", "end_of_batch", "see_summary", "card_meta",
           "date_unknown", "place_unknown", "current", "title_A", "title_B", "title_C", "title_D", "cote_placeholder",
           "all_A", "save_next", "skip", "change_reader", "who_prompt", "save_error", "stopped_title", "stopped_text",
           "row_reviewed", "row_A", "row_B", "row_C", "row_doubt", "row_left", "resume", "quit_server", "server_stopped")


def kind_label(kind):
    label = tr(f"kind.{kind}")
    return kind if label == f"kind.{kind}" else label


def render_page(reader):
    """The page in the current language: the texts of the browser interface are sent as a JSON object."""
    texts = {key: tr(f"ui.js.{key}") for key in UI_KEYS}
    texts_json = json.dumps(texts, ensure_ascii=False).replace("</", "<\\/")
    return (PAGE.replace("__LANG__", i18n.current()).replace("__TITLE__", html.escape(texts["title"]))
            .replace("__I18N__", texts_json).replace("__LECTEUR__", json.dumps(reader)))
PAGE = r"""<!doctype html><html lang="__LANG__"><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<title>__TITLE__</title>
<style>
:root{--bg:#f6f4ef;--fg:#222;--card:#fff;--mut:#6b6b6b;--ln:#ddd;--a:#1e7d3a;--b:#8a6d00;--c:#1f5fa8;--d:#b3261e}
@media (prefers-color-scheme:dark){:root{--bg:#1a1a1a;--fg:#eee;--card:#262626;--mut:#a0a0a0;--ln:#444;--a:#5bd17f;--b:#e3c04d;--c:#7db3f0;--d:#ff8a80}}
body{font:16px/1.4 system-ui,sans-serif;background:var(--bg);color:var(--fg);margin:0;padding:16px}
main{max-width:760px;margin:0 auto}h1{font-size:1.2rem;margin:0 0 4px}.mut{color:var(--mut);font-size:.9rem}
.card{background:var(--card);border:1px solid var(--ln);border-radius:10px;padding:16px;margin:12px 0}
table{width:100%;border-collapse:collapse}td{padding:8px 4px;border-top:1px solid var(--ln);vertical-align:middle}
td.k{font-weight:600;width:90px}td.v{width:52%}
button{font:inherit;border:1px solid var(--ln);background:var(--card);color:var(--fg);border-radius:8px;padding:6px 10px;cursor:pointer;margin:2px}
button.on{outline:2px solid currentColor;font-weight:700}.A.on{color:var(--a)}.B.on{color:var(--b)}.C.on{color:var(--c)}.D.on{color:var(--d)}
input.cote{width:100%;box-sizing:border-box;font:inherit;padding:6px;border:1px solid var(--ln);border-radius:6px;background:var(--bg);color:var(--fg)}
.row{display:flex;gap:8px;flex-wrap:wrap;margin-top:12px}.go{background:var(--a);color:#fff;border-color:var(--a)}
.badge{font-size:.8rem;border:1px solid var(--ln);border-radius:20px;padding:1px 8px;color:var(--mut)}
</style>
<main>
<h1 id="title"></h1>
<div style="display:flex;gap:8px;align-items:center;flex-wrap:wrap"><div class="mut" id="stat" style="flex:1"></div><button id="stop" style="border-color:var(--d);color:var(--d)"></button></div>
<div id="zone"></div>
</main>
<script>
const L=__I18N__;
const fmt=(s,v)=>s.replace(/\{(\w+)\}/g,(m,k)=>v[k]);
document.getElementById("title").textContent=L.title;document.getElementById("stat").textContent=L.loading;
const stopButton=document.getElementById("stop");stopButton.textContent=L.stop;stopButton.title=L.stop_tip;
const T=new URLSearchParams(location.search).get("t");const R=new URLSearchParams(location.search).get("racine")||"";
let queue=[],i=0,st={reste:0,valides:0},reader=localStorage.getItem("lecteur")||__LECTEUR__;
function stat(){document.getElementById("stat").textContent=fmt(L.stat,{left:st.reste,done:st.valides,reader:reader||L.reader_none})}
const $=(t,a={},...k)=>{const e=document.createElement(t);for(const[x,y]of Object.entries(a))x==="class"?e.className=y:e[x]=y;e.append(...k);return e};
async function load(){const r=await fetch("/api/queue?t="+T+"&racine="+encodeURIComponent(R));const d=await r.json();queue=d.items;i=0;
 st={reste:d.reste,valides:d.valides};stat();render()}
function render(){const z=document.getElementById("zone");z.replaceChildren();
 if(i>=queue.length){const e=$("div",{class:"card"},L.end_of_batch);const b=$("button",{class:"go"},L.see_summary);b.onclick=bilan;e.append(b);z.append(e);return}
 const p=queue[i];const card=$("div",{class:"card"});
 card.append($("div",{class:"mut"},fmt(L.card_meta,{gen:p.gen,n:i+1,total:queue.length})),$("h1",{},p.label),$("div",{class:"mut"},p.contexte));
 const tb=$("table");p.faits.forEach(f=>{f.choix=null;const tr=$("tr");
  tr.append($("td",{class:"k"},f.kind_label),$("td",{class:"v"},[f.date||L.date_unknown,f.place||L.place_unknown].join(" · "),$("br"),$("span",{class:"badge"},fmt(L.current,{level:f.certainty}))));
  const td=$("td");["A","B","C","D"].forEach(l=>{const b=$("button",{class:l,title:{A:L.title_A,B:L.title_B,C:L.title_C,D:L.title_D}[l]},l==="D"?"?":l);
   b.onclick=()=>{f.choix=l;td.querySelectorAll("button").forEach(x=>x.classList.remove("on"));b.classList.add("on")};td.append(b)});
  f.cote=$("input",{class:"cote",placeholder:L.cote_placeholder});td.append($("br"),f.cote);tr.append(td);tb.append(tr)});
 card.append(tb);const row=$("div",{class:"row"});
 const all=$("button",{},L.all_A);all.onclick=()=>{card.querySelectorAll("td button.A").forEach(b=>b.click())};
 const save=$("button",{class:"go"},L.save_next);save.onclick=async()=>{if(await saveCard()){i++;render()}};
 const skip=$("button",{},L.skip);skip.onclick=()=>{i++;render()};
 const who=$("button",{},L.change_reader);who.onclick=()=>{const n=prompt(L.who_prompt,reader);if(n){reader=n;localStorage.setItem("lecteur",n);stat()}};
 row.append(all,save,skip,who);card.append(row);z.append(card)}
async function saveCard(){const p=queue[i];if(!p)return true;
 const faits=p.faits.filter(f=>f.choix).map(f=>({event_id:f.event_id,evidence_id:f.evidence_id,claim:f.claim,certainty:f.choix,cote:f.cote.value}));
 if(!faits.length)return true;
 const r=await fetch("/api/save?t="+T,{method:"POST",body:JSON.stringify({reader,faits})});if(!r.ok){alert(L.save_error);return false}
 st.valides+=faits.length;if(faits.length===p.faits.length)st.reste--;stat();return true}
async function bilan(){const r=await fetch("/api/bilan?t="+T+"&racine="+encodeURIComponent(R));const d=await r.json();const z=document.getElementById("zone");z.replaceChildren();
 const c=$("div",{class:"card"});c.append($("h1",{},L.stopped_title),$("p",{},L.stopped_text));
 const t=$("table");[[L.row_reviewed,d.revus],[L.row_A,d.A],[L.row_B,d.B],[L.row_C,d.C],[L.row_doubt,d.douteux],[L.row_left,d.reste]].forEach(([k,v])=>t.append($("tr",{},$("td",{},k),$("td",{},String(v)))));
 c.append(t);const row=$("div",{class:"row"});
 const back=$("button",{class:"go"},L.resume);back.onclick=()=>load();
 const quit=$("button",{},L.quit_server);quit.onclick=async()=>{await fetch("/api/stop?t="+T,{method:"POST"});z.replaceChildren($("div",{class:"card"},L.server_stopped));document.getElementById("stop").remove()};
 row.append(back,quit);c.append(row);z.append(c)}
document.getElementById("stop").onclick=async()=>{if(await saveCard())await bilan()};
load();
</script></html>"""


def make_handler(db_path, token, default_root, default_reader):
    tree = Tree(db_path)  # structure de l'arbre : chargée une fois
    static_page = render_page(default_reader)

    def conn():
        c = sqlite3.connect(db_path)
        c.row_factory = sqlite3.Row
        return c

    def build_queue(racine):
        root = tree.one(racine) if racine else None
        gens = tree.ancestors(root) if root else {p: 0 for p in tree.people}
        db = conn()
        ev = {}
        for e in db.execute("SELECT e.id eid, e.person_id, e.kind, e.date, e.place, "
                            "v.id vid, v.certainty, v.notes FROM events e LEFT JOIN evidence v ON v.event_id=e.id "
                            f"WHERE e.kind IN ({','.join('?'*len(KINDS))})", KINDS):
            ev.setdefault(e["person_id"], []).append(e)
        items, reste, valides = [], 0, 0
        for pid, g in sorted(gens.items(), key=lambda x: x[1]):
            faits, todo = [], False
            for e in ev.get(pid, []):
                reviewed = "[revu" in (e["notes"] or "")
                valides += reviewed
                if not reviewed:
                    todo = True
                    faits.append({"event_id": e["eid"], "evidence_id": e["vid"], "kind": e["kind"],
                                  "kind_label": kind_label(e["kind"]), "date": e["date"],
                                  "place": (e["place"] or "").replace("_", " "),
                                  "certainty": e["certainty"] or "B",
                                  "claim": f"{tree.name(pid)} : {e['kind']} {e['date'] or ''} {e['place'] or ''}".strip()})
            if todo:
                reste += 1
                par = [tree.name(x) for x in sorted(tree.parents[pid])]
                sp = [tree.name(x) for x in sorted(tree.spouses[pid])]
                ctx = " · ".join(filter(None, [tr("ui.ctx.parents", names=tr("ui.and").join(par)) if par else "",
                                               tr("ui.ctx.spouses", names=", ".join(sp)) if sp else ""]))
                items.append({"label": tree.label(pid), "gen": g, "contexte": ctx or tr("ui.ctx.none"), "faits": faits})
        db.close()
        return {"items": items[:40], "reste": reste, "valides": valides}

    def bilan(racine):
        db = conn()
        rows = db.execute("SELECT certainty, notes FROM evidence WHERE notes LIKE '[revu%'").fetchall()
        db.close()
        doubt = sum("[DOUTEUX]" in r["notes"] for r in rows)
        return {"revus": len(rows), "douteux": doubt,
                "A": sum(r["certainty"] == "A" for r in rows), "B": sum(r["certainty"] == "B" for r in rows),
                "C": sum(r["certainty"] == "C" and "[DOUTEUX]" not in r["notes"] for r in rows),
                "reste": build_queue(racine)["reste"]}

    def save(payload):
        reader = (payload.get("reader") or "inconnu").strip()[:60]
        today = date.today().isoformat()
        db = conn()
        src = db.execute("SELECT id FROM sources WHERE label='Validation locale (interface)'").fetchone()
        src_id = src["id"] if src else db.execute(
            "INSERT INTO sources(label, consulted) VALUES ('Validation locale (interface)', ?)", (today,)).lastrowid
        for f in payload["faits"]:
            level = "C" if f["certainty"] == "D" else f["certainty"]
            flag = " [DOUTEUX]" if f["certainty"] == "D" else ""
            note = f"[revu {today} par {reader}]{flag}" + (f" cote : {f['cote'].strip()}" if f.get("cote", "").strip() else "")
            if f.get("evidence_id"):
                db.execute("UPDATE evidence SET certainty=?, reader=?, notes=? WHERE id=?",
                           (level, reader, note, f["evidence_id"]))
            else:
                db.execute("INSERT INTO evidence(claim, event_id, source_id, certainty, reader, notes) VALUES (?,?,?,?,?,?)",
                           (f["claim"], f["event_id"], src_id, level, reader, note))
        db.commit()
        db.close()

    class Handler(BaseHTTPRequestHandler):
        def log_message(self, *a):
            pass

        def _ok(self):
            q = parse_qs(urlparse(self.path).query)
            return secrets.compare_digest(q.get("t", [""])[0], token) and self.client_address[0] == "127.0.0.1"

        def _send(self, code, body, ctype="application/json; charset=utf-8"):
            data = body.encode("utf-8") if isinstance(body, str) else body
            self.send_response(code)
            self.send_header("Content-Type", ctype)
            self.send_header("Content-Length", str(len(data)))
            self.send_header("Cache-Control", "no-store")
            self.end_headers()
            self.wfile.write(data)

        def do_GET(self):
            if not self._ok():
                return self._send(403, json.dumps({"erreur": tr("ui.err.token")}, ensure_ascii=False))
            u = urlparse(self.path)
            if u.path == "/":
                return self._send(200, static_page, "text/html; charset=utf-8")
            if u.path == "/api/queue":
                racine = parse_qs(u.query).get("racine", [""])[0] or default_root
                try:
                    return self._send(200, json.dumps(build_queue(racine), ensure_ascii=False))
                except SystemExit as e:
                    return self._send(400, json.dumps({"erreur": str(e)}))
            if u.path == "/api/bilan":
                racine = parse_qs(u.query).get("racine", [""])[0] or default_root
                return self._send(200, json.dumps(bilan(racine), ensure_ascii=False))
            self._send(404, "{}")

        def do_POST(self):
            path = urlparse(self.path).path
            if not self._ok() or path not in ("/api/save", "/api/stop"):
                return self._send(403, json.dumps({"erreur": tr("ui.err.refused")}, ensure_ascii=False))
            if path == "/api/stop":
                self._send(200, '{"ok":true}')
                threading.Thread(target=self.server.shutdown, daemon=True).start()
                return
            n = int(self.headers.get("Content-Length", 0))
            try:
                save(json.loads(self.rfile.read(n)))
            except (ValueError, KeyError, sqlite3.Error) as e:
                return self._send(400, json.dumps({"erreur": str(e)}))
            self._send(200, '{"ok":true}')

    return Handler


def main():
    args = i18n.init(sys.argv[1:])
    if not args or args[0] in ("-h", "--help"):
        print(tr("ui.help"))
        return 0 if args else 2

    def opt(name, default=None):
        if name in args:
            i = args.index(name)
            v = args[i + 1]
            del args[i:i + 2]
            return v
        return default

    root, port, reader = opt("--racine"), int(opt("--port", "8765")), opt("--lecteur", "")
    db_path = args[0]
    token = secrets.token_urlsafe(16)
    server = ThreadingHTTPServer(("127.0.0.1", port), make_handler(db_path, token, root, reader))
    url = f"http://127.0.0.1:{port}/?t={token}" + (f"&racine={root}" if root else "")
    print(tr("ui.launch", url=url), flush=True)
    if "--no-browser" not in args:
        threading.Timer(0.5, lambda: webbrowser.open(url)).start()
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        pass
    return 0


if __name__ == "__main__":
    sys.exit(main())
