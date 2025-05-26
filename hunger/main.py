from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from recipe import router as recipe_router
from locator import router as locator_router

app = FastAPI(title="HungerHelp Bot API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(recipe_router, prefix="/recipe")
app.include_router(locator_router, prefix="/locator")

@app.get("/")
def root():
    return {"message": "Welcome to HungerHelp Bot API"}
