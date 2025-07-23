from flask import Flask, request, jsonify
from datetime import datetime, timedelta
from send_to_aws import send_to_aws
from subscribe_from_aws import main as mqtt_main  # MQTT受信用
import threading

app = Flask(__name__)

# グローバルステータス
current_status = "UNKNOWN"

@app.route("/data", methods=["POST"])
def receive_data():
    global current_status
    data = request.get_json()
    if not data:
        return "No data", 400

    # JST（日本時間）でタイムスタンプを追加
    jst = datetime.utcnow() + timedelta(hours=9)
    data["timestamp"] = jst.isoformat()

    print(f"受信データ: {data}")

    # 状態を更新（必要なら）
    if "status" in data:
        current_status = data["status"]
        print(f"状態を更新: {current_status}")

    # AWS IoT Coreへ転送
    send_to_aws(data)

    return jsonify({"status": "received", "data": data}), 200

@app.route("/status", methods=["GET"])
def get_status():
    return jsonify({"status": current_status}), 200

@app.route("/update_status", methods=["POST"])
def update_status():
    global current_status
    data = request.get_json()
    if not data or "status" not in data:
        return jsonify({"error": "Missing status"}), 400

    current_status = data["status"]
    print(f"[MQTT] ステータス更新: {current_status}")
    return jsonify({"updated_status": current_status}), 200

if __name__ == "__main__":
    # MQTT Subscribeをバックグラウンドで起動
    threading.Thread(target=mqtt_main, daemon=True).start()
    
    # Flask起動
    app.run(host="0.0.0.0", port=5000)
