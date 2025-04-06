from fastapi import FastAPI, HTTPException
# For models in /home/anshuman-shukla/Documents/inventory_system/models
from models import PlaceRequest, RetrieveRequest, Item
# For placement_logic in /home/anshuman-shukla/Documents/inventory_system/services
from services.placement_logic import place_item, find_item, retrieve_item


app = FastAPI()

@app.post("/api/place")
def place_item_api(request: PlaceRequest):
    success, item = place_item(request.containerId, request.itemId, request.position)
    if success:
        return {"success": True, "item": item}
    raise HTTPException(status_code=400, detail="Placement failed")

@app.get("/api/search")
def search_item(itemId: Optional[str] = None, itemName: Optional[str] = None):
    item = find_item(itemId, itemName)
    if item:
        return {"success": True, "found": True, "item": item}
    return {"success": True, "found": False}

@app.post("/api/retrieve")
def retrieve_item_api(request: RetrieveRequest):
    success = retrieve_item(request.itemId)
    if success:
        return {"success": True}
    raise HTTPException(status_code=400, detail="Item not found or already retrieved")


