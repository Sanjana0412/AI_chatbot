import os
import requests
import gradio as gr
from dotenv import load_dotenv
from urllib3.util.retry import Retry
from requests.adapters import HTTPAdapter

# Load environment variables
load_dotenv()

# Configuration
BACKEND_URL = os.getenv("BACKEND_URL", "http://127.0.0.1:8000")
GOOGLE_MAPS_KEY = os.getenv("GOOGLE_MAPS_API_KEY")
SPOONACULAR_KEY = os.getenv("SPOONACULAR_API_KEY")

# Configure session with retries
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

def get_address_suggestions(query):
    if len(query) < 3:
        return []
    try:
        url = "https://maps.googleapis.com/maps/api/place/autocomplete/json"
        params = {
            "input": query,
            "types": "address",
            "key": GOOGLE_MAPS_KEY
        }
        response = session.get(url, params=params, timeout=5)
        if response.ok:
            predictions = response.json().get("predictions", [])
            return [pred["description"] for pred in predictions]
        return []
    except requests.exceptions.RequestException:
        return []

def submit_donation(name, contact, address, description):
    if not all([name.strip(), contact.strip(), address.strip(), description.strip()]):
        return "❌ Please fill all fields"
    
    payload = {
        "name": name,
        "contact": contact,
        "address": address,
        "food_description": description,
    }
    
    try:
        response = session.post(
            f"{BACKEND_URL}/donor/submit",
            json=payload,
            timeout=10
        )
        if response.ok:
            return "✅ Thank you for your donation! We'll contact you soon."
        return f"❌ Error: {response.text}"
    except requests.exceptions.RequestException as e:
        return f"❌ Connection error: {str(e)}"

def get_recipes(ingredients):
    if not ingredients.strip():
        return "⚠️ Please enter some ingredients"
    
    try:
        response = session.post(
            f"{BACKEND_URL}/recipe/suggest",
            json={"ingredients": ingredients},
            timeout=10
        )
        
        if not response.ok:
            return f"❌ API Error: {response.status_code} - {response.text}"
        
        recipes = response.json()
        
        if isinstance(recipes, dict) and recipes.get("error"):
            return f"❌ {recipes['error']}"
        
        if not recipes:
            return "🍽️ No recipes found. Try different ingredients."
        
        results = []
        for recipe in recipes[:5]:  # Limit to 5 recipes
            title = recipe.get("title", "Untitled Recipe")
            used = [ing["name"] for ing in recipe.get("usedIngredients", [])]
            missed = [ing["name"] for ing in recipe.get("missedIngredients", [])]
            
            recipe_card = (
                f"## 🍳 {title}\n"
                f"**✅ You have:** {', '.join(used) if used else 'None'}\n"
                f"**❌ You need:** {', '.join(missed) if missed else 'None'}\n"
            )
            results.append(recipe_card)
        
        return "\n\n".join(results)
    
    except requests.exceptions.RequestException as e:
        return f"❌ Connection error: {str(e)}"

def find_foodbanks(address):
    if not address.strip():
        return "⚠️ Please enter an address"
    
    try:
        response = session.post(
            f"{BACKEND_URL}/locator/foodbanks",
            json={"address": address},
            timeout=10
        )
        
        if not response.ok:
            return f"❌ API Error: {response.status_code} - {response.text}"
        
        data = response.json()
        
        if isinstance(data, dict) and data.get("error"):
            return f"❌ {data['error']}"
        
        places = data.get("results", [])
        
        if not places:
            return "🏢 No food banks found nearby. Try a different location."
        
        results = []
        for place in places[:5]:  # Limit to 5 results
            name = place.get("name", "Unknown Food Bank")
            address = place.get("formatted_address", "Address not available")
            rating = place.get("rating", "Not rated")
            
            location_card = (
                f"## 🏢 {name}\n"
                f"**📍 Address:** {address}\n"
                f"**⭐ Rating:** {rating}/5\n"
            )
            results.append(location_card)
        
        return "\n\n".join(results)
    
    except requests.exceptions.RequestException as e:
        return f"❌ Connection error: {str(e)}"

# Initialize Gradio interface
with gr.Blocks(theme=gr.themes.Soft(), title="HungerHelp Bot") as app:
    
    # Backend connection check
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
        with gr.Tab("💚 Donate Food"):
            gr.Markdown("### Donate your excess food to those in need")
            with gr.Row():
                with gr.Column():
                    name = gr.Textbox(label="Your Name", placeholder="John Doe")
                    contact = gr.Textbox(label="Contact Info", placeholder="Phone/Email")
                    address = gr.Textbox(label="Pickup Address", placeholder="Start typing your address...")
                    address_dropdown = gr.Dropdown(
                        label="Address Suggestions",
                        visible=False,
                        interactive=True
                    )
                    description = gr.Textbox(
                        label="Food Description",
                        placeholder="What food are you donating? Include quantity and expiration if possible",
                        lines=3
                    )
                    donate_btn = gr.Button("Submit Donation", variant="primary")
                
                with gr.Column():
                    donate_output = gr.Markdown()
            
            # Address autocomplete logic
            address.change(
                fn=lambda q: gr.Dropdown.update(
                    choices=get_address_suggestions(q),
                    visible=bool(get_address_suggestions(q))
                ),
                inputs=address,
                outputs=address_dropdown
            )
            address_dropdown.select(
                fn=lambda x: x,
                inputs=address_dropdown,
                outputs=address
            )
            donate_btn.click(
                fn=submit_donation,
                inputs=[name, contact, address, description],
                outputs=donate_output
            )
        
        with gr.Tab("🍳 Find Recipes"):
            gr.Markdown("### Get recipes based on ingredients you have")
            with gr.Row():
                with gr.Column():
                    ingredients = gr.Textbox(
                        label="Available Ingredients",
                        placeholder="e.g., chicken, rice, tomatoes",
                        lines=3
                    )
                    recipe_btn = gr.Button("Find Recipes", variant="primary")
                
                with gr.Column():
                    recipe_output = gr.Markdown()
            
            recipe_btn.click(
                fn=get_recipes,
                inputs=ingredients,
                outputs=recipe_output
            )
        
        with gr.Tab("🏢 Locate Food Banks"):
            gr.Markdown("### Find nearby food banks and pantries")
            with gr.Row():
                with gr.Column():
                    location = gr.Textbox(
                        label="Your Location",
                        placeholder="Enter your address or zip code"
                    )
                    locate_btn = gr.Button("Search Nearby", variant="primary")
                
                with gr.Column():
                    locate_output = gr.Markdown()
            
            locate_btn.click(
                fn=find_foodbanks,
                inputs=location,
                outputs=locate_output
            )

if __name__ == "__main__":
    app.launch(
        server_name="0.0.0.0",
        server_port=7860,
        share=True,
        show_error=True
    )