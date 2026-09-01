# Deutsch hören

**Type a German word. Hear real people say it, in a real sentence.**

A self-hosted, offline-first alternative to [YouGlish](https://youglish.com) for
German, built on open speech corpora. One narrator teaches you one accent; this
searches **985,052 recordings from 19,759 speakers** and plays them back to you
one after another, with an English translation underneath where one exists.

Nothing is sent anywhere. The corpus sits on your disk, the search runs in
SQLite, and the page is served from `127.0.0.1`.

![no screenshot yet](https://img.shields.io/badge/python-3.9%2B-blue) ![licence](https://img.shields.io/badge/licence-MIT-green)

---

## What it searches

| Source | Recordings | Voices | Translations |
|---|---|---|---|
| **Common Voice** (local mp3s) | 951,850 | 19,720 | no |
| **Tatoeba** (streamed from tatoeba.org) | 32,940 | 12 | 31,585 have English |
| **Spontaneous Speech** (local mp3s) | 262 | 27 | no, but each shows its prompt |
| **Wikimedia Commons** (fetched live) | the word alone | ~1–3 | n/a |

Tatoeba comes back first so translated examples surface first; Common Voice
supplies the range. *Flussbett* returns 23 recordings from 23 different
speakers where Tatoeba alone had none.

Full detail on match modes, the speaker-rotation shuffle, IPA, keyboard
shortcuts and the licence of every clip: **[spoken/README.md](spoken/README.md)**.

---

## Try it in five minutes (Tatoeba only, no big download)

Needs Python 3.9+ and about 120 MB.

```bash
git clone https://github.com/YOURNAME/deutsch-hoeren.git
cd deutsch-hoeren/spoken/data
curl -sLO https://downloads.tatoeba.org/exports/per_language/deu/deu_sentences.tsv.bz2
curl -sLO https://downloads.tatoeba.org/exports/per_language/deu/deu-eng_links.tsv.bz2
curl -sLO https://downloads.tatoeba.org/exports/per_language/eng/eng_sentences.tsv.bz2
curl -sLO https://downloads.tatoeba.org/exports/sentences_with_audio.tar.bz2
tar -xjf sentences_with_audio.tar.bz2
cd ..
python _build_index.py    # -> data/clips_tatoeba.json
python _build_app.py      # -> ../word-audio-search.html
```

Open `word-audio-search.html`. That single file works with no server at all,
on 32,940 Tatoeba recordings. It is the whole app minus the million clips.

## The full corpus (19,759 voices)

Adds Mozilla **Common Voice** (CC0): a 35 GB archive that unpacks to about a
million mp3s. Free, but it needs a Mozilla account for the download link.

```bash
# 1. get the archive (prompts for your key, resumes if the link expires)
powershell -ExecutionPolicy Bypass -File spoken/_download_commonvoice.ps1

# 2. unpack it OUTSIDE this repo
tar -xzf <the-downloaded>.tar.gz -C C:\data\commonvoice

# 3. load it into SQLite (~1 hour for a million files)
python spoken/_ingest.py --cv "C:\data\commonvoice"

# 4. run it
python spoken/serve.py          # http://127.0.0.1:8731
```

On Windows, `Setup-CommonVoice.bat` does steps 2–3 and `Deutsch-hoeren.bat`
does step 4, both by double-click.

**Keep the audio outside the working tree.** A million files inside a repo
makes `git status` crawl even when they are ignored, and they are reproducible
from the archive. `data/spoken.db` records where they live, so nothing else
needs the path.

Optional extra: **Spontaneous Speech** (262 clips of unscripted talk — the
*ehm*s, the restarts, the real sentence melody), 35 MB, CC0, from the
[Mozilla Data Collective](https://mozilladatacollective.com/):

```bash
python spoken/_ingest.py --sps "C:\data\commonvoice\sps-corpus-4.0-2026-06-12-de"
```

`_ingest.py` replaces only the sources you give it, so re-loading one leaves
the others alone.

---

## Another language?

Nothing here is German at the core. Common Voice ships 100+ languages in the
same `validated.tsv` schema, and Tatoeba exports every language pair the same
way. To retarget:

- swap the Tatoeba export filenames in `_build_index.py` (`deu`/`eng`)
- point `_ingest.py --cv` at that language's corpus folder
- the UI strings in `app_template.html` are German (`Stimmen mischen`, `Treffer`)
- `/api/ipa` proxies DWDS, which is German-only — drop it or swap the source

The column-name mapping in `_ingest.py` is deliberate, not incidental: the
Common Voice schema drifted between corpus versions (`accent` became `accents`,
`sentence_id` appeared), so it reads the header and maps by name. Position-based
parsing breaks.

---

## Why this exists / prior art

- **[YouGlish](https://youglish.com)** — the closest thing, and the inspiration.
  Proprietary, online-only, pulls from YouTube, so you get whatever the video
  gives you and no control over the corpus.
- **[Forvo](https://forvo.com)** — the biggest pronunciation dictionary, but
  single words in isolation, not words inside sentences. Proprietary.
- **[Tatoeba](https://tatoeba.org)** — has the sentences and some audio, and is
  fully open, but is a sentence database with a search box, not a listening
  drill: no speaker rotation, no loop, no speed control, 12 German voices.
- **[Artikulate](https://apps.kde.org/artikulate/)** (KDE) — open source, but a
  pronunciation *trainer* built on fixed authored courses, not a search over a
  corpus.

I could not find an open-source tool that does the YouGlish thing — arbitrary
word, many different speakers, real sentences, self-hosted — which is why this
got built. If one exists, please open an issue and I will link it.

---

## Licence

Code: **MIT**, see [LICENSE](LICENSE).

The corpora are **not** distributed here and carry their own terms — Common
Voice CC0, Tatoeba sentences CC BY 2.0 FR, Tatoeba audio per-reciter (many
recordings state no licence, which is why the app streams them from tatoeba.org
and never copies audio locally), Commons audio per-uploader with credit shown.
Details in [LICENSE](LICENSE) and [spoken/README.md](spoken/README.md).
