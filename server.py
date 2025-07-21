from flask import Flask, request, jsonify
from datetime import datetime, timedelta
from send_to_aws import send_to_aws  # ← 追加！

app = Flask(__name__)

@app.route("/data", methods=["POST"])
def receive_data():
    data = request.get_json()
    if not data:
        return "No data", 400

    # JST（日本時間）でタイムスタンプを追加
    jst = datetime.utcnow() + timedelta(hours=9)
    data["timestamp"] = jst.isoformat()

    print(f"受信データ: {data}")

    # AWS IoT Coreに送信！
    send_to_aws(data)  # ← 追加！

    return jsonify({"status": "received", "data": data}), 200

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
