# translate.py — BubbleLux DeepL Demo
#
# Three HTML translation patterns, each suited to a different production scenario:
#
#   Pattern 1 — Build-time  (build_time_translate)
#     Translate the full page once when content is published, write a static
#     German file, and serve the cached result.  Zero API calls at request time.
#     Recommended for e-commerce: fast, cost-predictable, glossary-consistent.
#
#   Delta      (delta_translate)
#     Parse the page with BeautifulSoup, compare each element's text against a
#     local JSON cache, and only translate what has changed.  Ideal for large
#     product catalogues where most content stays the same between deploys.
#
#   Pattern 2 — Runtime     (runtime_translate)
#     Translate an HTML string on demand, called by the server at request time.
#     Flexible, but adds latency to every page load.  Shown here for demo
#     completeness; build-time translation is preferred in production.

import json
import os

import deepl
import yaml
from bs4 import BeautifulSoup
from dotenv import load_dotenv

from glossary import setup_glossary

# ── 1. Load environment variables from .env ──────────────────────────────────
load_dotenv()
api_key = os.getenv("DEEPL_API_KEY")

# ── 2. Load project config from config.yaml ──────────────────────────────────
with open("config.yaml", "r", encoding="utf-8") as f:
    config = yaml.safe_load(f)

target_lang  = config["target_lang"]   # "DE"
source_lang  = config["source_lang"]   # "EN"
tag_handling = config["tag_handling"]  # "html"
formality    = config["formality"]     # "less"

# ── 3. Initialise the DeepL client ───────────────────────────────────────────
client = deepl.DeepLClient(api_key)


# ─────────────────────────────────────────────────────────────────────────────
# PATTERN 1 — Build-time translation
# Translate the whole page once, write a static file, serve that for every
# German visitor.  One API call per deploy; no latency at request time.
# ─────────────────────────────────────────────────────────────────────────────
def build_time_translate():
    # Read the source HTML file as a plain string — DeepL handles the markup.
    with open("index.html", "r", encoding="utf-8") as f:
        html_source = f.read()

    # Retrieve (or create) the glossary so brand terms are always correct.
    glossary = setup_glossary()

    # Translate the full HTML document in a single API call.
    result = client.translate_text(
        html_source,
        target_lang=target_lang,
        source_lang=source_lang,
        tag_handling=tag_handling,
        formality=formality,
        glossary=glossary.glossary_id,
    )

    # Write the translated HTML to a new file — ready to deploy as-is.
    with open("index.de.html", "w", encoding="utf-8") as f:
        f.write(result.text)

    print(f"  Billed characters : {result.billed_characters}")
    print(f"  Output saved to   : index.de.html")


# ─────────────────────────────────────────────────────────────────────────────
# DELTA TRANSLATION
# Parse the page and only translate elements whose text has changed since the
# last run.  A JSON file acts as a lightweight cache of previously seen text.
# Perfect for catalogues with thousands of products where only a few lines
# change with each content update.
# ─────────────────────────────────────────────────────────────────────────────
def delta_translate():
    CACHE_FILE = "seen_translations.json"

    # Parse the HTML and collect every element that carries an id attribute.
    with open("index.html", "r", encoding="utf-8") as f:
        soup = BeautifulSoup(f, "html.parser")

    current = {
        tag["id"]: tag.get_text(strip=True)
        for tag in soup.find_all(id=True)
        if tag.get_text(strip=True)   # skip empty/structural elements
    }

    # Load the cache that records what was translated on the previous run.
    with open(CACHE_FILE, "r", encoding="utf-8") as f:
        seen = json.load(f)

    # Identify elements whose text is new or has changed since last run.
    changed = {
        elem_id: text
        for elem_id, text in current.items()
        if seen.get(elem_id) != text
    }

    if not changed:
        print("  No changes detected — 0 characters billed")
        return

    # Retrieve the glossary so brand terms stay consistent.
    glossary = setup_glossary()

    total_billed = 0
    translated_ids = []

    for elem_id, text in changed.items():
        result = client.translate_text(
            text,
            target_lang=target_lang,
            source_lang=source_lang,
            formality=formality,
            glossary=glossary.glossary_id,
        )
        total_billed += result.billed_characters
        translated_ids.append(elem_id)

        # Update the cache with the new source text so this element is skipped
        # on the next run unless its content changes again.
        seen[elem_id] = text

    print(f"  Translated IDs    : {', '.join(translated_ids)}")
    print(f"  Billed characters : {total_billed}")

    # Persist the updated cache for the next delta run.
    with open(CACHE_FILE, "w", encoding="utf-8") as f:
        json.dump(seen, f, ensure_ascii=False, indent=2)

    print(f"  Cache updated     : {CACHE_FILE}")


# ─────────────────────────────────────────────────────────────────────────────
# PATTERN 2 — Runtime translation
# Called by server.py with a freshly-rendered HTML string.  Translates on
# every request — useful when content is fully dynamic (e.g. personalised
# pages).  In production e-commerce, prefer build-time translation with a
# cache to avoid per-request latency and unpredictable API costs.
# ─────────────────────────────────────────────────────────────────────────────
def runtime_translate(html_string: str, target_lang: str = target_lang) -> tuple[str, int]:
    # target_lang defaults to the value in config.yaml ("DE") so that existing
    # calls from translate.py's __main__ block continue to work unchanged.
    # server.py passes the language requested by the client at runtime.
    glossary = setup_glossary()

    result = client.translate_text(
        html_string,
        target_lang=target_lang,
        source_lang=source_lang,
        tag_handling=tag_handling,
        formality=formality,
        glossary=glossary.glossary_id,
    )

    return result.text, result.billed_characters


# ─────────────────────────────────────────────────────────────────────────────
# MAIN — run all demo patterns in sequence
# ─────────────────────────────────────────────────────────────────────────────
if __name__ == "__main__":
    print("\n── Pattern 1: Build-time translation ───────────────────────────────")
    build_time_translate()

    print("\n── Delta translation ────────────────────────────────────────────────")
    delta_translate()

    print("\n── Pattern 2: Runtime translation ──────────────────────────────────")
    print("  runtime_translate() is called by server.py — not run here directly.")
