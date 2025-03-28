from flask import Flask, request, jsonify
import hmac
import hashlib
import time
import requests
import os

app = Flask(__name__)

# Bybit API 金鑰（填上你自己的）
API_KEY = os.getenv("BYBIT_API_KEY", "YOUR_API_KEY")
API_SECRET = os.getenv("BYBIT_API_SECRET", "YOUR_API_SECRET")
BASE_URL = "https://api.bybit.com"

# 下單函數
def place_order(side, symbol="BTCUSDT", qty=0.01):
    endpoint = "/v2/private/order/create"
    url = BASE_URL + endpoint

    params = {
        "api_key": API_KEY,
        "symbol": symbol,
        "side": side.upper(),
        "order_type": "Market",
        "qty": qty,
        "time_in_force": "GoodTillCancel",
        "timestamp": int(time.time() * 1000),
    }

    # 簽名
    sign = "&".join([f"{k}={params[k]}" for k in sorted(params)])
    params["sign"] = hmac.new(
        API_SECRET.encode("utf-8"), sign.encode("utf-8"), hashlib.sha256
    ).hexdigest()

    # 發送請求
    res = requests.post(url, data=params)
    return res.json()

@app.route("/webhook", methods=["POST"])
def webhook():
    data = request.json
    print("收到訊號：", data)

    if data.get("signal") == "buy":
        result = place_order("Buy")
    elif data.get("signal") == "sell":
        result = place_order("Sell")
    else:
        return jsonify({"error": "Invalid signal"}), 400

    return jsonify(result)

if __name__ == "__main__":
    app.run(debug=True, port=5000)
