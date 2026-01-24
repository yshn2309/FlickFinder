import os
from flask import Flask, jsonify, request
from flask_cors import CORS
import requests

app = Flask(__name__)
CORS(app)

# جلب المفتاح من إعدادات Render
TMDB_API_KEY = os.getenv("TMDB_API_KEY")

@app.route('/api/trending')
def trending():
    url = f"https://api.themoviedb.org/3/trending/all/day?api_key={TMDB_API_KEY}&language=en-US"
    return jsonify(requests.get(url).json().get('results', []))

@app.route('/api/search')
def search():
    query = request.args.get('q')
    url = f"https://api.themoviedb.org/3/search/multi?api_key={TMDB_API_KEY}&query={query}&language=en-US"
    return jsonify(requests.get(url).json().get('results', []))

if __name__ == "__main__":
    app.run()
