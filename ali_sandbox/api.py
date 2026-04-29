from .demo_scripts import build_initial_demo_code
from .self_healing import run_self_healing_bridge

try:
    from flask import Flask, jsonify, request
except ImportError:  # pragma: no cover - exercised only when Flask is not installed
    Flask = None
    jsonify = None
    request = None


def create_app():
    if Flask is None:
        raise RuntimeError("Flask is not installed. Run: python -m pip install -r requirements.txt")

    app = Flask(__name__)

    @app.after_request
    def add_frontend_cors_headers(response):
        origin = request.headers.get("Origin") or "*"
        response.headers["Access-Control-Allow-Origin"] = origin
        response.headers["Access-Control-Allow-Headers"] = "Content-Type, Authorization"
        response.headers["Access-Control-Allow-Methods"] = "GET, POST, OPTIONS"
        return response

    def with_frontend_summary(payload):
        attempts = payload.get("attempts") or []
        return {
            **payload,
            "attempts_count": len(attempts),
        }

    @app.route("/run", methods=["OPTIONS"])
    def run_bridge_preflight():
        return "", 204

    @app.route("/run", methods=["POST"], provide_automatic_options=False)
    def run_bridge():
        try:
            payload = request.get_json(silent=True) or {}
            mode = payload.get("mode", "discord_live")
            demo_failure = payload.get("demo_failure", "bad_endpoint")
            initial_code = payload.get("initial_code") or build_initial_demo_code(demo_failure, mode)
            result = run_self_healing_bridge(
                initial_code,
                mode=mode,
                max_retries=int(payload.get("max_retries", 3)),
                timeout_seconds=int(payload.get("timeout_seconds", 30)),
            )
            return jsonify(with_frontend_summary(result)), 200
        except Exception as exc:
            return (
                jsonify(
                    with_frontend_summary(
                        {
                        "success": False,
                        "generated_code": "",
                        "output": "",
                        "error": f"Pipeline failed before sandbox execution: {exc}",
                        "attempts": [],
                        "stage": "failed",
                    }
                    )
                ),
                200,
            )

    @app.get("/health")
    def health():
        return jsonify({"ok": True, "service": "ali-sandbox"})

    return app


if __name__ == "__main__":
    create_app().run(host="0.0.0.0", port=5000, debug=True)
