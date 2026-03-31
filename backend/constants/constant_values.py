
import os
from enum import IntEnum
BASE_URL  = os.getenv("BASE_URL")
DEBUG_PORT = os.getenv("DEBUG_PORT")
PAGE_LOADING_TIME = 30
LOADING_TIME = 20
ELEMENT_LOADING_TIME=5
SWITCHING_TIME = 2
TOTAL_ATTEMPT = 2
SEND_WAITING_TIME = 10
CHANNEL_ID = "1579616"

PROFILE_MAP = {
        "98158": "store1",
        "1471480": "store2",
        "1579196": "store3"
    }

STATUS_TRANSLATION = {
        '等待发货':     'Awaiting shipment',
        '等待买家收货': 'Awaiting buyer receipt',
        '交易成功':     'Transaction complete',
        '已关闭':       'Closed',
        '等待付款':     'Awaiting payment',
        '等待买家付款': 'Awaiting payment',
        '等待仓库发货': 'Awaiting warehouse shipment',
    }



SAFE_USERS = [
    "ae800292 user"
]

driver_pool = {}

class OrderStatus(IntEnum):
    PENDING_PAYMENT = 0      # 等待付款
    WAIT_SHIPMENT = 1       # 等待发货
    IN_TRANSIT = 2          # 等待买家收货
    COMPLETED = 3           # 交易完成
    CLOSED = 4              # 订单关闭
    DISPUTE = 5             # 纠纷中
    NO_ORDER = -1           # 暂无订单

ORDER_STATUS_MAP = {
    # ✅ 中文
    "等待付款": OrderStatus.PENDING_PAYMENT,
    "等待买家付款": OrderStatus.PENDING_PAYMENT,

    "等待发货": OrderStatus.WAIT_SHIPMENT,
    "等待仓库发货": OrderStatus.WAIT_SHIPMENT,

    "等待买家收货": OrderStatus.IN_TRANSIT,

    "交易完成": OrderStatus.COMPLETED,
    "交易成功": OrderStatus.COMPLETED,

    "订单关闭": OrderStatus.CLOSED,
    "已关闭": OrderStatus.CLOSED,

    "纠纷中订单": OrderStatus.DISPUTE,
    "纠纷中": OrderStatus.DISPUTE,
    "交易纠纷": OrderStatus.DISPUTE,

    "暂无订单": OrderStatus.NO_ORDER,

    # ✅ 英文
    "awaiting payment": OrderStatus.PENDING_PAYMENT,
    "awaiting shipment": OrderStatus.WAIT_SHIPMENT,
    "awaiting buyer receipt": OrderStatus.IN_TRANSIT,
    "arder completed": OrderStatus.COMPLETED,
    "transaction complete": OrderStatus.COMPLETED,
    "closed": OrderStatus.CLOSED,
    "in dispute": OrderStatus.DISPUTE,
    "no orders": OrderStatus.NO_ORDER
}