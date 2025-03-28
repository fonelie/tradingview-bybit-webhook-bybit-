from flask import Flask, request, jsonify
import requests
import os

app = Flask(__name__)

# 讀取環境變數中的 Bybit API 金鑰與密鑰
BYBIT_API_KEY = os.getenv("BYBIT_API_KEY")
BYBIT_API_SECRET = os.getenv("BYBIT_API_SECRET")

# Bybit 下單網址 (Testnet 或 Mainnet)
BYBIT_API_URL = "https://api.bybit.com"  # 如用測試網，改為 https://api-testnet.bybit.com

@app.route('/')
def home():
    return "✅ Webhook 伺服器正在運行"

@app.route('/webhook', methods=['POST'])
def webhook():
    data = request.json
    print("📬 收到 TradingView 訊號：", data)

    signal = data.get("signal")
    if signal not in ["buy", "sell"]:
        return jsonify({"status": "error", "message": "未知的 signal"}), 400

    side = "Buy" if signal == "buy" else "Sell"

    order = place_order(symbol="BTCUSDT", side=side, qty=0.01)
    return jsonify(order)

def place_order(symbol, side, qty):
    url = f"{BYBIT_API_URL}/v5/order/create"
    headers = {
        "X-BYBIT-API-KEY": BYBIT_API_KEY,
        "Content-Type": "application/json"
    }
    
    import time, hmac, hashlib, json
    timestamp = str(int(time.time() * 1000))

    body = {
        "category": "linear",
        "symbol": symbol,
        "side": side,
        "orderType": "Market",
        "qty": str(qty),
        "timeInForce": "GTC"
    }

    # 建立簽名
    payload = json.dumps(body)
    params_str = timestamp + BYBIT_API_KEY + payload
    sign = hmac.new(
        bytes(BYBIT_API_SECRET, "utf-8"),
        params_str.encode("utf-8"),
        hashlib.sha256
    ).hexdigest()

    headers["X-BYBIT-SIGN"] = sign
    headers["X-BYBIT-TIMESTAMP"] = timestamp

    response = requests.post(url, headers=headers, data=payload)
    print("📤 Bybit 回傳：", response.text)
    return response.json()

if __name__ == '__main__':
    app.run(host="0.0.0.0", port=5000)
