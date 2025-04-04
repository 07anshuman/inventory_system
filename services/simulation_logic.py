from datetime import datetime, timedelta
from sqlalchemy.orm import Session
from typing import List, Dict, Any, Optional
from ..models.simulation_model import SimulationRequest, SimulationResponse, SimulationChanges, ItemUsage
from ..data.database import get_all_items, update_item_usage, log_action, get_item_by_id, get_item_by_name

def simulate_day(db: Session, request: SimulationRequest) -> SimulationResponse:
    """
    Simulate daily item usage based on the provided request.
    Track changes such as items used, expired, and depleted.
    """
    current_date = datetime.utcnow()
    items_used = []
    items_expired = []
    items_depleted = []

    # Process items to be used per day
    for item in request.itemsToBeUsedPerDay:
        item_id = item.itemId if hasattr(item, 'itemId') and item.itemId else None
        item_name = item.name if hasattr(item, 'name') and item.name else None
        
        # Fetch item details from the database
        item_details = get_item_by_id(db, item_id) if item_id else get_item_by_name(db, item_name)
        
        if item_details:
            # Update item usage
            update_item_usage(db, item_details['id'])
            
            # Add to items used
            remaining_uses = item_details.get('max_uses', 0) - item_details.get('usage_count', 0)
            items_used.append(
                ItemUsage(
                    itemId=item_details['id'],
                    name=item_details['name'],
                    remainingUses=remaining_uses
                )
            )
            
            # Check for expiration
            if item_details.get('expiry_date') and item_details['expiry_date'] < current_date:
                items_expired.append(
                    ItemUsage(
                        itemId=item_details['id'],
                        name=item_details['name'],
                        remainingUses=remaining_uses
                    )
                )
            
            # Check for depletion
            if item_details.get('max_uses') and item_details.get('usage_count', 0) >= item_details['max_uses']:
                items_depleted.append(
                    ItemUsage(
                        itemId=item_details['id'],
                        name=item_details['name'],
                        remainingUses=0
                    )
                )
    
    # Calculate new date
    if request.numOfDays:
        new_date = current_date + timedelta(days=request.numOfDays)
    elif request.toTimestamp:
        try:
            new_date = datetime.fromisoformat(request.toTimestamp.replace('Z', '+00:00'))
        except ValueError:
            # If timestamp is invalid, use current time plus one day
            new_date = current_date + timedelta(days=1)
    else:
        # Default to one day if neither is provided
        new_date = current_date + timedelta(days=1)
    
    # Check for items that expire during the simulation period
    all_items = get_all_items(db)
    for item in all_items:
        if item.get('expiry_date') and current_date < item['expiry_date'] <= new_date:
            # Item expires during simulation period
            if item['id'] not in [expired.itemId for expired in items_expired]:
                items_expired.append(
                    ItemUsage(
                        itemId=item['id'],
                        name=item['name'],
                        remainingUses=item.get('max_uses', 0) - item.get('usage_count', 0)
                    )
                )
    
    # Create changes object
    changes = SimulationChanges(
        itemsUsed=items_used,
        itemsExpired=items_expired,
        itemsDepletedToday=items_depleted
    )
    
    # Log the simulation action
    log_action(
        db,
        "simulation",
        "system",  # System action
        "simulation",
        f"Simulated {request.numOfDays if request.numOfDays else 'to specific date'} days"
    )
    
    return SimulationResponse(
        success=True,
        newDate=new_date.isoformat(),
        changes=changes
    )

