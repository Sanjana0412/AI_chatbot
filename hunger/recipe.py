import requests
from fastapi import APIRouter, Query

router = APIRouter()

SPOONACULAR_API_KEY = "5741097a287a45f781ade5e54fb8b4d0"  # Replace with actual key or env var

@router.get("/search")
def get_recipes(ingredients: str = Query(..., description="Comma separated ingredients")):
    url = f"https://api.spoonacular.com/recipes/findByIngredients?ingredients={ingredients}&number=3&apiKey={SPOONACULAR_API_KEY}"
    response = requests.get(url)
    if response.status_code != 200:
        return {"error": "Error fetching recipes from Spoonacular."}

    recipes = response.json()
    results = []
    for r in recipes:
        recipe_id = r['id']
        title = r['title']
        image = r['image']

        # Get nutrition info
        nutrition_url = f"https://api.spoonacular.com/recipes/{recipe_id}/nutritionWidget.json?apiKey={SPOONACULAR_API_KEY}"
        nutri_resp = requests.get(nutrition_url)
        if nutri_resp.status_code != 200:
            nutrition = "Nutrition info unavailable."
        else:
            nutri = nutri_resp.json()
            nutrition = f"Calories: {nutri.get('calories')}, Fat: {nutri.get('fat')}, Carbs: {nutri.get('carbs')}, Protein: {nutri.get('protein')}"

        results.append({
            "title": title,
            "image": image,
            "nutrition": nutrition
        })
    return {"recipes": results}
