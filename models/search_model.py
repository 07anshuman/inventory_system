from pydantic import BaseModel, Field
from typing import List, Optional
from datetime import datetime

# Base coordinate model
class Coordinates(BaseModel):
    width: float
    depth: float
    height: float

# Position model with start and end coordinates
class Position(BaseModel):
    startCoordinates: Coordinates
    endCoordinates: Coordinates

# Retrieval step model
class RetrievalStep(BaseModel):
    step: int
    action: str = Field(..., description="Action to take: 'remove', 'setAside', 'retrieve', 'placeBack'")
    itemId: str
    itemName: str

# Item detail model
class ItemDetail(BaseModel):
    itemId: str
    name: str
    containerId: str
    zone: str
    position: Position

# Search response model
class SearchResponse(BaseModel):
    success: bool
    found: bool
    message: Optional[str] = None
    item: Optional[ItemDetail] = None
    retrievalSteps: Optional[List[RetrievalStep]] = None

# Retrieve request model
class RetrieveRequest(BaseModel):
    itemId: str
    userId: str
    timestamp: Optional[str] = Field(None, description="ISO format timestamp")

# Retrieve response model
class RetrieveResponse(BaseModel):
    success: bool
    message: Optional[str] = None

# Place request model
class PlaceRequest(BaseModel):
    itemId: str
    userId: str
    timestamp: Optional[str] = Field(None, description="ISO format timestamp")
    containerId: str
    position: Position

# Place response model
class PlaceResponse(BaseModel):
    success: bool
    message: Optional[str] = None

# Example data for documentation
class Config:
    schema_extra = {
        "example": {
            "search_response": {
                "success": True,
                "found": True,
                "item": {
                    "itemId": "item-123",
                    "name": "Medical Kit",
                    "containerId": "container-A1",
                    "zone": "Medical",
                    "position": {
                        "startCoordinates": {
                            "width": 10,
                            "depth": 20,
                            "height": 30
                        },
                        "endCoordinates": {
                            "width": 20,
                            "depth": 30,
                            "height": 40
                        }
                    }
                },
                "retrievalSteps": [
                    {
                        "step": 1,
                        "action": "setAside",
                        "itemId": "item-456",
                        "itemName": "Oxygen Tank"
                    },
                    {
                        "step": 2,
                        "action": "retrieve",
                        "itemId": "item-123",
                        "itemName": "Medical Kit"
                    },
                    {
                        "step": 3,
                        "action": "placeBack",
                        "itemId": "item-456",
                        "itemName": "Oxygen Tank"
                    }
                ]
            }
        }
    }

