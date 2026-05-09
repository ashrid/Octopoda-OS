"""
Synrix Agent Runtime — Dashboard API Routes
All REST API endpoints for the dashboard.
"""

import os
import time
import json
import sqlite3
from datetime import datetime, timezone
from flask import Blueprint, jsonify, request, Response
from synrix.agent_backend import get_synrix_backend
from synrix_runtime.extraction_config import (
    apply_extraction_settings,
    load_extraction_settings,
    save_extraction_settings,
)

api = Blueprint("api", __name__)

_backend = None

def get_backend():
    global _backend
    if _backend is None:
        try:
            from synrix_runtime.core.daemon import RuntimeDaemon
            daemon = RuntimeDaemon.get_instance()
            if daemon.backend is not None:
                _backend = daemon.backend
                return _backend
        except Exception:
            pass
        from synrix_runtime.config import SynrixConfig
        config = SynrixConfig.from_env()
        _backend = get_synrix_backend(**config.get_backend_kwargs())
    return _backend


WEBHOOKS_PATH = os.path.expanduser("~/.octopoda/webhooks.json")


def _load_webhooks():
    if not os.path.exists(WEBHOOKS_PATH):
        return []
    try:
        with open(WEBHOOKS_PATH) as handle:
            return json.load(handle)
    except Exception:
        return []


def _save_webhooks(webhooks):
    os.makedirs(os.path.dirname(WEBHOOKS_PATH), exist_ok=True)
    with open(WEBHOOKS_PATH, "w") as handle:
        json.dump(webhooks, handle, indent=2)


def _sqlite_db_path():
    backend = get_backend()
    client = getattr(backend, "client", None)
    return getattr(client, "db_path", None)


def _local_runtime(agent_id: str = "dashboard"):
    from synrix_runtime.api.runtime import AgentRuntime
    return AgentRuntime(agent_id, agent_type="dashboard", require_account=False)


@api.route("/api/system/status")
def system_status():
    try:
        from synrix_runtime.core.daemon import RuntimeDaemon
        daemon = RuntimeDaemon.get_instance()
        return jsonify(daemon.get_system_status())
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@api.route("/api/health")
def health_status():
    try:
        backend = get_backend()
        uptime = 0
        total_agents = 0
        running = False
        try:
            from synrix_runtime.core.daemon import RuntimeDaemon
            daemon = RuntimeDaemon.get_instance()
            running = bool(daemon.running)
            if running:
                status = daemon.get_system_status()
                uptime = status.get("uptime_seconds", 0)
                total_agents = status.get("total_agents", 0)
        except Exception:
            pass
        return jsonify({
            "status": "ok" if running else "starting",
            "backend": getattr(backend, "backend_type", "unknown"),
            "uptime_seconds": uptime,
            "total_agents": total_agents,
        })
    except Exception as e:
        return jsonify({"status": "error", "error": str(e)}), 500


@api.route("/api/authentication")
def authentication_status():
    return jsonify({
        "authenticated": False,
        "local_mode": True,
        "mode": "local",
        "account_required": False,
    })


@api.route("/api/pricing/")
def pricing_status():
    return jsonify({
        "plan": "local",
        "status": "active",
        "limits": {"agents": "unlimited", "memories": "unlimited"},
        "billing": "disabled_in_local_mode",
    })


@api.route("/api/settings")
def settings_status():
    return jsonify({
        "local_mode": True,
        "extraction": load_extraction_settings(),
        "webhook_count": len(_load_webhooks()),
    })


