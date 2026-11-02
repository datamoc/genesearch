#!/usr/bin/env python3
"""Interface locale de validation des preuves (navigateur, sur ce poste uniquement).

Usage : python validation_ui.py <base.db> [--racine "Nom ou n°"] [--port 8765] [--lecteur "Prénom"]

Une fiche par personne : naissance, mariage, décès, avec le niveau de certitude actuel.
Pour chaque fait, un clic : A (acte lu), B (notice, pas d'acte), C (déduction), ? (douteux).
Champ « cote / où lu » facultatif. Les fiches se parcourent des ancêtres les plus proches de la racine
vers les plus lointains. Les résultats sont écrits dans la table `evidence` de la base.

Sécurité : le serveur écoute seulement 127.0.0.1 et exige un jeton aléatoire (affiché au lancement).
Les données ne quittent pas le poste. Stdlib uniquement.
"""
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
from analyse_arbre import Tree  # noqa: E402

KINDS = ("naissance", "baptême", "mariage", "décès", "inhumation")
PAGE = r"""<!doctype html><html lang="fr"><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<title>Validation des preuves</title>
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
<h1>Validation des preuves</h1>
<div style="display:flex;gap:8px;align-items:center;flex-wrap:wrap"><div class="mut" id="stat" style="flex:1">Chargement…</div><button id="stop" style="border-color:var(--d);color:var(--d)" title="Enregistre la fiche en cours et affiche le bilan">Arrêter</button></div>
<div id="zone"></div>
</main>
<script>
const T=new URLSearchParams(location.search).get("t");const R=new URLSearchParams(location.search).get("racine")||"";
let queue=[],i=0,st={reste:0,valides:0},reader=localStorage.getItem("lecteur")||__LECTEUR__;
function stat(){document.getElementById("stat").textContent=st.reste+" fiches à revoir · "+st.valides+" faits déjà revus · lecteur : "+(reader||"(à choisir : bouton en bas)")+" · toutes les données restent sur ce poste"}
const $=(t,a={},...k)=>{const e=document.createElement(t);for(const[x,y]of Object.entries(a))x==="class"?e.className=y:e[x]=y;e.append(...k);return e};
async function load(){const r=await fetch("/api/queue?t="+T+"&racine="+encodeURIComponent(R));const d=await r.json();queue=d.items;i=0;
 st={reste:d.reste,valides:d.valides};stat();render()}
function render(){const z=document.getElementById("zone");z.replaceChildren();
 if(i>=queue.length){const e=$("div",{class:"card"},"Plus de fiche à revoir dans ce lot. ");const b=$("button",{class:"go"},"Voir le bilan");b.onclick=bilan;e.append(b);z.append(e);return}
 const p=queue[i];const card=$("div",{class:"card"});
 card.append($("div",{class:"mut"},"Génération "+p.gen+" · fiche "+(i+1)+"/"+queue.length),$("h1",{},p.label),$("div",{class:"mut"},p.contexte));
 const tb=$("table");p.faits.forEach(f=>{f.choix=null;const tr=$("tr");
  tr.append($("td",{class:"k"},f.kind),$("td",{class:"v"},[f.date||"date ?",f.place||"lieu ?"].join(" · "),$("br"),$("span",{class:"badge"},"actuel : "+f.certainty)));
  const td=$("td");["A","B","C","D"].forEach(l=>{const b=$("button",{class:l,title:{A:"acte lu",B:"notice / arbre, pas d'acte",C:"déduction",D:"douteux"}[l]},l==="D"?"?":l);
   b.onclick=()=>{f.choix=l;td.querySelectorAll("button").forEach(x=>x.classList.remove("on"));b.classList.add("on")};td.append(b)});
  f.cote=$("input",{class:"cote",placeholder:"cote / lien / où lu (facultatif)"});td.append($("br"),f.cote);tr.append(td);tb.append(tr)});
 card.append(tb);const row=$("div",{class:"row"});
 const all=$("button",{},"Tout en A (actes lus)");all.onclick=()=>{card.querySelectorAll("td button.A").forEach(b=>b.click())};
 const save=$("button",{class:"go"},"Enregistrer et suivant");save.onclick=async()=>{if(await saveCard()){i++;render()}};
 const skip=$("button",{},"Passer");skip.onclick=()=>{i++;render()};
 const who=$("button",{},"Changer de lecteur");who.onclick=()=>{const n=prompt("Qui valide ?",reader);if(n){reader=n;localStorage.setItem("lecteur",n);stat()}};
 row.append(all,save,skip,who);card.append(row);z.append(card)}
async function saveCard(){const p=queue[i];if(!p)return true;
 const faits=p.faits.filter(f=>f.choix).map(f=>({event_id:f.event_id,evidence_id:f.evidence_id,claim:f.claim,certainty:f.choix,cote:f.cote.value}));
 if(!faits.length)return true;
 const r=await fetch("/api/save?t="+T,{method:"POST",body:JSON.stringify({reader,faits})});if(!r.ok){alert("Erreur d'enregistrement");return false}
 st.valides+=faits.length;if(faits.length===p.faits.length)st.reste--;stat();return true}
async function bilan(){const r=await fetch("/api/bilan?t="+T+"&racine="+encodeURIComponent(R));const d=await r.json();const z=document.getElementById("zone");z.replaceChildren();
 const c=$("div",{class:"card"});c.append($("h1",{},"Séance arrêtée"),$("p",{},"Tout ce qui a été enregistré est dans la base : rien n'est perdu si vous fermez cet onglet."));
 const t=$("table");[["Faits revus (tous niveaux)",d.revus],["dont A (acte lu)",d.A],["dont B (notice seulement)",d.B],["dont C (déduction)",d.C],["dont marqués douteux",d.douteux],["Fiches encore à revoir",d.reste]].forEach(([k,v])=>t.append($("tr",{},$("td",{},k),$("td",{},String(v)))));
 c.append(t);const row=$("div",{class:"row"});
 const back=$("button",{class:"go"},"Reprendre");back.onclick=()=>load();
 const quit=$("button",{},"Quitter le serveur");quit.onclick=async()=>{await fetch("/api/stop?t="+T,{method:"POST"});z.replaceChildren($("div",{class:"card"},"Serveur arrêté. Vous pouvez fermer cet onglet. Pour reprendre : relancer validation_ui.py."));document.getElementById("stop").remove()};
 row.append(back,quit);c.append(row);z.append(c)}
document.getElementById("stop").onclick=async()=>{if(await saveCard())await bilan()};
load();
</script></html>"""


