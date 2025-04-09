from fastapi import APIRouter, HTTPException, Body

from .models import EarthingSystem

from services.components import prepare_component_data
from services.schemas import ComponentResponse
from services.db import db_manager

earthing_system_routes = APIRouter()


# Earthing System Endpoints
@earthing_system_routes.post("/", response_model=ComponentResponse)
async def add_earthing_system(system: EarthingSystem = Body(...)):
    try:
        system_data = prepare_component_data(system)
        inserted_id = db_manager.add_material("earthing_system", system_data)
        return {"id": inserted_id, "message": "Earthing system added successfully"}
    except Exception as e:
        raise HTTPException(
            status_code=500, detail=f"Failed to add earthing system: {str(e)}"
        )


@earthing_system_routes.get("/")
async def get_earthing_systems():
    try:
        systems = db_manager.get_all_materials("earthing_system")
        return {"earthing_systems": systems}
    except Exception as e:
        raise HTTPException(
            status_code=500, detail=f"Failed to retrieve earthing systems: {str(e)}"
        )
