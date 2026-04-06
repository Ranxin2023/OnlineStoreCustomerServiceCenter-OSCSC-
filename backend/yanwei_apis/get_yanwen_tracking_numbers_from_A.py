import pandas as pd
import os


def get_yanwen_tracking_numbers_from_A():

    # 📂 Excel 路径（建议用绝对路径）
    BASE_DIR = os.path.dirname(os.path.abspath(__file__))

    file_path = os.path.join(BASE_DIR, "A记录test.xlsx")

    # 👉 读取 Excel
    df = pd.read_excel(file_path)

    # 🔥 关键：根据你的截图列结构
    # D列 = 物流公司
    # G列 = tracking number

    yanwen_df = df[df.iloc[:, 3] == "燕文"]   # 第4列（D）

    tracking_numbers = yanwen_df.iloc[:, 6]   # 第7列（G）

    # 👉 清洗数据
    result = [
        str(tn).strip()
        for tn in tracking_numbers
        if pd.notna(tn) and str(tn).strip() != ""
    ]

    # 👉 去重（很重要🔥）
    result = list(set(result))

    print(f"[YANWEN] from Excel total: {len(result)}")

    return result