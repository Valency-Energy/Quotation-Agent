from fastapi import APIRouter, HTTPException, Body

from .models import NetMetering

from services.components import prepare_component_data
from services.schemas import ComponentResponse
from services.db import db_manager

net_metering_routes = APIRouter()


# Net Metering Endpoints
@net_metering_routes.post("/", response_model=ComponentResponse)
async def add_net_metering(metering: NetMetering = Body(...)):
    try:
        metering_data = prepare_component_data(metering)
        inserted_id = db_manager.add_material("net_metering", metering_data)
        return {"id": inserted_id, "message": "Net metering added successfully"}
    except Exception as e:
        raise HTTPException(
            status_code=500, detail=f"Failed to add net metering: {str(e)}"
        )


@net_metering_routes.get("/")
async def get_net_metering():
    try:
        metering = db_manager.get_all_materials("net_metering")
        return {"net_metering": metering}
    except Exception as e:
        raise HTTPException(
            status_code=500, detail=f"Failed to retrieve net metering: {str(e)}"
        )
