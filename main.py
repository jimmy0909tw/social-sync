import os
import io
import pandas as pd
from datetime import datetime
from typing import List, Dict, Any
from flask import Flask, render_template, jsonify, send_file, request

base_dir = os.path.dirname(os.path.abspath(__file__))
app = Flask(__name__, template_folder=base_dir)

latest_metrics_data: List[Dict[str, Any]] = []
COLLECTORS: Dict[str, Any] = {}

def calculate_ctr(clicks: int, views: int) -> float:
    """計算點擊率 (%)，保留兩位小數"""
    if views and views > 0:
        return round((clicks / views) * 100, 2)
    return 0.0

@app.route("/")
def index():
    return render_template("index.html")

@app.route("/api/fetch/all", methods=["GET"])
def fetch_all():
    global latest_metrics_data
    results = []
    current_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    # 模擬 8 個平台的測試貼文資料，結構符合新版 headers 要求
    mock_platforms = [
        {"platform": "YouTube", "post_id": "yt_001", "title": "【教學】Python 自動化社群儀表板專案實作", "views": 12500, "clicks": 850},
        {"platform": "Instagram", "post_id": "ig_102", "title": "社群數據追蹤術！一張圖看懂關鍵指標", "views": 8400, "clicks": 420},
        {"platform": "Facebook", "post_id": "fb_305", "title": "【最新消息】我們的跨平台數據監控系統上線囉！", "views": 5600, "clicks": 210},
        {"platform": "TikTok", "post_id": "tk_881", "title": "15秒帶你看懂行銷自動化！ #python #dashbaord", "views": 32000, "clicks": 1100},
        {"platform": "X (Twitter)", "post_id": "tw_904", "title": "Building a modular social dashboard with Python & Firebase. 🚀", "views": 4100, "clicks": 180},
        {"platform": "Reddit", "post_id": "rd_512", "title": "[Showoff Sunday] Open source social analytics dashboard", "views": 2900, "clicks": 310},
        {"platform": "Threads", "post_id": "th_201", "title": "大家平常都是怎麼追蹤各社群平台點擊數據的？", "views": 1800, "clicks": 95},
        {"platform": "Pinterest", "post_id": "pin_603", "title": "Social Media Dashboard UI Architecture Blueprint", "views": 3100, "clicks": 140}
    ]

    for item in mock_platforms:
        # 若未來已註冊真實 Collector 則從 API 抓取，否則預設使用模擬資料
        p_name = item["platform"].lower()
        if p_name in COLLECTORS:
            data = COLLECTORS[p_name].fetch_metrics()
        else:
            data = item

        # 計算點擊率並補上更新時間
        views = data.get("views", 0)
        clicks = data.get("clicks", 0)
        data["ctr_%"] = calculate_ctr(clicks, views)
        data["timestamp"] = current_time
        
        results.append(data)

    latest_metrics_data = results
    return jsonify({"status": "success", "data": results})

@app.route("/api/export/csv", methods=["GET"])
def export_csv():
    global latest_metrics_data
    if not latest_metrics_data:
        fetch_all()

    df = pd.DataFrame(latest_metrics_data)
    
    # 重新整理欄位順序並重新命名 CSV 標頭
    headers_map = {
        "platform": "平台",
        "post_id": "內容 ID",
        "title": "標題 / 內文",
        "views": "觀看數",
        "clicks": "點擊數",
        "ctr_%": "點擊率 (%)",
        "timestamp": "更新時間"
    }
    
    # 確保導出的 CSV 遵循此欄位順序
    df = df.reindex(columns=list(headers_map.keys()))
    df.rename(columns=headers_map, inplace=True)

    output = io.BytesIO()
    df.to_csv(output, index=False, encoding="utf-8-sig")
    output.seek(0)

    return send_file(
        output,
        mimetype="text/csv",
        as_attachment=True,
        download_name="social_media_metrics.csv"
    )

if __name__ == "__main__":
    app.run(debug=True, port=5000)
