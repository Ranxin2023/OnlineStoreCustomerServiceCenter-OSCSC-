
import os
BASE_URL  = os.getenv("BASE_URL")
DEBUG_PORT = os.getenv("DEBUG_PORT")
PAGE_LOADING_TIME = 30
LOADING_TIME = 15
SWITCHING_TIME = 2
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

tag_list = [
    ("order_id_el","span.header--valueHighLight--wCk3sLF", False), 
    ("time_el","span.header--value--E2HYUZn:not(.header--valueHighLight--wCk3sLF)", True), 
    ("buyer_el","a.buyerInfo--inline--U3y4fIR", False),
    ("product_el","span.productInfo--itemTitle--QshSnPH", False),
    ("sku_el","span.productInfo--skuCodeValue--FJA_1Ru", True),
    ("price_el","span.productInfo--unitFee--mVPKC9G", False),
    ("qty_el","td[data-next-table-col='3'] div", False),
    ("amount_el","div.amount--amount--YdsJokJ", False),
    ("status_el","div.chc-state-label__stateText", False),
    ("tag_el","span.chc-color-tag", True),
    ("btns","button.next-btn span.next-btn-helper", True)
]