import os
from flask import Flask, jsonify, request
from flask_cors import CORS
import requests
import telebot # تصحيح الاستدعاء
from telebot import types

app = Flask(__name__)
CORS(app)

# جلب المفاتيح من إعدادات Render (Environment Variables)
TMDB_API_KEY = os.getenv("TMDB_API_KEY")
BOT_TOKEN = os.getenv("BOT_TOKEN")

# تعريف البوت (اختياري إذا كنت ستستخدمه داخل السيرفر)
if BOT_TOKEN:
    bot = telebot.TeleBot(BOT_TOKEN)

@app.route('/')
def home():
    return "FlickFinder API is Running Successfully! 🚀"

@app.route('/api/trending', methods=['GET'])
def get_trending():
    lang = request.args.get('lang', 'en-US')
    url = f"https://api.themoviedb.org/3/trending/all/day?api_key={TMDB_API_KEY}&language={lang}"
    try:
        response = requests.get(url, timeout=10)
        return jsonify(response.json().get('results', []))
    except Exception as e:
        return jsonify({"error": str(e)})

@app.route('/api/search', methods=['GET'])
def search():
    query = request.args.get('q')
    lang = request.args.get('lang', 'en-US')
    if not query:
        return jsonify([])
    
    url = f"https://api.themoviedb.org/3/search/multi?api_key={TMDB_API_KEY}&query={query}&language={lang}"
    try:
        response = requests.get(url, timeout=10)
        return jsonify(response.json().get('results', []))
    except Exception as e:
        return jsonify({"error": str(e)})

if __name__ == "__main__":
    # هذا السطر مهم للتشغيل المحلي، لكن Render يستخدم gunicorn
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port)
