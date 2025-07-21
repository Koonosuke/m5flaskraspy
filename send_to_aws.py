# send_to_aws.py

import json
import ssl
import paho.mqtt.client as mqtt

# ====== AWS IoT Core 接続情報 ======
AWS_ENDPOINT = "ayhwynhqtsmv-ats.iot.us-west-2.amazonaws.com"  # ← ここを実際のエンドポイントに置き換えてください
TOPIC = "iot/m5core2/sensor"

# ====== 証明書ファイルのパス（フルパス） ======
CA_PATH = "/m5flask/m5flaskraspy/certs/AmazonRootCA1.pem"
CERT_PATH = "/m5flask/m5flaskraspy/certs/device-cert.pem.crt"  # 例：リネーム後のデバイス証明書
KEY_PATH = "/m5flask/m5flaskraspy/certs/private-key.pem.key"   # 例：リネーム後の秘密鍵
    

# ====== 送信関数 ======
def send_to_aws(payload: dict):
    try:
        client = mqtt.Client()
        client.tls_set(
            ca_certs=CA_PATH,
            certfile=CERT_PATH,
            keyfile=KEY_PATH,
            tls_version=ssl.PROTOCOL_TLSv1_2
        )

        client.connect(AWS_ENDPOINT, 8883, 60)
        client.loop_start()

        payload_json = json.dumps(payload)
        print(f"Sending to AWS IoT: {payload_json}")
        client.publish(TOPIC, payload_json, qos=1)

        client.loop_stop()
        client.disconnect()
        print("Successfully sent to AWS IoT Core")

    except Exception as e:
        print(f"Failed to send to AWS IoT Core: {e}")
