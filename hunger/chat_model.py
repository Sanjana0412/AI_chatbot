from pydantic import BaseModel

class RecipeRequest(BaseModel):
    ingredients: str

class LocationRequest(BaseModel):
    address: str

