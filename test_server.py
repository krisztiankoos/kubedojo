from http.server import HTTPServer, BaseHTTPRequestHandler
import urllib.request
import json
import os

UNLEASH_URL = os.getenv("UNLEASH_URL", "http://localhost:4242/api")
API_TOKEN = os.getenv("UNLEASH_API_TOKEN", "*:*.unleash-admin-api-token")

def check_flag(flag_name, user_id):
    """Simple flag check against Unleash API."""
    try:
        url = f"{UNLEASH_URL}/client/features/{flag_name}"
        req = urllib.request.Request(url)
        req.add_header("Authorization", API_TOKEN)
        with urllib.request.urlopen(req, timeout=2) as resp:
            data = json.loads(resp.read())
            # Simple check - in production use the SDK
            if not data.get("enabled", False):
                return False
            for strategy in data.get("strategies", []):
                if strategy["name"] == "userWithId":
                    user_ids = strategy["parameters"]["userIds"].split(",")
                    return user_id in user_ids
            return data.get("enabled", False)
    except Exception as e:
        print(f"Flag check failed: {e}")
        return False  # Safe default

class Handler(BaseHTTPRequestHandler):
    def do_GET(self):
        # Extract user ID from query param
        user_id = "anonymous"
        if "?" in self.path:
            params = dict(p.split("=") for p in self.path.split("?")[1].split("&"))
            user_id = params.get("user", "anonymous")

        # Check feature flag
        new_ui = check_flag("new-ui-dashboard", user_id)

        if new_ui:
            body = f"<h1>NEW Dashboard for {user_id}</h1><p>Charts, graphs, and analytics!</p>"
        else:
            body = f"<h1>Classic Dashboard for {user_id}</h1><p>Simple text view.</p>"

        self.send_response(200)
        self.send_header("Content-Type", "text/html")
        self.end_headers()
        self.wfile.write(body.encode())

if __name__ == '__main__':
    print("Starting...")
    # HTTPServer(("", 8080), Handler).serve_forever()
    print(check_flag("new-ui-dashboard", "user-42"))
