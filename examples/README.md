# Link your flashcards to the app

The app takes a word in the address bar. This one line is the whole feature:

```
http://127.0.0.1:8731/?q=Straße
```

Open that and the app searches `Straße` straight away. So any flashcard deck,
any word list, any notes app that lets you write a link can send you here.

This is what the app is actually for day to day. You meet a new word, you make
a card for it, and the card carries a button. Tap the button and you hear
twenty strangers say that word. You are not guessing at the pronunciation from
the spelling any more.

**The server has to be running.** Start it first with `Deutsch-hoeren.bat`, or
`python spoken/serve.py`. If it is not running the link just fails, it does no
harm.

---

## Anki

Open your note type, click **Cards**, and paste this into the **Back Template**,
under whatever is already there:

```html
<a href="http://127.0.0.1:8731/?q={{Front}}"
   style="display:inline-block;margin-top:12px;padding:6px 12px;
          border:1px solid #888;border-radius:6px;
          text-decoration:none;font-size:15px">
  🎧 Hear real people say {{Front}}
</a>
```

Change `{{Front}}` to whatever your German field is called. If your field is
called `Wort`, use `{{Wort}}` in both places.

Umlauts and ß are fine. You do not have to encode them, the browser does it.

Notes:

- **Anki on the computer works.** Clicking the link opens your normal browser.
- **AnkiDroid and AnkiMobile will not work** with `127.0.0.1`. On a phone that
  address means the phone itself, not your computer. See "Using it from a
  phone" below.

## Any HTML deck of your own

If your deck is a web page you wrote yourself, `link-snippet.html` in this
folder is a working example you can open in a browser and copy from. The
important part is three lines:

```js
function hoerenLink(word) {
  return "http://127.0.0.1:8731/?q=" + encodeURIComponent(word);
}
```

## Side panel mode

Add `&compact=1` and the page shrinks to fit a narrow column, about 300px. It
is meant for embedding the app in an `<iframe>` beside your own tool, so you
can see the card and the recordings at the same time.

```
http://127.0.0.1:8731/?q=Straße&compact=1
```

## Using it from a phone

`127.0.0.1` only ever means "this same machine", so a phone cannot reach it.

The server also deliberately refuses connections from anywhere except your own
computer. That is a safety choice, not an oversight, and there is no setting to
turn it off. If you want this on a phone you would have to change the bind
address in `spoken/serve.py` yourself, and you should only do that on a network
you trust.
