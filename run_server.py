import http.server
import socketserver
import socket
import os
from pathlib import Path
import json
import urllib.request
import urllib.error

HOST = os.environ.get("HOST", "127.0.0.1")
PORT = int(os.environ.get("PORT", "8000"))

class ThreadingTCPServer(socketserver.ThreadingMixIn, socketserver.TCPServer):
    daemon_threads = True
    allow_reuse_address = True

    def server_bind(self):
        self.socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        super().server_bind()


class TeaRequestHandler(http.server.SimpleHTTPRequestHandler):
    def do_OPTIONS(self):
        if self.path.rstrip("/") != "/api/chat":
            self.send_error(404)
            return
        self.send_response(204)
        self.send_header("Access-Control-Allow-Origin", "*")
        self.send_header("Access-Control-Allow-Methods", "POST, OPTIONS")
        self.send_header("Access-Control-Allow-Headers", "Content-Type")
        self.end_headers()

    def do_GET(self):
        if self.path in ("/", "/index.html"):
            self.send_response(302)
            self.send_header("Location", "/tea_platform/shop.html")
            self.end_headers()
            return
        if self.path == "/b":
            self.send_response(302)
            self.send_header("Location", "/tea_platform/index.html")
            self.end_headers()
            return
        return super().do_GET()

    def do_POST(self):
        if self.path.rstrip("/") != "/api/chat":
            self.send_error(404)
            return

        content_length = int(self.headers.get("Content-Length", "0") or "0")
        if content_length <= 0:
            self._send_json({"reply": None, "error": "empty request body"}, status=400)
            return
        if content_length > 32768:
            self._send_json({"reply": None, "error": "request body too large"}, status=413)
            return

        raw = self.rfile.read(content_length)
        try:
            payload = json.loads(raw.decode("utf-8"))
        except Exception:
            self._send_json({"reply": None, "error": "invalid json"}, status=400)
            return

        message = str(payload.get("message", "") or "").strip()
        if not message:
            self._send_json({"reply": None, "error": "message is required"}, status=400)
            return

        history = payload.get("history", [])
        if not isinstance(history, list):
            history = []

        api_key = os.environ.get("LLM_API_KEY") or os.environ.get("OPENAI_API_KEY")
        if not api_key:
            self._send_json({"reply": None, "error": "LLM_API_KEY not set"}, status=200)
            return

        base_url = str(os.environ.get("LLM_BASE_URL") or "https://api.openai.com/v1").rstrip("/")
        model = str(os.environ.get("LLM_MODEL") or "gpt-4o-mini")

        system_prompt = (
            "你是“茶小泽”，安顶山云雾茶数字焕新平台的AI客服与导览助手。"
            "用中文回答，语气亲切但信息密度高。"
            "优先基于用户问题给出可执行建议（路线/预约/购买/团购/溯源/就餐）。"
            "不确定时，明确说明不确定并给出下一步（比如建议查看页面的常见问题/导览图/预约入口）。"
            "不要编造价格、政策、联系电话。"
        )

        messages = [{"role": "system", "content": system_prompt}]
        for item in history[-10:]:
            if not isinstance(item, dict):
                continue
            role = item.get("role")
            content = item.get("content")
            if role not in ("user", "assistant"):
                continue
            if not isinstance(content, str) or not content.strip():
                continue
            messages.append({"role": role, "content": content.strip()[:2000]})
        messages.append({"role": "user", "content": message[:4000]})

        request_body = {
            "model": model,
            "messages": messages,
            "temperature": 0.5,
        }

        url = f"{base_url}/chat/completions"
        req = urllib.request.Request(
            url,
            data=json.dumps(request_body, ensure_ascii=False).encode("utf-8"),
            headers={
                "Content-Type": "application/json",
                "Authorization": f"Bearer {api_key}",
            },
            method="POST",
        )

        try:
            with urllib.request.urlopen(req, timeout=60) as resp:
                data = json.loads(resp.read().decode("utf-8"))
        except urllib.error.HTTPError as e:
            err_text = ""
            try:
                err_text = e.read().decode("utf-8", errors="ignore")[:800]
            except Exception:
                err_text = ""
            self._send_json({"reply": None, "error": f"upstream http {e.code}: {err_text or 'error'}"}, status=200)
            return
        except Exception as e:
            self._send_json({"reply": None, "error": f"upstream error: {type(e).__name__}"}, status=200)
            return

        reply = None
        try:
            reply = data["choices"][0]["message"]["content"]
        except Exception:
            reply = None

        if not isinstance(reply, str) or not reply.strip():
            self._send_json({"reply": None, "error": "empty reply"}, status=200)
            return

        self._send_json({"reply": reply.strip()}, status=200)

    def _send_json(self, obj, status=200):
        body = json.dumps(obj, ensure_ascii=False).encode("utf-8")
        self.send_response(status)
        self.send_header("Content-Type", "application/json; charset=utf-8")
        self.send_header("Content-Length", str(len(body)))
        self.send_header("Cache-Control", "no-store")
        self.send_header("Access-Control-Allow-Origin", "*")
        self.end_headers()
        self.wfile.write(body)

try:
    project_root = Path(__file__).resolve().parent.parent
    os.chdir(project_root)
    with ThreadingTCPServer((HOST, PORT), TeaRequestHandler) as httpd:
        print(f"Serving at http://{HOST}:{PORT}")
        httpd.serve_forever()
except Exception as e:
    print(f"Error starting server: {e}")
