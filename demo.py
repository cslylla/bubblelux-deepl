import deepl
from dotenv import load_dotenv
import os

load_dotenv()
client = deepl.DeepLClient(os.getenv("DEEPL_API_KEY"))

html = """
<h1> Our Collection </h1>
<p> Each bath bomb is <strong>handcrafted</strong> with pure botanical ingredients, designed to turn your bath into a <em>ritual</em>.</p>
<ul>
    <li> Free returns within 30 days </li>
    <li> 100 % natural ingredients </li>
    <li> Handcrafted in Switzerland </li>
</ul>
<p> Discover our <a href = "/collection"> full collection </a> and find your perfect match. </p>
<img src = "assets/products/rose-vanilla.png" alt = "Rose and Vanilla Dream bath bomb"/>
"""

result = client.translate_text(
    html,
    target_lang="DE",
    source_lang="EN",
    tag_handling="html",
    tag_handling_version="v2"
)

print(result.text)
print(f"Billed characters: {result.billed_characters}")
