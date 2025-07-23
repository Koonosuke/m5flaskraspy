# subscribe_from_aws.py
import ssl
import json
import paho.mqtt.client as mqtt
import requests

AWS_ENDPOINT = "ayhwynhqtsmv-ats.iot.us-west-2.amazonaws.com"
TOPIC = "cmd/change/field/1/m5-thing"

CA_PATH = "/home/kishi/m5flask/m5flaskraspy/certs/AmazonRootCA1.pem"
CERT_PATH = "/home/kishi/m5flask/m5flaskraspy/certs/device-cert.pem.crt"
KEY_PATH = "/home/kishi/m5flask/m5flaskraspy/certs/private-key.pem.key"

FLASK_URL = "http://localhost:5000/update_status"

client = mqtt.Client()

def on_message(client, userdata, msg):
    try:
        payload = msg.payload.decode()
        print(f"受信: {msg.topic} -> {payload}")
        data = json.loads(payload)
        if "status" in data:
            res = requests.post(FLASK_URL, json=data)
            print(f"Flaskに転送: {res.status_code}")
    except Exception as e:
        print(f"受信処理エラー: {e}")

def main():
    client.tls_set(
        ca_certs=CA_PATH,
        certfile=CERT_PATH,
        keyfile=KEY_PATH,
        tls_version=ssl.PROTOCOL_TLSv1_2,
    )
    client.on_message = on_message
    client.connect(AWS_ENDPOINT, 8883, 60)
    client.subscribe(TOPIC)
    client.loop_start()  # ← ここが重要！（threadingと相性◎）
