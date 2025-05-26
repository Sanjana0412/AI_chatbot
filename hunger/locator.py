from fastapi import APIRouter, Query
import math
import re

router = APIRouter()

# Full food bank data embedded as a Python list
foodbanks = [
  {
    "name": "Hope Food Center",
    "address": "123 Hope Street, New York, NY 10001",
    "latitude": 40.753182,
    "longitude": -73.982253
  },
  {
    "name": "Second Harvest Community Bank",
    "address": "987 Harvest Rd, Brooklyn, NY 11201",
    "latitude": 40.693943,
    "longitude": -73.985880
  },
  {
    "name": "Sunrise Pantry",
    "address": "4321 Sunrise Ave, Bronx, NY 10453",
    "latitude": 40.856415,
    "longitude": -73.912834
  },
  {
    "name": "Feeding Hands Center",
    "address": "284 Feeding Ln, Jersey City, NJ 07306",
    "latitude": 40.733125,
    "longitude": -74.071789
  },
  {
    "name": "Compassion Kitchen",
    "address": "22 Kindness Blvd, Queens, NY 11375",
    "latitude": 40.720822,
    "longitude": -73.844849
  },
  {
    "name": "NeighborCare Food Distribution",
    "address": "77 Community Way, Newark, NJ 07104",
    "latitude": 40.758231,
    "longitude": -74.171013
  },
  {
    "name": "Unity Food Relief",
    "address": "101 Unity Rd, Harlem, NY 10027",
    "latitude": 40.811550,
    "longitude": -73.946477
  },
  {
    "name": "Bridge to Nourishment",
    "address": "456 Bridge Street, Staten Island, NY 10301",
    "latitude": 40.643748,
    "longitude": -74.085081
  },
  {
    "name": "Helping Hands Food Program",
    "address": "789 Giving Ave, Long Island, NY 11510",
    "latitude": 40.654321,
    "longitude": -73.609321
  },
  {
    "name": "Caring Community Meals",
    "address": "369 Care St, White Plains, NY 10601",
    "latitude": 41.033986,
    "longitude": -73.762909
  },
  {
    "name": "Bengaluru Food Bank",
    "address": "50 Food Street, Bengaluru, Karnataka 560001, India",
    "latitude": 12.971599,
    "longitude": 77.594566
  },
  {
    "name": "Mumbai Hunger Relief",
    "address": "102 Hunger Lane, Mumbai, Maharashtra 400001, India",
    "latitude": 19.076090,
    "longitude": 72.877426
  },
  {
    "name": "Chennai Food Aid Center",
    "address": "23 Relief Rd, Chennai, Tamil Nadu 600001, India",
    "latitude": 13.082680,
    "longitude": 80.270718
  },
  {
    "name": "Delhi Community Kitchen",
    "address": "77 Hope Blvd, Delhi 110001, India",
    "latitude": 28.613939,
    "longitude": 77.209021
  },
  {
    "name": "Kolkata Food Help",
    "address": "12 Kindness Ave, Kolkata, West Bengal 700001, India",
    "latitude": 22.572646,
    "longitude": 88.363895
  }
]

def normalize_text(text):
    text = text.lower().strip()
    text = re.sub(r'[^\w\s]', '', text)
    text = re.sub(r'\s+', ' ', text)
    return text

def haversine(lat1, lon1, lat2, lon2):
    R = 6371  # Earth radius in km
    phi1, phi2 = math.radians(lat1), math.radians(lat2)
    dphi = math.radians(lat2 - lat1)
    dlambda = math.radians(lon2 - lon1)
    a = math.sin(dphi / 2) ** 2 + math.cos(phi1) * math.cos(phi2) * math.sin(dlambda / 2) ** 2
    c = 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))
    return R * c

@router.get("/foodbanks")
def find_foodbanks(latitude: float = Query(None), longitude: float = Query(None), query: str = Query("")):
    if latitude is not None and longitude is not None:
        nearby = []
        for fb in foodbanks:
            dist = haversine(latitude, longitude, fb["latitude"], fb["longitude"])
            if dist <= 20:
                fb_copy = fb.copy()
                fb_copy["distance_km"] = round(dist, 2)
                nearby.append(fb_copy)

        if not nearby:
            return {
                "response": "I couldn’t find any food banks within 20 km of your location.",
                "level": "medium",
                "suggestions": []
            }

        return {
            "response": f"I found {len(nearby)} food bank(s) near you.",
            "level": "low",
            "suggestions": [fb["name"] for fb in nearby[:5]],
            "results": sorted(nearby, key=lambda x: x["distance_km"])
        }

    elif query:
        normalized_query = normalize_text(query)
        filtered = []
        for fb in foodbanks:
            name = normalize_text(fb["name"])
            address = normalize_text(fb["address"])
            if normalized_query in name or normalized_query in address:
                filtered.append(fb)

        if not filtered:
            return {
                "response": f"I couldn’t find any food banks matching '{query}'. Try another place or keyword.",
                "level": "medium",
                "suggestions": []
            }

        return {
            "response": f"I found {len(filtered)} food bank(s) that match your search.",
            "level": "low",
            "suggestions": [fb["name"] for fb in filtered[:5]],
            "results": filtered
        }

    return {
        "response": "Please provide either your location (latitude & longitude) or a keyword like city or area name.",
        "level": "medium",
        "suggestions": []
    }
