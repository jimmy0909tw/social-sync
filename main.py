import os
import io
import pandas as pd
from flask import Flask, render_template, jsonify, send_file, request

# 初始化 Flask App
app = Flask(__name__)

# 模擬存放目前抓取到的最新數據
latest_metrics_data = []

# --- 平台調度器 (模組載入區) ---
# 後續將在 collectors/ 內實作具體平台後匯入
# 目前先建立可延伸的邏輯架構
COLLECTORS = {}

def get_all_metrics():
    """向所有已連接的平台抓取數據"""
    global latest_metrics_data
    results = []
    
    for name, collector in COLLECTORS.items():
        try:
            data = collector.fetch_metrics()
            results.append(data)
        except Exception as e:
            results.append({
                "platform": name,
                "status": "Error",
                "clicks": 0,
                "views": 0,
                "engagement": 0,
                "error_message": str(e)
            })
            
    latest_metrics_data = results
    return results

# --- 路由 API ---

@app.route("/")
def index():
    """渲染主頁面"""
    return render_template("index.html")

@app.route("/api/fetch/<platform_name>", methods=["GET"])
def fetch_single(platform_name):
    """單獨抓取指定平台的數據"""
    if platform_name in COLLECTORS:
        data = COLLECTORS[platform_name].fetch_metrics()
        return jsonify({"status": "success", "data": data})
    else:
        # Mock Data 用於介面測試 (當平台尚未接入時)
        mock_data = {
            "platform": platform_name.capitalize(),
            "clicks": 120,
            "views": 3400,
            "points_engagement": 85,
            "status": "Connected (Mock)"
        }
        return jsonify({"status": "success", "data": mock_data})

@app.route("/api/fetch/all", methods=["GET"])
def fetch_all():
    """抓取所有平台的數據"""
    # 當前若無真實 collector，給予預設測試列表
    platforms = ["instagram", "facebook", "tiktok", "x", "reddit", "threads", "youtube", "pinterest"]
    results = []
    
    for p in platforms:
        if p in COLLECTORS:
            results.append(COLLECTORS[p].fetch_metrics())
        else:
            results.append({
                "platform": p.capitalize(),
                "clicks": 0,
                "views": 0,
                "points_engagement": 0,
                "status": "Pending Setup"
            })
            
    global latest_metrics_data
    latest_metrics_data = results
    return jsonify({"status": "success", "data": results})

@app.route("/api/export/csv", methods=["GET"])
def export_csv():
    """將目前的數據轉換並匯出成 CSV 檔案"""
    global latest_metrics_data
    if not latest_metrics_data:
        # 如果尚未抓取，先執行一次全抓取
        fetch_all()

    # 使用 Pandas 轉換成 CSV
    df = pd.DataFrame(latest_metrics_data)
    
    # 建立記憶體內的 Buffer 檔案供下載
    output = io.BytesIO()
    df.to_csv(output, index=False, encoding="utf-8-sig") # utf-8-sig 防止 Excel 開啟亂碼
    output.seek(0)

    return send_file(
        output,
        mimetype="text/csv",
        as_attachment=True,
        download_name="social_media_metrics.csv"
    )

if __name__ == "__main__":
    app.run(debug=True, port=5000)