@api.route("/api/overview")
def overview():
    try:
        backend = get_backend()
        db_path = _sqlite_db_path()
        nodes = len(backend.query_prefix("", limit=100000))
        shared_spaces = len(backend.query_prefix("shared:", limit=500))
        db_bytes = os.path.getsize(db_path) if db_path and os.path.exists(db_path) else 0
        growth = []
        if db_path and os.path.exists(db_path):
            conn = sqlite3.connect(db_path)
            conn.row_factory = sqlite3.Row
            cur = conn.cursor()
            cur.execute("SELECT DATE(created_at,'unixepoch') as day, COUNT(*) as cnt FROM nodes GROUP BY day ORDER BY day LIMIT 30")
            growth = [{"day": row["day"], "count": row["cnt"]} for row in cur.fetchall()]
            conn.close()
        return jsonify({
            "nodes": nodes,
            "shared_records": shared_spaces,
            "db_path": db_path,
            "db_exists": bool(db_path and os.path.exists(db_path)),
            "db_bytes": db_bytes,
            "db_size": f"{db_bytes / 1024:.1f} KB" if db_bytes < 1048576 else f"{db_bytes / 1048576:.1f} MB",
            "growth": growth,
            "webhooks": len(_load_webhooks()),
            "extraction": load_extraction_settings(),
        })
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@api.route("/api/agents")
def list_agents():
    try:
        from synrix_runtime.core.daemon import RuntimeDaemon
        daemon = RuntimeDaemon.get_instance()
        agents = daemon.get_active_agents()

        from synrix_runtime.monitoring.metrics import MetricsCollector
        collector = MetricsCollector.get_instance(get_backend())

        enriched = []
        for agent in agents:
            agent_id = agent.get("agent_id", "")
            try:
                m = collector.get_agent_metrics(agent_id)
                agent["performance_score"] = m.performance_score
                agent["total_operations"] = m.total_operations
                agent["avg_write_latency_us"] = m.avg_write_latency_us
                agent["avg_read_latency_us"] = m.avg_read_latency_us
                agent["memory_node_count"] = m.memory_node_count
                agent["crash_count"] = m.crash_count
                agent["uptime_seconds"] = m.uptime_seconds
                agent["error_rate"] = m.error_rate
            except Exception:
                pass
            # Normalize: frontend uses "status", backend uses "state"
            agent["status"] = agent.get("state", "unknown")
            enriched.append(agent)

        return jsonify(enriched)
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@api.route("/api/agents/<agent_id>")
def agent_detail(agent_id):
    try:
        from synrix_runtime.monitoring.metrics import MetricsCollector
        collector = MetricsCollector.get_instance(get_backend())
        m = collector.get_agent_metrics(agent_id)
        breakdown = collector.get_performance_breakdown(agent_id)

        from synrix_runtime.core.daemon import RuntimeDaemon
        daemon = RuntimeDaemon.get_instance()
        agents = daemon.get_all_agents()
        agent_info = next((a for a in agents if a.get("agent_id") == agent_id), {})

        return jsonify({
            "agent_id": agent_id,
            "info": agent_info,
            "metrics": {
                "total_operations": m.total_operations,
                "total_writes": m.total_writes,
                "total_reads": m.total_reads,
                "total_queries": m.total_queries,
                "avg_write_latency_us": m.avg_write_latency_us,
                "avg_read_latency_us": m.avg_read_latency_us,
                "crash_count": m.crash_count,
                "recovery_count": m.recovery_count,
                "memory_node_count": m.memory_node_count,
                "performance_score": m.performance_score,
                "uptime_seconds": m.uptime_seconds,
                "error_rate": m.error_rate,
            },
            "breakdown": breakdown,
        })
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@api.route("/api/agents/<agent_id>/memory")
def agent_memory(agent_id):
    try:
        backend = get_backend()
        results = backend.query_prefix(f"agents:{agent_id}:", limit=200)
        items = []
        for r in results:
            key = r.get("key", "")
            data = r.get("data", {})
            val = data.get("value", data)
            items.append({
                "key": key,
                "value": val,
                "node_id": r.get("id"),
                "size_bytes": len(json.dumps(val).encode()) if val else 0,
            })
        return jsonify(items)
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@api.route("/api/agents/<agent_id>/metrics")
def agent_metrics(agent_id):
    try:
        from synrix_runtime.monitoring.metrics import MetricsCollector
        collector = MetricsCollector.get_instance(get_backend())
        minutes = request.args.get("minutes", 60, type=int)
        metric_type = request.args.get("type", "write")
        series = collector.get_time_series(agent_id, metric_type, minutes)
        return jsonify(series)
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@api.route("/api/agents/<agent_id>/audit")
def agent_audit(agent_id):
    try:
        from synrix_runtime.monitoring.audit import AuditSystem
        audit = AuditSystem(get_backend())
        events = audit.replay(agent_id)
        return jsonify(events)
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@api.route("/api/agents/<agent_id>/replay")
def agent_replay(agent_id):
    try:
        from synrix_runtime.monitoring.audit import AuditSystem
        audit = AuditSystem(get_backend())
        from_ts = request.args.get("from", None, type=float)
        to_ts = request.args.get("to", None, type=float)
        events = audit.replay(agent_id, from_ts=from_ts, to_ts=to_ts)
        return jsonify(events)
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@api.route("/api/shared")
def shared_spaces():
    try:
        from synrix_runtime.api.shared_memory import SharedMemoryBus
        bus = SharedMemoryBus(get_backend())
        return jsonify(bus.list_spaces())
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@api.route("/api/shared/<space>")
def shared_space_detail(space):
    try:
        from synrix_runtime.api.shared_memory import SharedMemoryBus
        bus = SharedMemoryBus(get_backend())
        items = bus.get_all(space)
        changelog = bus.get_changelog(space, limit=20)
        return jsonify({"items": items, "changelog": changelog})
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@api.route("/api/shared/write", methods=["POST"])
def shared_write():
    data = request.json or {}
    key = data.get("key", "").strip()
    value = data.get("value")
    space = data.get("space", "global")
    author = data.get("author", "dashboard")
    if not key or value is None:
        return jsonify({"error": "key and value required"}), 400
    try:
        from synrix_runtime.api.shared_memory import SharedMemoryBus
        bus = SharedMemoryBus(get_backend())
        result = bus.write(space=space, key=key, value=value, author_agent=author)
        return jsonify({"success": True, **result})
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@api.route("/api/metrics/system")
def system_metrics():
    try:
        from synrix_runtime.monitoring.metrics import MetricsCollector
        collector = MetricsCollector.get_instance(get_backend())
        m = collector.get_system_metrics()
        return jsonify({
            "total_agents": m.total_agents,
            "active_agents": m.active_agents,
            "total_operations": m.total_operations,
            "system_uptime_seconds": m.system_uptime_seconds,
            "mean_recovery_time_us": m.mean_recovery_time_us,
            "operations_per_minute": m.operations_per_minute,
            "total_crashes": m.total_crashes,
            "total_recoveries": m.total_recoveries,
            "most_active_agent": m.most_active_agent,
            "slowest_agent": m.slowest_agent,
        })
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@api.route("/api/metrics/timeseries")
def metrics_timeseries():
    try:
        from synrix_runtime.monitoring.metrics import MetricsCollector
        collector = MetricsCollector.get_instance(get_backend())
        agent_id = request.args.get("agent_id", "")
        metric_type = request.args.get("type", "write")
        minutes = request.args.get("minutes", 60, type=int)
        series = collector.get_time_series(agent_id, metric_type, minutes)
        return jsonify(series)
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@api.route("/api/anomalies")
def anomalies():
    try:
        from synrix_runtime.monitoring.anomaly import AnomalyDetector
        detector = AnomalyDetector(get_backend())
        return jsonify(detector.get_all_anomalies())
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@api.route("/api/audit/timeline")
def audit_timeline():
    try:
        from synrix_runtime.monitoring.audit import AuditSystem
        audit = AuditSystem(get_backend())
        limit = request.args.get("limit", 50, type=int)
        return jsonify(audit.get_global_timeline(limit))
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@api.route("/api/audit/explain/<agent_id>/<timestamp>")
def audit_explain(agent_id, timestamp):
    try:
        from synrix_runtime.monitoring.audit import AuditSystem
        audit = AuditSystem(get_backend())
        return jsonify(audit.explain_decision(agent_id, float(timestamp)))
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@api.route("/api/recovery/history")
def recovery_history():
    try:
        from synrix_runtime.core.recovery import RecoveryOrchestrator
        orchestrator = RecoveryOrchestrator(get_backend())
        history = orchestrator.get_all_recovery_history()
        stats = orchestrator.get_recovery_stats()
        return jsonify({"history": history, "stats": stats})
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@api.route("/api/loop")
def loop_status():
    try:
        with _local_runtime("dashboard-loop") as rt:
            return jsonify({"status": rt.get_loop_status(), "history": rt.get_loop_history(24)})
    except Exception as e:
        return jsonify({"error": str(e), "status": {"severity": "unknown", "score": 0}}), 500


