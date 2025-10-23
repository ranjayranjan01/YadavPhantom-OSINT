import os
import json
import urllib.request
from flask import Flask, send_from_directory, jsonify
from flask_cors import CORS

app = Flask(__name__)
CORS(app)

@app.route('/')
def home():
    return send_from_directory('static', 'index.html')

@app.route('/<path:path>')
def static_files(path):
    return send_from_directory('static', path)

@app.route('/api/<query_type>/<query_value>')
def api_search(query_type, query_value):
    try:
        url = f"http://dark-op.dev-is.xyz/?key=wasdark&{query_type}={query_value}"
        with urllib.request.urlopen(url) as response:
            data = json.loads(response.read())
        return jsonify(data)
    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 10000))
    app.run(host='0.0.0.0', port=port)
EOF
