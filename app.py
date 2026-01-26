"""
🎬 FlickFinder PRO - Ultimate Movie App Backend
📅 Version: 1.2.0
📦 API للعرض والبحث عن الأفلام والمسلسلات

🔧 المميزات:
- واجهات REST API لـ TMDB
- نظام تخزين مؤقت لتحسين الأداء
- معالجة أخطاء محسنة
- تكامل مع Telegram Bot
- دعم متعدد اللغات

⚠️ المفاتيح المطلوبة في البيئة:
- TMDB_API_KEY: مفتاح واجهة TMDB (مطلوب)
- BOT_TOKEN: رمز بوت Telegram (اختياري)

🏃‍♂️ التشغيل: python app.py
🌐 العنوان: http://localhost:5000
📡 Endpoints:
  - GET  /                    → صفحة الترحيب
  - GET  /api/trending        → الأفلام الرائجة
  - GET  /api/search?q=query  → بحث عن محتوى
"""

import os
import time
from functools import wraps
from flask import Flask, jsonify, request
from flask_cors import CORS
import requests
import telebot
from telebot import types

app = Flask(__name__)
CORS(app)  # ✅ السماح بطلبات من أي مصدر

# 📦 نظام Cache بسيط
cache = {}

def cache_response(ttl=600):  # ⏰ 10 دقائق بالثواني
    """
    🗂️ ديكوراتور للتخزين المؤقت
    @param ttl: وقت انتهاء الصلاحية بالثواني
    @return: دالة مغلقة تحقق من التخزين المؤقت
    """
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            # 🔑 مفتاح Cache بناء على اسم الدالة والمعلمات
            cache_key = f"{func.__name__}:{str(args)}:{str(kwargs)}"
            
            # 🔍 تحقق إذا كانت البيانات موجودة في Cache
            if cache_key in cache:
                cached_data, timestamp = cache[cache_key]
                if time.time() - timestamp < ttl:
                    app.logger.info(f"📦 Cache hit for {func.__name__}")
                    return cached_data
            
            # 📥 إذا لم تكن في Cache، احصل عليها وخزنها
            result = func(*args, **kwargs)
            cache[cache_key] = (result, time.time())
            app.logger.info(f"💾 Cache miss for {func.__name__}, storing for {ttl}s")
            return result
        return wrapper
    return decorator

# 🔑 جلب المفاتيح من إعدادات البيئة (Render Environment Variables)
TMDB_API_KEY = os.getenv("TMDB_API_KEY")
BOT_TOKEN = os.getenv("BOT_TOKEN")

# 📝 التحقق من وجود المفاتيح المطلوبة
if not TMDB_API_KEY:
    app.logger.warning("⚠️ TMDB_API_KEY not found in environment variables")

if BOT_TOKEN:
    bot = telebot.TeleBot(BOT_TOKEN)
    app.logger.info("🤖 Telegram Bot initialized successfully")
else:
    app.logger.warning("⚠️ BOT_TOKEN not found, Telegram Bot disabled")

@app.route('/')
def home():
    """
    🏠 صفحة الترحيب الرئيسية
    @return: رسالة ترحيب نصية
    """
    return jsonify({
        "message": "FlickFinder API is Running Successfully! 🚀",
        "version": "1.2.0",
        "endpoints": {
            "trending": "/api/trending?lang=en-US",
            "search": "/api/search?q=query&lang=en-US"
        }
    })

