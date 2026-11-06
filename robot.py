#!/usr/bin/env python3
"""MineScript IDE - kincskereső robot.

Használat:
    python robot.py input.txt output.txt        (grafikus IDE a böngészőben)
    python robot.py -q input.txt output.txt     (csendes mód: napló kiírása, kilépés)
"""
import json
import os
import sys
import threading
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer

import minescript as ms

HERE = os.path.dirname(os.path.abspath(__file__))


def quiet(inp, out):
    rows, cols, grid, prog = ms.read_input(inp)
    run = ms.execute(rows, cols, grid, prog)
    ms.write_log(out, run.log_text())


class App:
    def __init__(self, inp, out):
        self.inp, self.out = inp, out
        self.rows, self.cols, self.grid, self.prog = ms.read_input(inp)
        self.last = None
        self.lock = threading.Lock()
        self.server = None

    def init_payload(self):
        ast = ms.parse_program(self.prog)
        st0 = ms.Run(self.rows, self.cols, self.grid).state0
        return {
            "rows": self.rows, "cols": self.cols, "ast": ast, "state0": st0,
            "input": os.path.basename(self.inp), "log": os.path.basename(self.out),
            "logPath": os.path.abspath(self.out),
        }

    def run(self, text):
        with self.lock:
            self.last = ms.execute(self.rows, self.cols, self.grid, text)
            ms.write_log(self.out, "")
            r = self.last
            return {"entries": r.entries, "end": r.end, "state0": r.state0,
                    "final": r.final_line()}

    def logsync(self, n):
        with self.lock:
            if self.last is None:
                return {"log": ""}
            text = self.last.log_text(n) if n < len(self.last.texts) else self.last.log_text()
            if n == 0:
                text = ""
            ms.write_log(self.out, text)
            return {"log": text}

    def read_log(self):
        try:
            with open(self.out, "r", encoding="utf-8") as f:
                return {"log": f.read()}
        except OSError:
            return {"log": ""}


def make_handler(app, window=None):
    class H(BaseHTTPRequestHandler):
        def log_message(self, *a):
            pass

        def _send(self, code, body, ctype="application/json; charset=utf-8"):
            if not isinstance(body, bytes):
                body = json.dumps(body).encode("utf-8")
            self.send_response(code)
            self.send_header("Content-Type", ctype)
            self.send_header("Content-Length", str(len(body)))
            self.send_header("Cache-Control", "no-store")
            self.end_headers()
            self.wfile.write(body)

        def do_GET(self):
            if self.path in ("/", "/index.html"):
                with open(os.path.join(HERE, "ui.html"), "rb") as f:
                    self._send(200, f.read(), "text/html; charset=utf-8")
            elif self.path == "/api/init":
                self._send(200, app.init_payload())
            elif self.path == "/api/log":
                self._send(200, app.read_log())
            else:
                self._send(404, {"error": "not found"})

        def do_POST(self):
            n = int(self.headers.get("Content-Length", 0) or 0)
            data = json.loads(self.rfile.read(n) or b"{}")
            if self.path == "/api/run":
                self._send(200, app.run(data.get("text", "")))
            elif self.path == "/api/logsync":
                self._send(200, app.logsync(int(data.get("n", 0))))
            elif self.path == "/api/exit":
                if window is not None:
                    window.destroy()
                self._send(200, {"ok": True})
                threading.Thread(target=app.server.shutdown, daemon=True).start()
            else:
                self._send(404, {"error": "not found"})

    return H


def gui(inp, out):
    import webview
    app = App(inp, out)
    srv = ThreadingHTTPServer(("127.0.0.1", 0), make_handler(app))
    app.server = srv
    port = srv.server_address[1]
    url = "http://127.0.0.1:%d/" % port
    print("MineScript IDE fut: " + url)

    def run_server():
        try:
            srv.serve_forever()
        except Exception:
            pass

    threading.Thread(target=run_server, daemon=True).start()

    window = webview.create_window("MineScript IDE", url, width=1200, height=800)
    webview.start()

    srv.shutdown()
    srv.server_close()


def main(argv):
    if len(argv) == 4 and argv[1] == "-q":
        quiet(argv[2], argv[3])
    elif len(argv) == 3:
        gui(argv[1], argv[2])
    else:
        print(__doc__)
        return 2
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv))
