~/Yadav $ cat > server.py << 'EOF'
import os
from flask import Flask, send_from_directory, jsonify
import json
import urllib.request
from flask_cors import CORS

# Create Flask app
app = Flask(__name__)
CORS(app)

@app.route('/')
def serve_home():
    return send_from_directory('static', 'index.html')

@app.route('/<path:filename>')
def serve_static(filename):
    return send_from_directory('static', filename)

@app.route('/api/<query_type>/<query_value>')
def api_search(query_type, query_value):
    try:
        # Make API call to external service
        api_url = f"http://dark-op.dev-is.xyz/?key=wasdark&{query_type}={query_value}"
        response = urllib.request.urlopen(api_url)
        data = json.loads(response.read())
        
        # Remove duplicates
        if 'data' in data and isinstance(data['data'], list):
            unique_data = []
            seen = set()
            for record in data['data']:
                record_id = f"{record.get('name', '')}-{record.get('mobile', '')}"
                if record_id not in seen:
                    seen.add(record_id)
                    unique_data.append(record)
            data['data'] = unique_data
            
        return jsonify(data)
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 10000))
    app.run(host='0.0.0.0', port=port)
EOF
