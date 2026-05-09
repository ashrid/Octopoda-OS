"""
Octopoda Local Dashboard (legacy, deprecated).
Run:  python app.py   →   http://localhost:7844

Deprecated: use the runtime-backed dashboard on http://localhost:7842 instead.
"""

import sqlite3, os, json, subprocess, time
from datetime import datetime, timezone
from pathlib import Path
from flask import Flask, jsonify, request, render_template

app = Flask(__name__)
DB_PATH = os.path.expanduser("~/.synrix/data/synrix.db")
WEBHOOKS_PATH = os.path.expanduser("~/.octopoda/webhooks.json")

def get_db():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn

def fmt_size(b):
    for u in ["B","KB","MB","GB"]:
        if b < 1024: return f"{b:.1f} {u}"
        b /= 1024
    return f"{b:.1f} TB"

def load_webhooks():
    try:
        if os.path.exists(WEBHOOKS_PATH):
            with open(WEBHOOKS_PATH) as f: return json.load(f)
    except: pass
    return []

def save_webhooks(wh):
    os.makedirs(os.path.dirname(WEBHOOKS_PATH), exist_ok=True)
    with open(WEBHOOKS_PATH, 'w') as f: json.dump(wh, f, indent=2)

@app.route("/")
def index(): return render_template("index.html")

@app.route("/api/overview")
def overview():
    conn = get_db(); cur = conn.cursor()
    cur.execute("SELECT COUNT(*) FROM nodes"); nodes = cur.fetchone()[0]
    cur.execute("SELECT COUNT(*) FROM collections"); cols = cur.fetchone()[0]
    cur.execute("SELECT COUNT(*) FROM entities"); ents = cur.fetchone()[0]
    cur.execute("SELECT COUNT(*) FROM relationships"); rels = cur.fetchone()[0]
    cur.execute("SELECT COUNT(DISTINCT name) FROM nodes WHERE name LIKE 'agents:%'"); agents = max(cur.fetchone()[0], 1)
    # Memory growth (nodes per day for chart)
    cur.execute("SELECT DATE(created_at,'unixepoch') as day, COUNT(*) as cnt FROM nodes GROUP BY day ORDER BY day LIMIT 30")
    growth = [{"day": r["day"], "count": r["cnt"]} for r in cur.fetchall()]
    conn.close()
    db_size = os.path.getsize(DB_PATH) if os.path.exists(DB_PATH) else 0
    mcp = bool(subprocess.run(["pgrep","-f","mcp_server"], capture_output=True, text=True, timeout=2).stdout.strip())
    try:
        from synrix.licensing import TIER_LIMITS
        tiers = {k: {"agents": v["max_agents"], "memories": v["max_memories_per_agent"]} for k,v in TIER_LIMITS.items()}
    except: tiers = {}
    return jsonify({"nodes":nodes,"agents":agents,"collections":cols,"entities":ents,"relationships":rels,
                    "db_size":fmt_size(db_size),"db_bytes":db_size,"mcp_alive":mcp,"tiers":tiers,"growth":growth})

@app.route("/api/agent/<agent_id>")
def agent_detail(agent_id):
    conn = get_db(); cur = conn.cursor()
    # Get memory count
    cur.execute("SELECT COUNT(*) FROM nodes WHERE name LIKE ?", (f"agents:{agent_id}%",))
    mem_count = cur.fetchone()[0]
    # Timeline (last 50 writes)
    cur.execute("SELECT name, data, created_at FROM nodes WHERE name LIKE ? ORDER BY created_at DESC LIMIT 50",
                (f"agents:{agent_id}%",))
    timeline = []
    for r in cur.fetchall():
        val = ""
        try:
            p = json.loads(r["data"]); v = p.get("value", p)
            if isinstance(v, dict): v = v.get("value", str(v))
            val = str(v)[:120]
        except: val = str(r["data"])[:120]
        timeline.append({"key": r["name"], "value": val, "time": r["created_at"]})
    # Checkpoints (snapshots)
    cur.execute("SELECT name, created_at FROM nodes WHERE name LIKE ? AND name LIKE '%snapshot%' ORDER BY created_at DESC",
                (f"agents:{agent_id}%",))
    checkpoints = [{"name": r["name"], "time": r["created_at"]} for r in cur.fetchall()]
    conn.close()
    return jsonify({"agent_id": agent_id, "memories": mem_count, "timeline": timeline, "checkpoints": checkpoints})

