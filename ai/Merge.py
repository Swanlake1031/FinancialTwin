# ✅ merge.py（終極穩定版 with BASE_DIR）
import os
import sys
import csv

# ✅ 最穩定取得根目錄 demo1 2
try:
    CURRENT_FILE = __file__
except NameError:
    CURRENT_FILE = sys.argv[0]

BASE_DIR = os.path.abspath(os.path.join(os.path.dirname(CURRENT_FILE), ".."))

# 👉 定義每個 training_data 檔案與對應月份
training_files = [
    (os.path.join(BASE_DIR, "process", "training_data_1.csv"), "October"),
    (os.path.join(BASE_DIR, "process", "training_data_2.csv"), "November"),
    (os.path.join(BASE_DIR, "process", "training_data_3.csv"), "December"),
]

# 👉 讀取所有分類結果（合併後的 mapping）
mapping_path = os.path.join(BASE_DIR, "ai", "description_category_mapping.csv")
if not os.path.exists(mapping_path):
    print(f"❌ 找不到 mapping 檔案：{mapping_path}")
    exit(1)


with open(mapping_path, newline='') as f:
    reader = csv.DictReader(f)
    all_classified = list(reader)

# 👉 初始化變數
classified_all = []
training_all = []
month_all = []

# 👉 根據每份 training_data 的長度，依序對應分類結果
cursor = 0
for training_path, month_label in training_files:
    if not os.path.exists(training_path):
        print(f"❌ 找不到 training data：{training_path}")
        exit(1)

    with open(training_path, newline='') as f:
        reader = csv.DictReader(f)
        data = list(reader)
        training_all.extend(data)
        batch_len = len(data)

        # 對應 mapping 中相同數量筆數
        classified_batch = all_classified[cursor:cursor + batch_len]
        classified_all.extend(classified_batch)
        month_all.extend([month_label] * batch_len)
        cursor += batch_len

# 👉 檢查筆數是否一致
if len(classified_all) != len(training_all):
    print(f"❌ 筆數不一致：分類結果 {len(classified_all)} 筆，training_data 共 {len(training_all)} 筆")
    exit(1)

# 👉 合併金額與月份欄位
for i in range(len(classified_all)):
    classified_all[i]["amount"] = training_all[i].get("amount", "")
    classified_all[i]["month"] = month_all[i]

# 👉 輸出合併結果
output_file = os.path.join(BASE_DIR, "process", "final_output.csv")
with open(output_file, "w", newline='') as f:
    fieldnames = ["description", "main_category", "sub_category", "amount", "month"]
    writer = csv.DictWriter(f, fieldnames=fieldnames)
    writer.writeheader()
    for row in classified_all:
        writer.writerow(row)

print(f"✅ 成功合併 {len(classified_all)} 筆交易，已儲存到 {output_file}")
