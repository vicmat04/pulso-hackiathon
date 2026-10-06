"""Servidor local (stdlib, sin dependencias): sirve web/ y /api/ask. Sin internet."""
from __future__ import annotations

import http.server
import json
import urllib.parse
from functools import partial

from . import config
from .ask import ask, load_snapshot


class Handler(http.server.SimpleHTTPRequestHandler):
    snap: dict = {}

    def do_GET(self):  # noqa: N802
        u = urllib.parse.urlparse(self.path)
        if u.path == "/api/ask":
            q = urllib.parse.parse_qs(u.query).get("q", [""])[0][:500]
            body = json.dumps(ask(q, self.snap), ensure_ascii=False).encode()
            self.send_response(200)
            self.send_header("Content-Type", "application/json; charset=utf-8")
            self.end_headers()
            self.wfile.write(body)
            return
        super().do_GET()

    def log_message(self, *a):  # sin logs de consultas (privacidad)
        pass


def serve(port: int = 8000):
    Handler.snap = load_snapshot()
    ask("calentamiento del índice", Handler.snap)  # evita latencia en la primera consulta de la demo
    h = partial(Handler, directory=str(config.ROOT / "web"))
    with http.server.ThreadingHTTPServer(("127.0.0.1", port), h) as s:
        print(f"PULSO en http://127.0.0.1:{port}  (Ctrl+C para salir)")
        s.serve_forever()
