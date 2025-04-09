from fastapi import APIRouter, HTTPException, Body

from .models import BOSComponent

from services.components import prepare_component_data
from services.schemas import ComponentResponse
from services.db import db_manager

bos_component_routes = APIRouter()


# BOS Component Endpoints
@bos_component_routes.post("/", response_model=ComponentResponse)
async def add_bos_component(component: BOSComponent = Body(...)):
    try:
        component_data = prepare_component_data(component)
        inserted_id = db_manager.add_material("bos_component", component_data)
        return {"id": inserted_id, "message": "BOS component added successfully"}
    except Exception as e:
        raise HTTPException(
            status_code=500, detail=f"Failed to add BOS component: {str(e)}"
        )


@bos_component_routes.get("")
async def get_bos_components():
    try:
        components = db_manager.get_all_materials("bos_component")
        return {"bos_components": components}
    except Exception as e:
        raise HTTPException(
            status_code=500, detail=f"Failed to retrieve BOS components: {str(e)}"
        )
