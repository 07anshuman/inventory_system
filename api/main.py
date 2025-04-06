from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

# Import routers from each API module using absolute imports
from api.search import router as search_router
from api.waste import router as waste_router
from api.simulation import router as simulation_router
from api.placement import router as placement_router
from api.rearrange import router as rearrange_router
from api.import_export import router as import_export_router
from api.logs import router as logs_router


# Create FastAPI app
app = FastAPI(
    title="Inventory Management System",
    description="API for managing inventory in space",
    version="1.0.0"
)

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Allows all origins
    allow_credentials=True,
    allow_methods=["*"],  # Allows all methods
    allow_headers=["*"],  # Allows all headers
)

# Include routers from each API module
app.include_router(search_router, prefix="/api", tags=["Search"])
app.include_router(waste_router, prefix="/api", tags=["Waste Management"])
app.include_router(simulation_router, prefix="/api", tags=["Simulation"])
app.include_router(placement_router, prefix="/api", tags=["Placement"])
app.include_router(rearrange_router, prefix="/api", tags=["Rearrangement"])
app.include_router(import_export_router, prefix="/api", tags=["Import/Export"])
app.include_router(logs_router, prefix="/api", tags=["Logs"])

@app.get("/")
async def root():
    return {
        "message": "Welcome to the Inventory Management System API",
        "documentation": "/docs",
        "redoc": "/redoc"
    }