@api.route("/api/agents/<agent_id>/similar")
def agent_semantic_search(agent_id):
    """Semantic search across an agent's memories."""
    try:
        from synrix_runtime.api.runtime import AgentRuntime
        q = request.args.get("q", "")
        limit = request.args.get("limit", 10, type=int)
        if not q:
            return jsonify({"error": "Query parameter 'q' is required"}), 400
        with AgentRuntime(agent_id) as agent:
            result = agent.recall_similar(q, limit=limit)
        return jsonify({
            "agent_id": agent_id,
            "query": q,
            "items": result.items,
            "count": result.count,
            "latency_us": result.latency_us,
        })
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@api.route("/api/agents/<agent_id>/history/<path:key>")
def agent_memory_history(agent_id, key):
    """Get version history of a memory key."""
    try:
        from synrix_runtime.api.runtime import AgentRuntime
        with AgentRuntime(agent_id) as agent:
            result = agent.recall_history(key)
        return jsonify({
            "agent_id": agent_id,
            "key": result.key,
            "current_version": result.current_version,
            "versions": result.versions,
            "latency_us": result.latency_us,
        })
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@api.route("/api/agents/<agent_id>/related/<entity>")
def agent_related_entities(agent_id, entity):
    """Query the knowledge graph for entity relationships."""
    try:
        from synrix_runtime.api.runtime import AgentRuntime
        with AgentRuntime(agent_id) as agent:
            result = agent.related(entity)
        return jsonify({
            "agent_id": agent_id,
            "entity": result.entity,
            "entity_type": result.entity_type,
            "found": result.found,
            "relationships": result.relationships,
            "latency_us": result.latency_us,
        })
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@api.route("/api/memory/browse")
def memory_browse():
    try:
        prefix = request.args.get("prefix", "")
        limit = request.args.get("limit", 100, type=int)
        offset = request.args.get("offset", 0, type=int)
        backend = get_backend()

        start = time.perf_counter_ns()
        results = backend.query_prefix(prefix, limit=limit + offset)
        latency_us = (time.perf_counter_ns() - start) / 1000
        if offset:
            results = results[offset:]

        items = []
        for r in results:
            key = r.get("key", "")
            data = r.get("data", {})
            val = data.get("value", data)
            items.append({
                "key": key,
                "value": val,
                "node_id": r.get("id"),
                "size_bytes": len(json.dumps(val).encode()) if val else 0,
            })
        return jsonify({"items": items, "count": len(items), "offset": offset, "limit": limit, "latency_us": latency_us})
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@api.route("/api/memory/delete", methods=["POST"])
def memory_delete():
    data = request.json or {}
    key = data.get("key", "").strip()
    if not key:
        return jsonify({"error": "no key"}), 400
    try:
        backend = get_backend()
        deleted = bool(backend.delete(key))
        db_path = _sqlite_db_path()
        if not deleted and db_path and os.path.exists(db_path):
            conn = sqlite3.connect(db_path)
            cur = conn.cursor()
            cur.execute("DELETE FROM nodes WHERE name = ?", (key,))
            deleted = cur.rowcount > 0
            conn.commit()
            conn.close()
        return jsonify({"deleted": deleted, "key": key})
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@api.route("/api/search")
def global_search():
    query = request.args.get("q", "").strip()
    if not query:
        return jsonify({"results": []})
    try:
        backend = get_backend()
        results = []
        try:
            results = backend.semantic_search(query=query, limit=20)
        except Exception:
            prefix_matches = backend.query_prefix("agents:", limit=1000)
            query_terms = [term.lower() for term in query.split() if term.strip()]
            for row in prefix_matches:
                data = row.get("data", {})
                value = data.get("value", data)
                text = json.dumps(value, default=str).lower()
                if any(term in text for term in query_terms):
                    results.append({
                        "key": row.get("key", ""),
                        "value": value,
                        "score": 1.0,
                    })
                    if len(results) >= 20:
                        break

        formatted = []
        for row in results:
            data = row.get("data", row)
            value = data.get("value", data) if isinstance(data, dict) else data
            formatted.append({
                "key": row.get("key", ""),
                "value": value,
                "score": row.get("score"),
            })
        return jsonify({"results": formatted, "count": len(formatted)})
    except Exception as e:
        return jsonify({"error": str(e), "results": []}), 500


