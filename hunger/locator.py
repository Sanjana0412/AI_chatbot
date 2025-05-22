import os
import requests
import logging
from fastapi import APIRouter, HTTPException
from chat_model import LocationRequest
from dotenv import load_dotenv

load_dotenv()

router = APIRouter()
GOOGLE_MAPS_KEY = os.getenv("GOOGLE_API_KEY")
logger = logging.getLogger(__name__)

@router.post("/foodbanks")
def find_foodbanks(location: LocationRequest):
    if not GOOGLE_MAPS_KEY:
        logger.error("Google Maps API key not configured")
        raise HTTPException(
            status_code=500,
            detail="Location service not configured properly"
        )
    
    if not location.address.strip():
        raise HTTPException(
            status_code=400,
            detail="Please provide a location"
        )
    
    try:
        url = "https://maps.googleapis.com/maps/api/place/textsearch/json"
        params = {
            "query": "food bank near " + location.address,
            "key": GOOGLE_MAPS_KEY,
            "radius": 10000,  # 10km radius
            "type": "food_bank|nonprofit"
        }
        
        logger.info(f"Searching food banks near: {location.address}")
        response = requests.get(url, params=params, timeout=10)
        response.raise_for_status()
        
        data = response.json()
        if data.get("status") != "OK":
            return {"results": [], "message": "No food banks found"}
        
        return data
    except requests.exceptions.RequestException as e:
        logger.error(f"Google Maps API error: {str(e)}")
        raise HTTPException(
            status_code=502,
            detail=f"Could not search locations: {str(e)}"
        )