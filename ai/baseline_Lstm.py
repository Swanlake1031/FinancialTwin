# ✅ baseline_Lstm.py（加路徑與檔案檢查）
import os
import sys
import pandas as pd
import numpy as np
import tensorflow as tf
from tensorflow.keras.models import Model
from tensorflow.keras.layers import Input, LSTM, Dense, Dropout, LayerNormalization, RepeatVector, TimeDistributed, Attention, Lambda
from sklearn.preprocessing import MinMaxScaler
import matplotlib.pyplot as plt

try:
    CURRENT_FILE = __file__
except NameError:
    CURRENT_FILE = sys.argv[0]

BASE_DIR = os.path.abspath(os.path.join(os.path.dirname(CURRENT_FILE), ".."))

# === 步驟 1：載入資料 ===
data_path = os.path.join(BASE_DIR, "process", "combined_monthly_by_category.csv")
if not os.path.exists(data_path):
    print(f"\u274c 找不到輸入資料：{data_path}")
    sys.exit(1)


df = pd.read_csv(data_path)  

df["amount"] = pd.to_numeric(df["amount"], errors="coerce")
df = df.dropna(subset=["amount"])

data = df.pivot_table(index="month", columns="sub_category", values="amount", aggfunc="sum", fill_value=0)
data = data.sort_index(key=lambda x: pd.to_datetime(x, format='%B'))

scaler = MinMaxScaler()
data_scaled = scaler.fit_transform(data)

X, y = [], []
input_len = 6   
output_len = 6  # 預測未來 6 個月

if len(data_scaled.shape) < 2:
    raise ValueError("資料維度不足，請檢查 pivot table 是否正確生成")

n_features = data_scaled.shape[1]

for i in range(len(data_scaled) - input_len - output_len + 1):
    X.append(data_scaled[i:i+input_len])
    y.append(data_scaled[i+input_len:i+input_len+output_len])

X, y = np.array(X), np.array(y)

if X.shape[0] == 0:
    raise ValueError("❌ 無法產生訓練樣本，請確認資料量是否足夠與 input/output 長度是否合理")

inputs = Input(shape=(input_len, n_features))
x = LayerNormalization()(inputs)
x = LSTM(128, return_sequences=True)(x)
x = Dropout(0.3)(x)
x = LSTM(64, return_sequences=True)(x)
x = Dropout(0.3)(x)

# Attention Layer 包裝成 Lambda 層
def mean_attention(tensors):
    attention = Attention()([tensors, tensors])
    return tf.reduce_mean(attention, axis=1)

context = Lambda(mean_attention)(x)

x = RepeatVector(output_len)(context)
x = LSTM(64, return_sequences=True)(x)
x = Dropout(0.3)(x)
out = TimeDistributed(Dense(n_features))(x)

model = Model(inputs, out)
model.compile(optimizer='adam', loss='mse')
model.summary()

if X.shape[0] > 1:
    history = model.fit(
        X, y,
        epochs=150,
        batch_size=4,
        validation_split=0.2,
        verbose=1
    )
else:
    history = model.fit(
        X, y,
        epochs=150,
        batch_size=1,
        verbose=1
    )

pred = model.predict(X[-1:])  # 用最後一筆作預測
pred_unscaled = scaler.inverse_transform(pred[0])

# 建立月份欄位
month_order = list(pd.date_range("2025-01-01", periods=output_len, freq='MS').strftime('%B'))
pred_df = pd.DataFrame(pred_unscaled, columns=data.columns)
pred_df.insert(0, "month", month_order)

output_path = os.path.join(BASE_DIR, "ai", "lstm_predicted_next_6_months.csv")
pred_df.to_csv(output_path, index=False)
print(f"✅ 預測完成，已儲存至 {output_path}")

subcat_summary = pred_df.drop(columns=["month"]).sum().sort_values(ascending=False)
print("🔍 未來 6 個月預測支出（前幾名）:")
print(subcat_summary.head(5))

target_saving = 600
reduction_plan = (subcat_summary.head(5) / subcat_summary.head(5).sum()) * target_saving
print("\n💡 建議節省金額：")
print(reduction_plan)

adjusted_pred = pred_df.copy()
for subcat, reduce_amount in reduction_plan.items():
    monthly_reduce = reduce_amount / output_len
    adjusted_pred[subcat] = adjusted_pred[subcat] - monthly_reduce
    adjusted_pred[subcat] = adjusted_pred[subcat].clip(lower=0)

original_total = pred_df.drop(columns="month").sum().sum()
adjusted_total = adjusted_pred.drop(columns="month").sum().sum()

print(f"\n📉 原始總支出：${original_total:.2f}")
print(f"✅ 節省後支出：${adjusted_total:.2f}")
print(f"✅ 總共可節省：${original_total - adjusted_total:.2f}")

# 節省建議輸出
print("\n📋 消費建議：")
for subcat, amount in reduction_plan.items():
    print(f"🔻 每月減少 {subcat}：${amount/output_len:.2f}")