@api.route("/api/live")
def live_updates():
    try:
        rows = get_backend().query_prefix("", limit=20)
        writes = []
        for row in rows:
            writes.append({
                "name": row.get("key", ""),
                "time": row.get("valid_from") or row.get("created_at") or time.time(),
            })
        return jsonify({"writes": writes, "cycles": []})
    except Exception as e:
        return jsonify({"error": str(e), "writes": [], "cycles": []}), 500


@api.route("/api/knowledge-graph")
def knowledge_graph():
    db_path = _sqlite_db_path()
    if not db_path or not os.path.exists(db_path):
        return jsonify({"entities": [], "relationships": []})
    try:
        conn = sqlite3.connect(db_path)
        conn.row_factory = sqlite3.Row
        cur = conn.cursor()
        cur.execute("SELECT COUNT(*) FROM entities")
        has_entities = cur.fetchone()[0] > 0

        if has_entities:
            cur.execute("SELECT name, data FROM entities LIMIT 100")
            ents = [{"id": r["name"], "data": str(r["data"])[:100]} for r in cur.fetchall()]
            cur.execute("SELECT source, target, type FROM relationships LIMIT 200")
            rels = [{"source": r["source"], "target": r["target"], "type": r["type"]} for r in cur.fetchall()]
        else:
            cur.execute("SELECT fact_text, node_name FROM fact_embeddings LIMIT 200")
            rows = cur.fetchall()
            seen = set()
            ents = []
            for r in rows:
                fact_text = r[0]
                if fact_text and fact_text not in seen:
                    seen.add(fact_text)
                    ents.append({"id": fact_text, "data": r[1]})
            rels = []
            grouped = {}
            for r in rows:
                if r[0]:
                    grouped.setdefault(r[1], []).append(r[0])
            for facts in grouped.values():
                for i in range(len(facts)):
                    for j in range(i + 1, len(facts)):
                        rels.append({"source": facts[i], "target": facts[j], "type": "co_occurrence"})
            rels = rels[:200]
        conn.close()
        return jsonify({"entities": ents, "relationships": rels})
    except Exception as e:
        return jsonify({"error": str(e), "entities": [], "relationships": []}), 500


