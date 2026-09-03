import os
import io
import pandas as pd
from datetime import datetime
from flask import Flask, render_template, jsonify, send_file, request

base_dir = os.path.dirname(os.path.abspath(__file__))
app = Flask(__name__, template_folder=base_dir)

latest_metrics_data = []
COLLECTORS = {}

def calculate_ctr(clicks, views):
    if views and views > 0:
        return round((clicks / views) * 100, 2)
    return 0.0

@app.route("/")
def index():
    return render_template("index.html")

@app.route("/api/fetch/<platform_name>", methods=["GET"])
def fetch_single(platform_name):
    current_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    if platform_name in COLLECTORS:
        data = COLLECTORS[platform_name].fetch_metrics()
    else:
        clicks = 120
        views = 3400
        data = {
            "platform": platform_name.capitalize(),
            "post_id": f"{platform_name[:2]}_001",
            "title": f"模擬測試貼文 ({platform_name.capitalize()})",
            "views": views,
            "clicks": clicks,
            "ctr_%": calculate_ctr(clicks, views),
            "timestamp": current_time
        }
    return jsonify({"status": "success", "data": data})

@app.route("/api/fetch/all", methods=["GET"])
def fetch_all():
    platforms = ["instagram", "facebook", "tiktok", "x", "reddit", "threads", "youtube", "pinterest"]
    results = []
    current_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    
    for p in platforms:
        if p in COLLECTORS:
            data = COLLECTORS[p].fetch_metrics()
        else:
            clicks = 0
            views = 0
            data = {
                "platform": p.capitalize(),
                "post_id": f"{p[:2]}_001",
                "title": f"預設貼文 ({p.capitalize()})",
                "views": views,
                "clicks": clicks,
                "ctr_%": calculate_ctr(clicks, views),
                "timestamp": current_time
            }
        results.append(data)
            
    global latest_metrics_data
    latest_metrics_data = results
    return jsonify({"status": "success", "data": results})

@app.route("/api/export/csv", methods=["GET"])
def export_csv():
    global latest_metrics_data
    if not latest_metrics_data:
        fetch_all()

    df = pd.DataFrame(latest_metrics_data)
    
    # 映射欄位表頭為指定中文名稱
    headers_map = {
        "platform": "平台",
        "post_id": "內容 ID",
        "title": "標題 / 內文",
        "views": "觀看數",
        "clicks": "點擊數",
        "ctr_%": "點擊率 (%)",
        "timestamp": "更新時間"
    }
    
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
