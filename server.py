from http.server import HTTPServer, BaseHTTPRequestHandler
import json
import urllib.request
from urllib.parse import unquote
import os

class APIHandler(BaseHTTPRequestHandler):
    
    def do_GET(self):
        print(f"🌐 Request: {self.path}")
        
        if self.path == '/':
            # Serve HTML file
            self.send_response(200)
            self.send_header('Content-type', 'text/html')
            self.end_headers()
            with open('yadavphantom.html', 'rb') as f:
                self.wfile.write(f.read())
                
        elif self.path.startswith('/api/'):
            # API proxy
            try:
                parts = self.path.split('/')
                if len(parts) >= 4:
                    query_type = parts[2]
                    query_value = unquote(parts[3])
                    
                    print(f"🔍 API Call: {query_type} = {query_value}")
                    
                    api_url = f"http://dark-op.dev-is.xyz/?key=wasdark&{query_type}={query_value}"
                    
                    # Make request to actual API
                    req = urllib.request.Request(api_url)
                    with urllib.request.urlopen(req, timeout=10) as response:
                        api_data = response.read()
                        
                    # Parse and remove duplicates
                    data = json.loads(api_data)
                    cleaned_data = self.remove_duplicates(data, query_type)
                    
                    self.send_response(200)
                    self.send_header('Content-type', 'application/json')
                    self.send_header('Access-Control-Allow-Origin', '*')
                    self.end_headers()
                    self.wfile.write(json.dumps(cleaned_data).encode())
                    print(f"✅ API Success: {len(api_data)} bytes")
                    
                else:
                    raise Exception("Invalid API path")
                    
            except Exception as e:
                print(f"❌ API Error: {e}")
                self.send_response(500)
                self.send_header('Content-type', 'application/json')
                self.send_header('Access-Control-Allow-Origin', '*')
                self.end_headers()
                error_msg = json.dumps({"error": str(e)})
                self.wfile.write(error_msg.encode())
        else:
            self.send_response(404)
            self.end_headers()

    def remove_duplicates(self, data, query_type):
        """Remove duplicate records from API response"""
        if query_type == 'vehicle':
            return data
            
        if 'data' in data and isinstance(data['data'], list):
            unique_records = []
            seen_records = set()
            
            for record in data['data']:
                # Create unique identifier for each record
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
        """Create unique identifier for a record"""
        # Use combination of key fields to identify duplicates
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
    server = HTTPServer(('localhost', 8000), APIHandler)
    server.serve_forever()
