import requests
import pandas as pd
import time
import ta

# ========== НАСТРОЙКИ ==========
TOKEN = "ВАШ_TG_TOKEN"
CHAT_ID = "ВАШ_CHAT_ID"

COIN_ID = "bitcoin"  # Пример: 'bitcoin', 'ethereum', 'solana'
INTERVAL = 'hourly'  # 'daily', 'hourly'
LIMIT = 100          # Кол-во точек (до 90 для hourly, до 365 для daily)
RSI_PERIOD = 14

# ========== ФУНКЦИИ ==========

def send_signal(message):
    url = f"https://api.telegram.org/bot{TOKEN}/sendMessage"
    data = {"chat_id": CHAT_ID, "text": message}
    requests.post(url, data=data)

def fetch_ohlc(coin_id, interval, limit):
    url = f"https://api.coingecko.com/api/v3/coins/{coin_id}/market_chart"
    params = {
        "vs_currency": "usd",
        "days": "7",
        "interval": interval
    }
    try:
        r = requests.get(url, params=params)
        data = r.json()
        prices = data.get("prices", [])[-limit:]
        df = pd.DataFrame(prices, columns=["timestamp", "price"])
        df["price"] = df["price"].astype(float)
        return df
    except Exception as e:
        send_signal(f"⚠️ Ошибка при загрузке данных: {e}")
        return pd.DataFrame()

def calculate_rsi(series, period):
    try:
        rsi = ta.momentum.RSIIndicator(close=series, window=period)
        return rsi.rsi()
    except Exception as e:
        send_signal(f"⚠️ Ошибка при расчёте RSI: {e}")
        return pd.Series()

# ========== ОСНОВНОЙ ЦИКЛ ==========

def run_bot():
    df = fetch_ohlc(COIN_ID, INTERVAL, LIMIT)
    
    if df.empty or len(df) < RSI_PERIOD:
        send_signal("⚠️ Ошибка: недостаточно данных для анализа.")
        return

    df["rsi"] = calculate_rsi(df["price"], RSI_PERIOD)
    
    try:
        last_price = df["price"].iloc[-1]
        last_rsi = df["rsi"].iloc[-1]

        if last_rsi < 30:
            send_signal(f"📉 Сигнал на покупку {COIN_ID.upper()}\nЦена: ${last_price:.2f}\nRSI: {last_rsi:.2f}")
        elif last_rsi > 70:
            send_signal(f"📈 Сигнал на продажу {COIN_ID.upper()}\nЦена: ${last_price:.2f}\nRSI: {last_rsi:.2f}")
        else:
            send_signal(f"ℹ️ {COIN_ID.upper()} нейтрально\nЦена: ${last_price:.2f}\nRSI: {last_rsi:.2f}")

    except IndexError:
        send_signal("⚠️ Ошибка в боте: данные по RSI или цене не получены")

# ========== ЗАПУСК ==========
if __name__ == "__main__":
    run_bot()

