from datetime import datetime
from sqlalchemy.orm import Session
from typing import Optional, List, Dict, Any

from ..models.search_model import (
    SearchResponse, 
    ItemDetail, 
    Position, 
    Coordinates, 
    RetrievalStep,
    RetrieveRequest, 
    RetrieveResponse, 
    PlaceRequest, 
    PlaceResponse
)
from ..data.database import get_item_by_id, get_items_by_name, log_action, update_item_position

def search_item(
    db: Session, 
    item_id: Optional[str], 
    item_name: Optional[str], 
    user_id: Optional[str]
) -> SearchResponse:
    """
    Search for an item by ID or name and generate retrieval instructions.
    Prioritizes items based on:
    1. Ease of retrieval (items that require moving fewer other items)
    2. Closeness to expiry date
    """
    # Log the search action
    if user_id:
        log_action(db, "search", user_id, item_id or "unknown", item_name or "unknown")
    
    # Find the item(s)
    items = []
    if item_id:
        item = get_item_by_id(db, item_id)
        if item:
            items = [item]
    elif item_name:
        items = get_items_by_name(db, item_name)
    
    if not items:
        return SearchResponse(
            success=True,
            found=False,
            message=f"No items found matching the criteria"
        )
    
    # Select the optimal item based on retrieval ease and expiry date
    selected_item = select_optimal_item(items)
    
    # Generate retrieval steps
    retrieval_steps = generate_retrieval_steps(db, selected_item)
    
    # Create response
    item_detail = ItemDetail(
        itemId=selected_item["id"],
        name=selected_item["name"],
        containerId=selected_item["container_id"],
        zone=selected_item["zone"],
        position=Position(
            startCoordinates=Coordinates(
                width=selected_item["position"]["start"]["width"],
                depth=selected_item["position"]["start"]["depth"],
                height=selected_item["position"]["start"]["height"]
            ),
            endCoordinates=Coordinates(
                width=selected_item["position"]["end"]["width"],
                depth=selected_item["position"]["end"]["depth"],
                height=selected_item["position"]["end"]["height"]
            )
        )
    )
    
    return SearchResponse(
        success=True,
        found=True,
        item=item_detail,
        retrievalSteps=retrieval_steps
    )

def select_optimal_item(items: List[Dict[str, Any]]) -> Dict[str, Any]:
    """
    Select the optimal item from a list based on:
    1. Ease of retrieval (fewer items to move)
    2. Closeness to expiry date
    """
    if len(items) == 1:
        return items[0]
    
    # Sort by expiry date (ascending) and then by retrieval complexity (ascending)
    sorted_items = sorted(
        items,
        key=lambda x: (
            x.get("expiry_date", datetime.max),  # Items closer to expiry first
            x.get("retrieval_complexity", 100)   # Items easier to retrieve first
        )
    )
    
    return sorted_items[0]

def generate_retrieval_steps(db: Session, item: Dict[str, Any]) -> List[RetrievalStep]:
    """
    Generate step-by-step instructions for retrieving an item
    while minimizing movement of other items.
    """
    # Get items that need to be moved to access the target item
    items_to_move = get_blocking_items(db, item)
    
    steps = []
    step_counter = 1
    
    # Add steps for moving blocking items
    for blocking_item in items_to_move:
        steps.append(
            RetrievalStep(
                step=step_counter,
                action="setAside",
                itemId=blocking_item["id"],
                itemName=blocking_item["name"]
            )
        )
        step_counter += 1
    
    # Add step for retrieving the target item
    steps.append(
        RetrievalStep(
            step=step_counter,
            action="retrieve",
            itemId=item["id"],
            itemName=item["name"]
        )
    )
    step_counter += 1
    
    # Add steps for placing back the blocking items
    for blocking_item in reversed(items_to_move):
        steps.append(
            RetrievalStep(
                step=step_counter,
                action="placeBack",
                itemId=blocking_item["id"],
                itemName=blocking_item["name"]
            )
        )
        step_counter += 1
    
    return steps

