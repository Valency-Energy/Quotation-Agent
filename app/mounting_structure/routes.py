from fastapi import APIRouter, HTTPException, Body

from .models import MountingStructure

from services.schemas import ComponentResponse
from services.components import prepare_component_data
from services.db import db_manager

mounting_strcture_routes = APIRouter()


# Mounting Structure Endpoints
@mounting_strcture_routes.post("/", response_model=ComponentResponse)
async def add_mounting_structure(structure: MountingStructure = Body(...)):
    try:
        structure_data = prepare_component_data(structure)
        inserted_id = db_manager.add_material("mounting_structure", structure_data)
        return {"id": inserted_id, "message": "Mounting structure added successfully"}
    except Exception as e:
        raise HTTPException(
            status_code=500, detail=f"Failed to add mounting structure: {str(e)}"
        )


@mounting_strcture_routes.get("/")
async def get_mounting_structures():
    try:
        structures = db_manager.get_all_materials("mounting_structure")
        return {"mounting_structures": structures}
    except Exception as e:
        raise HTTPException(
            status_code=500, detail=f"Failed to retrieve mounting structures: {str(e)}"
        )
