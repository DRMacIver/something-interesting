"""Serve the site locally, telling browsers to check every file with the
server before using a cached copy (Python's plain http.server says nothing,
so browsers guess, and can go on showing an old page or font for a while).

Usage: uv run tools/serve.py [port]
"""

import sys
from functools import partial
from http.server import SimpleHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent


class Handler(SimpleHTTPRequestHandler):
    def end_headers(self):
        self.send_header("Cache-Control", "no-cache")
        super().end_headers()


if __name__ == "__main__":
    port = int(sys.argv[1]) if len(sys.argv) > 1 else 8765
    server = ThreadingHTTPServer(("", port), partial(Handler, directory=ROOT))
    print(f"Serving on http://localhost:{port}")
    server.serve_forever()