def make_handler(db_path, token, default_root, default_reader):
    tree = Tree(db_path)  # structure de l'arbre : chargée une fois
    static_page = PAGE.replace("__LECTEUR__", json.dumps(default_reader))

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
                                  "date": e["date"], "place": (e["place"] or "").replace("_", " "),
                                  "certainty": e["certainty"] or "B",
                                  "claim": f"{tree.name(pid)} : {e['kind']} {e['date'] or ''} {e['place'] or ''}".strip()})
            if todo:
                reste += 1
                par = [tree.name(x) for x in sorted(tree.parents[pid])]
                sp = [tree.name(x) for x in sorted(tree.spouses[pid])]
                ctx = " · ".join(filter(None, [("fils/fille de " + " et ".join(par)) if par else "",
                                               ("conjoint(e) : " + ", ".join(sp)) if sp else ""]))
                items.append({"label": tree.label(pid), "gen": g, "contexte": ctx or "aucun lien connu", "faits": faits})
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
                return self._send(403, '{"erreur":"jeton invalide"}')
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
                return self._send(403, '{"erreur":"refusé"}')
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
    args = sys.argv[1:]
    if not args or args[0] in ("-h", "--help"):
        print(__doc__)
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
    print(f"Interface de validation : {url}\n(Ctrl+C pour arrêter ; les données restent sur ce poste.)", flush=True)
    if "--no-browser" not in args:
        threading.Timer(0.5, lambda: webbrowser.open(url)).start()
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        pass
    return 0


if __name__ == "__main__":
    sys.exit(main())
