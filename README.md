# M5Stack Core2 IoT Gateway System

M5Stack Core2デバイスとAWS IoT Coreを連携させるIoTゲートウェイシステムです。ラズベリーパイをゲートウェイとして使用し、センサーデータの収集と双方向通信を実現します。

## システム構成

```
┌─────────────────┐    WiFi    ┌──────────────────┐    MQTT/SSL    ┌─────────────────┐
│                 │ ◄─────────► │                  │ ◄─────────────► │                 │
│   M5Stack       │            │  Raspberry Pi    │                │   AWS IoT Core  │
│   Core2         │            │  Gateway         │                │                  │
│                 │            │                  │                │                  │
│ • センサー       │            │ • Flask Server   │                │ • データ蓄積     │
│ • データ送信     │            │ • MQTT Client    │                │ • コマンド送信   │
│ • コマンド受信   │            │ • データ処理     │                │ • 分析・可視化   │
└─────────────────┘            └──────────────────┘                └─────────────────┘
```

## 機能概要

### データフロー
1. **M5Stack Core2** → センサーデータをWiFi経由でラズパイに送信
2. **ラズパイゲートウェイ** → データを受信し、タイムスタンプを追加してAWS IoT Coreに転送
3. **AWS IoT Core** → データを蓄積・分析し、必要に応じてコマンドを送信
4. **ラズパイゲートウェイ** → AWSからのコマンドを受信し、M5Stackに転送

### 主要機能
- **リアルタイムデータ収集**: M5Stack Core2からのセンサーデータを継続的に収集
- **双方向通信**: AWS IoT CoreからのコマンドでM5Stackデバイスを制御
- **データ前処理**: 日本時間（JST）でのタイムスタンプ自動追加
- **セキュア通信**: SSL/TLS証明書を使用した安全なMQTT通信

## ファイル構成

```
m5flask/
├── server.py              # Flask Webサーバー（メイン）
├── send_to_aws.py         # AWS IoT Core送信モジュール
├── subscribe_from_aws.py  # AWS IoT Core受信モジュール
├── config.py              # 設定ファイル
├── requirements.txt       # Python依存関係
└── README.md              # このファイル
```

## セットアップ

### 1. 依存関係のインストール
```bash
pip install -r requirements.txt
```

### 2. 証明書ファイルの配置
以下の証明書ファイルを`certs/`ディレクトリに配置してください：

```
certs/
├── AmazonRootCA1.pem      # AWS IoT Coreルート証明書
├── device-cert.pem.crt    # デバイス証明書
└── private-key.pem.key    # プライベートキー
```

### 3. 環境変数の設定（オプション）
必要に応じて環境変数で設定をカスタマイズできます：

```bash
export AWS_IOT_ENDPOINT="your-endpoint.iot.region.amazonaws.com"
export FLASK_HOST="0.0.0.0"
export FLASK_PORT="5000"
export LOG_LEVEL="INFO"
```

### 4. システム起動
```bash
python server.py
```

## API エンドポイント

### データ受信
- **POST** `/data` - M5Stack Core2からのセンサーデータを受信
- **GET** `/status` - 現在のステータスを取得
- **POST** `/update_status` - ステータス更新（AWS IoT Coreからのコマンド用）
- **GET** `/health` - ヘルスチェック

## MQTT トピック

### 送信トピック
- `iot/m5core2/sensor` - センサーデータをAWS IoT Coreに送信

### 受信トピック
- `cmd/change/field/1/m5-thing` - AWS IoT Coreからのコマンドを受信

## 技術仕様

- **Webサーバー**: Flask (ポート5000)
- **通信プロトコル**: MQTT over SSL/TLS
- **AWS IoT Core エンドポイント**: `ayhwynhqtsmv-ats.iot.us-west-2.amazonaws.com`
- **ポート**: 8883 (MQTT over SSL)

## 使用例

### M5Stack Core2からのデータ送信
```json
POST http://ラズパイのIP:5000/data
{
    "temperature": 25.5,
    "humidity": 60.2,
    "status": "NORMAL"
}
```

### ステータス確認
```bash
curl http://ラズパイのIP:5000/status
```

## 新機能・改善点

### コード品質向上
- **型ヒント**: 全関数に型アノテーションを追加
- **エラーハンドリング**: 包括的な例外処理とログ機能
- **設定管理**: 環境変数による柔軟な設定
- **ログ機能**: 構造化されたログ出力
- **スレッドセーフ**: ステータス管理の並行処理対応

### セキュリティ強化
- **証明書検証**: 起動時の証明書ファイル存在確認
- **入力検証**: リクエストデータの型・内容チェック
- **エラーレスポンス**: 適切なHTTPステータスコード

### 運用性向上
- **ヘルスチェック**: `/health`エンドポイント追加
- **設定ファイル**: `config.py`による一元管理
- **依存関係管理**: `requirements.txt`による明確化

## 注意事項

- 証明書ファイルは`certs/`ディレクトリに配置してください
- ラズパイのファイアウォール設定でポート5000を開放してください
- AWS IoT Coreのポリシーで適切な権限を設定してください
- 環境変数で設定をカスタマイズできます

## ライセンス

このプロジェクトはMITライセンスの下で公開されています。
