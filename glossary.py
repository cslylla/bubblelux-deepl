import os
import deepl
import yaml
from dotenv import load_dotenv

# ── 1. Load environment variables from .env ──────────────────────────────────
load_dotenv()
api_key = os.getenv("DEEPL_API_KEY")

# ── 2. Load project config from config.yaml ──────────────────────────────────
with open("config.yaml", "r", encoding="utf-8") as f:
    config = yaml.safe_load(f)

glossary_name = config["glossary_name"]   # "BubbleLux Glossary"
source_lang   = config["source_lang"]     # "EN"
target_lang   = config["target_lang"]     # "DE"

# ── 3. BubbleLux brand-specific translation pairs (EN → DE) ──────────────────
entries = {
    "Bath Bomb":                     "Badebombe",
    "Add to Cart":                   "In den Warenkorb",
    "More Info":                     "Mehr erfahren",
    "Free returns within 30 days":   "Kostenlose Rücksendung innerhalb von 30 Tagen",
    "Natural ingredients":           "Natürliche Zutaten",
    "Our Collection":                "Unsere Kollektion",
    "Save for Later":                "Für später speichern",
    "Qty":                           "Menge",
}


def setup_glossary():
    """Create or retrieve the BubbleLux DeepL glossary."""

    # ── 4. Initialise the DeepL client ────────────────────────────────────────
    client = deepl.DeepLClient(api_key)

    # ── 5. Check whether the glossary already exists ─────────────────────────
    # List all glossaries on the account and look for a name + language match.
    existing_glossaries = client.list_glossaries()

    for glossary in existing_glossaries:
        if (
            glossary.name == glossary_name
            and glossary.source_lang.upper() == source_lang.upper()
            and glossary.target_lang.upper() == target_lang.upper()
        ):
            print(f"Glossary already exists — ID: {glossary.glossary_id}")
            return glossary

    # ── 6. Glossary not found — create it now ────────────────────────────────
    glossary = client.create_glossary(
        name=glossary_name,
        source_lang=source_lang,
        target_lang=target_lang,
        entries=entries,
    )

    print(f"Glossary created — ID: {glossary.glossary_id}, "
          f"entries: {glossary.entry_count}")
    return glossary


# ── 7. Run directly for the live demo ────────────────────────────────────────
if __name__ == "__main__":
    setup_glossary()