@api.route("/api/webhooks", methods=["GET", "POST", "DELETE"])
def webhooks():
    if request.method == "GET":
        return jsonify({"webhooks": _load_webhooks()})

    if request.method == "POST":
        data = request.json or {}
        webhooks = _load_webhooks()
        webhooks.append({
            "id": str(int(time.time() * 1000)),
            "url": data.get("url", ""),
            "events": data.get("events", ["memory.write"]),
            "description": data.get("description", ""),
            "created": datetime.now(timezone.utc).isoformat(),
            "active": True,
        })
        _save_webhooks(webhooks)
        return jsonify({"success": True, "webhooks": webhooks})

    data = request.json or {}
    webhook_id = data.get("id", "")
    webhooks = [w for w in _load_webhooks() if w.get("id") != webhook_id]
    _save_webhooks(webhooks)
    return jsonify({"success": True, "webhooks": webhooks})


@api.route("/api/settings/extraction", methods=["GET", "POST"])
def extraction_settings():
    if request.method == "GET":
        return jsonify(load_extraction_settings())

    data = request.json or {}
    settings = {**load_extraction_settings(), **data}
    if settings.get("api_key") == "":
        settings["api_key"] = None
    save_extraction_settings(settings)
    apply_extraction_settings(settings)
    return jsonify({"success": True, **settings})


@api.route("/api/settings/test-llm", methods=["POST"])
def test_llm():
    data = request.json or {}
    provider = data.get("provider", "")
    api_key = data.get("api_key", "")
    model = data.get("model", "gpt-4o-mini")
    base_url = data.get("base_url", "https://api.openai.com/v1")

    if not api_key:
        return jsonify({"ok": False, "error": "No API key provided"})

    try:
        import httpx
        if provider == "ollama":
            response = httpx.get(f"{base_url.replace('/v1', '')}/api/tags", timeout=5)
            return jsonify({"ok": response.status_code == 200, "error": "" if response.status_code == 200 else f"HTTP {response.status_code}"})

        response = httpx.post(
            f"{base_url}/chat/completions",
            headers={"Authorization": f"Bearer {api_key}", "Content-Type": "application/json"},
            json={
                "model": model,
                "messages": [{"role": "user", "content": "Respond with only the word: OK"}],
                "max_tokens": 10,
            },
            timeout=10,
        )
        if response.status_code == 200:
            return jsonify({"ok": True, "model": response.json().get("model", "")})
        return jsonify({"ok": False, "error": f"HTTP {response.status_code}: {response.text[:200]}"})
    except Exception as e:
        return jsonify({"ok": False, "error": str(e)})


@api.route("/api/demo/start", methods=["POST"])
def demo_start():
    try:
        import threading
        from synrix_runtime.demo.three_agent_demo import run_demo
        t = threading.Thread(target=run_demo, daemon=True)
        t.start()
        return jsonify({"started": True, "message": "Three agent demo started"})
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@api.route("/api/demo/crash/<agent_id>", methods=["POST"])
def demo_crash(agent_id):
    try:
        from synrix_runtime.api.system_calls import SystemCalls
        syscalls = SystemCalls(get_backend())
        result = syscalls.simulate_crash(agent_id)
        return jsonify(result)
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@api.route("/api/demo/reboot/<agent_id>", methods=["POST"])
def demo_reboot(agent_id):
    try:
        from synrix_runtime.api.system_calls import SystemCalls
        syscalls = SystemCalls(get_backend())
        result = syscalls.trigger_recovery(agent_id)
        return jsonify(result)
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@api.route("/stream/events")
def stream_events():
    from synrix_runtime.dashboard.sse import SSEManager
    manager = SSEManager(get_backend())
    return Response(
        manager.event_stream(),
        mimetype="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "Connection": "keep-alive",
            "X-Accel-Buffering": "no",
        }
    )
