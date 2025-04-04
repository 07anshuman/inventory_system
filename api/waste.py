from fastapi import APIRouter, Depends, Query
from typing import Optional
from sqlalchemy.orm import Session

from ..models.waste_model import (
    WasteIdentifyResponse, 
    ReturnPlanRequest, 
    ReturnPlanResponse, 
    CompleteUndockingRequest, 
    CompleteUndockingResponse
)
from ..services.waste_logic import (
    identify_waste_items, 
    generate_return_plan, 
    complete_undocking
)
from ..data.database import get_db

router = APIRouter()

@router.get("/waste/identify", response_model=WasteIdentifyResponse)
async def identify_waste_endpoint(
    db: Session = Depends(get_db)
):
    """
    Identify items that are expired or out of uses and should be returned.
    """
    return identify_waste_items(db)

@router.post("/waste/return-plan", response_model=ReturnPlanResponse)
async def return_plan_endpoint(
    request: ReturnPlanRequest,
    db: Session = Depends(get_db)
):
    """
    Generate a plan for returning waste items to Earth.
    Includes steps for retrieval and loading into the undocking container.
    """
    return generate_return_plan(db, request)

@router.post("/waste/complete-undocking", response_model=CompleteUndockingResponse)
async def complete_undocking_endpoint(
    request: CompleteUndockingRequest,
    db: Session = Depends(get_db)
):
    """
    Mark the undocking as complete and remove the items from inventory.
    """
    return complete_undocking(db, request)

