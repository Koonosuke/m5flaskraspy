"""
設定ファイル
AWS IoT Core接続情報とアプリケーション設定を管理
"""
import os
from pathlib import Path

# AWS IoT Core設定
AWS_ENDPOINT = os.getenv("AWS_IOT_ENDPOINT", "ayhwynhqtsmv-ats.iot.us-west-2.amazonaws.com")
AWS_PORT = int(os.getenv("AWS_IOT_PORT", "8883"))

# MQTT トピック設定
SENSOR_TOPIC = os.getenv("SENSOR_TOPIC", "iot/m5core2/sensor")
COMMAND_TOPIC = os.getenv("COMMAND_TOPIC", "cmd/change/field/1/m5-thing")

# 証明書ファイルパス
BASE_DIR = Path(__file__).parent
CERTS_DIR = BASE_DIR / "certs"

CA_PATH = os.getenv("CA_PATH", str(CERTS_DIR / "AmazonRootCA1.pem"))
CERT_PATH = os.getenv("CERT_PATH", str(CERTS_DIR / "device-cert.pem.crt"))
KEY_PATH = os.getenv("KEY_PATH", str(CERTS_DIR / "private-key.pem.key"))

# Flask設定
FLASK_HOST = os.getenv("FLASK_HOST", "0.0.0.0")
FLASK_PORT = int(os.getenv("FLASK_PORT", "5000"))
FLASK_DEBUG = os.getenv("FLASK_DEBUG", "False").lower() == "true"

# ログ設定
LOG_LEVEL = os.getenv("LOG_LEVEL", "INFO")
LOG_FORMAT = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"

# MQTT設定
MQTT_KEEPALIVE = int(os.getenv("MQTT_KEEPALIVE", "60"))
MQTT_QOS = int(os.getenv("MQTT_QOS", "1"))

# タイムゾーン設定
TIMEZONE_OFFSET = int(os.getenv("TIMEZONE_OFFSET", "9"))  # JST = UTC+9
