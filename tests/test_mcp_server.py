"""
Tests for the Octopoda MCP Server tools.
Calls tool functions directly (no MCP transport needed).
"""

import pytest


@pytest.fixture
def mcp_env(tmp_dir, monkeypatch):
    """Set up environment for MCP tool testing (local mode, no API key)."""
    monkeypatch.setenv("SYNRIX_BACKEND", "sqlite")
    monkeypatch.setenv("SYNRIX_DATA_DIR", tmp_dir)
    monkeypatch.delenv("OCTOPODA_API_KEY", raising=False)

    from synrix_runtime.core.daemon import RuntimeDaemon
    from synrix_runtime.monitoring.metrics import MetricsCollector
    RuntimeDaemon.reset_instance()
    MetricsCollector._instance = None

    # Reset the MCP server state to force local mode
    from synrix_runtime.api import mcp_server
    for adapter in list(mcp_server._runtimes.values()):
        try:
            adapter.delete()
        except Exception:
            pass
    mcp_server._client = None
    mcp_server._local_mode = False
    mcp_server._agents.clear()
    mcp_server._runtimes.clear()

    yield

    for adapter in list(mcp_server._runtimes.values()):
        try:
            adapter.delete()
        except Exception:
            pass
    mcp_server._client = None
    mcp_server._local_mode = False
    mcp_server._agents.clear()
    mcp_server._runtimes.clear()
    RuntimeDaemon.reset_instance()
    MetricsCollector._instance = None


class TestMCPRememberRecall:

    def test_remember_and_recall(self, mcp_env):
        from synrix_runtime.api.mcp_server import octopoda_remember, octopoda_recall

        result = octopoda_remember("test_agent", "greeting", '{"msg": "hello"}')
        assert result["success"] is True
        assert result["key"] == "greeting"
        assert result["agent_id"] == "test_agent"

        recall = octopoda_recall("test_agent", "greeting")
        assert recall["found"] is True
        assert recall["value"]["msg"] == "hello"

    def test_remember_plain_text(self, mcp_env):
        from synrix_runtime.api.mcp_server import octopoda_remember, octopoda_recall

        octopoda_remember("text_agent", "note", "just a string")
        recall = octopoda_recall("text_agent", "note")
        assert recall["found"] is True
        assert recall["value"] == "just a string"

    def test_recall_missing_key(self, mcp_env):
        from synrix_runtime.api.mcp_server import octopoda_recall

        recall = octopoda_recall("ghost_agent", "nonexistent")
        assert recall["found"] is False

    def test_remember_with_tags(self, mcp_env):
        from synrix_runtime.api.mcp_server import octopoda_remember

        result = octopoda_remember("tag_agent", "task", '{"status": "done"}', tags=["work", "done"])
        assert result["success"] is True


class TestMCPSearch:

    def test_search_by_prefix(self, mcp_env):
        from synrix_runtime.api.mcp_server import octopoda_remember, octopoda_search

        octopoda_remember("search_agent", "task:1", '{"name": "first"}')
        octopoda_remember("search_agent", "task:2", '{"name": "second"}')
        octopoda_remember("search_agent", "other:1", '{"name": "other"}')

        result = octopoda_search("search_agent", "task:")
        assert result["count"] == 2

    def test_search_empty_prefix(self, mcp_env):
        from synrix_runtime.api.mcp_server import octopoda_search

        result = octopoda_search("empty_agent", "nothing:")
        assert result["count"] == 0


class TestMCPSnapshot:

    def test_snapshot_and_restore(self, mcp_env):
        from synrix_runtime.api.mcp_server import (
            octopoda_remember, octopoda_recall, octopoda_snapshot, octopoda_restore,
        )

        octopoda_remember("snap_agent", "key1", '{"val": "before"}')
        snap = octopoda_snapshot("snap_agent", label="v1")
        assert snap["label"] == "v1"
        assert snap["keys_captured"] >= 1

        # Overwrite
        octopoda_remember("snap_agent", "key1", '{"val": "after"}')
        recall = octopoda_recall("snap_agent", "key1")
        assert recall["value"]["val"] == "after"

        # Restore
        restore = octopoda_restore("snap_agent", label="v1")
        assert restore["label"] == "v1"
        assert restore["keys_restored"] >= 1

        # Value should be back
        recall2 = octopoda_recall("snap_agent", "key1")
        assert recall2["value"]["val"] == "before"


class TestMCPSharedMemory:

    def test_share_and_read(self, mcp_env):
        from synrix_runtime.api.mcp_server import octopoda_share, octopoda_read_shared

        result = octopoda_share("writer", "signal", '{"ready": true}', space="team")
        assert result["success"] is True

        read = octopoda_read_shared("reader", "signal", space="team")
        assert read["found"] is True
        assert read["value"]["ready"] is True

    def test_read_shared_missing(self, mcp_env):
        from synrix_runtime.api.mcp_server import octopoda_read_shared

        read = octopoda_read_shared("lonely", "missing_key")
        assert read["found"] is False