@app.route('/api/trending', methods=['GET'])
@cache_response(ttl=600)  # 🚀 تخزين لمدة 10 دقائق
def get_trending():
    """
    🔥 جلب الأفلام والمسلسلات الرائجة
    @query_param lang: لغة المحتوى (الافتراضي: en-US)
    @return: قائمة بالعناصر الرائجة
    @error: 400 لغة غير مدعومة، 500 خطأ داخلي، 502/504 خطأ في الاتصال
    """
    lang = request.args.get('lang', 'en-US')
    
    # 🔒 تحقق من صحة اللغة
    valid_langs = ['en-US', 'fr-FR', 'ar-SA', 'es-ES', 'de-DE']
    if lang not in valid_langs:
        app.logger.warning(f"❌ Language not supported: {lang}")
        return jsonify({
            "error": "Language not supported",
            "supported_languages": valid_langs
        }), 400
    
    url = f"https://api.themoviedb.org/3/trending/all/day?api_key={TMDB_API_KEY}&language={lang}"
    
    try:
        app.logger.info(f"📡 Fetching trending content in {lang}")
        response = requests.get(url, timeout=10)
        response.raise_for_status()  # 📊 يرفع استثناء إذا كانت حالة HTTP غير 200
        
        data = response.json()
        
        # 🔍 تحقق من وجود النتائج
        if 'results' not in data:
            app.logger.error("❌ Invalid API response structure from TMDB")
            return jsonify({
                "error": "Invalid API response from TMDB",
                "details": "Missing 'results' field"
            }), 500
        
        results = data.get('results', [])
        app.logger.info(f"✅ Found {len(results)} trending items")
        
        # 🎭 تصفية العناصر بدون صورة
        filtered_results = [
            item for item in results 
            if item.get('poster_path') or item.get('backdrop_path')
        ]
        
        if len(filtered_results) < len(results):
            app.logger.info(f"🗑️ Filtered out {len(results) - len(filtered_results)} items without images")
        
        return jsonify(filtered_results[:20])  # 📏 تحديد النتائج لـ 20 عنصر
        
    except requests.exceptions.Timeout:
        app.logger.error("⏰ TMDB API timeout")
        return jsonify({
            "error": "TMDB API timeout. Please try again.",
            "tip": "The request took too long to complete"
        }), 504
        
    except requests.exceptions.RequestException as e:
        app.logger.error(f"🔌 TMDB API connection error: {e}")
        return jsonify({
            "error": "Could not fetch trending content",
            "details": str(e)
        }), 502
        
    except Exception as e:
        app.logger.error(f"💥 Unexpected error in get_trending: {e}")
        return jsonify({
            "error": "Internal server error",
            "request_id": str(hash(time.time()))[:8]
        }), 500

@app.route('/api/search', methods=['GET'])
def search():
    """
    🔍 البحث عن أفلام ومسلسلات
    @query_param q: نص البحث (مطلوب)
    @query_param lang: لغة النتائج (الافتراضي: en-US)
    @return: قائمة بنتائج البحث
    @error: 400 نص قصير أو مفقود، 500 خطأ داخلي
    """
    query = request.args.get('q', '').strip()
    lang = request.args.get('lang', 'en-US')
    
    # 🔒 تحقق من وجود واستيفاء نص البحث
    if not query:
        app.logger.warning("❌ Search query missing")
        return jsonify({
            "error": "Search query is required",
            "example": "/api/search?q=inception"
        }), 400
    
    if len(query) < 2:
        app.logger.warning(f"❌ Search query too short: '{query}'")
        return jsonify({
            "error": "Search query must be at least 2 characters",
            "query_length": len(query)
        }), 400
    
    # 🔒 تحقق من صحة اللغة
    valid_langs = ['en-US', 'fr-FR', 'ar-SA', 'es-ES', 'de-DE']
    if lang not in valid_langs:
        return jsonify({
            "error": "Language not supported",
            "supported_languages": valid_langs
        }), 400
    
    url = f"https://api.themoviedb.org/3/search/multi?api_key={TMDB_API_KEY}&query={query}&language={lang}"
    
    try:
        app.logger.info(f"🔍 Searching for: '{query}' in {lang}")
        response = requests.get(url, timeout=10)
        response.raise_for_status()
        
        data = response.json()
        
        if 'results' not in data:
            app.logger.error("❌ Invalid search response from TMDB")
            return jsonify({"error": "Invalid search response"}), 500
        
        results = data.get('results', [])
        app.logger.info(f"✅ Found {len(results)} results for '{query}'")
        
        # 🎭 تصفية العناصر ذات الصلة فقط (أفلام ومسلسلات)
        filtered_results = [
            item for item in results 
            if item.get('media_type') in ['movie', 'tv'] and 
               (item.get('poster_path') or item.get('backdrop_path'))
        ]
        
        if len(filtered_results) < len(results):
            app.logger.info(f"🗑️ Filtered out {len(results) - len(filtered_results)} irrelevant items")
        
        return jsonify(filtered_results[:15])  # 📏 تحديد النتائج لـ 15 عنصر
        
    except requests.exceptions.Timeout:
        app.logger.error(f"⏰ Search timeout for: '{query}'")
        return jsonify({
            "error": "Search timeout. Please try again.",
            "query": query
        }), 504
        
    except requests.exceptions.RequestException as e:
        app.logger.error(f"🔌 Search connection error for '{query}': {e}")
        return jsonify({
            "error": "Search service unavailable",
            "details": str(e)
        }), 502
        
    except Exception as e:
        app.logger.error(f"💥 Unexpected error in search for '{query}': {e}")
        return jsonify({
            "error": "Internal server error during search",
            "request_id": str(hash(f"{query}{time.time()}"))[:8]
        }), 500

