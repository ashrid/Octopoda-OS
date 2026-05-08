"""
Octopoda Local Dashboard — 1:1 replica of cloud dashboard design.
Run:  python app.py   →   http://localhost:7844
"""

import sqlite3, os, json, subprocess
from datetime import datetime, timezone
from pathlib import Path
from flask import Flask, jsonify, request, render_template

app = Flask(__name__)
DB_PATH = os.path.expanduser("~/.synrix/data/synrix.db")

def get_db():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn

def fmt_size(b):
    for u in ["B","KB","MB","GB"]:
        if b < 1024: return f"{b:.1f} {u}"
        b /= 1024
    return f"{b:.1f} TB"

# ── API ─────────────────────────────────────────────────────────────

@app.route("/")
def index():
    return render_template("index.html")

@app.route("/api/overview")
def overview():
    conn = get_db(); cur = conn.cursor()
    cur.execute("SELECT COUNT(*) FROM nodes"); nodes = cur.fetchone()[0]
    cur.execute("SELECT COUNT(*) FROM collections"); cols = cur.fetchone()[0]
    cur.execute("SELECT COUNT(*) FROM entities"); ents = cur.fetchone()[0]
    cur.execute("SELECT COUNT(*) FROM relationships"); rels = cur.fetchone()[0]
    cur.execute("SELECT COUNT(DISTINCT name) FROM nodes WHERE name LIKE 'agents:%'"); agents = max(cur.fetchone()[0], 1)
    conn.close()
    db_size = os.path.getsize(DB_PATH) if os.path.exists(DB_PATH) else 0
    mcp = bool(subprocess.run(["pgrep","-f","mcp_server"], capture_output=True, text=True, timeout=2).stdout.strip())
    try:
        from synrix.licensing import TIER_LIMITS
        tiers = {k: {"agents": v["max_agents"], "memories": v["max_memories_per_agent"]} for k,v in TIER_LIMITS.items()}
    except:
        tiers = {}
    return jsonify({"nodes": nodes, "agents": agents, "collections": cols, "entities": ents, "relationships": rels,
                    "db_size": fmt_size(db_size), "db_bytes": db_size, "mcp_alive": mcp, "tiers": tiers})

@app.route("/api/memories")
def memories():
    conn = get_db(); cur = conn.cursor()
    q = request.args.get("q","").strip()
    prefix = request.args.get("prefix","").strip()
    limit = min(int(request.args.get("limit",100)), 500)
    offset = int(request.args.get("offset",0))
    where = "WHERE 1=1"; params = []
    if q:
        where += " AND (name LIKE ? OR data LIKE ?)"
        params.extend([f"%{q}%", f"%{q}%"])
    cur.execute(f"SELECT COUNT(*) FROM nodes {where}", params); total = cur.fetchone()[0]
    cur.execute(f"SELECT name, data, created_at FROM nodes {where} ORDER BY created_at DESC LIMIT ? OFFSET ?", params + [limit, offset])
    rows = cur.fetchall(); conn.close()
    mems = []
    for r in rows:
        val = ""
        try:
            p = json.loads(r["data"])
            v = p.get("value", p)
            if isinstance(v, dict): v = v.get("value", str(v))
            val = str(v)[:200]
        except: val = str(r["data"])[:200]
        mems.append({"name": r["name"], "value": val, "created": r["created_at"]})
    return jsonify({"memories": mems, "total": total})

@app.route("/api/agents")
def agents():
    conn = get_db(); cur = conn.cursor()
    cur.execute("""SELECT DISTINCT substr(name,1,instr(name||'/','/')-1) as aid, COUNT(*) as cnt, MAX(created_at) as last
                   FROM nodes WHERE name LIKE 'agents:%' GROUP BY aid ORDER BY cnt DESC LIMIT 50""")
    rows = cur.fetchall(); conn.close()
    return jsonify({"agents": [{"id": r["aid"].replace("agents:",""), "memories": r["cnt"], "last": r["last"]} for r in rows]})

@app.route("/api/search")
def search():
    query = request.args.get("q","").strip()
    if not query: return jsonify({"results":[]})
    try:
        from synrix import Memory
        r = Memory().search(query)
        results = [str(x)[:200] for x in (r if isinstance(r,list) else [r])] if r else []
        return jsonify({"results": results})
    except Exception as e:
        return jsonify({"error": str(e), "results": []})

@app.route("/api/live")
def live():
    conn = get_db(); cur = conn.cursor()
    cur.execute("SELECT name, created_at FROM nodes ORDER BY created_at DESC LIMIT 20")
    recent = cur.fetchall(); conn.close()
    cycles = []
    try:
        cp = os.path.expanduser("~/.projects/Vibe-trader/data/cycles.jsonl")
        if os.path.exists(cp):
            with open(cp) as f:
                for line in f.readlines()[-10:]:
                    line = line.strip()
                    if line: cycles.append(json.loads(line))
    except: pass
    return jsonify({"writes": [{"name": r["name"], "time": r["created_at"]} for r in recent], "cycles": cycles})

@app.route("/api/loop")
def loop():
    try:
        from synrix_runtime.api.runtime import AgentRuntime
        rt = AgentRuntime("dashboard")
        return jsonify({"status": rt.get_loop_status(), "history": rt.get_loop_history(24)})
    except Exception as e:
        import traceback; traceback.print_exc()
        return jsonify({"error": str(e), "status": {"severity": "unknown", "score": 0}})

@app.route("/api/system")
def system():
    mcp_count = 0
    try:
        r = subprocess.run(["ps","aux"], capture_output=True, text=True, timeout=2)
        mcp_count = r.stdout.count("mcp_server")
    except: pass
    return jsonify({
        "db_path": DB_PATH, "db_exists": os.path.exists(DB_PATH),
        "version": "3.1.7 (local, unlimited)", "mcp_processes": mcp_count,
        "vibe_trader": os.path.exists(os.path.expanduser("~/.projects/Vibe-trader")),
    })

@app.route("/api/delete", methods=["POST"])
def delete():
    key = request.json.get("key","").strip()
    if not key: return jsonify({"error":"no key"}), 400
    conn = get_db(); cur = conn.cursor()
    cur.execute("DELETE FROM nodes WHERE name = ?", (key,))
    deleted = cur.rowcount; conn.commit(); conn.close()
    return jsonify({"deleted": deleted})

if __name__ == "__main__":
    print("  Octopoda Local Dashboard")
    print("  http://localhost:7844\n")
    app.run(host="0.0.0.0", port=7844, debug=True)
