import os
from flask import Flask, send_from_directory

app = Flask(__name__)
BASE_DIR = os.path.abspath(os.path.dirname(__file__))

# Serve main platform (Root)
@app.route('/')
@app.route('/index.html')
def main_platform():
    # If the user merges this with the main platform folder, serve it:
    if os.path.exists(os.path.join(BASE_DIR, 'index.html')):
        return send_from_directory(BASE_DIR, 'index.html')
    return "<h3>Main Aahar-Parampara Platform</h3><p><a href='/discover/'>Go to QR Discovery Landing Experience &rarr;</a></p>"

# Serve QR Landing Page
@app.route('/discover/')
@app.route('/discover/index.html')
def discover_landing():
    return send_from_directory(os.path.join(BASE_DIR, 'discover'), 'index.html')

# Serve Mobile Reveal Experience
@app.route('/discover/reveal.html')
def discover_reveal():
    return send_from_directory(os.path.join(BASE_DIR, 'discover'), 'reveal.html')

# Serve Static Assets inside /discover/ (CSS, JS, Images)
@app.route('/discover/<path:filename>')
def discover_static(filename):
    return send_from_directory(os.path.join(BASE_DIR, 'discover'), filename)

# Serve the master dataset
@app.route('/master_database.json')
def serve_master_db():
    return send_from_directory(BASE_DIR, 'master_database.json')

# Serve preparation dataset
@app.route('/preparation.json')
def serve_prep_db():
    return send_from_directory(BASE_DIR, 'preparation.json')

if __name__ == '__main__':
    # PORT is assigned dynamically by Render/Railway
    port = int(os.environ.get("PORT", 8000))
    app.run(host='0.0.0.0', port=port, debug=True)
