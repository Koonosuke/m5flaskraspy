from flask import Flask, request, jsonify
from datetime import datetime, timedelta

app = Flask(__name__)

@app.route("/data", methods=["POST"])
def receive_data():
    data = request.get_json()
    if not data:
        return "No data", 400

    # 日本時間（JST）を追加
    jst = datetime.utcnow() + timedelta(hours=9)
    data["timestamp"] = jst.isoformat()

    # ログ出力
    print(f"受信データ: {data}")

    return jsonify({"status": "received", "data": data}), 200

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
