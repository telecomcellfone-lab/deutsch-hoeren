#!/usr/bin/env python3
"""Bake the clip index into app_template.html and write the finished app.

Output is one self-contained HTML file with no server and no build step for
the user: double-click it and search. Audio itself is streamed from Tatoeba
and Wikimedia on demand, so nothing large is ever copied into the repo.

    python _build_app.py            # -> ../word-audio-search.html
"""
import json, os, sys

HERE = os.path.dirname(os.path.abspath(__file__))
TEMPLATE = os.path.join(HERE, "app_template.html")
CLIPS = os.path.join(HERE, "data", "clips_tatoeba.json")
OUT = os.path.abspath(os.path.join(HERE, "..", "word-audio-search.html"))


def main():
    for path in (TEMPLATE, CLIPS):
        if not os.path.exists(path):
            sys.exit("missing: " + path + "  (run _build_index.py first)")

    with open(CLIPS, encoding="utf-8") as fh:
        clips = json.load(fh)
    with open(TEMPLATE, encoding="utf-8") as fh:
        html = fh.read()

    payload = json.dumps(clips, ensure_ascii=False, separators=(",", ":"))
    # Stop the JSON from closing the <script> block. "\/" is legal JSON, so the
    # payload still parses; "<!--" would open an HTML comment, so break it too.
    payload = payload.replace("</", "<\\/").replace("<!--", "<\\u0021--")

    if "__CLIPS__" not in html:
        sys.exit("template has no __CLIPS__ placeholder")
    html = html.replace("__CLIPS__", payload)

    with open(OUT, "w", encoding="utf-8") as fh:
        fh.write(html)

    speakers = {c[3] for c in clips}
    with_en = sum(1 for c in clips if c[2])
    print("wrote %s" % OUT)
    print("  %.1f MB" % (os.path.getsize(OUT) / 1e6))
    print("  %s clips, %d speakers, %s with an English translation"
          % (format(len(clips), ","), len(speakers), format(with_en, ",")))


if __name__ == "__main__":
    main()
