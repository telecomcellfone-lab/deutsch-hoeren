#!/usr/bin/env python3
"""Local server for the spoken-word search.

Needed once Common Voice is ingested: a million clips is far too much to bake
into a single HTML file, and the mp3s live on disk rather than behind a URL.
The same goes for the Spontaneous Speech corpus. The standalone
../word-audio-search.html keeps working without this, on the Tatoeba data
alone.

    python serve.py            # http://127.0.0.1:8731, opens a browser
    python serve.py --port N --no-open
"""
import argparse, json, os, posixpath, sqlite3, threading, urllib.request, webbrowser
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from urllib.parse import urlparse, parse_qs, unquote, quote

HERE = os.path.dirname(os.path.abspath(__file__))
DB = os.path.join(HERE, "data", "spoken.db")
APP = os.path.join(HERE, "app_template.html")
LIMIT = 600
# Where each source's mp3s live on disk. Tatoeba has no entry: it is streamed
# from tatoeba.org by the page itself.
CLIP_DIRS = {"c": "cv_clips_dir", "s": "sps_clips_dir"}
# Common Voice holds 950k of the 985k rows, so one plain "LIMIT 600" over the
# whole table lets it fill the page and bury the other two sources entirely.
# Each source is queried on its own instead, and the small ones get a reserved
# share of the cap. Query order decides who gets squeezed; ORDER decides what
# the page shows first.
SHARE = (("s", 40), ("t", LIMIT), ("c", LIMIT))
ORDER = ("t", "s", "c")  # translated first, then unscripted, then read-aloud
DWDS_IPA = "https://www.dwds.de/api/ipa?q="

_local = threading.local()
_ipa_lock = threading.Lock()


def db():
    if not hasattr(_local, "conn"):
        _local.conn = sqlite3.connect(DB, check_same_thread=False)
    return _local.conn


def clips_dir(source):
    key = CLIP_DIRS.get(source)
    if not key:
        return None
    row = db().execute("SELECT v FROM meta WHERE k=?", (key,)).fetchone()
    return row[0] if row else None


def fold(s):
    return s.lower().replace("ß", "ss")


def quote_fts(term):
    return '"' + term.replace('"', '""') + '"'


def resolve(term):
    """Turn "smart" into a real mode: the narrowest match that finds anything.

    Decided once over the whole table rather than per source, so a compound hit
    in one corpus cannot outrank a whole-word hit in another.
    """
    con = db()
    for kind, expr in (("exact", quote_fts(term)),
                       ("prefix", quote_fts(term) + "*")):
        if con.execute("SELECT 1 FROM clips_fts WHERE clips_fts MATCH ? LIMIT 1",
                       (expr,)).fetchone():
            return kind
    return "any"


def run_query(term, mode):
    """Return [[ref, sentence, english, speaker, licence, source, prompt], ...]."""
    con = db()
    cols = "c.ref,c.sentence,c.english,c.speaker,c.licence,c.source,c.prompt"
    if mode not in ("exact", "prefix", "any"):
        mode = resolve(term)

    def hits(source, cap):
        if mode == "any":
            return con.execute(
                "SELECT %s FROM clips c WHERE c.source=? AND c.lower LIKE ? "
                "LIMIT ?" % cols,
                (source, "%" + fold(term) + "%", cap)).fetchall()
        expr = quote_fts(term) + ("*" if mode == "prefix" else "")
        return con.execute(
            "SELECT %s FROM clips_fts f JOIN clips c ON c.id=f.rowid "
            "WHERE clips_fts MATCH ? AND c.source=? LIMIT ?" % cols,
            (expr, source, cap)).fetchall()

    got, left = {}, LIMIT
    for source, cap in SHARE:
        if left <= 0:
            break
        got[source] = hits(source, min(cap, left))
        left -= len(got[source])
    return [list(r) for src in ORDER for r in got.get(src, ())]


def stats():
    con = db()
    n = con.execute("SELECT COUNT(*) FROM clips").fetchone()[0]
    s = con.execute("SELECT COUNT(DISTINCT speaker) FROM clips").fetchone()[0]
    return {"clips": n, "speakers": s}


