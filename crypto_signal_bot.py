import requests
import pandas as pd
import time
import ta

# ========== НАСТРОЙКИ ==========
TOKEN = "ВАШ_TG_ТОКЕН"
CHAT_ID = "ВАШ_CHAT_ID"
COIN_ID = "bitcoin"  # можно заменить на 'ethereum', 'solana' и т.д.
INTERVAL = '1h'  # '1h', '4h', '1d' — период свечей
LIMIT = 100  # количество свечей для расчёта RSI
RSI_PERIOD = 14  # период RSI

# ========== ФУНКЦИИ ==========
def fetch_ohlc(coin_id, interval, limit):
    url = f"https://api.coingecko.com/api/v3/coins/{coin_id}/market_chart"
    params = {
        "vs_currency": "usd",
        "days": "7",
        "interval": interval
    }
    r = requests.get(url, params=params)
    data = r.json()
    prices = data.get("prices", [])[-limit:]

    df = pd.DataFrame(prices, columns=["timestamp", "price"])
    df["price"] = df["price"].astype(float)
    return df

def calculate_rsi(df):
    df["rsi"] = ta.momentum.RSIIndicator(close=df["price"], window=RSI_PERIOD).rsi()
    return df

def send_signal(message):
    url = f"https://api.telegram.org/bot{TOKEN}/sendMessage"
    payload = {
        "chat_id": CHAT_ID,
        "text": message,
        "parse_mode": "HTML"
    }
    requests.post(url, data=payload)

# ========== ОСНОВНОЙ ЦИКЛ ==========
try:
    df = fetch_ohlc(COIN_ID, INTERVAL, LIMIT)
    df = calculate_rsi(df)

    last_price = df["price"].iloc[-1]
    last_rsi = df["rsi"].iloc[-1]

    print(f"🔍 {COIN_ID.upper()} | Цена: {last_price:.2f} USD | RSI: {last_rsi:.2f}")

    if last_rsi > 70:
        send_signal(f"🔴 <b>{COIN_ID.upper()} RSI > 70</b>\nЦена: {last_price:.2f} USD\nВозможен шорт 📉")
    elif last_rsi < 30:
        send_signal(f"🟢 <b>{COIN_ID.upper()} RSI < 30</b>\nЦена: {last_price:.2f} USD\nВозможен лонг 📈")
except Exception as e:
    send_signal(f"⚠️ Ошибка в боте: {e}")
    print("Ошибка:", e)
bot.send_message(chat_id=chat_id, text="✅ Тестовое сообщение: бот отработал.")

