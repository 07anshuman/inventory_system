from pydantic import BaseModel, Field
from typing import List, Optional, Dict, Any, Union

# Item usage model
class ItemUsage(BaseModel):
    itemId: str
    name: str
    remainingUses: int

# Item input model
class ItemInput(BaseModel):
    itemId: Optional[str] = None
    name: Optional[str] = None

# Simulation changes model
class SimulationChanges(BaseModel):
    itemsUsed: List[ItemUsage] = []
    itemsExpired: List[ItemUsage] = []
    itemsDepletedToday: List[ItemUsage] = []

# Simulation request model
class SimulationRequest(BaseModel):
    numOfDays: Optional[int] = Field(None, description="Number of days to simulate")
    toTimestamp: Optional[str] = Field(None, description="ISO format timestamp to simulate to")
    itemsToBeUsedPerDay: List[Union[Dict[str, Any], ItemInput]] = Field(
        ..., 
        description="List of items to be used per day"
    )
    
    class Config:
        schema_extra = {
            "example": {
                "numOfDays": 7,
                "itemsToBeUsedPerDay": [
                    {
                        "itemId": "item-123",
                        "name": "Medical Kit"
                    },
                    {
                        "itemId": "item-456",
                        "name": "Food Ration"
                    }
                ]
            }
        }

# Simulation response model
class SimulationResponse(BaseModel):
    success: bool
    newDate: str
    changes: SimulationChanges
    message: Optional[str] = None
    
    class Config:
        schema_extra = {
            "example": {
                "success": True,
                "newDate": "2025-04-11T12:35:00",
                "changes": {
                    "itemsUsed": [
                        {
                            "itemId": "item-123",
                            "name": "Medical Kit",
                            "remainingUses": 4
                        }
                    ],
                    "itemsExpired": [
                        {
                            "itemId": "item-456",
                            "name": "Food Ration",
                            "remainingUses": 0
                        }
                    ],
                    "itemsDepletedToday": [
                        {
                            "itemId": "item-456",
                            "name": "Food Ration",
                            "remainingUses": 0
                        }
                    ]
                }
            }
        }

