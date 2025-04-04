import uvicorn
import logging
from fastapi import FastAPI, Body, HTTPException, Query, Path
from typing import List, Dict, Optional, Any
from datetime import datetime
from pydantic import BaseModel, Field
from fastapi.middleware.cors import CORSMiddleware
import uuid
from itertools import product

# Import your component models
from models import (
    SolarPanel, Inverter, MountingStructure, BOSComponent, 
    ProtectionEquipment, EarthingSystem, NetMetering,
)
from db import db_manager

app = FastAPI(title="Solar Quotation System API", docs_url="/docs", redoc_url="/redoc")

# Set up CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Setup logging
logger = logging.getLogger(__name__)

# Response models with ID field
class ComponentResponse(BaseModel):
    id: str
    message: str = "Component added successfully"

# Convert Pydantic models to dict with additional fields
def prepare_component_data(component):
    component_dict = component.dict()
    component_dict["created_at"] = datetime.now()
    return component_dict

# Solar Panel Endpoints
@app.post("/api/solar-panels/", response_model=ComponentResponse)
async def add_solar_panel(panel: SolarPanel = Body(...)):
    try:
        panel_data = prepare_component_data(panel)
        inserted_id = db_manager.add_material("solar_panel", panel_data)
        return {"id": inserted_id, "message": "Solar panel added successfully"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to add solar panel: {str(e)}")

@app.get("/api/solar-panels/")
async def get_solar_panels():
    try:
        panels = db_manager.get_all_materials("solar_panel")
        return {"solar_panels": panels}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to retrieve solar panels: {str(e)}")

# Inverter Endpoints
@app.post("/api/inverters/", response_model=ComponentResponse)
async def add_inverter(inverter: Inverter = Body(...)):
    try:
        inverter_data = prepare_component_data(inverter)
        inserted_id = db_manager.add_material("inverter", inverter_data)
        return {"id": inserted_id, "message": "Inverter added successfully"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to add inverter: {str(e)}")

@app.get("/api/inverters/")
async def get_inverters():
    try:
        inverters = db_manager.get_all_materials("inverter")
        return {"inverters": inverters}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to retrieve inverters: {str(e)}")

# Mounting Structure Endpoints
@app.post("/api/mounting-structures/", response_model=ComponentResponse)
async def add_mounting_structure(structure: MountingStructure = Body(...)):
    try:
        structure_data = prepare_component_data(structure)
        inserted_id = db_manager.add_material("mounting_structure", structure_data)
        return {"id": inserted_id, "message": "Mounting structure added successfully"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to add mounting structure: {str(e)}")

@app.get("/api/mounting-structures/")
async def get_mounting_structures():
    try:
        structures = db_manager.get_all_materials("mounting_structure")
        return {"mounting_structures": structures}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to retrieve mounting structures: {str(e)}")

# BOS Component Endpoints
@app.post("/api/bos-components/", response_model=ComponentResponse)
async def add_bos_component(component: BOSComponent = Body(...)):
    try:
        component_data = prepare_component_data(component)
        inserted_id = db_manager.add_material("bos_component", component_data)
        return {"id": inserted_id, "message": "BOS component added successfully"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to add BOS component: {str(e)}")

@app.get("/api/bos-components/")
async def get_bos_components():
    try:
        components = db_manager.get_all_materials("bos_component")
        return {"bos_components": components}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to retrieve BOS components: {str(e)}")

# Protection Equipment Endpoints
@app.post("/api/protection-equipment/", response_model=ComponentResponse)
async def add_protection_equipment(equipment: ProtectionEquipment = Body(...)):
    try:
        equipment_data = prepare_component_data(equipment)
        inserted_id = db_manager.add_material("protection_equipment", equipment_data)
        return {"id": inserted_id, "message": "Protection equipment added successfully"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to add protection equipment: {str(e)}")

@app.get("/api/protection-equipment/")
async def get_protection_equipment():
    try:
        equipment = db_manager.get_all_materials("protection_equipment")
        return {"protection_equipment": equipment}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to retrieve protection equipment: {str(e)}")

# Earthing System Endpoints
@app.post("/api/earthing-systems/", response_model=ComponentResponse)
async def add_earthing_system(system: EarthingSystem = Body(...)):
    try:
        system_data = prepare_component_data(system)
        inserted_id = db_manager.add_material("earthing_system", system_data)
        return {"id": inserted_id, "message": "Earthing system added successfully"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to add earthing system: {str(e)}")

@app.get("/api/earthing-systems/")
async def get_earthing_systems():
    try:
        systems = db_manager.get_all_materials("earthing_system")
        return {"earthing_systems": systems}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to retrieve earthing systems: {str(e)}")

# Net Metering Endpoints
@app.post("/api/net-metering/", response_model=ComponentResponse)
async def add_net_metering(metering: NetMetering = Body(...)):
    try:
        metering_data = prepare_component_data(metering)
        inserted_id = db_manager.add_material("net_metering", metering_data)
        return {"id": inserted_id, "message": "Net metering added successfully"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to add net metering: {str(e)}")

@app.get("/api/net-metering/")
async def get_net_metering():
    try:
        metering = db_manager.get_all_materials("net_metering")
        return {"net_metering": metering}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to retrieve net metering: {str(e)}")

# Quotation Models
# Add these imports to your existing imports
from itertools import product
from typing import List, Optional
from pydantic import BaseModel, Field

# Define the request model
class QuotationFilterRequest(BaseModel):
    system_capacity_kw: float = Field(..., description="Desired system capacity in kilowatts")
    installation_type: Optional[str] = Field(None, description="Type of installation (residential, commercial, industrial)")
    location: Optional[str] = Field(None, description="Installation location")
    inverter_brands: Optional[List[str]] = Field(None, description="Filter by inverter brands")
    panel_brands: Optional[List[str]] = Field(None, description="Filter by solar panel brands")
    mounting_material: Optional[List[str]] = Field(None, description="Filter by mounting structure material")
    mounting_coating: Optional[List[str]] = Field(None, description="Filter by mounting structure coating")

# Define response models
class ComponentQuotation(BaseModel):
    id: str
    brand: str
    model: str
    specifications: str
    warranty: int
    cost: float
    profit: float
    total_price: float

class MountingQuotation(BaseModel):
    id: str
    material: str
    coating_type: str
    brand: str
    specifications: str
    warranty: int
    cost: float
    profit: float
    total_price: float

class QuotationOption(BaseModel):
    quotation_id: str
    inverter: ComponentQuotation
    solar_panel: ComponentQuotation
    mounting_structure: MountingQuotation
    bos_components: List[ComponentQuotation]
    protection_equipment: List[ComponentQuotation]
    total_system_cost: float
    total_profit: float
    total_price: float

class QuotationResponse(BaseModel):
    quotation_options: List[QuotationOption]
    total_options: int
    system_capacity_kw: float

@app.post("/api/quotations/", response_model=QuotationResponse)
async def get_quotation(request: QuotationFilterRequest = Body(...)):
    try:
        # Fetch all components
        inverters = db_manager.get_all_materials("inverter")
        solar_panels = db_manager.get_all_materials("solar_panel")
        mounting_structures = db_manager.get_all_materials("mounting_structure")
        bos_components = db_manager.get_all_materials("bos_component")
        protection_equipment = db_manager.get_all_materials("protection_equipment")
        
        # Apply filters if provided
        if request.inverter_brands:
            inverters = [inv for inv in inverters if inv.get("brand") in request.inverter_brands]
        
        if request.panel_brands:
            solar_panels = [panel for panel in solar_panels if panel.get("brand") in request.panel_brands]
        
        if request.mounting_material:
            mounting_structures = [mount for mount in mounting_structures 
                                  if mount.get("Material") in request.mounting_material]
        
        if request.mounting_coating:
            mounting_structures = [mount for mount in mounting_structures 
                                  if mount.get("Coating_Type") in request.mounting_coating]
        
        # Generate all permutations
        permutations = list(product(inverters, solar_panels, mounting_structures))
        
        # Create quotation options
        quotation_options = []
        
        for i, (inverter, panel, mount) in enumerate(permutations):
            # Calculate required number of panels based on system capacity
            panel_capacity_kw = panel.get("power_w", 0) / 1000
            required_panels = max(1, round(request.system_capacity_kw / panel_capacity_kw))
            
            # Calculate costs for components
            inverter_cost = inverter.get("cost", 0)
            inverter_profit = inverter.get("profit", 0)
            inverter_total = inverter_cost * (1 + inverter_profit)
            
            panel_cost = panel.get("cost", 0) * required_panels
            panel_profit = panel.get("profit", 0)
            panel_total = panel_cost * (1 + panel_profit)
            
            mount_cost = mount.get("cost", 0)
            mount_profit = mount.get("profit", 0)
            mount_total = mount_cost * (1 + mount_profit)
            
            # Calculate BOS and protection equipment costs
            bos_total_cost = sum(item.get("cost", 0) for item in bos_components)
            bos_total_profit = sum(item.get("cost", 0) * item.get("profit", 0) for item in bos_components)
            
            protection_total_cost = sum(item.get("cost", 0) for item in protection_equipment)
            protection_total_profit = sum(item.get("cost", 0) * item.get("profit", 0) for item in protection_equipment)
            
            # Calculate total system cost and profit
            total_system_cost = inverter_cost + panel_cost + mount_cost + bos_total_cost + protection_total_cost
            total_profit = inverter_cost * inverter_profit + panel_cost * panel_profit + mount_cost * mount_profit + bos_total_profit + protection_total_profit
            total_price = total_system_cost + total_profit
            
            # Create component quotations
            inverter_quotation = ComponentQuotation(
                id=inverter.get("id", str(uuid.uuid4())),
                brand=inverter.get("brand", ""),
                model=inverter.get("model", ""),
                specifications=f"{inverter.get('Efficiency', 0)}% efficiency, {inverter.get('MPPT_Channels', 0)} MPPT channels",
                warranty=inverter.get("Warranty", 0),
                cost=inverter_cost,
                profit=inverter_profit,
                total_price=inverter_total
            )
            
            panel_quotation = ComponentQuotation(
                id=panel.get("id", str(uuid.uuid4())),
                brand=panel.get("brand", ""),
                model=panel.get("model_number", ""),
                specifications=f"{panel.get('power_w', 0)}W, {panel.get('efficiency_percent', 0)}% efficiency, {required_panels} panels",
                warranty=panel.get("Warranty", 0),
                cost=panel_cost,
                profit=panel_profit,
                total_price=panel_total
            )
            
            mounting_quotation = MountingQuotation(
                id=mount.get("id", str(uuid.uuid4())),
                material=mount.get("Material", ""),
                coating_type=mount.get("Coating_Type", ""),
                brand=mount.get("Brand", ""),
                specifications=mount.get("Specifications", ""),
                warranty=mount.get("Warranty", 0),
                cost=mount_cost,
                profit=mount_profit,
                total_price=mount_total
            )
            
            # Create BOS component quotations
            bos_quotations = []
            for bos in bos_components:
                bos_cost = bos.get("cost", 0)
                bos_profit = bos.get("profit", 0)
                bos_total = bos_cost * (1 + bos_profit)
                
                bos_quotations.append(ComponentQuotation(
                    id=bos.get("id", str(uuid.uuid4())),
                    brand=bos.get("Brand", ""),
                    model=bos.get("Component_Type", ""),
                    specifications=bos.get("Specifications", ""),
                    warranty=bos.get("Warranty", 0),
                    cost=bos_cost,
                    profit=bos_profit,
                    total_price=bos_total
                ))
            
            # Create protection equipment quotations
            protection_quotations = []
            for protection in protection_equipment:
                protection_cost = protection.get("cost", 0)
                protection_profit = protection.get("profit", 0)
                protection_total = protection_cost * (1 + protection_profit)
                
                protection_quotations.append(ComponentQuotation(
                    id=protection.get("id", str(uuid.uuid4())),
                    brand=protection.get("Brand", ""),
                    model=protection.get("Model", ""),
                    specifications=protection.get("Specifications", ""),
                    warranty=protection.get("Warranty", 0),
                    cost=protection_cost,
                    profit=protection_profit,
                    total_price=protection_total
                ))
                
            # Create quotation option
            quotation_option = QuotationOption(
                quotation_id=f"QT-{i+1}-{uuid.uuid4().hex[:6]}",
                inverter=inverter_quotation,
                solar_panel=panel_quotation,
                mounting_structure=mounting_quotation,
                bos_components=bos_quotations,
                protection_equipment=protection_quotations,
                total_system_cost=total_system_cost,
                total_profit=total_profit,
                total_price=total_price
            )
            
            quotation_options.append(quotation_option)
        
        # Create and return the response
        response = QuotationResponse(
            quotation_options=quotation_options,
            total_options=len(quotation_options),
            system_capacity_kw=request.system_capacity_kw
        )
        
        return response
        
    except Exception as e:
        logger.error(f"Error generating quotation: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Failed to generate quotation: {str(e)}")




@app.get("/")
async def root():
    return {"message": "Solar System Quotation Generator API"}

if __name__ == "__main__":
    uvicorn.run(app, host="127.0.0.1", port=8000)