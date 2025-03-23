import os
import re
import json

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
AI_DIR = os.path.join(ROOT, "ai")
OUT_PATH = os.path.join(ROOT, "ai_outputs.json")

EXEC_ORDER = [
    "extraction.py",
    "Gemini_Classification.py",
    "Merge.py",
    "Month.py",
    "Synthetic_data_combine.py",
    "baseline_Lstm.py"
]

def run_ai_pipeline(target_saving=600):
    outputs = {}

    for script in EXEC_ORDER:
        path = os.path.join(AI_DIR, script)
        namespace = {"__name__": "__main__"}

        # 對 baseline_Lstm 注入 target_saving
        if script == "baseline_Lstm.py":
            namespace["target_saving"] = target_saving

        with open(path, "r", encoding="utf-8") as f:
            code = f.read()

        try:
            exec(code, namespace)
        except Exception as e:
            print(f"❌ Error in {script}: {e}")
            continue

        if script == "baseline_Lstm.py":
            try:
                # 提取所需結果
                summary = namespace["subcat_summary"].head(5).to_dict()
                plan = namespace["reduction_plan"]
                original_total = float(namespace["original_total"])
                adjusted_total = float(namespace["adjusted_total"])
                diff = round(original_total - adjusted_total, 2)

                # amount/output_len 與 subcat 綁定輸出
                output_len = int(namespace.get("output_len", 6))
                combo_list = []
                for subcat, amount in plan:
                    combo_list.append({
                        "subcat": subcat,
                        "avg_per_month": round(amount / output_len, 2)
                    })

                outputs["subcat_summary_top5"] = summary
                outputs["reduction_plan"] = plan
                outputs["original_total"] = round(original_total, 2)
                outputs["adjusted_total"] = round(adjusted_total, 2)
                outputs["reduction_total"] = diff
                outputs["avg_monthly_saving_plan"] = combo_list

            except Exception as e:
                outputs["baseline_Lstm_error"] = str(e)

    # 輸出 JSON
    with open(OUT_PATH, "w", encoding="utf-8") as f:
        json.dump(outputs, f, ensure_ascii=False, indent=2)

    print("✅ AI分析完成，已輸出到 ai_outputs.json")