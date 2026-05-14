# BubbleLux × DeepL API Demo

![DeepL Logo](/assets/deepl_logo.svg)

*BubbleLux* is a fictional luxury bath bomb webshop used as the context for this technical case study. It demonstrates three HTML translation patterns using the DeepL API (build-time, delta, and runtime) in a realistic e-commerce localisation scenario.

## What it demonstrates

**Build-time translation**: `translate.py` sends the full `index.html` to the DeepL API and writes the result to `index.de.html`. Translate once, serve statically.

**Delta translation**: on subsequent runs, `translate.py` compares the current page against `seen_translations.json` and only sends new or changed leaf elements to the API. Reduces API usage as content evolves.

**Runtime translation**: `server.py` exposes a `/translate` endpoint that translates arbitrary text on demand via a live API call. Used by the language switcher in the browser.

**Glossary**: brand-specific terms (product names, taglines) are enforced across all three patterns using a DeepL glossary, created once via `glossary.py`.

## Project structure

```
bubblelux-deepl/
├── index.html            # Source page (English)
├── index.de.html         # Generated German translation (gitignored)
├── style.css             # Shared stylesheet
├── assets/               # Favicon and product images
├── translate.py          # Build-time and delta translation
├── server.py             # Flask dev server with runtime translation endpoint
├── glossary.py           # Creates the DeepL glossary
├── script.js             # Language switcher logic and runtime translation trigger
├── seen_translations.json# Tracks translated content for delta diffing (gitignored)
├── config.yaml           # Glossary terms and translation config
├── .env.example          # Environment variable template
└── requirements.txt      # Python dependencies
```

## Setup

```bash
git clone https://github.com/cslylla/bubblelux-deepl
cd bubblelux-deepl
python -m venv venv
venv\Scripts\activate        # Windows
# source venv/bin/activate   # macOS/Linux
pip install -r requirements.txt
cp .env.example .env         # then add your DEEPL_API_KEY
python glossary.py
```

A free DeepL API key works — 500,000 characters/month. Get one at [deepl.com/pro-api](https://www.deepl.com/pro-api).

## Running the demo

**Build-time and delta translation:**

```bash
python translate.py
```

The first run translates the full page and writes `index.de.html`. Run it again — only elements that changed since the last run are sent to the API. The output shows which elements were translated and the billed character count.

**Live server (runtime translation):**

```bash
python server.py
```

Open [http://localhost:5000](http://localhost:5000) and use the language dropdown to switch between EN and DE. Text is translated on demand via the `/translate` endpoint.

**Reset for a fresh demo run:**

```bash
echo {} > seen_translations.json
del index.de.html
```

## Notes

- `alt` attributes on images are not translated by the DeepL HTML handling API, this is a known limitation of the API and is covered in the demo.
- `index.de.html` and `seen_translations.json` are gitignored; both are generated at runtime.
- JavaScript and CSS are served as separate static files — do not inline scripts before sending HTML to the DeepL API. In HTML mode, inline `<script>` content may be incorrectly encoded in the response. This is a known v2 behaviour not documented in the current API docs.

## Built with

DeepL Python library · Flask · BeautifulSoup4 · Python 3.13
