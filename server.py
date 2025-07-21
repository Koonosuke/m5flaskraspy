from flask import Flask, request

app = Flask(__name__)

@app.route("/data", methods=["POST"])
def receive_data():
    data = request.get_json()
    if data:
        print(f"📥 温度: {data['temperature']}°C, 湿度: {data['humidity']}%")
        return "Received", 200
    return "No data", 400

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
