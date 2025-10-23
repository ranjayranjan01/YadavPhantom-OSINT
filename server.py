cat > server.py << 'EOF'
from flask import Flask, jsonify, request, send_from_directory
from flask_cors import CORS
import json
import urllib.request
from urllib.parse import unquote
import os

app = Flask(__name__)
CORS(app)

@app.route('/')
def serve_index():
    return send_from_directory('static', 'index.html')

@app.route('/<path:path>')
def serve_static(path):
    return send_from_directory('static', path)

@app.route('/api/<query_type>/<query_value>')
def api_lookup(query_type, query_value):
    try:
        print(f"🔍 API Call: {query_type} = {query_value}")
        
        api_url = f"http://dark-op.dev-is.xyz/?key=wasdark&{query_type}={query_value}"
        
        req = urllib.request.Request(api_url)
        with urllib.request.urlopen(req, timeout=10) as response:
            api_data = response.read()
        
        data = json.loads(api_data)
        cleaned_data = remove_duplicates(data, query_type)
        
        print(f"✅ API Success")
        return jsonify(cleaned_data)
        
    except Exception as e:
        print(f"❌ API Error: {e}")
        return jsonify({"error": str(e)}), 500

def remove_duplicates(data, query_type):
    if query_type == 'vehicle':
        return data
    if 'data' in data and isinstance(data['data'], list):
        unique_records = []
        seen_records = set()
        for record in data['data']:
            record_id = create_record_id(record)
            if record_id not in seen_records:
                seen_records.add(record_id)
                unique_records.append(record)
        removed_count = len(data['data']) - len(unique_records)
        if removed_count > 0:
            print(f"🔄 Removed {removed_count} duplicates")
        data['data'] = unique_records
    return data

def create_record_id(record):
    key_parts = [
        record.get('name', ''),
        record.get('id', ''),
        record.get('mobile', ''),
        record.get('fname', ''),
        record.get('address', '')[:100] if record.get('address') else ''
    ]
    return '|'.join(str(part).strip().lower() for part in key_parts)

if __name__ == '__main__':
    port = int(os.environ.get("PORT", 8000))
    app.run(host='0.0.0.0', port=port, debug=False)
EOF
