# Deutsch hören

**Type a German word. Hear real people say it, in a real sentence.**

This is a free tool you run on your own computer. It is like
[YouGlish](https://youglish.com), but offline. You type a German word. It finds
that word inside **985,052 recordings from 19,759 different speakers** and plays
them to you one after another. Where an English translation exists, it is shown
under the sentence.

One audiobook narrator only teaches you one voice. This gives you a thousand.

It is for two things:

- **Listening comprehension.** Hearing one word from twenty different people
  trains your ear to catch it whoever is speaking, however fast, wherever they
  are from. That is the skill that decides whether you follow a real
  conversation.
- **Pronunciation.** You hear how the word is actually said by native speakers,
  and copy that, instead of guessing it from the spelling.

Almost all of it works with no internet, and nothing you type is ever sent to
anybody. See [What works offline](#what-works-offline) for the exact split.

![python](https://img.shields.io/badge/python-3.9%2B-blue) ![licence](https://img.shields.io/badge/licence-MIT-green)

---

## What it searches

| Source | Recordings | Voices | Translations |
|---|---|---|---|
| **Common Voice** (local mp3s) | 951,850 | 19,720 | no |
| **Tatoeba** (streamed from tatoeba.org) | 32,940 | 12 | 31,585 have English |
| **Spontaneous Speech** (local mp3s) | 262 | 27 | no, but each shows its prompt |
| **Wikimedia Commons** (fetched live) | the word alone | ~1–3 | n/a |

Tatoeba comes back first so translated examples surface first. Common Voice
supplies the range.

**How many clips will a word get?** That depends entirely on how often people
happened to say it. Measured on a real install:

| Word | Clips |
|---|---|
| `Straße`, `natürlich`, `Kirche` | 600 (the cap) |
| `Frühstück` | 169 |
| `Schornstein` | 61 |
| `Flussbett` | 23 |
| `Wetterleuchten` | 3 |
| `Kummerbund` | 0 |

Obscure words are mostly present, just thin. *Wetterleuchten* appears about
6,000 times in 53 billion words of written German, and three people still
recorded it. One search returns at most 600 clips.

Full detail on match modes, the speaker-rotation shuffle, IPA, keyboard
shortcuts and the licence of every clip: **[spoken/README.md](spoken/README.md)**.

---

## Who you hear

This is the whole point. You do not hear one voice. You hear a crowd.

The speakers are men and women. They are teenagers, people in their twenties,
and people in their seventies and eighties. They come from Germany, Austria and
Switzerland. Of the speakers who chose to say where they are from, 4,676 said
German German, 414 said Austrian German, and 193 said Swiss German. So most
voices are from Germany, but the other two are there in real numbers.

About one speaker in three tells you anything about themselves. When they do,
the app shows it under the clip, like this:

```
Stimme 19720 (Deutschland Deutsch, male, fifties)
```

Two things to be honest about.

- **There are more men than women.** Of the speakers who gave a gender, about
  4,000 said male and about 700 said female. That is the corpus, not a choice
  this app made.
- **The sound quality varies.** These are real people recording at home on
  whatever equipment they own. The audio is generally good, but some clips are
  clearer than others.

That trade is worth it. Online dictionaries usually give you one recording per
word, and more and more of them are made by a computer. A synthetic voice is
always clean and always the same. It cannot show you that a word sounds a
little different in Vienna. It cannot show you that a fast speaker swallows a
syllable, or how the word really sits inside a normal sentence. A thousand real
people can.

---

## What works offline

Not everything, and it would be dishonest to say otherwise.

**Works with no internet** (952,112 clips, 19,747 speakers, 96.7% of the total):

- Common Voice, 951,850 clips. These are mp3 files on your own disk.
- Spontaneous Speech, 262 clips. Also on your disk.
- Search itself, which runs in a local database.

**Needs the internet:**

- Tatoeba, 32,940 clips. These are streamed from tatoeba.org and never copied to
  your disk. That is a licensing choice, not a technical one: many of those
  recordings state no licence, so the app is not entitled to keep a copy.
- **The English translations.** All 31,585 of them are attached to Tatoeba
  sentences. Offline you still hear the German, but nothing is translated.
- The single-word recordings from Wikimedia Commons.
- The IPA line, which is fetched from DWDS. Once fetched it is cached, so a word
  you have looked up before still shows its IPA offline.

So offline you keep the thing that matters most, a million recordings of real
speakers, and you lose the English glosses. On a plane that is a fair trade. At
your desk, leave the internet on and you get everything.

---

## Link it to your flashcards

This is what makes it part of a daily routine instead of a thing you open now
and then.

The app takes a word in the address bar:

```
http://127.0.0.1:8731/?q=Stra%C3%9Fe
```

So any flashcard deck that lets you write a link can send you straight here. You
meet a new word, you make a card for it, and the card gets a button. Press the
button and you hear twenty strangers say that word, instead of guessing the
sound from the spelling.

For **Anki**, this goes in the Back Template of your note type:

```html
<a href="http://127.0.0.1:8731/?q={{Front}}">🎧 Hear real people say {{Front}}</a>
```

The server has to be running first. Then clicking the link on a card opens the
app in your normal browser, already searching that word. Tested in Anki 2.1.65
on Windows.

AnkiDroid and AnkiMobile cannot reach `127.0.0.1` on your PC. That follows from
what `127.0.0.1` means and no version will change it.

Copy-paste versions for Anki and for your own HTML decks, plus the narrow
side-panel mode, are in **[examples/](examples/)**.

---

## Try it in five minutes (Tatoeba only, no big download)

Needs Python 3.9+ and about 47 MB. Note this version **does** need the internet
while you use it, because the Tatoeba audio is streamed. It is a way to try the
idea, not the offline version.

```bash
git clone https://github.com/telecomcellfone-lab/deutsch-hoeren.git
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

Open `word-audio-search.html`. That single file needs no server and no
database. It searches 32,940 Tatoeba recordings, and most of them come with an
English translation. It is the whole app minus the million local clips.

It streams its audio from tatoeba.org, so keep the internet on. Offline is what
the full corpus above is for.

## The full corpus (19,759 voices)

Adds Mozilla **Common Voice** (CC0), from the Mozilla Data Collective:

- **<https://commonvoice.mozilla.org/en/datasets>** is the front door. Pick
  German, and it sends you to the Mozilla Data Collective to download.
- **<https://mozilladatacollective.com/>** is where the file actually lives.

**You need a free account, and it gives you an API key.** There is no public
direct link, because Mozilla wants to count downloads. `_download_commonvoice.ps1`
asks for that key when you run it, uses it once to request a download link, then
wipes it. The key is never written to a file, and it is not in this repo.

If you would rather not deal with a key at all, download it by hand from the
website and skip straight to `_ingest.py`. The script is a convenience, not a
requirement.

It is free, and it is genuinely large:

| | |
|---|---|
| archive to download | 34.8 GB, one file |
| unpacked | 36.4 GB, 1,018,463 mp3 files |
| search database it builds | 273 MB |
| **free space needed during setup** | **about 70 GB** |

You need the 70 GB because the archive and the unpacked copy both exist for a
while. Delete the archive afterwards and you settle at 36.4 GB. Unpacking a
million small files takes about an hour and looks frozen the whole time. It is
not frozen.

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

Optional extra: **Spontaneous Speech** (262 clips of unscripted talk, the
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
- `/api/ipa` proxies DWDS, which is German only, so drop it or swap the source

The column-name mapping in `_ingest.py` is deliberate, not incidental: the
Common Voice schema drifted between corpus versions (`accent` became `accents`,
`sentence_id` appeared), so it reads the header and maps by name. Position-based
parsing breaks.

---

## Why this exists / prior art

- **[YouGlish](https://youglish.com)** is the closest thing to this, and it is
  where the idea came from. It is a very good tool and you should try it. It
  pulls its clips from YouTube, so you also see the speaker and the setting,
  which this app cannot do. Two things to know. The free plan only lets you
  search a limited number of times each day, around fifty when I checked, and
  then it asks you to come back tomorrow. And it needs the internet, because
  the videos live on YouTube. If you use it a lot, pay for it. It is a few
  euros a month and the people who built it earned that. This app is not trying
  to beat YouGlish. It is a free thing you can run when you are offline, or
  when you have used up your searches for the day, or when you want to hear one
  word forty times in a row without spending a search on each one.
- **[Forvo](https://forvo.com)** is the biggest pronunciation dictionary there
  is. But it gives you single words on their own, not words inside a sentence.
  It is also a paid service.
- **[Tatoeba](https://tatoeba.org)** is fully open and it has the sentences and
  some of the audio this app uses. It is a sentence database with a search box,
  though, not a listening drill. There is no speaker shuffle, no loop button, no
  speed control, and only 12 German voices.
- **[Artikulate](https://apps.kde.org/artikulate/)** from KDE is open source,
  but it is a pronunciation trainer built on a fixed set of written courses. You
  cannot search it for any word you like.

I could not find an open source tool that does what YouGlish does: any word you
type, lots of different speakers, real sentences, running on your own machine.
That is why this was built. If one already exists, please open an issue and I
will link to it.

---

## Licence

Code: **MIT**, see [LICENSE](LICENSE).

The speech corpora are **not** included here. Each one has its own terms.
Common Voice is CC0. Tatoeba sentences are CC BY 2.0 FR. Tatoeba audio is
licensed by whoever recorded it, and many recordings state no licence at all,
which is why this app streams them from tatoeba.org and never saves a copy.
Wikimedia Commons audio is credited to its uploader on screen. Details are in
[LICENSE](LICENSE) and [spoken/README.md](spoken/README.md).
