"""Serve only the selected public placeholder folder on loopback."""
import argparse
from functools import partial
from http.server import SimpleHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path

class Handler(SimpleHTTPRequestHandler):
    def list_directory(self, path):
        self.send_error(404)
        return None

    def end_headers(self):
        self.send_header('Cache-Control', 'no-store, max-age=0')
        self.send_header('X-Content-Type-Options', 'nosniff')
        super().end_headers()

if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--site', required=True, choices=['website', 'app'])
    parser.add_argument('--port', required=True, type=int)
    args = parser.parse_args()
    directory = Path(__file__).resolve().parents[1] / 'sites' / args.site
    if not (directory / 'index.html').is_file():
        parser.error('Missing placeholder index.html')
    server = ThreadingHTTPServer(('127.0.0.1', args.port), partial(Handler, directory=str(directory)))
    server.serve_forever()
