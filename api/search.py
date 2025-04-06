from fastapi import APIRouter, Depends, Query
from typing import Optional
from sqlalchemy.orm import Session

from models.search_model import (
    SearchResponse, 
    RetrieveRequest, 
    RetrieveResponse, 
    PlaceRequest, 
    PlaceResponse
)
from services.search_logic import (
    search_item, 
    retrieve_item, 
    place_item
)
from data.database import get_db


router = APIRouter()

@router.get("/search", response_model=SearchResponse)
async def search_endpoint(
    itemId: Optional[str] = Query(None, description="Unique identifier of the item"),
    itemName: Optional[str] = Query(None, description="Name of the item to search"),
    userId: Optional[str] = Query(None, description="ID of the user performing the search"),
    db: Session = Depends(get_db)
):
    """
    Search for an item by ID or name and get retrieval instructions.
    Either itemId or itemName must be provided.
    """
    if not itemId and not itemName:
        return SearchResponse(
            success=False,
            found=False,
            message="Either itemId or itemName must be provided"
        )
    
    return search_item(db, itemId, itemName, userId)

@router.post("/retrieve", response_model=RetrieveResponse)
async def retrieve_endpoint(
    request: RetrieveRequest,
    db: Session = Depends(get_db)
):
    """
    Log that an item has been retrieved from storage.
    This marks the item as used once.
    """
    return retrieve_item(db, request)

@router.post("/place", response_model=PlaceResponse)
async def place_endpoint(
    request: PlaceRequest,
    db: Session = Depends(get_db)
):
    """
    Log that an item has been placed back into storage.
    """
    return place_item(db, request)

