from fastapi import APIRouter, HTTPException, Body

from .models import ProtectionEquipment

from services.schemas import ComponentResponse
from services.components import prepare_component_data
from services.db import db_manager


protection_equipment_routes = APIRouter()


# Protection Equipment Endpoints
@protection_equipment_routes.post("/", response_model=ComponentResponse)
async def add_protection_equipment(equipment: ProtectionEquipment = Body(...)):
    try:
        equipment_data = prepare_component_data(equipment)
        inserted_id = db_manager.add_material("protection_equipment", equipment_data)
        return {"id": inserted_id, "message": "Protection equipment added successfully"}
    except Exception as e:
        raise HTTPException(
            status_code=500, detail=f"Failed to add protection equipment: {str(e)}"
        )


@protection_equipment_routes.get("/")
async def get_protection_equipment():
    try:
        equipment = db_manager.get_all_materials("protection_equipment")
        return {"protection_equipment": equipment}
    except Exception as e:
        raise HTTPException(
            status_code=500, detail=f"Failed to retrieve protection equipment: {str(e)}"
        )
