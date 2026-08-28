import os
import io
import pandas as pd
from flask import Flask, render_template, jsonify, send_file, request

# ---- 修正重點：將 template_folder 指向當前 main.py 所在的同層目錄 ----
base_dir = os.path.dirname(os.path.abspath(__file__))
app = Flask(__name__, template_folder=base_dir)
# -----------------------------------------------------------------

latest_metrics_data = []
COLLECTORS = {}

@app.route("/")
def index():
    return render_template("index.html")

@app.route("/api/fetch/<platform_name>", methods=["GET"])
def fetch_single(platform_name):
    if platform_name in COLLECTORS:
        data = COLLECTORS[platform_name].fetch_metrics()
        return jsonify({"status": "success", "data": data})
    else:
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
    global latest_metrics_data
    if not latest_metrics_data:
        fetch_all()

    df = pd.DataFrame(latest_metrics_data)
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
