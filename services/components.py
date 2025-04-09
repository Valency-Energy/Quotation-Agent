from fastapi import Body
from pydantic import BaseModel, Field
from typing import Optional, List
from datetime import datetime


# Define the request model
class QuotationFilterRequest(BaseModel):
    system_capacity_kw: float = Field(
        ..., description="Desired system capacity in kilowatts"
    )
    installation_type: Optional[str] = Field(
        None, description="Type of installation (residential, commercial, industrial)"
    )
    location: Optional[str] = Field(None, description="Installation location")
    inverter_brands: Optional[List[str]] = Field(
        None, description="Filter by inverter brands"
    )
    panel_brands: Optional[List[str]] = Field(
        None, description="Filter by solar panel brands"
    )
    mounting_material: Optional[List[str]] = Field(
        None, description="Filter by mounting structure material"
    )
    mounting_coating: Optional[List[str]] = Field(
        None, description="Filter by mounting structure coating"
    )


# Convert Pydantic models to dict with additional fields
def prepare_component_data(component):
    component_dict = component.dict()
    component_dict["created_at"] = datetime.now()
    return component_dict


async def apply_filters(
    inverters,
    solar_panels,
    mounting_structures,
    request: QuotationFilterRequest = Body(...),
):
    if request.inverter_brands:
        inverters = [
            inv for inv in inverters if inv.get("brand") in request.inverter_brands
        ]

    if request.panel_brands:
        solar_panels = [
            panel
            for panel in solar_panels
            if panel.get("brand") in request.panel_brands
        ]

    if request.mounting_material:
        mounting_structures = [
            mount
            for mount in mounting_structures
            if mount.get("Material") in request.mounting_material
        ]

    if request.mounting_coating:
        mounting_structures = [
            mount
            for mount in mounting_structures
            if mount.get("Coating_Type") in request.mounting_coating
        ]

    return inverters, solar_panels, mounting_structures