def get_blocking_items(db: Session, target_item: Dict[str, Any]) -> List[Dict[str, Any]]:
    """
    Identify items that need to be moved to access the target item.
    This is a simplified implementation - in a real system, this would use
    spatial algorithms to determine which items are blocking access.
    """
    # Simplified implementation - in a real system, this would be more complex
    container_id = target_item["container_id"]
    target_position = target_item["position"]
    
    # Get all items in the same container
    container_items = get_items_by_container(db, container_id)
    
    # Filter out the target item
    container_items = [item for item in container_items if item["id"] != target_item["id"]]
    
    # Determine which items are blocking access
    # This is a simplified algorithm - in reality, you'd need more complex spatial reasoning
    blocking_items = []
    for item in container_items:
        if is_blocking(item["position"], target_position):
            blocking_items.append(item)
    
    # Sort blocking items by the order they need to be moved
    # (items on top or in front need to be moved first)
    blocking_items.sort(key=lambda x: get_blocking_priority(x["position"], target_position))
    
    return blocking_items

def is_blocking(item_position: Dict[str, Any], target_position: Dict[str, Any]) -> bool:
    """
    Determine if an item is blocking access to the target item.
    This is a simplified implementation.
    """
    # Simplified check - in reality, this would be more complex
    # Check if item is directly in front of or on top of the target
    if (item_position["start"]["height"] >= target_position["end"]["height"] and
        item_position["start"]["width"] <= target_position["end"]["width"] and
        item_position["end"]["width"] >= target_position["start"]["width"] and
        item_position["start"]["depth"] <= target_position["end"]["depth"] and
        item_position["end"]["depth"] >= target_position["start"]["depth"]):
        return True
    return False

def get_blocking_priority(item_position: Dict[str, Any], target_position: Dict[str, Any]) -> int:
    """
    Calculate a priority value for blocking items.
    Items with higher priority need to be moved first.
    """
    # Simplified priority calculation - in reality, this would be more complex
    # Higher height means the item is on top and should be moved first
    return item_position["start"]["height"]

def get_items_by_container(db: Session, container_id: str) -> List[Dict[str, Any]]:
    """
    Get all items in a specific container.
    """
    # This would be implemented to query the database
    # Simplified implementation for now
    return []

def retrieve_item(db: Session, request: RetrieveRequest) -> RetrieveResponse:
    """
    Log that an item has been retrieved and mark it as used once.
    """
    try:
        # Log the retrieval action
        log_action(
            db, 
            "retrieve", 
            request.userId, 
            request.itemId, 
            None, 
            request.timestamp
        )
        
        # Update item usage count
        update_item_usage(db, request.itemId)
        
        return RetrieveResponse(success=True)
    except Exception as e:
        return RetrieveResponse(success=False, message=str(e))

def place_item(db: Session, request: PlaceRequest) -> PlaceResponse:
    """
    Log that an item has been placed back into storage.
    """
    try:
        # Log the placement action
        log_action(
            db, 
            "place", 
            request.userId, 
            request.itemId, 
            None, 
            request.timestamp
        )
        
        # Update item position
        position = {
            "start": {
                "width": request.position.startCoordinates.width,
                "depth": request.position.startCoordinates.depth,
                "height": request.position.startCoordinates.height
            },
            "end": {
                "width": request.position.endCoordinates.width,
                "depth": request.position.endCoordinates.depth,
                "height": request.position.endCoordinates.height
            }
        }
        
        update_item_position(
            db, 
            request.itemId, 
            request.containerId, 
            position
        )
        
        return PlaceResponse(success=True)
    except Exception as e:
        return PlaceResponse(success=False, message=str(e))

def update_item_usage(db: Session, item_id: str) -> None:
    """
    Update the usage count of an item.
    """
    # This would be implemented to update the database
    # Simplified implementation for now
    pass

