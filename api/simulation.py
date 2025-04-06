from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from models.simulation_model import SimulationRequest, SimulationResponse
from services.simulation_logic import simulate_day
from data.database import get_db


router = APIRouter()

@router.post("/simulate/day", response_model=SimulationResponse)
async def simulate_day_endpoint(request: SimulationRequest, db: Session = Depends(get_db)):
    """
    Simulate daily item usage and track changes such as items used, expired, and depleted.
    """
    return simulate_day(db, request)

