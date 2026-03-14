
import os
BASE_URL  = os.getenv("BASE_URL")
DEBUG_PORT = os.getenv("DEBUG_PORT")
PAGE_LOADING_TIME = 30
LOADING_TIME = 20
SWITCHING_TIME = 2
SEND_WAITING_TIME = 10
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
    "ae800292"
]

driver_pool = {}