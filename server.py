"""Local static server; Vercel uses the same API handler through api/*.py."""
import os
from http.server import SimpleHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from urllib.parse import unquote, urlparse

from backend import APIHandler, load_env

ROOT = Path(__file__).resolve().parent
load_env()


class Handler(APIHandler, SimpleHTTPRequestHandler):
    def __init__(self, *args, **kwargs):
        SimpleHTTPRequestHandler.__init__(self, *args, directory=str(ROOT), **kwargs)

    def do_GET(self):
        path = unquote(urlparse(self.path).path)
        if path.startswith("/api/"):
            return APIHandler.do_GET(self)
        if any(part.startswith(".") for part in path.split("/") if part) or path.endswith(".py") or path.startswith("/supabase/"):
            return self.respond(404, {"error": "Not found"})
        return SimpleHTTPRequestHandler.do_GET(self)

    def do_HEAD(self):
        path = unquote(urlparse(self.path).path)
        if any(part.startswith(".") for part in path.split("/") if part) or path.endswith(".py") or path.startswith(("/api/", "/supabase/")):
            self.send_error(404)
            return
        return SimpleHTTPRequestHandler.do_HEAD(self)


if __name__ == "__main__":
    port = int(os.getenv("PORT", "8000"))
    print(f"Medi Guide: http://localhost:{port}")
    ThreadingHTTPServer(("127.0.0.1", port), Handler).serve_forever()
