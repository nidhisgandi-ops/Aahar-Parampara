import os
import json
import random
from flask import Flask, send_from_directory, redirect, url_for, jsonify, request

app = Flask(__name__)
BASE_DIR = os.path.abspath(os.path.dirname(__file__))
DISCOVER_DIR = os.path.join(BASE_DIR, 'discover')

# Helper to determine configured or deployed base URL
def get_base_url():
    """
    Detects public URL in production environments:
    - Custom user variable: APP_URL or PUBLIC_URL
    - Render: RENDER_EXTERNAL_URL
    - Railway: RAILWAY_PUBLIC_DOMAIN or RAILWAY_STATIC_URL
    """
    app_url = os.environ.get('APP_URL') or os.environ.get('PUBLIC_URL')
    if app_url:
        return app_url.rstrip('/')
    
    render_url = os.environ.get('RENDER_EXTERNAL_URL')
    if render_url:
        return render_url.rstrip('/')
        
    railway_domain = os.environ.get('RAILWAY_PUBLIC_DOMAIN') or os.environ.get('RAILWAY_STATIC_URL')
    if railway_domain:
        if not railway_domain.startswith('http://') and not railway_domain.startswith('https://'):
            return f"https://{railway_domain}".rstrip('/')
        return railway_domain.rstrip('/')
        
    return None

# Add permissive CORS headers for seamless cross-origin and mobile webview fetching
@app.after_request
def add_cors_headers(response):
    response.headers['Access-Control-Allow-Origin'] = '*'
    response.headers['Access-Control-Allow-Methods'] = 'GET, OPTIONS'
    response.headers['Access-Control-Allow-Headers'] = 'Content-Type'
    return response

MAIN_WEBSITE_URL = os.environ.get('MAIN_WEBSITE_URL', 'https://aahar-parampara.vercel.app/').rstrip('/') + '/'

# Root Platform Route: If root index.html exists, serve it; otherwise redirect directly to the actual main website
@app.route('/')
@app.route('/index.html')
def index():
    root_index = os.path.join(BASE_DIR, 'index.html')
    if os.path.exists(root_index) and root_index != os.path.join(DISCOVER_DIR, 'index.html'):
        return send_from_directory(BASE_DIR, 'index.html')
    return redirect(MAIN_WEBSITE_URL)

# QR Discovery Landing Page
@app.route('/discover')
@app.route('/discover/')
@app.route('/discover/index.html')
def discover_landing():
    return send_from_directory(DISCOVER_DIR, 'index.html')

# Mobile Reveal Experience Page
@app.route('/discover/reveal.html')
@app.route('/discover/reveal')
def discover_reveal():
    return send_from_directory(DISCOVER_DIR, 'reveal.html')

# Alias /reveal.html to /discover/reveal.html in case direct root link is accessed
@app.route('/reveal.html')
@app.route('/reveal')
def reveal_alias():
    return redirect('/discover/reveal.html')

# Static Assets inside /discover/ (CSS, JS, images, etc.)
@app.route('/discover/<path:filename>')
def discover_static(filename):
    return send_from_directory(DISCOVER_DIR, filename)

# Root-level fallbacks for style.css & script.js to safeguard against any relative path resolution
@app.route('/style.css')
def serve_root_style():
    return send_from_directory(DISCOVER_DIR, 'style.css')

@app.route('/script.js')
def serve_root_script():
    return send_from_directory(DISCOVER_DIR, 'script.js')

# Serve master_database.json with proper JSON MIME type
@app.route('/master_database.json')
@app.route('/discover/master_database.json')
def serve_master_db():
    return send_from_directory(BASE_DIR, 'master_database.json', mimetype='application/json')

# Serve preparation.json with proper JSON MIME type
@app.route('/preparation.json')
@app.route('/discover/preparation.json')
def serve_prep_db():
    return send_from_directory(BASE_DIR, 'preparation.json', mimetype='application/json')

# Deployment & Domain configuration endpoint
@app.route('/api/config')
def api_config():
    base_url = get_base_url()
    return jsonify({
        'base_url': base_url,
        'reveal_url': f"{base_url}/discover/reveal.html" if base_url else None,
        'main_website_url': MAIN_WEBSITE_URL
    })

# Health check endpoint for Render / Railway
@app.route('/health')
@app.route('/api/health')
def health_check():
    return jsonify({'status': 'healthy', 'service': 'aahar-parampara-qr'})

# API endpoint for random heritage food item (utility/fallback)
@app.route('/api/random-food')
def api_random_food():
    db_path = os.path.join(BASE_DIR, 'master_database.json')
    if not os.path.exists(db_path):
        return jsonify({'error': 'Dataset not found'}), 404
    
    with open(db_path, 'r', encoding='utf-8') as f:
        data = json.load(f)
    
    foods = []
    dataset = data.get('master_dataset', {})
    for region, items in dataset.items():
        if isinstance(items, list):
            for item in items:
                foods.append({**item, 'region': region})
                
    if not foods:
        return jsonify({'error': 'No foods found in dataset'}), 404
        
    return jsonify(random.choice(foods))

if __name__ == '__main__':
    # PORT is assigned dynamically by Render/Railway, defaulting to 8000
    port = int(os.environ.get("PORT", 8000))
    debug_mode = os.environ.get("FLASK_DEBUG", "false").lower() in ("true", "1", "yes")
    app.run(host='0.0.0.0', port=port, debug=debug_mode)
