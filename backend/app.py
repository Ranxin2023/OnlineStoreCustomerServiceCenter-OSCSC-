import os
from flask import Flask, send_from_directory
from flask_cors import CORS


from sockets.socket_bp import socketio, init_socket

from routes.web_scrapy_route import web_scrapy_bp


def create_app():
    app = Flask(__name__, static_folder="dist", static_url_path="")
    CORS(app)
    app.register_blueprint(web_scrapy_bp)
    init_socket(app=app)
    @app.route("/", defaults={"path": ""})
    @app.route("/<path:path>")
    def serve_react(path):
        if path and os.path.exists(os.path.join("dist", path)):
            return send_from_directory("dist", path)
        return send_from_directory("dist", "index.html")

    return app

if __name__ == "__main__":
    app = create_app()
    
    socketio.run(app, host="0.0.0.0", port=5000, debug=True)