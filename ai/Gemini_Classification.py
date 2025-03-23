import pandas as pd
from google import genai
from google.genai import types
import json
import re
import time

def generate():
    client = genai.Client(
        vertexai=True,
        project="financial-twin",
        location="us-central1",
    )

    # ⬇️ 支援多個 training_data_x.csv
    training_files = [
        "process/training_data_1.csv",
        "process/training_data_2.csv",
        "process/training_data_3.csv",
    ]

    all_results = []

    for file_idx, path in enumerate(training_files):
        print(f"\n📂 正在處理：{path}")
        try:
            df = pd.read_csv(path)
            df = df.dropna(subset=["description"])
            descriptions = df["description"].tolist()
        except Exception as e:
            print(f"⚠️ 無法讀取 {path}：{e}")
            continue

        system_instruction = """
🔮 Gemini 提示模板：

你是一個財務交易分類助手。請依據每筆交易的「描述」，將其分類為以下主分類與子分類。

請從下列選項中選擇：

主分類選項：
- Food
- Groceries
- Transport
- Bills
- Rent
- Entertainment
- Other

子分類選項：
- Coffee/Beverage
- Alcohol/SLIQUOR/LCBO
- Restaurant
- Takeout
- Groceries
- Life Style (E.g Barbershop)
- Home Supplies
- Ride Share
- Gas
- Utilities
- Rent
- Mortgage
- Physical Activity
- Other Entertainment
- Subscription
- Transfer
- Pet Stuff
- Unknown

請輸出一個 JSON 陣列，每筆交易包含以下欄位：
- description
- main_category
- sub_category

請注意：
- 每一行代表一筆交易，請不要拆開或合併。
- 僅根據提供的描述分類，勿增加額外筆數。
"""

        batch_size = 30
        for i in range(0, len(descriptions), batch_size):
            batch = descriptions[i:i + batch_size]
            indexed_batch = [f"{j+1}. {desc}" for j, desc in enumerate(batch)]
            joined = "\n".join(indexed_batch)

            contents = [
                types.Content(role="user", parts=[types.Part.from_text(text=joined)])
            ]

            config = types.GenerateContentConfig(
                temperature=0.4,
                max_output_tokens=4096,
                system_instruction=[types.Part.from_text(text=system_instruction)],
            )

            success = False
            for attempt in range(10):
                try:
                    response = client.models.generate_content(
                        model="gemini-2.0-flash-001",
                        contents=contents,
                        config=config,
                    )
                    cleaned = re.sub(r"^```json|```$", "", response.text.strip()).strip()
                    parsed = json.loads(cleaned)
                    all_results.extend(parsed)
                    print(f"✅ 第 {i // batch_size + 1} 批完成，共 {len(parsed)} 筆")
                    success = True
                    break
                except Exception as e:
                    print(f"⚠️ 第 {i // batch_size + 1} 批第 {attempt+1} 次失敗：{e}")
                    time.sleep(2)

            if not success:
                print("❌ 無法處理該批次")

            time.sleep(3)

    # 最後儲存結果
    if all_results:
        output_df = pd.DataFrame(all_results)
        output_df.to_csv("demo1 2/ai/description_category_mapping.csv", index=False)
        print(f"\n🎉 全部分類完成，共 {len(all_results)} 筆，已儲存為 ai/description_category_mapping.csv")
    else:
        print("⚠️ 沒有成功分類的資料產生")

generate()
