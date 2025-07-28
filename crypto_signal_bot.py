
import requests
from telegram import Bot
import time

# 🔐 Настройки
TELEGRAM_TOKEN = '7903581351:AAG8oKUsMc_u7L3bKj8T4oJLbL4SfeSmGnc'
CHAT_ID = '5723647968'
bot = Bot(token=TELEGRAM_TOKEN)

TOKENS = ['solana', 'avalanche-2', 'near', 'sui', 'jito', 'ethereum', 'bitcoin']

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

def analyze_and_send(data):
    for coin in data:
        name = coin['name']
        price = coin['current_price']
        change = coin['price_change_percentage_24h']
        volume = coin['total_volume']
        symbol = coin['symbol']
        spark = coin.get('sparkline_in_7d', {}).get('price', [])

        if change and change < -5 and volume > 20_000_000:
            msg = f"📉 ALERT: {name} (${symbol.upper()})\n"
            msg += f"Цена: ${price:.2f} | Изм: {change:.2f}% | Объём: ${volume:,.0f}\n"
            if len(spark) >= 20:
                rsi = calc_rsi(spark[-20:])
                msg += f"📊 RSI: {rsi}\n"
                if rsi and rsi < 30:
                    msg += "🟢 RSI < 30 — возможный отскок\n"
            bot.send_message(chat_id=CHAT_ID, text=msg)

if __name__ == "__main__":
    data = get_market_data(TOKENS)
    if data:
        analyze_and_send(data)
        CryptoPulseBot/
├── .github/
│   └── workflows/
│       └── crypto-bot.yml   ← это мы добавим
├── crypto_signal_bot.py

