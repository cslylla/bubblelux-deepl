import json
import os
import deepl
import yaml
from bs4 import BeautifulSoup
from dotenv import load_dotenv
from glossary import setup_glossary

# Load environment variables from .env 
load_dotenv()
api_key = os.getenv("DEEPL_API_KEY")

# Load project config from config.yaml 
with open("config.yaml", "r", encoding="utf-8") as f:
    config = yaml.safe_load(f)

target_lang = config["target_lang"]
source_lang = config["source_lang"]
tag_handling = config["tag_handling"]
formality = config["formality"]

# Initialise the DeepL client 
client = deepl.DeepLClient(api_key)


# Build-time translation
# Translate the whole page once, write a static file
def build_time_translate():
    # Read the source HTML file as a plain string
    with open("index.html", "r", encoding="utf-8") as f:
        html_source = f.read()

    # Retrieve (or create) the glossary
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

    # Write the translated HTML to a new file — ready to deploy
    with open("index.de.html", "w", encoding="utf-8") as f:
        f.write(result.text)

    print(f"  Billed characters : {result.billed_characters}")
    print(f"  Output saved to   : index.de.html")


# DELTA TRANSLATION
# Parse the page and only translate elements whose text has changed since the last run.
def delta_translate():
    CACHE_FILE = "seen_translations.json"

    # Parse the HTML and collect only leaf elements — elements with an id
    with open("index.html", "r", encoding="utf-8") as f:
        soup = BeautifulSoup(f, "html.parser")

    all_id_elements = soup.find_all(id=True)

    current = {}
    for tag in all_id_elements:
        # Skip parent containers
        if tag.find_all(id=True):
            continue
        text = tag.get_text(strip=True)
        if text:
            current[tag["id"]] = text

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

    # Retrieve the glossary
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

        seen[elem_id] = text

    print(f"  Translated IDs    : {', '.join(translated_ids)}")
    print(f"  Billed characters : {total_billed}")

    # Persist the updated cache for the next delta run.
    with open(CACHE_FILE, "w", encoding="utf-8") as f:
        json.dump(seen, f, ensure_ascii=False, indent=2)

    print(f"  Cache updated     : {CACHE_FILE}")


# Runtime translation

def runtime_translate(html_string: str, target_lang: str = target_lang) -> tuple[str, int]:
    
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


# MAIN

if __name__ == "__main__":
    print("\n── Pattern 1: Build-time translation ───────────────────────────────")
    build_time_translate()

    print("\n── Delta translation ────────────────────────────────────────────────")
    delta_translate()

    print("\n── Pattern 2: Runtime translation ──────────────────────────────────")
    print("  runtime_translate() is called by server.py — not run here directly.")
