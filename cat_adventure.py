from flask import Flask, render_template, send_from_directory
import os

app = Flask(__name__)

# 設置目錄
PROJECT_ROOT = os.path.dirname(os.path.abspath(__file__))
STATIC_DIR = os.path.join(PROJECT_ROOT, 'static')
IMAGES_DIR = os.path.join(STATIC_DIR, 'images')

def ensure_directories():
    """確保必要的目錄存在"""
    for directory in [STATIC_DIR, IMAGES_DIR]:
        if not os.path.exists(directory):
            os.makedirs(directory)

@app.route('/')
def index():
    return render_template('music.html')

@app.route('/static/<path:filename>')
def serve_static(filename):
    return send_from_directory('static', filename)

@app.route('/static/images/<path:filename>')
def serve_image(filename):
    return send_from_directory(IMAGES_DIR, filename)

if __name__ == '__main__':
    ensure_directories()
    app.run(debug=True) 