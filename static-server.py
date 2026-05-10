import http.server
import json
import os
import subprocess
import sys
import threading
from datetime import datetime, timezone
from urllib.parse import urlparse, parse_qs

PORT = 8888
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DATA_FILE = os.path.join(BASE_DIR, "data", "odds.json")

class WebhookHandler(http.server.SimpleHTTPRequestHandler):
    
    def do_GET(self):
        parsed = urlparse(self.path)
        path = parsed.path.rstrip("/") or "/"

        if path == "/webhook/status":
            self.send_json(get_status())
            return

        # Serve static files (HTML, JSON, SVG, etc.)
        self.send_response(200)
        
        # Determine file path
        if path == "/":
            file_path = os.path.join(BASE_DIR, "stanley-cup-odds.html")
        else:
            file_path = os.path.join(BASE_DIR, path.lstrip("/"))
        
        # Set content type
        if file_path.endswith(".json"):
            content_type = "application/json"
        elif file_path.endswith(".svg"):
            content_type = "image/svg+xml"
        elif file_path.endswith(".html"):
            content_type = "text/html"
        elif file_path.endswith(".css"):
            content_type = "text/css"
        elif file_path.endswith(".js"):
            content_type = "application/javascript"
        else:
            content_type = "application/octet-stream"
        
        try:
            with open(file_path, "rb") as f:
                content = f.read()
            self.send_header("Content-Type", content_type)
            self.send_header("Access-Control-Allow-Origin", "*")
            self.send_header("Access-Control-Allow-Methods", "GET, POST, OPTIONS")
            self.send_header("Access-Control-Allow-Headers", "Content-Type")
            self.send_header("Content-Length", str(len(content)))
            self.end_headers()
            self.wfile.write(content)
        except FileNotFoundError:
            self.send_error(404, f"File not found: {path}")
        except Exception as e:
            self.send_error(500, str(e))

    def do_POST(self):
        parsed = urlparse(self.path)
        path = parsed.path.rstrip("/") or "/"

        if path == "/webhook/refresh":
            self.handle_webhook_refresh()
            return

        self.send_error(404, "Endpoint not found")

    def do_OPTIONS(self):
        self.send_response(200)
        self.send_header("Access-Control-Allow-Origin", "*")
        self.send_header("Access-Control-Allow-Methods", "GET, POST, OPTIONS")
        self.send_header("Access-Control-Allow-Headers", "Content-Type")
        self.end_headers()

    def handle_webhook_refresh(self):
        """Handle POST /webhook/refresh - runs parse-odds.py"""
        try:
            script_path = os.path.join(BASE_DIR, "parse-odds.py")
            result = subprocess.run(
                [sys.executable, script_path],
                capture_output=True,
                text=True,
                timeout=90
            )
            
            output = [line.strip() for line in result.stdout.split("\n") if line.strip()]
            success = result.returncode == 0

            response = {
                "status": "success" if success else "error",
        "timestamp": datetime.now(timezone.utc).isoformat(),
                "stdout": "\n".join(output),
                "stderr": result.stderr.strip() if result.stderr else None,
                "returnCode": result.returncode
            }

            # Load updated data if success
            if success and os.path.exists(DATA_FILE):
                try:
                    with open(DATA_FILE, "r", encoding="utf-8") as f:
                        data = json.load(f)
                    response["meta"] = data.get("metadata", {})
                except:
                    pass

            self.send_json(response)
        except subprocess.TimeoutExpired:
            self.send_json({
                "status": "error",
                "message": "Parse script timed out (90s)"
            })
        except Exception as e:
            self.send_json({
                "status": "error",
                "message": str(e)
            })

    def send_json(self, data):
        """Send JSON response with CORS headers."""
        body = json.dumps(data, indent=2, ensure_ascii=False).encode("utf-8")
        self.send_response(200)
        self.send_header("Content-Type", "application/json")
        self.send_header("Access-Control-Allow-Origin", "*")
        self.send_header("Access-Control-Allow-Methods", "GET, POST, OPTIONS")
        self.send_header("Access-Control-Allow-Headers", "Content-Type")
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)

    def log_message(self, format, *args):
        """Custom log format."""
        msg = format % args
        method, path, status = msg.split(" ")[0:3] if " " in msg else ("?", "/", "?")
        print(f"  [{datetime.now().strftime('%H:%M:%S')}] {method} {path} {status}")

def get_status():
    """Get server and data status."""
    status = {
        "server": "running",
        "port": PORT,
                "timestamp": datetime.now(timezone.utc).isoformat(),
        "endpoints": [
            "GET  /                      -> Stanley Cup HTML",
            "GET  /webhook/status        -> Server status",
            "POST /webhook/refresh       -> Trigger data refresh"
        ]
    }
    
    if os.path.exists(DATA_FILE):
        try:
            with open(DATA_FILE, "r", encoding="utf-8") as f:
                data = json.load(f)
            meta = data.get("metadata", {})
            status["data"] = {
                "lastUpdated": meta.get("lastUpdated", "N/A"),
                "sources": meta.get("sources", []),
                "teamsRemaining": meta.get("teamsRemaining", 0),
                "season": meta.get("season", "N/A")
            }
            status["data"]["status"] = "loaded"
        except json.JSONDecodeError:
            status["data"]["status"] = "corrupt"
        except Exception as e:
            status["data"]["status"] = f"error: {e}"
    else:
        status["data"] = {"status": "missing", "message": "data/odds.json not found"}
    
    return status

def run_server():
    """Start HTTPS server."""
    os.chdir(BASE_DIR)
    server = http.server.HTTPServer(("0.0.0.0", PORT), WebhookHandler)
    print("=" * 60)
    print("  STANLEY CUP ODDS - LOCAL SERVER")
    print(f"  Port: {PORT}")
    print(f"  URL:  http://localhost:{PORT}")
    print("=" * 60)
    print(f"\n  Endpoints:")
    print(f"    GET  /                   -> Stanley Cup chart")
    print(f"    POST /webhook/refresh      -> Refresh data")
    print(f"    GET  /webhook/status      -> Server status")
    print(f"\n  Webhook example:")
    print(f"    curl -X POST http://localhost:{PORT}/webhook/refresh")
    print("=" * 60)
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        print(f"\n  Server stopped.")
        server.shutdown()

if __name__ == "__main__":
    run_server()
