from flask import Flask
import os
import re
import json

# ----------------------------
# 你的 AI pipeline 函数定义（可接受参数）
# ----------------------------
def run_ai_pipeline(target_saving=600):
    print(f"🎯 AI Pipeline 开始执行，目标节省：{target_saving}")
    # 👉 你实际的执行逻辑放在这里
    # 注意：确保各脚本执行后会生成 ai_outputs.json
    pass

# ----------------------------
# Flask app 创建函数（供 run.py 使用）
# ----------------------------
def create_app():
    app = Flask(__name__)
    from . import routes
    routes.init_routes(app)
    return app

# ✅ 关键：暴露 run_ai_pipeline 给 routes.py 调用
run_ai_pipeline = run_ai_pipeline