~/Yadav $ cat > server.py << 'EOF'
import os
from flask import Flask, send_from_directory, jsonify
import json
import urllib.request
from flask_cors import CORS

app = Flask(__name__)
CORS(app)  # Enable CORS for all routes

@app.route('/')
def home():
    return send_from_directory('static', 'index.html')

@app.route('/<path:path>')
def serve_static(path):
    return send_from_directory('static', path)

@app.route('/api/<query_type>/<query_value>')
def api_call(query_type, query_value):
    try:
        print(f"🔍 API Call: {query_type} = {query_value}")
        url = f"http://dark-op.dev-is.xyz/?key=wasdark&{query_type}={query_value}"
        
        with urllib.request.urlopen(url) as response:
            data = json.loads(response.read())
        
        # Remove duplicates
        if 'data' in data and isinstance(data['data'], list):
            unique_data = []
            seen = set()
            for record in data['data']:
                record_id = f"{record.get('name','')}-{record.get('mobile','')}-{record.get('id','')}"
                if record_id not in seen:
                    seen.add(record_id)
                    unique_data.append(record)
            data['data'] = unique_data
        
        print(f"✅ API Success: Found {len(data.get('data', []))} records")
        return jsonify(data)
        
    except Exception as e:
        print(f"❌ API Error: {e}")
        return jsonify({"error": str(e)}), 500

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 10000))
    print(f"🚀 Server starting on port {port}")
    app.run(host='0.0.0.0', port=port)
EOF
