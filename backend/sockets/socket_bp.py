from flask import Blueprint
from flask_socketio import SocketIO
import builtins
socket_bp = Blueprint("socket_bp", __name__)

socketio = SocketIO(cors_allowed_origins="*")


old_print = print

def socket_print(*args, **kwargs):
    msg = " ".join(map(str, args))
    old_print(msg)
    # print("HOOK WORKING")
    try:
        socketio.emit("scrape_log", {"msg": msg})
    except Exception:
        pass

builtins.print = socket_print


def init_socket(app):
    socketio.init_app(app)

    @socketio.on("connect")
    def handle_connect():
        print("Socket client connected")

    @socketio.on("disconnect")
    def handle_disconnect():
        print("Socket client disconnected")


