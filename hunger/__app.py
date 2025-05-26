import os
import requests
import gradio as gr
from dotenv import load_dotenv
from urllib3.util.retry import Retry
from requests.adapters import HTTPAdapter

load_dotenv()

BACKEND_URL = os.getenv("BACKEND_URL", "http://127.0.0.1:8000")

session = requests.Session()
retry_strategy = Retry(
    total=3,
    backoff_factor=1,
    status_forcelist=[500, 502, 503, 504]
)
adapter = HTTPAdapter(max_retries=retry_strategy)
session.mount("http://", adapter)
session.mount("https://", adapter)

def check_backend_connection():
    try:
        response = session.get(f"{BACKEND_URL}/", timeout=5)
        return response.status_code == 200
    except requests.exceptions.RequestException:
        return False

def find_foodbanks(address):
    if not address.strip():
        return "⚠️ Please enter an address"
    try:
        params = {"query": address}
        response = session.get(f"{BACKEND_URL}/locator/foodbanks", params=params, timeout=10)
        if not response.ok:
            return f"❌ API Error: {response.status_code} - {response.text}"
        data = response.json()
        if "results" not in data or not data["results"]:
            return f"ℹ️ {data.get('response', 'No matching food banks found.')}"
        
        results = []
        for fb in data["results"][:5]:
            card = f"## 🏢 {fb.get('name', 'Unknown')}\n"
            card += f"**📍 Address:** {fb.get('address', 'N/A')}\n"
            if "distance_km" in fb:
                card += f"**📏 Distance:** {fb['distance_km']} km\n"
            results.append(card)
        return "\n\n".join(results)
    except requests.exceptions.RequestException as e:
        return f"❌ Connection error: {str(e)}"

def get_recipes_ui(ingredients):
    if not ingredients.strip():
        return "⚠️ Please enter ingredients separated by commas."
    try:
        params = {"ingredients": ingredients}
        response = session.get(f"{BACKEND_URL}/recipe/search", params=params, timeout=10)
        if not response.ok:
            return f"❌ API Error: {response.status_code} - {response.text}"
        data = response.json()
        if "error" in data:
            return f"❌ {data['error']}"
        output = ""
        for r in data.get("recipes", []):
            output += f"### {r['title']}\n"
            output += f"![{r['title']}]({r['image']})\n\n"
            output += f"**Nutrition:** {r['nutrition']}\n\n"
        if not output:
            return "No recipes found."
        return output
    except requests.exceptions.RequestException as e:
        return f"❌ Connection error: {str(e)}"

with gr.Blocks(theme=gr.themes.Soft(), title="HungerHelp Bot") as app:

    if not check_backend_connection():
        gr.Error(
            "🚨 Backend server is not running!\n\n"
            "Please start the FastAPI backend first with:\n"
            "`uvicorn main:app --reload`\n\n"
            "Then refresh this page."
        )

    gr.Markdown("# 🍲 HungerHelp Bot")
    gr.Markdown("### Reduce food waste and find affordable meals")

    with gr.Tabs():

        with gr.Tab("🍳 Find Recipes"):
            gr.Markdown("### Get recipes based on ingredients you have")
            ingredients_input = gr.Textbox(
                label="Ingredients (comma separated)",
                placeholder="e.g. tomato, cheese, basil"
            )
            recipe_output = gr.Markdown()
            get_recipes_btn = gr.Button("Get Recipes", variant="primary")

            get_recipes_btn.click(
                fn=get_recipes_ui,
                inputs=ingredients_input,
                outputs=recipe_output
            )

        with gr.Tab("🏢 Locate Food Banks"):
            gr.Markdown("### Find nearby food banks and pantries")
            location_input = gr.Textbox(
                label="Your Location",
                placeholder="Enter your city or address"
            )
            locate_btn = gr.Button("Search Nearby", variant="primary")
            locate_output = gr.Markdown()

            locate_btn.click(
                fn=find_foodbanks,
                inputs=location_input,
                outputs=locate_output
            )

if __name__ == "__main__":
    app.launch(server_name="0.0.0.0", server_port=7860, share=True, show_error=True)
