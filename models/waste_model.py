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

# Waste item model
class WasteItem(BaseModel):
    itemId: str
    name: str
    reason: str = Field(..., description="Reason for waste: 'Expired', 'Out of Uses'")
    containerId: str
    position: Position

# Waste identification response
class WasteIdentifyResponse(BaseModel):
    success: bool
    message: Optional[str] = None
    wasteItems: Optional[List[WasteItem]] = []

# Return plan request
class ReturnPlanRequest(BaseModel):
    undockingContainerId: str
    undockingDate: str = Field(..., description="ISO format date for undocking")
    maxWeight: float

# Return step model
class ReturnStep(BaseModel):
    step: int
    itemId: str
    itemName: str
    fromContainer: str
    toContainer: str

# Retrieval step model
class RetrievalStep(BaseModel):
    step: int
    action: str = Field(..., description="Action to take: 'remove', 'setAside', 'retrieve', 'placeBack'")
    itemId: str
    itemName: str

# Return item info for manifest
class ReturnItemInfo(BaseModel):
    itemId: str
    name: str
    reason: str

# Return manifest model
class ReturnManifest(BaseModel):
    undockingContainerId: str
    undockingDate: str
    returnItems: List[ReturnItemInfo]
    totalVolume: float
    totalWeight: float

# Return plan response
class ReturnPlanResponse(BaseModel):
    success: bool
    message: Optional[str] = None
    returnPlan: Optional[List[ReturnStep]] = []
    retrievalSteps: Optional[List[RetrievalStep]] = []
    returnManifest: Optional[ReturnManifest] = None

# Complete undocking request
class CompleteUndockingRequest(BaseModel):
    undockingContainerId: str
    timestamp: Optional[str] = Field(None, description="ISO format timestamp")

# Complete undocking response
class CompleteUndockingResponse(BaseModel):
    success: bool
    message: Optional[str] = None
    itemsRemoved: int

# Example data for documentation
class Config:
    schema_extra = {
        "example": {
            "waste_identify_response": {
                "success": True,
                "wasteItems": [
                    {
                        "itemId": "item-123",
                        "name": "Medical Kit",
                        "reason": "Expired",
                        "containerId": "container-A1",
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
                    }
                ]
            }
        }
    }