@app.route("/api/memories")
def memories():
    conn = get_db(); cur = conn.cursor()
    q = request.args.get("q","").strip()
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
            p = json.loads(r["data"]); v = p.get("value", p)
            if isinstance(v, dict): v = v.get("value", str(v))
            val = str(v)[:200]
        except: val = str(r["data"])[:200]
        mems.append({"name": r["name"], "value": val, "created": r["created_at"]})
    return jsonify({"memories": mems, "total": total})

@app.route("/api/agents")
def agents():
    conn = get_db(); cur = conn.cursor()
    # Get all agents with stats
    cur.execute("""SELECT DISTINCT substr(name,1,instr(name||'/','/')-1) as aid FROM nodes WHERE name LIKE 'agents:%'""")
    agent_ids = set()
    for r in cur.fetchall():
        aid = r["aid"].replace("agents:","")
        if aid: agent_ids.add(aid)
    agents_list = []
    for aid in sorted(agent_ids):
        cur.execute("SELECT COUNT(*) FROM nodes WHERE name LIKE ?", (f"agents:{aid}%",))
        cnt = cur.fetchone()[0]
        cur.execute("SELECT MAX(created_at) FROM nodes WHERE name LIKE ?", (f"agents:{aid}%",))
        last = cur.fetchone()[0]
        agents_list.append({"id": aid, "memories": cnt, "last": last})
    agents_list.sort(key=lambda x: -x["memories"])
    conn.close()
    return jsonify({"agents": agents_list})

@app.route("/api/shared")
def shared_memory():
    conn = get_db(); cur = conn.cursor()
    # Get all shared: prefixed nodes and organize by space
    cur.execute("SELECT name, data, created_at FROM nodes WHERE name LIKE 'shared:%' ORDER BY created_at DESC LIMIT 200")
    rows = cur.fetchall()
    conn.close()
    
    from collections import defaultdict
    spaces = defaultdict(list)
    for r in rows:
        parts = r["name"].split(":", 3)
        if len(parts) >= 3:
            space = parts[1]
            key = parts[2] if len(parts) >= 3 else ""
            spaces[space].append({
                "key": key,
                "value": str(r["data"])[:200],
                "time": r["created_at"],
            })
    
    return jsonify({"spaces": dict(spaces)})

@app.route("/api/shared/write", methods=["POST"])
def shared_write():
    data = request.json
    space = data.get("space", "global")
    key = data.get("key", "")
    value = data.get("value", "")
    author = data.get("author", "dashboard")
    
    if not key or not value:
        return jsonify({"error": "key and value required"}), 400
    
    full_key = f"shared:{space}:{key}"
    conn = get_db(); cur = conn.cursor()
    import time
    now = time.time()
    cur.execute("INSERT INTO nodes (name, data, created_at, updated_at, collection, node_type) VALUES (?, ?, ?, ?, 'agent_memory', 'shared_memory')",
                (full_key, json.dumps({"value": value, "author": author, "space": space}), now, now))
    conn.commit(); conn.close()
    return jsonify({"success": True, "key": full_key})

@app.route("/api/entity-graph")
def entity_graph():
    conn = get_db(); cur = conn.cursor()
    # Try entities table first, fall back to fact_embeddings
    cur.execute("SELECT COUNT(*) FROM entities")
    has_entities = cur.fetchone()[0] > 0
    
    if has_entities:
        cur.execute("SELECT name, data FROM entities LIMIT 100")
        ents = [{"id": r["name"], "data": str(r["data"])[:100]} for r in cur.fetchall()]
        cur.execute("SELECT source, target, type FROM relationships LIMIT 200")
        rels = [{"source": r["source"], "target": r["target"], "type": r["type"]} for r in cur.fetchall()]
    else:
        # Use fact_embeddings as knowledge graph nodes
        cur.execute("SELECT fact_text, node_name FROM fact_embeddings LIMIT 200")
        rows = cur.fetchall()
        seen = set()
        ents = []
        for r in rows:
            if r[0] and r[0] not in seen:
                seen.add(r[0])
                ents.append({"id": r[0], "data": r[1]})
        # Build relationships: facts sharing the same node_name are connected
        from collections import defaultdict
        groups = defaultdict(list)
        for r in rows:
            if r[0]: groups[r[1]].append(r[0])
        rels = []
        for node_name, facts in groups.items():
            for i in range(len(facts)):
                for j in range(i+1, len(facts)):
                    rels.append({"source": facts[i], "target": facts[j], "type": "co_occurrence"})
        # Limit relationships
        rels = rels[:200]
        conn.close()
        return jsonify({"entities": ents, "relationships": rels})
    
    conn.close()
    return jsonify({"entities": ents, "relationships": rels})

