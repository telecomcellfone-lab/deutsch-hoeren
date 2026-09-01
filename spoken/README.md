# Spoken-word search — a YouGlish alternative for German

Type a German word, hear it spoken by different people, in a real sentence,
with the English underneath. Built because a single audiobook narrator is one
voice, and one voice is not enough to learn what a word actually sounds like.

This is the reference manual. For setup start at the [top-level README](../README.md).

**Start it:** double-click `../Deutsch-hoeren.bat`. That runs `serve.py` and opens
the browser on the full corpus: **985,052 recordings from 19,759 speakers**.

**Offline fallback:** `../word-audio-search.html` is one self-contained file that
works with no server, on the Tatoeba clips alone. Useful when the corpus drive
is not around.

## What it searches

| Source | What you get | Voices |
|---|---|---|
| **Common Voice** (local mp3s, via `serve.py`) | 951,850 recordings, read aloud, no translations | **19,720** |
| **Tatoeba** (streamed from tatoeba.org) | 32,940 recordings, 31,585 with an English translation | 12 |
| **Spontaneous Speech** (local mp3s, via `serve.py`) | 262 recordings of unscripted talk, each answering a question | 27 |
| **Wikimedia Commons** (fetched live) | the word on its own, from the German Wiktionary pronunciation project | ~1–3 per word |

Results come back Tatoeba first, then spontaneous, then Common Voice, so the
translated examples surface first. Common Voice supplies the range: *Flussbett*
returns 23 recordings from 23 different speakers, *Wetterleuchten* 3 where
Tatoeba alone had none.

A result set is capped at 600 clips. For a common word that is still 400–550
distinct speakers, so the cap costs variety nothing, but it does mean very
common words always return the same 600 rather than a fresh sample.

Each source is searched separately and the small ones hold a reserved share of
that cap (40 for Spontaneous Speech). Without it Common Voice, holding 950k of
the 985k rows, would fill all 600 slots on any common word and the other two
sources would never appear at all.

## Controls

- `Enter` search · `Space` play/pause · `R` restart · `L` loop · `→` next voice ·
  `←` previous · `/` back to the box
- The round button plays and pauses the same clip, resuming where it stopped.
  `↻` restarts it, `∞` loops it until you switch it off. Each clip keeps one
  audio element across re-renders, which is what makes resume work rather than
  restart. Word clips use a separate element so they cannot hijack that state.
- **Stimmen mischen** (on by default) rotates through speakers, so consecutive
  clips are different people rather than eight in a row from the same voice.
- **Tempo** 0.6× to 1.25×.
- **Treffer** match mode:
  - `klug` — whole-word hits if any exist, otherwise compounds. The default.
  - `genau` — whole word only.
  - `Wortanfang` — words starting with what you typed (catches some inflection).
  - `enthält` — anywhere, including inside compounds (`Bett` finds `Bettdecke`).

There is no lemmatiser. Searching `gehen` will not find `ging`; search the form
you want, or use `Wortanfang`.

**Search the modern spelling.** The corpus was recorded after the 1996 spelling
reform, so it is full of `Fluss` and has almost no `Fluß`. Searching the old
spelling returns 3 clips where the new one returns 600. If you are reading an
older book, or anything printed before about 2000, look the word up in its
current form: `Fuß` stays `Fuß`, but `Fluß`, `Faß`, `daß` and `mußte` are now
`Fluss`, `Fass`, `dass` and `musste`.

## Spontaneous speech

Common Voice's other corpus: people answering a question in their own words,
not reading a prepared sentence. So it has the things scripted audio does not —
*ehm*, restarts, trailing-off, real sentence melody, and grammar that a
textbook would mark wrong. That is what German sounds like when nobody is
performing it.

Those clips show the question above the sentence, because an answer on its own
reads as a non sequitur:

```
Frage: Welche Art von Wetter magst du am liebsten und warum?
Ich mag sehr gerne Regen und zwar deswegen weil er einen dazu bringt …
```

They are longer than the rest — 10 seconds is typical, the longest is 64 — so
the loop button matters more here than on a five-word Tatoeba line.

Only 65 of the transcripts have been checked by a second person. The rest say
**Transkript ungeprüft** under the clip. Trust the audio over the text.

## Phonetic spelling

Each search shows the IPA under the header, e.g. `Straße [ˈʃtʀaːsə]`, from
DWDS. An `automatisch` badge means DWDS generated it rather than checking it —
worth distrusting, since even a nonsense word gets one.

DWDS sends no `Access-Control-Allow-Origin`, so the page cannot call it: the
request goes through `serve.py` at `/api/ipa`, which caches every answer
(misses included) in an `ipa_cache` table. A word costs one round trip ever.
Offline mode has no IPA, since there is no server to proxy it.

## Deep-linking from anywhere

`?q=` deep-links a search, so any other tool can link straight into a word:

```
http://127.0.0.1:8731/?q=Stra%C3%9Fe
```

The original use for this was a flashcard deck, whose card backs carry two rows:

```
🔊 YouGlish: Straße
🎧 Deutsch hören: Straße
```

The second needs this server running; the first does not.

## Rebuilding

