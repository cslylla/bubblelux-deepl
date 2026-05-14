# server.py — BubbleLux Demo Server
#
# Minimal Flask server with two routes:
#
#   GET  /           Serve the English source page as a static file.
#   POST /translate  Receive a target language, translate index.html on the fly
#                    using DeepL, and return the translated HTML — Pattern 2
#                    (runtime translation) from translate.py.
#
# In production e-commerce, runtime translation adds per-request latency and
# unpredictable API costs.  Build-time translation (Pattern 1) is preferred.
# This server exists to demonstrate the runtime pattern live.

import os

from dotenv import load_dotenv
from flask import Flask, Response, jsonify, request, send_from_directory

from translate import runtime_translate

# ── 1. Load environment variables from .env ──────────────────────────────────
load_dotenv()

# ── 2. Initialise Flask ───────────────────────────────────────────────────────
app = Flask(__name__)

# Resolve the project root so send_from_directory has an absolute base path.
BASE_DIR = os.path.dirname(os.path.abspath(__file__))


# ── Route: GET / ──────────────────────────────────────────────────────────────
# Serves index.html directly from the project directory.
# This is the English source page — no translation involved.
@app.route("/")
def index():
    return send_from_directory(BASE_DIR, "index.html")


# ── Route: GET /style.css ─────────────────────────────────────────────────────
# Serves the stylesheet from the project root.
@app.route("/style.css")
def serve_css():
    return send_from_directory(".", "style.css")


# ── Route: GET /assets/<filename> ────────────────────────────────────────────
# Serves product images and any other files under the assets/ folder.
# <path:filename> matches nested paths, e.g. /assets/products/rose-vanilla.png
@app.route("/assets/<path:filename>")
def serve_assets(filename):
    return send_from_directory("assets", filename)


# ── Route: POST /translate ────────────────────────────────────────────────────
# Expects a JSON body:  { "target_lang": "DE" }
#
# Reads index.html, calls runtime_translate() with the requested language, and
# returns the fully translated HTML document.  DeepL processes the markup in a
# single API call, preserving all tags and attributes.
@app.route("/translate", methods=["POST"])
def translate():
    data = request.get_json(silent=True) or {}
    target_lang = data.get("target_lang")

    if not target_lang:
        return jsonify({"error": "Missing required field: target_lang"}), 400

    # Read the English source page on every request so any file-level edits
    # are picked up without restarting the server.
    with open(os.path.join(BASE_DIR, "index.html"), "r", encoding="utf-8") as f:
        html_source = f.read()

    # Translate the full HTML document via DeepL and return it directly.
    # The caller receives a ready-to-render HTML page — no client-side patching.
    html, billed_chars = runtime_translate(
        html_source, target_lang=target_lang)

    print(f"Billed characters: {billed_chars}")

    response = Response(html, mimetype="text/html")
    response.headers["X-Billed-Characters"] = str(billed_chars)
    return response


# ── 3. Start the development server ──────────────────────────────────────────
if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)
