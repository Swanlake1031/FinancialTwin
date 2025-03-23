# ✅ Synthetic_data_combine.py（終極穩定版 with BASE_DIR + 檔案檢查）
import os
import pandas as pd
import random
import sys

#  專案根目錄
try:
    CURRENT_FILE = __file__
except NameError:
    CURRENT_FILE = sys.argv[0]

BASE_DIR = os.path.abspath(os.path.join(os.path.dirname(CURRENT_FILE), ".."))
process_dir = os.path.join(BASE_DIR, "process")

real_path = os.path.join(process_dir, "monthly_aggregated_by_category.csv")
if not os.path.exists(real_path):
    print(f"❌ 找不到真實資料檔案：{real_path}")
    sys.exit(1)

real_df = pd.read_csv(real_path)

mean_by_category = (
    real_df.groupby(["main_category", "sub_category"])["amount"]
    .mean()
    .reset_index()
)

months = ["January", "February", "March", "April", "May", "June",
          "July", "August", "September", "October", "November", "December"]

rows = []
for month in months:
    for _, row in mean_by_category.iterrows():
        main = row["main_category"]
        sub = row["sub_category"]
        mean_amt = row["amount"]
        synthetic_amt = round(random.uniform(0.8, 1.2) * mean_amt, 2)
        rows.append({
            "month": month,
            "main_category": main,
            "sub_category": sub,
            "amount": synthetic_amt
        })

# ➤ 儲存合成資料
synth_path = os.path.join(process_dir, "synthetic_yearly_spending.csv")
df_synth = pd.DataFrame(rows)
df_synth.to_csv(synth_path, index=False)
print(f"✅ 基於真實分佈的虛擬資料已產出：{synth_path}")

# ➤ 載入真實與合成資料
df_real = pd.read_csv(real_path)  # 真實的 Oct–Dec
df_synth = pd.read_csv(synth_path)  # 合成_
