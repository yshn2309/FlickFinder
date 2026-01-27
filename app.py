import os
from flask import Flask, jsonify, request
from flask_cors import CORS
import requests
import telebot
from telebot import types

app = Flask(__name__)
CORS(app)

# 🔑 ضع مفاتيحك الحقيقية هنا لضمان عمل السيرفر على PythonAnywhere
TMDB_API_KEY = "da9186853fabc392b70f9337e1d68e4a"
BOT_TOKEN = "8293650495:AAFcGGv-MegL0JKgtRf8dZxRT--9asmV-sw"

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
    # هذا الجزء مهم للتشغيل المحلي، أما PythonAnywhere فيعتمد على إعدادات WSGI
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port)
