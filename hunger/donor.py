from fastapi import APIRouter
from chat_model import Donor

router = APIRouter()

# In-memory storage for demo
donations = []

@router.post("/submit")
def submit_donor(donor: Donor):
    donations.append(donor)
    return {"message": "Thank you for your donation!", "data": donor}

@router.get("/all")
def list_donations():
    return donations
