import os
from flask import Flask
from flask_cors import CORS
from routes.web_scrapy_route import web_scrapy_bp
def create_app():
    app = Flask(__name__)
    CORS(app)  # allow frontend (Vite) to call backend
    app.register_blueprint(web_scrapy_bp)
    FRONTEND = os.getenv("FRONTEND_ORIGIN", "http://localhost:5173")
    CORS(
        app,
        resources={r"/api/*": {"origins": [FRONTEND, "http://127.0.0.1:5173"]}},
        supports_credentials=True,
        allow_headers=["Content-Type", "Authorization"],
        methods=["GET", "POST", "PUT", "PATCH", "DELETE", "OPTIONS"],
    )
    return app


if __name__ == "__main__":
    app = create_app()
    app.run(host="0.0.0.0", port=5000, debug=True)
