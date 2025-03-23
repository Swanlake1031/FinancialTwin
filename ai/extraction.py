from google import genai
from google.genai import types
import base64
import os
import json
import csv

upload_dir = os.path.join(os.getcwd(), "uploads")
output_dir = os.path.join(os.getcwd(), "process")

# 自动构造 pdf -> csv 对应关系
pdf_paths = []
for idx, filename in enumerate(sorted(os.listdir(upload_dir))):
    if filename.lower().endswith(".pdf"):
        full_pdf_path = os.path.join(upload_dir, filename)
        output_csv_path = os.path.join(output_dir, f"training_data_{idx+1}.csv")
        pdf_paths.append((full_pdf_path, output_csv_path))

def extract_transactions_from_pdf(pdf_path, 
                                  csv_output_path):
    with open(pdf_path, 'rb') as f:
        pdf_bytes = f.read()

    client = genai.Client(
        vertexai=True,
        project="financial-twin",
        location="us-central1",
    )

    document_part = types.Part.from_bytes(
        data=pdf_bytes,
        mime_type="application/pdf",
    )

    system_instruction = """請判斷哪些是交易行，然後為所有支出withdraw，包括transfer, TFR, payment：- description：交易描述（不包含金額）- amount：金額（純數字，不含 $）請輸出 JSON 陣列格式，如：[ {{\"description\": \"TIM HORTONS #123\", \"amount\": \"3.84\"}}, {{\"description\": \"UBER TRIP 2424\", \"amount\": \"18.65\"}}]"""

    contents = [
        types.Content(
            role="user",
            parts=[
                document_part,
                types.Part.from_text(text="請不要漏掉任何一個withdrawals")
            ]
        )
    ]

    generate_content_config = types.GenerateContentConfig(
        temperature=1,
        top_p=0.95,
        max_output_tokens=8192,
        response_modalities=["TEXT"],
        safety_settings=[
            types.SafetySetting(category="HARM_CATEGORY_HATE_SPEECH", threshold="OFF"),
            types.SafetySetting(category="HARM_CATEGORY_DANGEROUS_CONTENT", threshold="OFF"),
            types.SafetySetting(category="HARM_CATEGORY_SEXUALLY_EXPLICIT", threshold="OFF"),
            types.SafetySetting(category="HARM_CATEGORY_HARASSMENT", threshold="OFF"),
        ],
        system_instruction=[types.Part.from_text(text=system_instruction)],
    )

    print(f"\n🧠 Gemini 正在處理 {os.path.basename(pdf_path)} ...\n")
    output_text = ""
    for chunk in client.models.generate_content_stream(
        model="gemini-2.0-flash-001",
        contents=contents,
        config=generate_content_config,
    ):
        print(chunk.text, end="")
        output_text += chunk.text

    try:
        start_idx = output_text.find("[")
        end_idx = output_text.rfind("]") + 1
        json_text = output_text[start_idx:end_idx]
        transactions = json.loads(json_text)

        with open(csv_output_path, "w", newline="") as csvfile:
            writer = csv.DictWriter(csvfile, fieldnames=["description", "amount"])
            writer.writeheader()
            writer.writerows(transactions)
        print(f"\n✅ 成功寫入 {len(transactions)} 筆交易到 {csv_output_path}\n")
    except Exception as e:
        print(f"\n⚠️ 轉換 CSV 時出錯: {e}\n")

if __name__ == "__main__":
    for pdf_path, output_csv in pdf_paths:
        extract_transactions_from_pdf(pdf_path, output_csv)
