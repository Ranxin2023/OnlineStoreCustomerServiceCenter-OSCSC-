
import os
BASE_URL  = os.getenv("BASE_URL")
DEBUG_PORT = os.getenv("DEBUG_PORT")
profile_map = {
        "98158": "store1",
        "1471480": "store2",
        "1579196": "store3"
    }


mapping = {
        '等待发货':     'Awaiting shipment',
        '等待买家收货': 'Awaiting buyer receipt',
        '交易成功':     'Transaction complete',
        '已关闭':       'Closed',
        '等待付款':     'Awaiting payment',
        '等待买家付款': 'Awaiting payment',
        '等待仓库发货': 'Awaiting warehouse shipment',
    }