from fastapi import APIRouter, HTTPException, Body

from .models import Inverter

from services.components import prepare_component_data
from services.schemas import ComponentResponse
from services.db import db_manager

inverter_routes = APIRouter()


# Inverter Endpoints
@inverter_routes.post("/", response_model=ComponentResponse)
async def add_inverter(inverter: Inverter = Body(...)):
    try:
        inverter_data = prepare_component_data(inverter)
        inserted_id = db_manager.add_material("inverter", inverter_data)
        return {"id": inserted_id, "message": "Inverter added successfully"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to add inverter: {str(e)}")


@inverter_routes.get("/")
async def get_inverters():
    try:
        inverters = db_manager.get_all_materials("inverter")
        return {"inverters": inverters}
    except Exception as e:
        raise HTTPException(
            status_code=500, detail=f"Failed to retrieve inverters: {str(e)}"
        )
