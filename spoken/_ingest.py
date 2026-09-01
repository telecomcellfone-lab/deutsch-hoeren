#!/usr/bin/env python3
"""Build data/spoken.db — the searchable clip database behind the app.

Ingests three sources into one table so a single search covers them all:

  tatoeba  streamed from tatoeba.org, has English translations, 12 speakers
  cv       Mozilla Common Voice, local mp3 files, ~20k speakers, no translation
  sps      Common Voice *Spontaneous Speech*, local mp3s: unscripted answers to
           a question, so filler, self-correction and real sentence melody —
           the thing scripted corpora cannot give. Small (hundreds of clips).

Common Voice column names have drifted between corpus versions (``accent`` vs
``accents``, ``sentence_id`` added later), so the TSV header is read and mapped
by name rather than by position.

    python _ingest.py                          # Tatoeba only
    python _ingest.py --cv "D:/cv-corpus-25.0-2026-03-09"
    python _ingest.py --sps "C:/data/commonvoice/sps-corpus-4.0-2026-06-12-de"
"""
import argparse, csv, json, os, sqlite3, sys

HERE = os.path.dirname(os.path.abspath(__file__))
DATA = os.path.join(HERE, "data")
DB = os.path.join(DATA, "spoken.db")

SCHEMA = """
PRAGMA journal_mode=WAL;
CREATE TABLE IF NOT EXISTS clips(
  id       INTEGER PRIMARY KEY,
  source   TEXT NOT NULL,      -- 't' tatoeba | 'c' common voice | 's' spontaneous
  ref      TEXT NOT NULL,      -- tatoeba audio id, or path under that source's clips dir
  sentence TEXT NOT NULL,
  english  TEXT NOT NULL DEFAULT '',
  speaker  TEXT NOT NULL,
  licence  TEXT NOT NULL DEFAULT '',
  lower    TEXT NOT NULL,      -- folded copy, for the LIKE (compound) search
  prompt   TEXT NOT NULL DEFAULT ''  -- spontaneous speech: the question answered
);
CREATE INDEX IF NOT EXISTS clips_source ON clips(source);
CREATE VIRTUAL TABLE IF NOT EXISTS clips_fts
  USING fts5(sentence, content='clips', content_rowid='id', tokenize='unicode61');
"""


def fold(s):
    return s.lower().replace("\u00df", "ss")


def connect():
    os.makedirs(DATA, exist_ok=True)
    db = sqlite3.connect(DB)
    db.executescript(SCHEMA)
    # prompt arrived with the spontaneous-speech source; databases built before
    # that are otherwise fine, so widen them in place rather than rebuilding.
    if "prompt" not in [r[1] for r in db.execute("PRAGMA table_info(clips)")]:
        db.execute("ALTER TABLE clips ADD COLUMN prompt TEXT NOT NULL DEFAULT ''")
    return db


def add(db, source, rows):
    """rows: iterable of (ref, sentence, english, speaker, licence[, prompt])"""
    db.execute("DELETE FROM clips WHERE source=?", (source,))
    db.executemany(
        "INSERT INTO clips(source,ref,sentence,english,speaker,licence,lower,prompt) "
        "VALUES(?,?,?,?,?,?,?,?)",
        ((source, r[0], r[1], r[2], r[3], r[4], fold(r[1]),
          r[5] if len(r) > 5 else "") for r in rows),
    )


def ingest_tatoeba(db):
    src = os.path.join(DATA, "clips_tatoeba.json")
    if not os.path.exists(src):
        print("  skip tatoeba (run _build_index.py first)")
        return 0
    with open(src, encoding="utf-8") as fh:
        clips = json.load(fh)
    add(db, "t", ((c[0], c[1], c[2], c[3], c[4]) for c in clips))
    return len(clips)


def find_tsv(root):
    """Locate validated.tsv (preferred) anywhere under the extracted corpus."""
    best = None
    for dirpath, _dirs, files in os.walk(root):
        for name in ("validated.tsv", "train.tsv", "other.tsv"):
            if name in files:
                path = os.path.join(dirpath, name)
                if name == "validated.tsv":
                    return path
                best = best or path
    return best