class TestMCPAgentManagement:

    def test_list_agents(self, mcp_env):
        from synrix_runtime.api.mcp_server import octopoda_remember, octopoda_list_agents

        # Create an agent by using it
        octopoda_remember("listed_agent", "k", '"v"')
        result = octopoda_list_agents()
        assert result["count"] >= 1

    def test_agent_stats(self, mcp_env):
        from synrix_runtime.api.mcp_server import octopoda_remember, octopoda_recall, octopoda_agent_stats

        octopoda_remember("stats_agent", "k1", '"v1"')
        octopoda_recall("stats_agent", "k1")

        stats = octopoda_agent_stats("stats_agent")
        assert stats["agent_id"] == "stats_agent"
        assert stats["total_writes"] >= 1
        assert stats["total_reads"] >= 1
        assert stats["total_operations"] >= 2

    def test_log_decision(self, mcp_env):
        from synrix_runtime.api.mcp_server import octopoda_log_decision

        result = octopoda_log_decision(
            "decision_agent", "chose_plan_B", "lower risk",
            context='{"alternatives": ["plan_A", "plan_B"]}'
        )
        assert result["logged"] is True
        assert result["decision"] == "chose_plan_B"

    def test_list_agents_includes_runtime_registered_agent(self, mcp_env):
        from synrix_runtime.api.runtime import AgentRuntime
        from synrix_runtime.api.mcp_server import octopoda_list_agents

        with AgentRuntime("runtime_registered", agent_type="test"):
            result = octopoda_list_agents()

        assert "runtime_registered" in result["agents"]


class TestMCPRuntimeCache:

    def test_runtime_reuse(self, mcp_env):
        from synrix_runtime.api.mcp_server import _get_runtime, _runtimes

        rt1 = _get_runtime("cache_test")
        rt2 = _get_runtime("cache_test")
        assert rt1 is rt2
        assert len(_runtimes) == 1

    def test_parse_value_json(self):
        from synrix_runtime.api.mcp_server import _parse_value

        assert _parse_value('{"a": 1}') == {"a": 1}
        assert _parse_value('[1, 2]') == [1, 2]
        assert _parse_value('"hello"') == "hello"

    def test_parse_value_plain(self):
        from synrix_runtime.api.mcp_server import _parse_value

        result = _parse_value("not json")
        assert result == {"value": "not json"}

    def test_delete_evicts_runtime_cache(self, mcp_env):
        from synrix_runtime.api.mcp_server import _get_runtime, _runtimes

        runtime = _get_runtime("evict_me")
        assert "evict_me" in _runtimes

        runtime.delete()
        assert "evict_me" not in _runtimes


class TestMCPAdvancedLocalMode:

    def test_related_returns_relationships(self, mcp_env):
        from synrix_runtime.api.mcp_server import octopoda_related

        result = octopoda_related("graph_agent", "missing_entity")
        assert result["entity"] == "missing_entity"
        assert isinstance(result["relationships"], list)

    def test_forget_and_forget_stale(self, mcp_env):
        from synrix_runtime.api.mcp_server import (
            octopoda_remember,
            octopoda_forget,
            octopoda_forget_stale,
            octopoda_recall,
        )

        octopoda_remember("forget_agent", "cleanup:key", '{"value": "gone"}')
        forget = octopoda_forget("forget_agent", "cleanup:key")
        assert forget["deleted"] is True
        recall = octopoda_recall("forget_agent", "cleanup:key")
        assert recall["found"] is False

        stale = octopoda_forget_stale("forget_agent", max_age_days=1)
        assert "deleted" in stale

    def test_memory_health_and_consolidate(self, mcp_env):
        from synrix_runtime.api.mcp_server import octopoda_remember, octopoda_memory_health, octopoda_consolidate

        octopoda_remember("health_agent", "k1", '"v1"')
        health = octopoda_memory_health("health_agent")
        assert health["agent_id"] == "health_agent"
        assert "health" in health

        consolidation = octopoda_consolidate("health_agent", dry_run=True)
        assert consolidation["agent_id"] == "health_agent"
        assert "consolidation" in consolidation

    def test_messaging_round_trip(self, mcp_env):
        from synrix_runtime.api.mcp_server import octopoda_send_message, octopoda_read_messages, octopoda_broadcast

        sent = octopoda_send_message("sender_agent", "receiver_agent", '{"hello": true}', message_type="alert")
        assert sent["sent"] is True

        inbox = octopoda_read_messages("receiver_agent")
        assert inbox["count"] >= 1
        assert inbox["messages"][0]["from_agent"] == "sender_agent"

        broadcast = octopoda_broadcast("sender_agent", '"system-wide"')
        assert broadcast["broadcast"] is True

    def test_goal_round_trip(self, mcp_env):
        from synrix_runtime.api.mcp_server import octopoda_set_goal, octopoda_get_goal, octopoda_update_progress

        set_result = octopoda_set_goal("goal_agent", "Ship local parity", milestones="adapter,dashboard")
        assert set_result["goal_set"] is True

        update = octopoda_update_progress("goal_agent", milestone_index=0, note="adapter done")
        assert "progress" in update

        goal = octopoda_get_goal("goal_agent")
        assert goal["goal"]["has_goal"] is True

    def test_filtered_search_and_context(self, mcp_env):
        from synrix_runtime.api.mcp_server import (
            octopoda_remember,
            octopoda_search_filtered,
            octopoda_process_conversation,
            octopoda_get_context,
        )

        octopoda_remember("filter_agent", "prefs:theme", '{"value": "dark mode", "__importance": "critical"}')
        search = octopoda_search_filtered("filter_agent", query="dark", importance="critical")
        assert search["agent_id"] == "filter_agent"
        assert "results" in search

        processed = octopoda_process_conversation(
            "filter_agent",
            "I prefer dark mode and concise replies",
            "Understood, I will keep responses concise.",
        )
        assert processed["processed"] is True

        context = octopoda_get_context("filter_agent", "dark mode", limit=5)
        assert "context" in context
