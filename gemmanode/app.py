from __future__ import annotations

import logging
from typing import Any

from flask import Flask, jsonify, render_template, request

from .orchestration import NoEligibleResourceError, Orchestrator, TaskRequirements
from .resource_manager import InvalidConfigurationError, ResourceManager, ResourceNotFoundError

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def create_app() -> Flask:
    app = Flask(__name__)
    manager = ResourceManager()
    orchestrator = Orchestrator()

    @app.get("/")
    def index() -> str:
        resources = [r.to_dict() for r in manager.list_resources()]
        return render_template("index.html", resources=resources)

    @app.get("/api/resources")
    def list_resources() -> Any:
        return jsonify([resource.to_dict() for resource in manager.list_resources()])

    @app.post("/api/resources/<resource_id>/enable")
    def toggle_resource(resource_id: str) -> Any:
        payload = request.get_json(silent=True) or {}
        enabled = bool(payload.get("enabled", True))
        try:
            resource = manager.set_enabled(resource_id, enabled)
        except ResourceNotFoundError:
            return jsonify({"error": "Resource not found."}), 404
        return jsonify(resource.to_dict())

    @app.post("/api/resources/<resource_id>/configure")
    def configure_resource(resource_id: str) -> Any:
        payload = request.get_json(silent=True) or {}
        configuration = payload.get("configuration") or {}
        secrets = payload.get("secrets") or {}
        try:
            resource = manager.configure_resource(resource_id, configuration=configuration, secrets=secrets)
        except ResourceNotFoundError:
            return jsonify({"error": "Resource not found."}), 404
        except InvalidConfigurationError:
            return jsonify({"error": "Configuration failed. Check required settings and secure storage availability."}), 400
        return jsonify(resource.to_dict())

    @app.post("/api/resources/<resource_id>/test")
    def test_resource(resource_id: str) -> Any:
        try:
            resource = manager.test_connection(resource_id)
        except ResourceNotFoundError:
            return jsonify({"error": "Resource not found."}), 404
        return jsonify(resource.to_dict())

    @app.delete("/api/resources/<resource_id>/credentials")
    def clear_resource_credentials(resource_id: str) -> Any:
        try:
            resource = manager.remove_credentials(resource_id)
        except ResourceNotFoundError:
            return jsonify({"error": "Resource not found."}), 404
        return jsonify(resource.to_dict())

    @app.post("/api/orchestrate")
    def orchestrate() -> Any:
        payload = request.get_json(silent=True) or {}
        task = payload.get("task", "")
        requirements = TaskRequirements(capabilities=set(payload.get("capabilities", [])))
        try:
            result = orchestrator.submit_task(task, requirements, manager.list_resources())
            return jsonify(result.__dict__)
        except NoEligibleResourceError:
            return jsonify({"success": False, "message": "No eligible resource is available for this task."}), 400

    return app


if __name__ == "__main__":
    create_app().run(host="0.0.0.0", port=8080)
