# subscribe_from_aws.py
import ssl
import json
import paho.mqtt.client as mqtt
import requests

# AWS IoT Core情報
AWS_ENDPOINT = "ayhwynhqtsmv-ats.iot.us-west-2.amazonaws.com"
TOPIC = "cmd/change/field/1/m5-thing"  # ← 受信対象トピック

# 証明書
CA_PATH = "./certs/AmazonRootCA1.pem"
CERT_PATH = "./certs/device-cert.pem.crt"
KEY_PATH = "./certs/private-key.pem.key"

# Flaskの/status更新API（Flaskサーバーが同一RaspiならlocalhostでOK）
FLASK_URL = "http://localhost:5000/update_status"

# MQTT受信時の処理
def on_message(client, userdata, msg):
    try:
        payload = msg.payload.decode()
        print(f"受信: {msg.topic} -> {payload}")
        data = json.loads(payload)
        if "status" in data:
            # Flaskサーバーに状態を伝える
            res = requests.post(FLASK_URL, json=data)
            print(f"Flaskに転送: {res.status_code}")
    except Exception as e:
        print(f"受信処理エラー: {e}")

def main():
    client = mqtt.Client()
    client.tls_set(
        ca_certs=CA_PATH,
        certfile=CERT_PATH,
        keyfile=KEY_PATH,
        tls_version=ssl.PROTOCOL_TLSv1_2,
    )
    client.on_message = on_message
    client.connect(AWS_ENDPOINT, 8883, 60)
    client.subscribe(TOPIC)
    print(f"Subscribed to: {TOPIC}")
    client.loop_forever()

if __name__ == "__main__":
    main()
