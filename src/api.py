"""BikDesk thin read-only HTTP API. Stdlib only.

Reads data/banks.jsonl + banks.meta.json into memory (directory is tiny).
Routes:
    GET /api/health            -> status, business_day, entries
    GET /api/banks/<9-digit>   -> record or 404
    GET /api/banks?name=...    -> substring search over name, max 50
    GET /api/dump              -> full snapshot as NDJSON

Usage:
    python src/api.py --data data --port 8789
"""

import argparse
import json
import urllib.parse
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path


def load_snapshot(data_dir):
    records = {}
    for line in (data_dir / "banks.jsonl").read_text(encoding="utf-8").splitlines():
        if line.strip():
            r = json.loads(line)
            records[r["bic"]] = r
    meta = json.loads((data_dir / "banks.meta.json").read_text(encoding="utf-8"))
    return records, meta


class Handler(BaseHTTPRequestHandler):
    server_version = "BikDesk/0.1"

    def _send(self, code, payload, ctype="application/json; charset=utf-8"):
        body = payload if isinstance(payload, bytes) else payload.encode("utf-8")
        self.send_response(code)
        self.send_header("Content-Type", ctype)
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)

    def do_GET(self):  # noqa: N802
        records, meta = self.server.snapshot
        url = urllib.parse.urlparse(self.path)
        parts = url.path.strip("/").split("/")
        if url.path == "/api/health":
            self._send(200, json.dumps({
                "status": "ok",
                "business_day": meta.get("business_day"),
                "entries": meta.get("entries"),
            }, ensure_ascii=False))
        elif len(parts) == 3 and parts[0] == "api" and parts[1] == "banks" \
                and len(parts[2]) == 9 and parts[2].isdigit():
            rec = records.get(parts[2])
            if rec is None:
                self._send(404, json.dumps({"error": "unknown bic"}, ensure_ascii=False))
            else:
                self._send(200, json.dumps(rec, ensure_ascii=False))
        elif url.path == "/api/banks":
            q = urllib.parse.parse_qs(url.query).get("name", [""])[0].strip().lower()
            if not q:
                self._send(400, json.dumps({"error": "name query required"}, ensure_ascii=False))
                return
            found = [r for r in records.values() if q in (r.get("name") or "").lower()][:50]
            self._send(200, json.dumps(found, ensure_ascii=False))
        elif url.path == "/api/dump":
            body = "".join(json.dumps(r, ensure_ascii=False) + "\n" for r in records.values())
            self._send(200, body, "application/x-ndjson; charset=utf-8")
        else:
            self._send(404, json.dumps({"error": "not found"}, ensure_ascii=False))

    def log_message(self, fmt, *args):
        pass


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--data", default="data")
    ap.add_argument("--port", type=int, default=8789)
    ap.add_argument("--host", default="127.0.0.1")
    args = ap.parse_args()
    server = ThreadingHTTPServer((args.host, args.port), Handler)
    server.snapshot = load_snapshot(Path(args.data))
    print(f"BikDesk API on http://{args.host}:{args.port} "
          f"({len(server.snapshot[0])} banks)")
    server.serve_forever()


if __name__ == "__main__":
    main()
