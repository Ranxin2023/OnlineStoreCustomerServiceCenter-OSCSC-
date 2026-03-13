
import os
BASE_URL  = os.getenv("BASE_URL")
DEBUG_PORT = os.getenv("DEBUG_PORT")
PAGE_LOADING_TIME = 30
LOADING_TIME = 20
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

PHONE_COUNTRY_MAP = {
    "+966": "SA",
    "+1": "US",
    "+44": "GB",
    "+86": "CN",
    "+91": "IN",
    "+971": "AE",
}

ADDRESS_COUNTRY_MAP = {
    "united states": "US",
    "usa": "US",
    "us": "US",
    "canada": "CA",
    "puerto rico": "PR",
    "jamaica": "JM",
    "bahamas": "BS",
}

FILL_COUNTRY_HEADERS=[
    ("fill","订单号","row_number", ""),	
    ("fill","平台交易号", "order_id",""),	
    ("fixed","交货仓","delivery_warehouse","北京燕文"),
    ("fixed","产品名称", "product_name","燕文专线快递-普货"),	
    ("fill", "收件人姓名", "recipient",""),	
    ("fill", "收件人电话", "phone",""),	
    ("blank","收件人邮箱","recipient_email_address",""),
    ("blank","收件人税号","recipient_tax_ID",""),
    ("blank","收件人公司","recipient_company",""),
    ("fixed", "收件人国家","recipient_country","Saudi Arabia"),
    ("fill", "收件人省/州", "recipient_province_state",""),
    ("fill","收件人城市","recipient_city",""),
    ("fill","收件人邮编", "postal_code",""),
    ("fill","收件人地址","address", ""),
    ("blank","收件人门牌号","recipient_address",""),	
    ("fill","收件人短地址(英文)","short_address",""),
    ("blank","销售平台","sales_platform",""),
    ("blank", "发件人税号信息", "sender_tax_ID_information",""),	
    ("blank","生产销售企业", "production_and_sales_enterprises",""),
    ("blank","生产销售企业代码","production_and_sales_enterprise_code",""),	
    ("blank","CSP","csp", ""),
    ("blank","包装尺寸【长】cm", "packaging_dimensions_length_cm","1"),	
    ("fixed","包装尺寸【宽】cm","packaging_dimensions_width_cm","1"),
    ("fixed","包装尺寸【高】cm","packaging_dimensions_height_cm","1"),
    ("blank","收款到账日期","date_of_receipt_of_payment",""),
    ("fixed","币种类型","currency_type","美元"),
    ("fixed","是否含电","contain_electricity","否"),
    ("blank","拣货单信息","picking_list_information",""),	
    ("blank","IOSS税号","ioss_tax_number",""),
    ("fixed","中文品名1","chinese_product_name_1", "塑料模具"),
    ("fixed","英文品名1","english_product_name_1","plastic moulde"),
    ("blank","出口国申报单价1","exporting_country_declared_unit_price_1",""),	
    ("fixed","单票数量1","number_of_tickets_per_ticket_1", "1"),
    ("fixed","重量1(g)","weight_one_gram","1"),
    ("fixed","目的国申报单价1","unit_price_declared_in_the_destination_country_1","9.99"),	
    ("fixed","商品材质1","product_material_1","测试材质1"),
    ("fixed","商品海关编码1","commodity_customs_code_1", "测试海关编码1"),
    ("blank","商品链接1","product_link_1", ""),
    ("blank","SKU1","sku1", ""),
    ("fixed","中文品名2","chinese_product_name_2", "杯子"),
    ("fixed","英文品名2","english_product_name_2", "cup"),
    ("blank","单票数量2","number_of_tickets_per_ticket_2",""),
    ("blank","重量2(g)","weight_two_gram", ""),
    ("blank","目的国申报单价2","unit_price_declared_in_the_destination_country_2",""),
    ("blank","出口国申报单价2","exporting_country_declared_unit_price_2", ""),
    ("fixed","商品材质2","product_material_2","测试材质2"),
    ("fixed","商品海关编码2","commodity_customs_code_2", "测试海关编码2"),
    ("blank","商品链接2","product_link_2", ""),
    ("blank","SKU2","sku2",""),
    ("blank","中文品名3","chinese_product_name_3",""),
    ("blank","英文品名3","english_product_name_3",""),
    ("blank","单票数量3","number_of_tickets_per_ticket_3",""),
    ("blank","重量3(g)","weight_three_gram",""),
    ("blank","目的国申报单价3","unit_price_declared_in_the_destination_country_3",""),
    ("blank","出口国申报单价3","exporting_country_declared_unit_price_3", ""),
    ("blank","商品材质3","product_material_3",""),
    ("blank","商品海关编码3","commodity_customs_code_3", ""),
    ("blank","商品链接3","product_link_3",""),
    ("blank","SKU3","sku3",""),
    ("blank","中文品名4","chinese_product_name_4",""),
    ("blank","英文品名4","english_product_name_4",""),
    ("blank","单票数量4","number_of_tickets_per_ticket_4",""),
    ("blank","重量4(g)","weight_four_gram",""),
    ("blank","目的国申报单价4","unit_price_declared_in_the_destination_country_4", ""),
    ("blank","出口国申报单价4","exporting_country_declared_unit_price_4", ""),
    ("blank","商品材质4","product_material_4", ""),
    ("blank","商品海关编码4","commodity_customs_code_4", ""),	
    ("blank","商品链接4","product_link_4",""),
    ("blank","SKU4","sku4", ""),
    ("blank","中文品名5", "chinese_product_name_5",""),	
    ("blank","英文品名5", "english_product_name_5",""),
    ("blank","单票数量5", "number_of_tickets_per_ticket_5",""),
    ("blank","重量5(g)","weight_five_gram",""),
    ("blank","目的国申报单价5","unit_price_declared_in_the_destination_country_5", ""),
    ("blank","出口国申报单价5","exporting_country_declared_unit_price_5", ""),
    ("blank","商品材质5","product_material_5", ""),
    ("blank","商品海关编码5","commodity_customs_code_5", ""),
    ("blank","商品链接5","product_link_5",""),
    ("blank","SKU5","sku5", ""),
]

SAFE_USERS = [
    "ae800292"
]

driver_pool = {}