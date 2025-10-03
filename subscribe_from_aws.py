"""
AWS IoT Core受信モジュール
AWS IoT CoreからのコマンドをMQTT経由で受信し、Flaskサーバーに転送する機能を提供
"""

import ssl
import json
import logging
import time
from typing import Dict, Any, Optional
from pathlib import Path
import paho.mqtt.client as mqtt
import requests
from requests.exceptions import RequestException

from config import (
    AWS_ENDPOINT, AWS_PORT, COMMAND_TOPIC,
    CA_PATH, CERT_PATH, KEY_PATH,
    MQTT_KEEPALIVE, FLASK_HOST, FLASK_PORT
)

# ログ設定
logger = logging.getLogger(__name__)


class AWSIoTSubscriber:
    """AWS IoT Core MQTTサブスクライバー"""
    
    def __init__(self):
        self.client: Optional[mqtt.Client] = None
        self.flask_url = f"http://{FLASK_HOST}:{FLASK_PORT}/update_status"
        self._validate_certificates()
    
    def _validate_certificates(self) -> None:
        """証明書ファイルの存在確認"""
        cert_files = [CA_PATH, CERT_PATH, KEY_PATH]
        for cert_file in cert_files:
            if not Path(cert_file).exists():
                raise FileNotFoundError(f"証明書ファイルが見つかりません: {cert_file}")
    
    def _on_connect(self, client: mqtt.Client, userdata: Any, flags: Dict, rc: int) -> None:
        """MQTT接続時のコールバック"""
        if rc == 0:
            logger.info("AWS IoT Coreに接続成功")
            client.subscribe(COMMAND_TOPIC)
            logger.info(f"トピック購読開始: {COMMAND_TOPIC}")
        else:
            logger.error(f"AWS IoT Core接続失敗: {rc}")
    
    def _on_disconnect(self, client: mqtt.Client, userdata: Any, rc: int) -> None:
        """MQTT切断時のコールバック"""
        if rc != 0:
            logger.warning(f"AWS IoT Core接続が予期せず切断されました: {rc}")
        else:
            logger.info("AWS IoT Coreから正常に切断されました")
    
    def _on_message(self, client: mqtt.Client, userdata: Any, msg: mqtt.MQTTMessage) -> None:
        """メッセージ受信時のコールバック"""
        try:
            payload = msg.payload.decode('utf-8')
            logger.info(f"コマンド受信: {msg.topic} -> {payload}")
            
            # JSONパース
            data = json.loads(payload)
            
            # ステータス更新コマンドの処理
            if "status" in data:
                self._forward_to_flask(data)
            else:
                logger.warning(f"ステータス情報が含まれていないメッセージ: {data}")
                
        except json.JSONDecodeError as e:
            logger.error(f"JSONパースエラー: {e}")
        except UnicodeDecodeError as e:
            logger.error(f"文字エンコードエラー: {e}")
        except Exception as e:
            logger.error(f"メッセージ処理エラー: {e}")
    
    def _forward_to_flask(self, data: Dict[str, Any]) -> None:
        """Flaskサーバーにデータを転送"""
        try:
            response = requests.post(
                self.flask_url, 
                json=data, 
                timeout=10,
                headers={'Content-Type': 'application/json'}
            )
            
            if response.status_code == 200:
                logger.info(f"Flaskサーバーへの転送成功: {response.status_code}")
            else:
                logger.error(f"Flaskサーバーへの転送失敗: {response.status_code}")
                
        except RequestException as e:
            logger.error(f"Flaskサーバーへの転送エラー: {e}")
        except Exception as e:
            logger.error(f"予期しないエラー: {e}")
    
    def start(self) -> None:
        """MQTTサブスクライバーを開始"""
        try:
            self.client = mqtt.Client()
            
            # SSL/TLS設定
            self.client.tls_set(
                ca_certs=CA_PATH,
                certfile=CERT_PATH,
                keyfile=KEY_PATH,
                tls_version=ssl.PROTOCOL_TLSv1_2
            )
            
            # コールバック設定
            self.client.on_connect = self._on_connect
            self.client.on_disconnect = self._on_disconnect
            self.client.on_message = self._on_message
            
            # 接続
            logger.info(f"AWS IoT Coreに接続中: {AWS_ENDPOINT}:{AWS_PORT}")
            result = self.client.connect(AWS_ENDPOINT, AWS_PORT, MQTT_KEEPALIVE)
            
            if result != mqtt.MQTT_ERR_SUCCESS:
                raise ConnectionError(f"MQTT接続失敗: {result}")
            
            # メッセージループ開始
            self.client.loop_start()
            logger.info("MQTTサブスクライバー開始")
            
        except Exception as e:
            logger.error(f"MQTTサブスクライバー開始エラー: {e}")
            raise
    
    def stop(self) -> None:
        """MQTTサブスクライバーを停止"""
        if self.client:
            self.client.loop_stop()
            self.client.disconnect()
            logger.info("MQTTサブスクライバー停止")


# グローバルインスタンス
_subscriber = AWSIoTSubscriber()


def main() -> None:
    """メイン関数 - MQTTサブスクライバーを開始"""
    try:
        _subscriber.start()
        
        # メインスレッドを維持
        while True:
            time.sleep(1)
            
    except KeyboardInterrupt:
        logger.info("キーボード割り込みを受信")
    except Exception as e:
        logger.error(f"予期しないエラー: {e}")
    finally:
        _subscriber.stop()
