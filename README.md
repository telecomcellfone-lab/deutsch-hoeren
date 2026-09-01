# Deutsch hören

**Type a German word. Hear real people say it, in a real sentence.**

This is a free tool you run on your own computer. It is like
[YouGlish](https://youglish.com), but offline. You type a German word. It finds
that word inside **985,052 recordings from 19,759 different speakers** and plays
them to you one after another. Where an English translation exists, it is shown
under the sentence.

One audiobook narrator only teaches you one voice. This gives you a thousand.

It works with no internet. The recordings sit on your own disk. Nothing you type
is sent anywhere.

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

The server has to be running. Anki on a computer works; AnkiDroid and AnkiMobile
cannot reach `127.0.0.1` on your PC.

Copy-paste versions for Anki and for your own HTML decks, plus the narrow
side-panel mode, are in **[examples/](examples/)**.

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
