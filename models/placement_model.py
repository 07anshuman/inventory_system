from pydantic import BaseModel
from typing import List, Optional

class Coordinates(BaseModel):
    width: float
    depth: float
    height: float

class Position(BaseModel):
    startCoordinates: Coordinates
    endCoordinates: Coordinates

class Item(BaseModel):
    itemId: str
    name: str
    containerId: str
    position: Position

class Container(BaseModel):
    containerId: str
    zone: str
    width: float
    depth: float
    height: float

class PlaceRequest(BaseModel):
    itemId: str
    userId: str
    timestamp: str
    containerId: str
    position: Position

