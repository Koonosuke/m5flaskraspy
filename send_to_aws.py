"""
AWS IoT Core送信モジュール
センサーデータをMQTT経由でAWS IoT Coreに送信する機能を提供
"""

import json
import ssl
import logging
from typing import Dict, Any, Optional
from pathlib import Path
import paho.mqtt.client as mqtt
from paho.mqtt.client import MQTTMessage

from config import (
    AWS_ENDPOINT, AWS_PORT, SENSOR_TOPIC,
    CA_PATH, CERT_PATH, KEY_PATH,
    MQTT_KEEPALIVE, MQTT_QOS
)

# ログ設定
logger = logging.getLogger(__name__)


class AWSIoTClient:
    """AWS IoT Core MQTTクライアント"""
    
    def __init__(self):
        self.client: Optional[mqtt.Client] = None
        self._validate_certificates()
    
    def _validate_certificates(self) -> None:
        """証明書ファイルの存在確認"""
        cert_files = [CA_PATH, CERT_PATH, KEY_PATH]
        for cert_file in cert_files:
            if not Path(cert_file).exists():
                raise FileNotFoundError(f"証明書ファイルが見つかりません: {cert_file}")
    
    def _create_client(self) -> mqtt.Client:
        """MQTTクライアントを作成・設定"""
        client = mqtt.Client()
        
        try:
            client.tls_set(
                ca_certs=CA_PATH,
                certfile=CERT_PATH,
                keyfile=KEY_PATH,
                tls_version=ssl.PROTOCOL_TLSv1_2
            )
            logger.info("SSL/TLS設定完了")
        except Exception as e:
            logger.error(f"SSL/TLS設定エラー: {e}")
            raise
        
        return client
    
    def send_data(self, payload: Dict[str, Any]) -> bool:
        """
        データをAWS IoT Coreに送信
        
        Args:
            payload: 送信するデータ
            
        Returns:
            bool: 送信成功時True、失敗時False
        """
        try:
            self.client = self._create_client()
            
            # 接続
            result = self.client.connect(AWS_ENDPOINT, AWS_PORT, MQTT_KEEPALIVE)
            if result != mqtt.MQTT_ERR_SUCCESS:
                raise ConnectionError(f"MQTT接続失敗: {result}")
            
            self.client.loop_start()
            
            # データ送信
            payload_json = json.dumps(payload, ensure_ascii=False)
            logger.info(f"AWS IoT Coreに送信中: {payload_json}")
            
            result = self.client.publish(SENSOR_TOPIC, payload_json, qos=MQTT_QOS)
            if result.rc != mqtt.MQTT_ERR_SUCCESS:
                raise RuntimeError(f"データ送信失敗: {result.rc}")
            
            logger.info("AWS IoT Coreへの送信完了")
            return True
            
        except Exception as e:
            logger.error(f"AWS IoT Core送信エラー: {e}")
            return False
            
        finally:
            if self.client:
                self.client.loop_stop()
                self.client.disconnect()
                logger.debug("MQTTクライアント切断完了")


# グローバルインスタンス
_aws_client = AWSIoTClient()


def send_to_aws(payload: Dict[str, Any]) -> bool:
    """
    AWS IoT Coreにデータを送信する関数
    
    Args:
        payload: 送信するデータ辞書
        
    Returns:
        bool: 送信成功時True、失敗時False
    """
    if not isinstance(payload, dict):
        logger.error(f"無効なペイロード型: {type(payload)}")
        return False
    
    if not payload:
        logger.warning("空のペイロードが送信されました")
        return False
    
    return _aws_client.send_data(payload)