def ingest_cv(db, root):
    tsv = find_tsv(root)
    if not tsv:
        sys.exit("no validated.tsv found under " + root)
    clips_dir = os.path.join(os.path.dirname(tsv), "clips")
    if not os.path.isdir(clips_dir):
        sys.exit("no clips/ folder next to " + tsv)
    print("  reading " + tsv)

    def pick(header, *names):
        for n in names:
            if n in header:
                return n
        return None

    voices, seen = {}, [0, 0]  # seen = [kept, skipped]

    def stream():
        with open(tsv, encoding="utf-8", newline="") as fh:
            rd = csv.DictReader(fh, delimiter="\t", quoting=csv.QUOTE_NONE)
            head = rd.fieldnames or []
            c_id = pick(head, "client_id")
            c_path = pick(head, "path")
            c_sent = pick(head, "sentence")
            c_gen = pick(head, "gender", "gender_category")
            c_age = pick(head, "age", "age_category")
            c_acc = pick(head, "accents", "accent")
            if not (c_id and c_path and c_sent):
                sys.exit("unexpected columns in %s: %s" % (tsv, head))

            for r in rd:
                sent = (r.get(c_sent) or "").strip()
                path = (r.get(c_path) or "").strip()
                if not sent or not path:
                    seen[1] += 1
                    continue
                cid = r.get(c_id) or ""
                if cid not in voices:
                    # client_id is a 128-char hash; give it something readable.
                    # Accent leads: for pronunciation it matters more than age.
                    bits = []
                    for col in (c_acc, c_gen, c_age):
                        v = (r.get(col) or "").strip() if col else ""
                        if not v:
                            continue
                        if col == c_acc:
                            # Speakers may tick several accents ("Deutschland
                            # Deutsch|Nordrhein-Westfalen|Hochdeutsch"). The
                            # first is enough; the whole list buries the name.
                            v = v.split("|")[0].strip()
                        elif col == c_gen:
                            # CV writes male_masculine / female_feminine.
                            v = v.split("_")[0]
                        bits.append(v)
                    label = "Stimme %04d" % (len(voices) + 1)
                    if bits:
                        label += " (" + ", ".join(bits) + ")"
                    voices[cid] = label
                seen[0] += 1
                yield (path, sent, "", voices[cid], "CC0-1.0")

    add(db, "c", stream())
    rows, skipped = seen[0], seen[1]
    db.execute("INSERT OR REPLACE INTO meta(k,v) VALUES('cv_clips_dir',?)", (clips_dir,))
    print("  %s clips, %s speakers, %s rows skipped"
          % (format(rows, ","), format(len(voices), ","), format(skipped, ",")))
    return rows


# Quality flags that mean the transcript and the audio do not match. A learner
# reading a wrong transcript is worse off than not having the clip at all, so
# these rows are dropped rather than shown.
SPS_BAD_TAGS = ("transcription-length", "speech-rate", "non-allowed-script",
                "mixed-script-words", "mixed-script-transcription")


def find_sps_tsv(root):
    """Locate the spontaneous-speech corpus TSV under the extracted folder.

    The file is named per locale (``ss-corpus-de.tsv``), so match on the prefix
    rather than hard-coding the language. ``ss-reported-audios-de.tsv`` sits
    beside it and is deliberately not matched by that prefix.
    """
    for dirpath, _dirs, files in os.walk(root):
        for name in sorted(files):
            if (name.startswith("ss-corpus-") and name.endswith(".tsv")):
                return os.path.join(dirpath, name)
    return None


