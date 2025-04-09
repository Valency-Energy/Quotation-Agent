from fastapi import APIRouter, HTTPException, Body
from services.schemas import ComponentResponse
from services.db import db_manager
from .models import SolarPanel
from services.components import prepare_component_data

solar_panel_routes = APIRouter()


# Solar Panel Endpoints
@solar_panel_routes.post("/", response_model=ComponentResponse)
async def add_solar_panel(panel: SolarPanel = Body(...)):
    try:
        panel_data = prepare_component_data(panel)
        inserted_id = db_manager.add_material("solar_panel", panel_data)
        return {"id": inserted_id, "message": "Solar panel added successfully"}
    except Exception as e:
        raise HTTPException(
            status_code=500, detail=f"Failed to add solar panel: {str(e)}"
        )


@solar_panel_routes.get("/")
async def get_solar_panels():
    try:
        panels = db_manager.get_all_materials("solar_panel")
        return {"solar_panels": panels}
    except Exception as e:
        raise HTTPException(
            status_code=500, detail=f"Failed to retrieve solar panels: {str(e)}"
        )
