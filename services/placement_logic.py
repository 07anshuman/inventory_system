database = {
    "items": {},       # Use dict for quick lookups (O(1) access)
    "containers": {}   # Store container dimensions and items
}

def place_item(container_id, item_id, position):
    """Places an item in a container only if there's enough space and no collision."""
    
    if container_id not in database["containers"]:
        return False, "Container does not exist"
    
    container = database["containers"][container_id]

    # Ensure the item fits in the container dimensions
    item_width = position.endCoordinates.width - position.startCoordinates.width
    item_depth = position.endCoordinates.depth - position.startCoordinates.depth
    item_height = position.endCoordinates.height - position.startCoordinates.height

    if (item_width > container["width"] or 
        item_depth > container["depth"] or 
        item_height > container["height"]):
        return False, "Item does not fit in the container"

    # Ensure no collision with existing items
    for existing_item in container["items"]:
        if is_overlapping(existing_item["position"], position):
            return False, "Collision detected with another item"

    # Place the item
    item = {
        "itemId": item_id,
        "containerId": container_id,
        "position": position.dict()
    }
    
    database["items"][item_id] = item  # Store in dict for O(1) lookup
    container["items"].append(item)  # Add to the container
    return True, item

def is_overlapping(pos1, pos2):
    """Check if two positions overlap in 3D space."""
    return not (
        pos1.endCoordinates.width <= pos2.startCoordinates.width or 
        pos1.startCoordinates.width >= pos2.endCoordinates.width or 
        pos1.endCoordinates.depth <= pos2.startCoordinates.depth or 
        pos1.startCoordinates.depth >= pos2.endCoordinates.depth or 
        pos1.endCoordinates.height <= pos2.startCoordinates.height or 
        pos1.startCoordinates.height >= pos2.endCoordinates.height
    )

def find_item(item_id=None, item_name=None):
    """Optimized search using dict (O(1) lookup for item ID)."""
    if item_id and item_id in database["items"]:
        return database["items"][item_id]
    return None  # More logic can be added for name-based search

def retrieve_item(item_id):
    """Retrieve (remove) an item efficiently."""
    if item_id in database["items"]:
        item = database["items"].pop(item_id)  # O(1) removal
        database["containers"][item["containerId"]]["items"].remove(item)
        return True
    return False