def ingest_sps(db, root):
    tsv = find_sps_tsv(root)
    if not tsv:
        sys.exit("no ss-corpus-*.tsv found under " + root)
    base = os.path.dirname(tsv)
    clips_dir = os.path.join(base, "audios")
    if not os.path.isdir(clips_dir):
        sys.exit("no audios/ folder next to " + tsv)
    print("  reading " + tsv)

    # Contributors can report a clip as broken or unusable; that list ships in
    # the same archive, so honour it.
    reported = set()
    for name in os.listdir(base):
        if name.startswith("ss-reported-audios") and name.endswith(".tsv"):
            with open(os.path.join(base, name), encoding="utf-8", newline="") as fh:
                for r in csv.DictReader(fh, delimiter="\t", quoting=csv.QUOTE_NONE):
                    f = (r.get("audio_file") or "").strip()
                    if f:
                        reported.add(f)

    voices, kept, skipped = {}, [0], [0]

    def stream():
        with open(tsv, encoding="utf-8", newline="") as fh:
            rd = csv.DictReader(fh, delimiter="\t", quoting=csv.QUOTE_NONE)
            head = rd.fieldnames or []
            for col in ("client_id", "audio_file", "transcription"):
                if col not in head:
                    sys.exit("unexpected columns in %s: %s" % (tsv, head))
            for r in rd:
                sent = (r.get("transcription") or "").strip()
                path = (r.get("audio_file") or "").strip()
                tags = (r.get("quality_tags") or "").split("|")
                # Untranscribed clips cannot be searched, so they are no use here
                # even though they are in the corpus.
                if (not sent or not path or path in reported
                        or any(t in SPS_BAD_TAGS for t in tags)
                        or not os.path.isfile(os.path.join(clips_dir, path))):
                    skipped[0] += 1
                    continue
                cid = r.get("client_id") or ""
                if cid not in voices:
                    bits = []
                    for col in ("accents", "gender", "age"):
                        v = (r.get(col) or "").strip()
                        if not v:
                            continue
                        if col == "accents":
                            v = v.split("|")[0].strip()
                        elif col == "gender":
                            v = v.split("_")[0]
                        bits.append(v)
                    # "S" keeps these labels apart from Common Voice's own
                    # "Stimme 0001"; the app counts distinct speakers by label.
                    label = "Stimme S%02d" % (len(voices) + 1)
                    if bits:
                        label += " (" + ", ".join(bits) + ")"
                    voices[cid] = label
                # Only a transcript with at least one upvote has been checked by
                # a second person. Say so on the clip rather than dropping the
                # rest — unchecked is most of the corpus.
                checked = (r.get("votes") or "0").strip() not in ("", "0")
                lic = "CC0-1.0" if checked else "CC0-1.0 · Transkript ungeprüft"
                kept[0] += 1
                yield (path, sent, "", voices[cid], lic,
                       (r.get("prompt") or "").strip())

    add(db, "s", stream())
    db.execute("INSERT OR REPLACE INTO meta(k,v) VALUES('sps_clips_dir',?)", (clips_dir,))
    print("  %s clips, %s speakers, %s rows skipped"
          % (format(kept[0], ","), format(len(voices), ","), format(skipped[0], ",")))
    return kept[0]


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--cv", metavar="DIR",
                    help="root of the extracted Common Voice corpus")
    ap.add_argument("--sps", metavar="DIR",
                    help="root of the extracted Spontaneous Speech corpus")
    args = ap.parse_args()

    db = connect()
    db.execute("CREATE TABLE IF NOT EXISTS meta(k TEXT PRIMARY KEY, v TEXT)")

    print("tatoeba:")
    n_t = ingest_tatoeba(db)
    print("  %s clips" % format(n_t, ","))

    if args.cv:
        print("common voice:")
        ingest_cv(db, args.cv)

    if args.sps:
        print("spontaneous speech:")
        ingest_sps(db, args.sps)

    print("rebuilding search index…")
    db.execute("INSERT INTO clips_fts(clips_fts) VALUES('rebuild')")
    db.commit()
    db.execute("ANALYZE")
    db.commit()

    total = db.execute("SELECT COUNT(*) FROM clips").fetchone()[0]
    spk = db.execute("SELECT COUNT(DISTINCT speaker) FROM clips").fetchone()[0]
    db.close()
    print("\n%s -> %s clips, %s speakers, %.0f MB"
          % (DB, format(total, ","), format(spk, ","), os.path.getsize(DB) / 1e6))


if __name__ == "__main__":
    main()
