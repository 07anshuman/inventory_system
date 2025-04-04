from datetime import datetime
from sqlalchemy.orm import Session
from typing import List, Dict, Any, Optional

from ..models.waste_model import (
    WasteIdentifyResponse, 
    WasteItem, 
    Position, 
    Coordinates, 
    ReturnPlanRequest, 
    ReturnPlanResponse, 
    ReturnStep,
    RetrievalStep,
    ReturnManifest,
    ReturnItemInfo,
    CompleteUndockingRequest, 
    CompleteUndockingResponse
)
from ..data.database import (
    get_all_items, 
    get_item_by_id, 
    get_container_by_id,
    log_action,
    remove_items_from_inventory
)

def identify_waste_items(db: Session) -> WasteIdentifyResponse:
    """
    Identify items that are expired or out of uses and should be returned.
    """
    try:
        # Get all items from inventory
        all_items = get_all_items(db)
        
        waste_items = []
        current_date = datetime.utcnow()
        
        for item in all_items:
            reason = None
            
            # Check if item is expired
            if item.get("expiry_date") and item["expiry_date"] < current_date:
                reason = "Expired"
            
            # Check if item is out of uses
            elif item.get("max_uses") and item.get("usage_count", 0) >= item["max_uses"]:
                reason = "Out of Uses"
            
            if reason:
                waste_items.append(
                    WasteItem(
                        itemId=item["id"],
                        name=item["name"],
                        reason=reason,
                        containerId=item["container_id"],
                        position=Position(
                            startCoordinates=Coordinates(
                                width=item["position"]["start"]["width"],
                                depth=item["position"]["start"]["depth"],
                                height=item["position"]["start"]["height"]
                            ),
                            endCoordinates=Coordinates(
                                width=item["position"]["end"]["width"],
                                depth=item["position"]["end"]["depth"],
                                height=item["position"]["end"]["height"]
                            )
                        )
                    )
                )
        
        return WasteIdentifyResponse(
            success=True,
            wasteItems=waste_items
        )
    except Exception as e:
        return WasteIdentifyResponse(
            success=False,
            message=str(e)
        )

def generate_return_plan(db: Session, request: ReturnPlanRequest) -> ReturnPlanResponse:
    """
    Generate a plan for returning waste items to Earth.
    Includes steps for retrieval and loading into the undocking container.
    """
    try:
        # Validate undocking container exists
        container = get_container_by_id(db, request.undockingContainerId)
        if not container:
            return ReturnPlanResponse(
                success=False,
                message=f"Undocking container {request.undockingContainerId} not found"
            )
        
        # Get waste items
        waste_response = identify_waste_items(db)
        if not waste_response.success:
            return ReturnPlanResponse(
                success=False,
                message=waste_response.message
            )
        
        waste_items = waste_response.wasteItems
        
        # Sort waste items by priority (expired first, then out of uses)
        waste_items.sort(key=lambda x: 0 if x.reason == "Expired" else 1)
        
        # Calculate total volume and weight
        total_volume = 0
        total_weight = 0
        return_items = []
        
        for item in waste_items:
            item_details = get_item_by_id(db, item.itemId)
            if not item_details:
                continue
                
            item_volume = calculate_item_volume(item.position)
            item_weight = item_details.get("weight", 0)
            
            # Check if adding this item would exceed max weight
            if total_weight + item_weight > request.maxWeight:
                continue
                
            total_volume += item_volume
            total_weight += item_weight
            
            return_items.append(
                ReturnItemInfo(
                    itemId=item.itemId,
                    name=item.name,
                    reason=item.reason
                )
            )
        
        # Generate return steps
        return_steps = []
        retrieval_steps = []
        
        for index, item in enumerate(return_items):
            # Add return step
            return_steps.append(
                ReturnStep(
                    step=index + 1,
                    itemId=item.itemId,
                    itemName=item.name,
                    fromContainer=get_item_container(db, item.itemId),
                    toContainer=request.undockingContainerId
                )
            )
            
            # Generate retrieval steps for this item
            item_retrieval_steps = generate_item_retrieval_steps(db, item.itemId)
            retrieval_steps.extend(item_retrieval_steps)
        
        # Create return manifest
        return_manifest = ReturnManifest(
            undockingContainerId=request.undockingContainerId,
            undockingDate=request.undockingDate,
            returnItems=return_items,
            totalVolume=total_volume,
            totalWeight=total_weight
        )
        
        return ReturnPlanResponse(
            success=True,
            returnPlan=return_steps,
            retrievalSteps=retrieval_steps,
            returnManifest=return_manifest
        )
    except Exception as e:
        return ReturnPlanResponse(
            success=False,
            message=str(e)
        )

def complete_undocking(db: Session, request: CompleteUndockingRequest) -> CompleteUndockingResponse:
    """
    Mark the undocking as complete and remove the items from inventory.
    """
    try:
        # Get all items in the undocking container
        items_in_container = get_items_by_container(db, request.undockingContainerId)
        
        if not items_in_container:
            return CompleteUndockingResponse(
                success=False,
                message=f"No items found in undocking container {request.undockingContainerId}",
                itemsRemoved=0
            )
        
        # Log the undocking action
        log_action(
            db, 
            "undocking", 
            "system",  # System action
            request.undockingContainerId,
            f"Undocking container with {len(items_in_container)} items",
            request.timestamp
        )
        
        # Remove items from inventory
        item_ids = [item["id"] for item in items_in_container]
        remove_items_from_inventory(db, item_ids)
        
        return CompleteUndockingResponse(
            success=True,
            itemsRemoved=len(items_in_container)
        )
    except Exception as e:
        return CompleteUndockingResponse(
            success=False,
            message=str(e),
            itemsRemoved=0
        )

def calculate_item_volume(position: Position) -> float:
    """
    Calculate the volume of an item based on its position.
    """
    width = position.endCoordinates.width - position.startCoordinates.width
    depth = position.endCoordinates.depth - position.startCoordinates.depth
    height = position.endCoordinates.height - position.startCoordinates.height
    
    return width * depth * height

def get_item_container(db: Session, item_id: str) -> str:
    """
    Get the container ID for an item.
    """
    item = get_item_by_id(db, item_id)
    if item:
        return item.get("container_id", "unknown")
    return "unknown"

def get_items_by_container(db: Session, container_id: str) -> List[Dict[str, Any]]:
    """
    Get all items in a specific container.
    """
    # This would query the database for all items in the container
    # Simplified implementation for now
    all_items = get_all_items(db)
    return [item for item in all_items if item.get("container_id") == container_id]

def generate_item_retrieval_steps(db: Session, item_id: str) -> List[RetrievalStep]:
    """
    Generate retrieval steps for a specific item.
    """
    item = get_item_by_id(db, item_id)
    if not item:
        return []
    
    # Get items that need to be moved to access the target item
    blocking_items = get_blocking_items(db, item)
    
    steps = []
    step_counter = 1
    
    # Add steps for moving blocking items
    for blocking_item in blocking_items:
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
    for blocking_item in reversed(blocking_items):
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