@app.route('/api/health', methods=['GET'])
def health_check():
    """
    🩺 فحص صحة الخادم والخدمات الخارجية
    @return: حالة الخادم والاتصالات
    """
    health_status = {
        "status": "healthy",
        "timestamp": time.time(),
        "services": {}
    }
    
    # 🔍 فحص اتصال TMDB
    try:
        test_url = f"https://api.themoviedb.org/3/movie/550?api_key={TMDB_API_KEY}"
        response = requests.get(test_url, timeout=5)
        health_status["services"]["tmdb"] = {
            "status": "up" if response.status_code == 200 else "down",
            "response_time": response.elapsed.total_seconds()
        }
    except Exception as e:
        health_status["services"]["tmdb"] = {
            "status": "down",
            "error": str(e)
        }
        health_status["status"] = "degraded"
    
    # 📊 إحصائيات Cache
    health_status["cache"] = {
        "entries": len(cache),
        "memory_usage": f"{sum(len(str(k)) + len(str(v)) for k, v in cache.items()) / 1024:.2f} KB"
    }
    
    # 📝 معلومات التطبيق
    health_status["app"] = {
        "name": "FlickFinder PRO API",
        "version": "1.2.0",
        "environment": os.getenv("FLASK_ENV", "production")
    }
    
    app.logger.info(f"🩺 Health check: {health_status['status']}")
    return jsonify(health_status)

@app.errorhandler(404)
def not_found(error):
    """
    🚫 معالجة صفحات غير موجودة
    @param error: كائن الخطأ
    @return: رسالة خطأ 404
    """
    app.logger.warning(f"🔍 404 Not Found: {request.path}")
    return jsonify({
        "error": "Endpoint not found",
        "path": request.path,
        "available_endpoints": ["/api/trending", "/api/search", "/api/health"]
    }), 404

@app.errorhandler(405)
def method_not_allowed(error):
    """
    🚫 معالجة طرق HTTP غير مسموحة
    @param error: كائن الخطأ
    @return: رسالة خطأ 405
    """
    app.logger.warning(f"🚫 405 Method Not Allowed: {request.method} {request.path}")
    return jsonify({
        "error": "Method not allowed",
        "method": request.method,
        "path": request.path,
        "allowed_methods": error.valid_methods
    }), 405

if __name__ == "__main__":
    """
    🚀 نقطة بداية التشغيل
    """
    # ⚙️ إعدادات التشغيل
    port = int(os.environ.get('PORT', 5000))
    debug = os.environ.get('FLASK_DEBUG', 'False').lower() == 'true'
    
    # 📝 إعدادات التسجيل
    import logging
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    
    app.logger.info(f"🚀 Starting FlickFinder PRO API on port {port}")
    app.logger.info(f"🔧 Debug mode: {debug}")
    app.logger.info(f"🔑 TMDB API Key: {'Set' if TMDB_API_KEY else 'Not Set'}")
    app.logger.info(f"🤖 Telegram Bot: {'Enabled' if BOT_TOKEN else 'Disabled'}")
    
    # 🏃‍♂️ تشغيل التطبيق
    app.run(
        host='0.0.0.0',
        port=port,
        debug=debug
    )


# 🔧 إعدادات خاصة بالسحابة
if __name__ == "__main__":
    # الحصول على المنفذ من متغير البيئة (Railway يضيفه تلقائياً)
    port = int(os.environ.get("PORT", 5000))
    
    # التحقق من وضع التشغيل
    debug_mode = os.environ.get("FLASK_ENV") == "development"
    
    # تشغيل الخادم
    app.run(
        host="0.0.0.0",  # مهم: يجب أن يكون 0.0.0.0 للسحابة
        port=port,
        debug=debug_mode,
        threaded=True  # ✅ لتحسين الأداء
    )