```bash
python _build_index.py    # data/*.tsv.bz2 -> data/clips_tatoeba.json
python _build_app.py      # + app_template.html -> ../word-audio-search.html
python _ingest.py         # -> data/spoken.db, for the server
```

`_ingest.py` replaces only the sources it is given, so re-loading one leaves
the others alone:

```bash
python _ingest.py --cv  "C:\data\commonvoice"
python _ingest.py --sps "C:\data\commonvoice\sps-corpus-4.0-2026-06-12-de"
```

Edit the UI in `app_template.html`, never in the generated
`word-audio-search.html` — the build overwrites it.

`data/` holds the raw Tatoeba exports (116 MB) and is gitignored. Re-fetch with:

```bash
cd data && for f in per_language/deu/deu_sentences.tsv.bz2 per_language/deu/deu-eng_links.tsv.bz2 per_language/eng/eng_sentences.tsv.bz2 sentences_with_audio.tar.bz2; do curl -sLO "https://downloads.tatoeba.org/exports/$f"; done && tar -xjf sentences_with_audio.tar.bz2
```

Tatoeba refreshes these every Saturday 06:30 UTC.

## Common Voice — installed

Corpus **26.0 (2026-06-12)**, German, CC0. Downloaded 2026-08-19: a 34.77 GB
archive, unpacked to `C:\data\commonvoice\cv-corpus-26.0-2026-06-12\de\`.

That path is deliberately **outside** this repo. A million files inside the
working tree makes `git status` crawl even when ignored, and the clips are
reproducible from the archive, so they do not belong in version control.
`data/spoken.db` records the clips directory, so nothing else needs the path.

Re-running the download (a newer corpus, or another language):

```bash
powershell -ExecutionPolicy Bypass -File _download_commonvoice.ps1
```

It prompts for the key, requests a fresh presigned URL, and downloads with
`curl -C -`. The archive is far larger than the link's lifetime, so if it dies
partway just run it again: it fetches a new URL and resumes the partial file.
Then unpack and ingest:

```bash
tar -xzf "C:\data\commonvoice\common-voice-scripted-speech-<version>-german-<id>.tar.gz" -C "C:\data\commonvoice"
python _ingest.py --cv "C:\data\commonvoice"
```

Or double-click `../Setup-CommonVoice.bat`, which does both. `tar` cannot
resume, so an interrupted unpack restarts from the beginning.

`_ingest.py` walks the folder for `validated.tsv`, reads its header and maps
columns by name — the schema drifted across corpus versions (`accent` became
`accents`, `sentence_id` was added), so position-based parsing breaks. Each
`client_id` becomes a readable label like
`Stimme 19720 (Deutschland Deutsch, male, fifties)`: accent first, because for
pronunciation it matters more than age. Speakers can tick several accents, so
only the first is kept — the full pipe-separated list buries the name.

### Why this needs a server

A million rows will not embed in an HTML file, and Common Voice clips are local
mp3s with no public URL. So the full corpus runs through `serve.py`, which puts
the clips in SQLite with an FTS5 index and answers `/api/search`. Double-click
`../Deutsch-hoeren.bat` to start it.

`app_template.html` handles both: opened as a file it searches the baked-in
Tatoeba clips, served over http it queries the database. So
`../word-audio-search.html` keeps working offline either way.

## Spontaneous Speech — installed

Corpus **sps-corpus-4.0 (2026-06-12)**, German, CC0, from the
[Mozilla Data Collective](https://mozilladatacollective.com/). Downloaded
2026-08-20: a 35 MB archive, unpacked to
`C:\data\commonvoice\sps-corpus-4.0-2026-06-12-de\`, beside the big corpus
and outside this repo for the same reason.

```bash
tar -xzf "<the downloaded .tar.gz>" -C "C:\data\commonvoice"
python _ingest.py --sps "C:\data\commonvoice\sps-corpus-4.0-2026-06-12-de"
```

The archive holds 319 clips (1.21 hours) from 28 speakers. 262 are ingested.
Of the 57 dropped, 55 have no transcript at all, so there is nothing to search
on; the other 2 carry a `transcription-length` flag, the corpus's own way of
saying the transcript does not match its audio. A wrong transcript teaches the
wrong word, so those go rather than get shown. The two clips contributors
reported as broken are already inside the untranscribed 55, but the ingest
checks the reported list anyway, since a future release may transcribe one.

`_ingest.py` reads `ss-corpus-de.tsv` — a different schema from the scripted
corpus: `audio_file` not `path`, `transcription` not `sentence`, plus `prompt`
and `votes`. Speakers are labelled `Stimme S01 (…)` so they cannot collide with
Common Voice's own `Stimme 0001`; the app counts distinct voices by that label.

### No-login alternative

**Multilingual LibriSpeech German** (OpenSLR 94, CC BY 4.0, 29 GB opus, no
account). LibriVox readers, so far fewer speakers than Common Voice, but book
prose, which matches the novel's register better than Common Voice's
Wikipedia-derived sentences.

## Licences

Tatoeba audio carries the reciter's chosen licence, shown under every clip.
16,344 of the 32,940 recordings state no licence, which means they may not be
reused outside Tatoeba — so the app streams from Tatoeba and never copies audio
locally. Commons audio is shown with its uploader credited.