def ipa(word):
    """Phonetic spelling from DWDS, cached forever.

    DWDS sends no Access-Control-Allow-Origin, so the page cannot call it
    itself. Every word is looked up once and then answered from the database,
    including the misses, so a rare word costs one round trip in its lifetime.
    status: "proved" = checked by DWDS, "auto" = machine-generated.
    """
    con = db()
    row = con.execute("SELECT ipa, status FROM ipa_cache WHERE word=?", (word,)).fetchone()
    if row:
        return {"ipa": row[0], "status": row[1]} if row[0] else {}
    found = {}
    try:
        with urllib.request.urlopen(DWDS_IPA + quote(word), timeout=8) as r:
            data = json.loads(r.read().decode("utf-8"))
        if isinstance(data, list) and data and data[0].get("ipa"):
            found = {"ipa": data[0]["ipa"], "status": data[0].get("status", "")}
    except Exception:
        return {}  # offline or DWDS down: no cache entry, so retry next time
    with _ipa_lock:
        con.execute("INSERT OR REPLACE INTO ipa_cache(word,ipa,status) VALUES(?,?,?)",
                    (word, found.get("ipa", ""), found.get("status", "")))
        con.commit()
    return found


class Handler(BaseHTTPRequestHandler):
    protocol_version = "HTTP/1.1"

    def log_message(self, *a):
        pass

    def _send(self, code, body, ctype, extra=None):
        self.send_response(code)
        self.send_header("Content-Type", ctype)
        self.send_header("Content-Length", str(len(body)))
        for k, v in (extra or {}).items():
            self.send_header(k, v)
        self.end_headers()
        self.wfile.write(body)

    def _json(self, obj):
        self._send(200, json.dumps(obj).encode("utf-8"),
                   "application/json; charset=utf-8")

    def do_GET(self):
        u = urlparse(self.path)
        path, qs = u.path, parse_qs(u.query)

        if path in ("/", "/index.html"):
            with open(APP, "rb") as fh:
                html = fh.read()
            # Server mode needs no baked-in clips; the API supplies them.
            html = html.replace(b"__CLIPS__", b"[]")
            return self._send(200, html, "text/html; charset=utf-8")

        if path == "/api/stats":
            return self._json(stats())

        if path == "/api/ipa":
            term = (qs.get("q", [""])[0] or "").strip()
            return self._json(ipa(term) if term else {})

        if path == "/api/search":
            term = (qs.get("q", [""])[0] or "").strip()
            if not term:
                return self._json([])
            mode = qs.get("mode", ["smart"])[0]
            try:
                return self._json(run_query(term, mode))
            except sqlite3.OperationalError as e:
                return self._json({"error": str(e)})

        if path.startswith("/audio/"):
            # /audio/<source letter>/<file under that source's clips dir>
            source, _, rel = path[len("/audio/"):].partition("/")
            return self.send_audio(source, unquote(rel))

        self._send(404, b"not found", "text/plain")

    def send_audio(self, source, rel):
        root = clips_dir(source)
        if not root:
            return self._send(404, b"no local clips for that source", "text/plain")
        # Keep the request inside the clips directory.
        rel = posixpath.normpath(rel.replace("\\", "/")).lstrip("/")
        if rel.startswith("..") or ":" in rel:
            return self._send(403, b"forbidden", "text/plain")
        full = os.path.abspath(os.path.join(root, rel))
        if not full.startswith(os.path.abspath(root)) or not os.path.isfile(full):
            return self._send(404, b"not found", "text/plain")
        with open(full, "rb") as fh:
            data = fh.read()
        self._send(200, data, "audio/mpeg", {"Cache-Control": "max-age=86400"})


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--port", type=int, default=8731)
    ap.add_argument("--no-open", action="store_true")
    args = ap.parse_args()

    if not os.path.exists(DB):
        raise SystemExit("no database yet — run:  python _ingest.py")

    db().execute("CREATE TABLE IF NOT EXISTS ipa_cache("
                 "word TEXT PRIMARY KEY, ipa TEXT, status TEXT)")
    db().commit()

    url = "http://127.0.0.1:%d/" % args.port
    st = stats()
    print("Deutsch hören  %s clips, %s speakers"
          % (format(st["clips"], ","), format(st["speakers"], ",")))
    print(url + "   (Strg+C zum Beenden)")
    if not args.no_open:
        threading.Timer(0.6, lambda: webbrowser.open(url)).start()
    # On Windows the default allow_reuse_address lets a SECOND server bind a
    # port that is already in use. Both then answer, at random, and a stale
    # instance can serve stale code. Refuse to start instead.
    class Server(ThreadingHTTPServer):
        allow_reuse_address = False

    try:
        srv = Server(("127.0.0.1", args.port), Handler)
    except OSError:
        raise SystemExit("Port %d ist belegt. Läuft die App schon? "
                         "Sonst: python serve.py --port 8732" % args.port)
    try:
        srv.serve_forever()
    except KeyboardInterrupt:
        print("\nbeendet")


if __name__ == "__main__":
    main()