@app.route("/api/search")
def search():
    q = request.args.get("q","").strip()
    if not q: return jsonify({"results":[]})
    try:
        from synrix import Memory
        r = Memory().search(q)
        results = [str(x)[:200] for x in (r if isinstance(r,list) else [r])] if r else []
        return jsonify({"results": results})
    except Exception as e:
        return jsonify({"error": str(e), "results": []})

@app.route("/api/live")
def live():
    conn = get_db(); cur = conn.cursor()
    cur.execute("SELECT name, created_at FROM nodes ORDER BY created_at DESC LIMIT 20")
    recent = [{"name": r["name"], "time": r["created_at"]} for r in cur.fetchall()]
    conn.close()
    return jsonify({"writes": recent, "cycles": []})

@app.route("/api/loop")
def loop():
    try:
        from synrix_runtime.api.runtime import AgentRuntime
        with AgentRuntime("dashboard") as rt:
            return jsonify({"status": rt.get_loop_status(), "history": rt.get_loop_history(24)})
    except Exception as e:
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
        "local_mode": True,
    })

@app.route("/api/webhooks", methods=["GET","POST","DELETE"])
def webhooks():
    if request.method == "GET":
        return jsonify({"webhooks": load_webhooks()})
    elif request.method == "POST":
        data = request.json
        wh = load_webhooks()
        wh.append({
            "id": str(int(time.time()*1000)),
            "url": data.get("url",""),
            "events": data.get("events",["memory.write"]),
            "description": data.get("description",""),
            "created": datetime.now(timezone.utc).isoformat(),
            "active": True
        })
        save_webhooks(wh)
        return jsonify({"success": True, "webhooks": wh})
    elif request.method == "DELETE":
        wid = request.json.get("id","")
        wh = [w for w in load_webhooks() if w.get("id") != wid]
        save_webhooks(wh)
        return jsonify({"success": True, "webhooks": wh})

@app.route("/api/settings/extraction", methods=["GET","POST"])
def extraction_settings():
    path = os.path.expanduser("~/.octopoda/extraction.json")
    if request.method == "GET":
        try:
            if os.path.exists(path):
                with open(path) as f: return jsonify(json.load(f))
        except: pass
        return jsonify({"provider":"openrouter","api_key":"","model":"qwen/qwen-turbo","base_url":"https://openrouter.ai/api/v1",
                        "auto_extract":True,"extract_preferences":True,"extract_facts":True,"extract_decisions":True,"max_extractions_per_min":10})
    else:
        data = request.json
        # Don't save empty api_key if it was masked
        if data.get("api_key") == "": data["api_key"] = None
        os.makedirs(os.path.dirname(path), exist_ok=True)
        with open(path, 'w') as f: json.dump(data, f, indent=2)
        return jsonify({"success": True, **data})

@app.route("/api/settings/test-llm", methods=["POST"])
def test_llm():
    data = request.json
    provider = data.get("provider","")
    api_key = data.get("api_key","")
    model = data.get("model","gpt-4o-mini")
    base_url = data.get("base_url","https://api.openai.com/v1")
    
    if not api_key:
        return jsonify({"ok": False, "error": "No API key provided"})
    
    try:
        import httpx
        if provider == "ollama":
            r = httpx.get(f"{base_url.replace('/v1','')}/api/tags", timeout=5)
            return jsonify({"ok": r.status_code == 200, "error": "" if r.status_code == 200 else f"HTTP {r.status_code}"})
        else:
            r = httpx.post(
                f"{base_url}/chat/completions",
                headers={"Authorization": f"Bearer {api_key}", "Content-Type": "application/json"},
                json={"model": model, "messages": [{"role": "user", "content": "Respond with only the word: OK"}], "max_tokens": 10},
                timeout=10,
            )
            if r.status_code == 200:
                return jsonify({"ok": True, "model": r.json().get("model","")})
            else:
                return jsonify({"ok": False, "error": f"HTTP {r.status_code}: {r.text[:200]}"})
    except Exception as e:
        return jsonify({"ok": False, "error": str(e)})

@app.route("/api/delete", methods=["POST"])
def delete():
    key = request.json.get("key","").strip()
    if not key: return jsonify({"error":"no key"}), 400
    conn = get_db(); cur = conn.cursor()
    cur.execute("DELETE FROM nodes WHERE name = ?", (key,))
    deleted = cur.rowcount; conn.commit(); conn.close()
    return jsonify({"deleted": deleted})

if __name__ == "__main__":
    print("  [DEPRECATED] This legacy dashboard is being phased out.")
    print("  [DEPRECATED] Use the runtime-backed dashboard on http://localhost:7842 instead.\n")
    print("  Octopoda Local Dashboard")
    print("  http://localhost:7844\n")
    app.run(host="0.0.0.0", port=7844)
