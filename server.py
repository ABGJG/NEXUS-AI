import json
import secrets
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
import litert_lm

MODEL = "gemma3-1b-it-int4.litertlm"
HOST = "0.0.0.0"
PORT = 8090

with open("nexus_api.key", "w") as f:
    API_KEY = "nexus-" + secrets.token_urlsafe(32)
    f.write(API_KEY)

print("Loading Gemma...")
engine = litert_lm.Engine(MODEL)
print("Gemma loaded.")
print("API KEY:", API_KEY)
print(f"API: http://127.0.0.1:{PORT}")

class Handler(BaseHTTPRequestHandler):
    def send_json(self, data, status=200):
        body = json.dumps(data, ensure_ascii=False).encode()
        self.send_response(status)
        self.send_header("Content-Type", "application/json; charset=utf-8")
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)

    def check_auth(self):
        auth = self.headers.get("Authorization", "")
        return auth == f"Bearer {API_KEY}"

    def do_GET(self):
        if not self.check_auth():
            return self.send_json({"error": "Invalid API key"}, 401)

        if self.path == "/v1/models":
            return self.send_json({
                "object": "list",
                "data": [{
                    "id": "nexus-gemma-3-1b",
                    "object": "model",
                    "owned_by": "NEXUS XS"
                }]
            })

        self.send_json({"error": "Not found"}, 404)

    def do_POST(self):
        if not self.check_auth():
            return self.send_json({"error": "Invalid API key"}, 401)

        if self.path != "/v1/chat/completions":
            return self.send_json({"error": "Not found"}, 404)

        try:
            length = int(self.headers.get("Content-Length", 0))
            data = json.loads(self.rfile.read(length))

            messages = data.get("messages", [])
            prompt = messages[-1].get("content", "") if messages else ""

            conversation = engine.create_conversation()
            result = conversation.send_message(prompt)
            conversation.close()

            text = ""
            for item in result.get("content", []):
                if item.get("type") == "text":
                    text += item.get("text", "")

            self.send_json({
                "id": "nexus-" + secrets.token_hex(8),
                "object": "chat.completion",
                "model": data.get("model", "nexus-gemma-3-1b"),
                "choices": [{
                    "index": 0,
                    "message": {
                        "role": "assistant",
                        "content": text
                    },
                    "finish_reason": "stop"
                }]
            })

        except Exception as e:
            self.send_json({
                "error": {
                    "message": str(e),
                    "type": "server_error"
                }
            }, 500)

    def log_message(self, format, *args):
        print(format % args)

server = ThreadingHTTPServer((HOST, PORT), Handler)

try:
    server.serve_forever()
except KeyboardInterrupt:
    print("\nStopping...")
finally:
    server.server_close()
    engine.close()
