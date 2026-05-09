"""Tests for the local 7842 Flask dashboard API routes."""


class TestLocalDashboardStatus:

    def test_health_status(self, flask_client):
        resp = flask_client.get("/api/health")
        assert resp.status_code == 200
        data = resp.get_json()
        assert data["status"] == "ok"
        assert data["backend"] == "sqlite"

    def test_authentication_stub(self, flask_client):
        resp = flask_client.get("/api/authentication")
        assert resp.status_code == 200
        data = resp.get_json()
        assert data["local_mode"] is True
        assert data["account_required"] is False

    def test_pricing_stub(self, flask_client):
        resp = flask_client.get("/api/pricing/")
        assert resp.status_code == 200
        data = resp.get_json()
        assert data["plan"] == "local"
        assert data["billing"] == "disabled_in_local_mode"

    def test_settings_status(self, flask_client):
        resp = flask_client.get("/api/settings")
        assert resp.status_code == 200
        data = resp.get_json()
        assert data["local_mode"] is True
        assert "extraction" in data

    def test_overview_includes_db_size_and_growth(self, flask_client):
        resp = flask_client.get("/api/overview")
        assert resp.status_code == 200
        data = resp.get_json()
        assert "db_size" in data
        assert "db_bytes" in data
        assert "growth" in data


class TestLocalDashboardAdminRoutes:

    def test_webhooks_crud(self, flask_client):
        create = flask_client.post("/api/webhooks", json={
            "url": "http://localhost:9999/hook",
            "events": ["memory.write"],
            "description": "test webhook",
        })
        assert create.status_code == 200
        created = create.get_json()
        assert created["success"] is True
        webhook_id = created["webhooks"][0]["id"]

        fetch = flask_client.get("/api/webhooks")
        assert fetch.status_code == 200
        assert len(fetch.get_json()["webhooks"]) >= 1

        delete = flask_client.delete("/api/webhooks", json={"id": webhook_id})
        assert delete.status_code == 200
        assert delete.get_json()["success"] is True

    def test_extraction_settings_round_trip(self, flask_client):
        save = flask_client.post("/api/settings/extraction", json={
            "provider": "none",
            "api_key": "",
            "model": "gpt-4o-mini",
        })
        assert save.status_code == 200
        saved = save.get_json()
        assert saved["success"] is True

        fetch = flask_client.get("/api/settings/extraction")
        assert fetch.status_code == 200
        assert fetch.get_json()["provider"] == "none"

    def test_test_llm_requires_api_key(self, flask_client):
        resp = flask_client.post("/api/settings/test-llm", json={"provider": "openai", "api_key": ""})
        assert resp.status_code == 200
        assert resp.get_json()["ok"] is False


class TestLocalDashboardDataRoutes:

    def test_shared_write_and_read(self, flask_client):
        write = flask_client.post("/api/shared/write", json={
            "space": "team",
            "key": "project",
            "value": {"name": "Octopoda"},
            "author": "dashboard",
        })
        assert write.status_code == 200
        assert write.get_json()["success"] is True

        detail = flask_client.get("/api/shared/team")
        assert detail.status_code == 200
        data = detail.get_json()
        assert "items" in data

    def test_search_and_delete_memory(self, flask_client):

        search = flask_client.get("/api/search?q=delete")
        assert search.status_code == 200
        assert "results" in search.get_json()

        delete = flask_client.post("/api/memory/delete", json={"key": "shared:global:cleanup-target"})
        assert delete.status_code == 200
        deleted_payload = delete.get_json()
        assert deleted_payload["key"] == "shared:global:cleanup-target"
        assert "deleted" in deleted_payload

    def test_knowledge_graph_endpoint(self, flask_client):
        resp = flask_client.get("/api/knowledge-graph")
        assert resp.status_code == 200
        data = resp.get_json()
        assert "entities" in data
        assert "relationships" in data

    def test_loop_endpoint(self, flask_client):
        resp = flask_client.get("/api/loop")
        assert resp.status_code == 200
        data = resp.get_json()
        assert "status" in data
        assert "history" in data

    def test_live_endpoint(self, flask_client):
        resp = flask_client.get("/api/live")
        assert resp.status_code == 200
        data = resp.get_json()
        assert "writes" in data
        assert data["cycles"] == []

    def test_memory_browse_supports_offset(self, flask_client):
        for index in range(3):
            flask_client.post("/api/shared/write", json={
                "space": "pagination",
                "key": f"item-{index}",
                "value": {"index": index},
                "author": "dashboard",
            })

        resp = flask_client.get("/api/memory/browse?prefix=shared:pagination:&limit=2&offset=1")
        assert resp.status_code == 200
        data = resp.get_json()
        assert data["limit"] == 2
        assert data["offset"] == 1
        assert len(data["items"]) <= 2
