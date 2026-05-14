import os
from dotenv import load_dotenv
from flask import Flask, Response, jsonify, request, send_from_directory

from translate import runtime_translate

# Load environment variables
load_dotenv()

# Initialise Flask 
app = Flask(__name__)

# Resolve the project root
BASE_DIR = os.path.dirname(os.path.abspath(__file__))


# Route: GET / 
@app.route("/")
def index():
    return send_from_directory(BASE_DIR, "index.html")


# Route: GET /style.css 
@app.route("/style.css")
def serve_css():
    return send_from_directory(".", "style.css")


# Route: GET /assets/<filename> 
@app.route("/assets/<path:filename>")
def serve_assets(filename):
    return send_from_directory("assets", filename)


# Route: POST /translate 
@app.route("/translate", methods=["POST"])
def translate():
    data = request.get_json(silent=True) or {}
    target_lang = data.get("target_lang")

    if not target_lang:
        return jsonify({"error": "Missing required field: target_lang"}), 400

    # Read the English source page on every request (edits are picked up without restarting the server)
    with open(os.path.join(BASE_DIR, "index.html"), "r", encoding="utf-8") as f:
        html_source = f.read()

    # Translate the full HTML document via DeepL and return it
    html, billed_chars = runtime_translate(
        html_source, target_lang=target_lang)

    print(f"Billed characters: {billed_chars}")

    response = Response(html, mimetype="text/html")
    response.headers["X-Billed-Characters"] = str(billed_chars)
    return response


# Start the dev server 
if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)
