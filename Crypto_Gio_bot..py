import os
import requests
import datetime
from telegram import Bot
from dotenv import load_dotenv

# Загрузка переменных окружения
load_dotenv()
TELEGRAM_TOKEN = os.getenv("8410463314:AAE926vorMsW-ubJC7sj0of8t_8ALUW2FJ8")
CHAT_ID = os.getenv("57236479685723647968")
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
        response.raise_for_status()
        return response.json()
    except Exception as e:
        log_error(f"Ошибка API: {e}")
        return []

def calc_rsi(prices, period=14):
    if len(prices) < period:
        return None
    deltas = [prices[i+





