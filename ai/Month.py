# ✅ month.py（終極穩定版 with BASE_DIR + 檔案檢查）
import pandas as pd
import os
import sys

# 設定根目錄路徑（指向 DEMO1 2 專案）
try:
    CURRENT_FILE = __file__
except NameError:
    CURRENT_FILE = sys.argv[0]

BASE_DIR = os.path.abspath(os.path.join(os.path.dirname(CURRENT_FILE), ".."))

input_file = os.path.join(BASE_DIR, "process", "final_output.csv")

if not os.path.exists(input_file):
    print(f"❌ 找不到輸入檔案：{input_file}")
    sys.exit(1)


df = pd.read_csv(input_file)

df["amount"] = pd.to_numeric(df["amount"], errors="coerce")

filtered_df = df[~((df['main_category'] == 'Bills') & (df['sub_category'] == 'Utilities') & (df['amount'] > 5000))]

monthly_by_category = (
    filtered_df.groupby(["month", "main_category", "sub_category"])["amount"]
    .sum()
    .reset_index()
    .sort_values(by=["month", "main_category", "sub_category"])
)

monthly_total = (
    filtered_df.groupby("month")["amount"]
    .sum()
    .reset_index()
    .rename(columns={"amount": "total_spending"})
)

output_category = os.path.join(BASE_DIR, "process", "monthly_aggregated_by_category.csv")
output_total = os.path.join(BASE_DIR, "process", "monthly_total_summary.csv")

monthly_by_category.to_csv(output_category, index=False)
monthly_total.to_csv(output_total, index=False)

print("✅ 已輸出：每月類別彙總 ➝ process/monthly_aggregated_by_category.csv")
print("✅ 已輸出：每月總支出 ➝ process/monthly_total_summary.csv")
