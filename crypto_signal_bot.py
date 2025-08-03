import requests
from telegram import Bot
import datetime

# 🔐 Настройки
TELEGRAM_TOKEN = '7903581351:AAG8oKUsMc_u7L3bKj8T4oJL-bL4SfeSmGnc'
CHAT_ID = '5723647968'
bot = Bot(token=TELEGRAM_TOKEN)

TOKENS = ['solana', 'avalanche-2', 'near', 'ethereum', 'bitcoin']
SYMBOLS = {
    'solana': 'SOLUSDT',
    'avalanche-2': 'AVAXUSDT',
    'near': 'NEARUSDT',
    'ethereum': 'ETHUSDT',
    'bitcoin': 'BTCUSDT'
}

def get_market_data(ids):
    url = 'https://api.coingecko.com/api/v3/coins/markets'
    params = {
        'vs_currency': 'usd',
        'ids': ','.join(ids),
        'order': 'market_cap_desc',
        'per_page': len(ids),
        'page': 1,
        'sparkline': True
    }
    try:
        response = requests.get(url, params=params)
        if response.status_code == 200:
            return response.json()
    except Exception as e:
        print("Ошибка API:", e)
    return []

def calc_rsi(prices, period=14):
    if len(prices) < period:
        return None
    deltas = [prices[i+1] - prices[i] for i in range(len(prices)-1)]
    gains = [d if d > 0 else 0 for d in deltas]
    losses = [-d if d < 0 else 0 for d in deltas]
    avg_gain = sum(gains[:period]) / period
    avg_loss = sum(losses[:period]) / period
    if avg_loss == 0:
        return 100
    rs = avg_gain / avg_loss
    return round(100 - (100 / (1 + rs)), 2)

def analyze_and_format(data):
    signal_lines = []
    rsi_values = []
    for idx, coin in enumerate(data, start=1):
        name = coin['name']
        symbol = SYMBOLS.get(coin['id'], coin['symbol'].upper() + 'USDT')
        price = coin['current_price']
        volume = coin['total_volume']
        spark = coin.get('sparkline_in_7d', {}).get('price', [])

        if len(spark) < 20:
            continue

        rsi = calc_rsi(spark[-20:])
        rsi_values.append(rsi if rsi is not None else 50)

        tp1 = round(price * 1.02, 2)
        tp2 = round(price * 1.05, 2)
        tp3 = round(price * 1.08, 2)
        sl = round(price * 0.97, 2)

        line = f"#{idx}. {symbol} — Вход: ${price:.2f}\n"
        line += f"🎯 TP1: ${tp1} | TP2: ${tp2} | TP3: ${tp3}\n"
        line += f"🛡 SL: ${sl} | 📊 RSI: {rsi} | 🔊 Объём: ${volume/1_000_000:.0f}M\n"
        signal_lines.append(line)

    if not signal_lines:
        return None

    avg_rsi = sum(rsi_values) / len(rsi_values)
    if avg_rsi > 60:
        trend = "🟢 Рынок: бычий тренд"
    elif avg_rsi < 40:
        trend = "🔴 Рынок: медвежий тренд"
    else:
        trend = "⚪ Рынок: нейтральный"

    timestamp = datetime.datetime.utcnow().strftime("%H:%M UTC")
    message = f"{trend}\n\n" + "\n".join(signal_lines) + f"\n📅 Время: {timestamp}"
    return message

if __name__ == "__main__":
    data = get_market_data(TOKENS)
    if data:
        msg = analyze_and_format(data)
        if msg:
            bot.send_message(chat_id=CHAT_ID, text=msg)



