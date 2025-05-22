from pydantic import BaseModel
from typing import Optional

class Donor(BaseModel):
    name: str
    contact: str
    address: str
    food_description: str

class RecipeRequest(BaseModel):
    ingredients: str

class LocationRequest(BaseModel):
    address: str
