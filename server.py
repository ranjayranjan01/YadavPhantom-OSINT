from http.server import HTTPServer, BaseHTTPRequestHandler
import json
import urllib.request
from urllib.parse import unquote
import os
import time

class APIHandler(BaseHTTPRequestHandler):
    
    def do_GET(self):
        if self.path == '/':
            self.send_response(200)
            self.send_header('Content-type', 'text/html')
            self.end_headers()
            with open('index.html', 'rb') as f:
                self.wfile.write(f.read())
        elif self.path.startswith('/api/'):
            self.handle_api_request()
        else:
            self.send_response(404)
            self.end_headers()

    def handle_api_request(self):
        try:
            parts = self.path.split('/')
            if len(parts) >= 4:
                query_type = parts[2]
                query_value = unquote(parts[3])
                
                print(f"🔍 API Call: {query_type} = {query_value}")
                
                # API URL for all types
                api_url = f"http://dark-op.dev-is.xyz/?key=wasdark&{query_type}={query_value}"
                
                # Make API request with better error handling
                req = urllib.request.Request(api_url)
                try:
                    with urllib.request.urlopen(req, timeout=15) as response:
                        api_data = response.read()
                    
                    data = json.loads(api_data)
                    
                    # Check if API returned error
                    if 'error' in data:
                        error_response = {
                            "error": f"API Error: {data['error']}",
                            "details": "The external API returned an error for this search type"
                        }
                        self.send_json_response(500, error_response)
                        return
                    
                    # Remove duplicates and send response
                    cleaned_data = self.remove_duplicates(data, query_type)
                    self.send_json_response(200, cleaned_data)
                    print(f"✅ {query_type.upper()} API Success")
                    
                except urllib.error.HTTPError as e:
                    if e.code == 500:
                        error_response = {
                            "error": f"External API Error {e.code}",
                            "details": f"The {query_type} lookup service is currently unavailable. Only Phone lookup is fully functional."
                        }
                    else:
                        error_response = {
                            "error": f"External API returned {e.code}",
                            "details": "The data source API is currently unavailable for this search type"
                        }
                    self.send_json_response(502, error_response)
                    print(f"❌ External API HTTP Error: {e.code} for {query_type}")
                    
            else:
                raise Exception("Invalid API path")
                
        except Exception as e:
            error_response = {
                "error": str(e),
                "details": "Please try phone number search or check the input format"
            }
            self.send_json_response(500, error_response)
            print(f"❌ API Error: {e}")

    def send_json_response(self, status_code, data):
        self.send_response(status_code)
        self.send_header('Content-type', 'application/json')
        self.send_header('Access-Control-Allow-Origin', '*')
        self.end_headers()
        self.wfile.write(json.dumps(data).encode())

    def remove_duplicates(self, data, query_type):
        if query_type == 'vehicle':
            return data
        if 'data' in data and isinstance(data['data'], list):
            unique_records = []
            seen_records = set()
            for record in data['data']:
                record_id = self.create_record_id(record)
                if record_id not in seen_records:
                    seen_records.add(record_id)
                    unique_records.append(record)
            removed_count = len(data['data']) - len(unique_records)
            if removed_count > 0:
                print(f"🔄 Removed {removed_count} duplicates")
            data['data'] = unique_records
        return data

    def create_record_id(self, record):
        key_parts = [
            record.get('name', ''),
            record.get('id', ''),
            record.get('mobile', ''),
            record.get('fname', ''),
            record.get('address', '')[:100] if record.get('address') else ''
        ]
        return '|'.join(str(part).strip().lower() for part in key_parts)

if __name__ == '__main__':
    print("🚀 Starting YadavPhantom OSINT Server...")
    print("📡 Server: http://localhost:8000")
    print("🔧 API Ready: http://localhost:8000/api/{type}/{value}")
    print("🔄 Duplicate removal: ENABLED")
    print("📁 Serving: index.html")
    print("💡 Status: Only Phone lookup is fully functional")
    print("⚠️  Other APIs (Aadhaar/Vehicle/UPI) have limited access")
    print("Press Ctrl+C to stop the server")
    
    try:
        server = HTTPServer(('localhost', 8000), APIHandler)
        print("✅ Server started successfully!")
        server.serve_forever()
    except KeyboardInterrupt:
        print("\n🛑 Server stopped by user")
    except Exception as e:
        print(f"❌ Server error: {e}")
