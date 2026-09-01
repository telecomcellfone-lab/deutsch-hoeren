#!/usr/bin/env python3
"""Build the clip index for the spoken-German word search app.

Reads the Tatoeba exports in ./data and writes ./data/clips_tatoeba.json:
a compact list of German sentences that have a human audio recording,
each with its speaker, licence and (where one exists) an English translation.

One German sentence read by three people becomes three clips - that is the
whole point of the app, so recordings are never collapsed by sentence.
"""
import bz2, json, os, sys
from collections import defaultdict

HERE = os.path.dirname(os.path.abspath(__file__))
DATA = os.path.join(HERE, "data")


def rows(path, sep="\t"):
    op = bz2.open if path.endswith(".bz2") else open
    with op(path, "rt", encoding="utf-8", newline="") as fh:
        for line in fh:
            line = line.rstrip("\n").rstrip("\r")
            if line:
                yield line.split(sep)


def main():
    # 1. sentence_id -> [(audio_id, speaker, licence, attribution), ...]
    audio = defaultdict(list)
    for r in rows(os.path.join(DATA, "sentences_with_audio.csv")):
        if len(r) < 3:
            continue
        sid, aid, user = r[0], r[1], r[2]
        lic = r[3] if len(r) > 3 else ""
        att = r[4] if len(r) > 4 else ""
        audio[sid].append((aid, user, lic, att))
    print(f"audio rows            : {sum(len(v) for v in audio.values()):,} "
          f"across {len(audio):,} sentences (all languages)")

    # 2. German sentences that have audio
    de = {}
    for r in rows(os.path.join(DATA, "deu_sentences.tsv.bz2")):
        if len(r) >= 3 and r[0] in audio:
            de[r[0]] = r[2]
    print(f"German with audio     : {len(de):,} sentences")

    # 3. German -> English links, restricted to the sentences we kept
    links = defaultdict(list)
    for r in rows(os.path.join(DATA, "deu-eng_links.tsv.bz2")):
        if len(r) >= 2 and r[0] in de:
            links[r[0]].append(r[1])
    wanted = {e for v in links.values() for e in v}
    print(f"linked English ids    : {len(wanted):,}")

    # 4. English text for those ids only
    en = {}
    for r in rows(os.path.join(DATA, "eng_sentences.tsv.bz2")):
        if len(r) >= 3 and r[0] in wanted:
            en[r[0]] = r[2]
    print(f"English resolved      : {len(en):,}")

    # 5. Emit one record per RECORDING, not per sentence.
    #    [audio_id, german, english, speaker, licence]
    clips, speakers, no_en = [], defaultdict(int), 0
    for sid, text in de.items():
        eng = ""
        for eid in links.get(sid, []):
            if eid in en:
                eng = en[eid]
                break
        if not eng:
            no_en += 1
        for aid, user, lic, att in audio[sid]:
            clips.append([aid, text, eng, user, lic])
            speakers[user] += 1

    clips.sort(key=lambda c: (-len(speakers[c[3]]) if False else 0, c[1]))
    out = os.path.join(DATA, "clips_tatoeba.json")
    with open(out, "w", encoding="utf-8") as fh:
        json.dump(clips, fh, ensure_ascii=False, separators=(",", ":"))

    print(f"\nclips written         : {len(clips):,}  -> {out}")
    print(f"  size                : {os.path.getsize(out)/1e6:.1f} MB")
    print(f"  distinct speakers   : {len(speakers):,}")
    print(f"  without translation : {no_en:,} sentences")
    print("\ntop speakers by clip count:")
    for user, n in sorted(speakers.items(), key=lambda kv: -kv[1])[:15]:
        print(f"  {n:7,}  {user}")
    licences = defaultdict(int)
    for c in clips:
        licences[c[4] or "(none stated)"] += 1
    print("\nlicences:")
    for lic, n in sorted(licences.items(), key=lambda kv: -kv[1]):
        print(f"  {n:7,}  {lic}")


if __name__ == "__main__":
    main()
