from flask import send_file, jsonify, request
import os
import json
import traceback  # ✅ 新增用于调试输出
from ai import run_ai_pipeline

def init_routes(app):
    @app.route("/")
    def index():
        return send_file(os.path.join(os.getcwd(), "wwwroot", "index.html"))

    @app.route("/home")
    def home():
        return send_file(os.path.join(os.getcwd(), "wwwroot", "searching_page.html"))

    @app.route("/detail")
    def detail():
        return send_file(os.path.join(os.getcwd(), "wwwroot", "first_page.html"))

    @app.route("/detail2")
    def detail2():
        return send_file(os.path.join(os.getcwd(), "wwwroot", "last_page.html"))  # ❗修复了拼写错误（原来是 wwroot）

    # ✅ 上传 PDF 文件（不立即执行分析）
    @app.route("/api/bill_upload", methods=["POST"])
    def upload_pdf():
        if 'file' not in request.files:
            return {"error": "No file part"}, 400

        file = request.files['file']
        if file.filename == '':
            return {"error": "No selected file"}, 400
        if not file.filename.lower().endswith('.pdf'):
            return {"error": "Only PDF files are allowed"}, 400

        save_path = os.path.join(os.getcwd(), "uploads", file.filename)
        file.save(save_path)

        return {"status": "file uploaded, waiting for analysis"}

    # ✅ 分析主输出（AI pipeline 触发 + 返回分析核心结果）
    @app.route("/api/analysis_result", methods=["GET"])
    def get_analysis_result():
        try:
            target_saving = float(request.args.get("target_saving", 600))
        except ValueError:
            return {"error": "Invalid target_saving value"}, 400

        try:
            print("🟡 正在执行 run_ai_pipeline...")
            run_ai_pipeline(target_saving=target_saving)
            print("🟢 run_ai_pipeline 执行完成")
        except Exception as e:
            traceback.print_exc()
            return {"error": "Failed to run analysis", "detail": str(e)}, 500

        output_path = os.path.join(os.getcwd(), "ai_outputs.json")
        if not os.path.exists(output_path):
            return {"error": "Analysis result not found"}, 404

        try:
            with open(output_path, "r", encoding="utf-8") as f:
                data = json.load(f)

            result = {
                "left": {
                    "original_total": data.get("original_total"),
                    "adjusted_total": data.get("adjusted_total"),
                    "reduction_total": data.get("reduction_total")
                },
                "right": {
                    "top_categories": data.get("subcat_summary_top5"),
                    "saving_plan": data.get("reduction_plan")
                }
            }

            return jsonify(result)
        except Exception as e:
            traceback.print_exc()
            return {"error": "Failed to read result", "detail": str(e)}, 500

    # ✅ 分析附加结果（其余字段）
    @app.route("/api/analysis_extra", methods=["GET"])
    def get_analysis_extra():
        output_path = os.path.join(os.getcwd(), "ai_outputs.json")
        if not os.path.exists(output_path):
            return {"error": "Analysis result not found"}, 404

        try:
            with open(output_path, "r", encoding="utf-8") as f:
                data = json.load(f)

            excluded_keys = {
                "original_total",
                "adjusted_total",
                "reduction_total",
                "subcat_summary_top5",
                "reduction_plan"
            }

            extra_data = {k: v for k, v in data.items() if k not in excluded_keys}
            return jsonify(extra_data)

        except Exception as e:
            traceback.print_exc()
            return {"error": "Failed to read extra result", "detail": str(e)}, 500