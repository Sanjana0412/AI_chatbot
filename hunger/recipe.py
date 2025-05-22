import os
import requests
import logging
from fastapi import APIRouter, HTTPException
from chat_model import RecipeRequest
from dotenv import load_dotenv

load_dotenv()

router = APIRouter()
SPOONACULAR_KEY = os.getenv("SPOONACULAR_KEY")
logger = logging.getLogger(__name__)

@router.post("/suggest")
def suggest_recipes(req: RecipeRequest):
    if not SPOONACULAR_KEY:
        logger.error("Spoonacular API key not configured")
        raise HTTPException(
            status_code=500,
            detail="Recipe service not configured properly"
        )
    
    if not req.ingredients.strip():
        raise HTTPException(
            status_code=400,
            detail="Please provide at least one ingredient"
        )
    
    try:
        url = "https://api.spoonacular.com/recipes/findByIngredients"
        params = {
            "ingredients": req.ingredients,
            "number": 5,  # Get 5 recipes
            "apiKey": SPOONACULAR_KEY,
            "ranking": 2,  # Maximize used ingredients
            "ignorePantry": True  # Ignore pantry staples
        }
        
        logger.info(f"Requesting recipes for ingredients: {req.ingredients}")
        response = requests.get(url, params=params, timeout=10)
        response.raise_for_status()
        
        recipes = response.json()
        if not recipes:
            return {"message": "No recipes found with these ingredients"}
        
        return recipes
    except requests.exceptions.RequestException as e:
        logger.error(f"Recipe API error: {str(e)}")
        raise HTTPException(
            status_code=502,
            detail=f"Could not fetch recipes: {str(e)}"
        )
