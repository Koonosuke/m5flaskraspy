"""
M5Stack Core2 IoT Gateway Server
Flask WebサーバーとしてM5Stackデバイスからのデータを受信し、
AWS IoT Coreとの双方向通信を管理する
"""

import logging
import threading
from datetime import datetime, timedelta
from typing import Dict, Any, Optional
from flask import Flask, request, jsonify
from werkzeug.exceptions import BadRequest

from config import (
    FLASK_HOST, FLASK_PORT, FLASK_DEBUG, 
    TIMEZONE_OFFSET, LOG_LEVEL, LOG_FORMAT
)
from send_to_aws import send_to_aws
from subscribe_from_aws import main as mqtt_main

# ログ設定
logging.basicConfig(
    level=getattr(logging, LOG_LEVEL.upper()),
    format=LOG_FORMAT
)
logger = logging.getLogger(__name__)

# Flaskアプリケーション初期化
app = Flask(__name__)
app.config['JSON_AS_ASCII'] = False  # 日本語対応

# グローバルステータス管理
class StatusManager:
    """ステータス管理クラス"""
    
    def __init__(self):
        self._status = "UNKNOWN"
        self._lock = threading.Lock()
    
    @property
    def status(self) -> str:
        with self._lock:
            return self._status
    
    @status.setter
    def status(self, value: str) -> None:
        with self._lock:
            self._status = value
            logger.info(f"ステータス更新: {value}")

# グローバルステータスマネージャー
status_manager = StatusManager()


def add_timestamp(data: Dict[str, Any]) -> None:
    """データにJSTタイムスタンプを追加"""
    jst = datetime.utcnow() + timedelta(hours=TIMEZONE_OFFSET)
    data["timestamp"] = jst.isoformat()


@app.route("/data", methods=["POST"])
def receive_data() -> tuple:
    """
    M5Stack Core2からのセンサーデータを受信
    
    Returns:
        tuple: (response_data, status_code)
    """
    try:
        data = request.get_json()
        if not data:
            logger.warning("空のデータが送信されました")
            return jsonify({"error": "No data provided"}), 400
        
        if not isinstance(data, dict):
            logger.error(f"無効なデータ型: {type(data)}")
            return jsonify({"error": "Invalid data format"}), 400
        
        # タイムスタンプ追加
        add_timestamp(data)
        logger.info(f"センサーデータ受信: {data}")
        
        # ステータス更新
        if "status" in data:
            status_manager.status = data["status"]
        
        # AWS IoT Coreへ転送
        success = send_to_aws(data)
        if not success:
            logger.error("AWS IoT Coreへの送信に失敗しました")
            return jsonify({
                "error": "Failed to send data to AWS IoT Core",
                "data": data
            }), 500
        
        return jsonify({
            "status": "received",
            "data": data,
            "aws_sent": True
        }), 200
        
    except BadRequest:
        logger.error("リクエストの解析に失敗しました")
        return jsonify({"error": "Invalid JSON format"}), 400
    except Exception as e:
        logger.error(f"データ受信処理エラー: {e}")
        return jsonify({"error": "Internal server error"}), 500


@app.route("/status", methods=["GET"])
def get_status() -> tuple:
    """
    現在のステータスを取得
    
    Returns:
        tuple: (response_data, status_code)
    """
    try:
        return jsonify({
            "status": status_manager.status,
            "timestamp": datetime.utcnow().isoformat()
        }), 200
    except Exception as e:
        logger.error(f"ステータス取得エラー: {e}")
        return jsonify({"error": "Failed to get status"}), 500


@app.route("/update_status", methods=["POST"])
def update_status() -> tuple:
    """
    AWS IoT Coreからのコマンドでステータスを更新
    
    Returns:
        tuple: (response_data, status_code)
    """
    try:
        data = request.get_json()
        if not data:
            logger.warning("ステータス更新: データが提供されていません")
            return jsonify({"error": "No data provided"}), 400
        
        if "status" not in data:
            logger.warning(f"ステータス更新: ステータス情報が含まれていません: {data}")
            return jsonify({"error": "Missing status field"}), 400
        
        new_status = data["status"]
        status_manager.status = new_status
        logger.info(f"[MQTT] ステータス更新: {new_status}")
        
        return jsonify({
            "updated_status": new_status,
            "timestamp": datetime.utcnow().isoformat()
        }), 200
        
    except BadRequest:
        logger.error("ステータス更新: リクエストの解析に失敗しました")
        return jsonify({"error": "Invalid JSON format"}), 400
    except Exception as e:
        logger.error(f"ステータス更新エラー: {e}")
        return jsonify({"error": "Internal server error"}), 500


@app.route("/health", methods=["GET"])
def health_check() -> tuple:
    """
    ヘルスチェックエンドポイント
    
    Returns:
        tuple: (response_data, status_code)
    """
    return jsonify({
        "status": "healthy",
        "service": "M5Stack IoT Gateway",
        "timestamp": datetime.utcnow().isoformat()
    }), 200


@app.errorhandler(404)
def not_found(error) -> tuple:
    """404エラーハンドラー"""
    return jsonify({"error": "Endpoint not found"}), 404


@app.errorhandler(405)
def method_not_allowed(error) -> tuple:
    """405エラーハンドラー"""
    return jsonify({"error": "Method not allowed"}), 405


def start_mqtt_subscriber() -> None:
    """MQTTサブスクライバーをバックグラウンドで開始"""
    try:
        mqtt_thread = threading.Thread(target=mqtt_main, daemon=True)
        mqtt_thread.start()
        logger.info("MQTTサブスクライバーをバックグラウンドで開始しました")
    except Exception as e:
        logger.error(f"MQTTサブスクライバー開始エラー: {e}")


if __name__ == "__main__":
    try:
        logger.info("M5Stack IoT Gateway Server を開始しています...")
        
        # MQTTサブスクライバー開始
        start_mqtt_subscriber()
        
        # Flaskサーバー起動
        logger.info(f"Flaskサーバーを開始: {FLASK_HOST}:{FLASK_PORT}")
        app.run(
            host=FLASK_HOST,
            port=FLASK_PORT,
            debug=FLASK_DEBUG,
            threaded=True
        )
        
    except KeyboardInterrupt:
        logger.info("キーボード割り込みを受信しました")
    except Exception as e:
        logger.error(f"サーバー起動エラー: {e}")
    finally:
        logger.info("サーバーを終了しています...")
