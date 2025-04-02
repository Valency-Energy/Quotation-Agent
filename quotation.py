from pydantic import BaseModel
from typing import List, Dict, Optional, Union
from fastapi import HTTPException, Body
from datetime import datetime
import itertools

# Component models
class SolarPanel(BaseModel):
    brand: str
    model_number: str
    technology: str
    power_w: int
    efficiency_percent: float
    dimensions_mm: str
    weight_kg: float
    cell_configuration: str
    cost: float
    profit: float

class Inverter(BaseModel):
    brand: str
    model: str
    Efficiency: float
    MPPT_Channels: int
    Input_Voltage_Range: str
    Output_Voltage: str
    IP_Rating: str
    Cooling_Method: str
    Communication: str
    Warranty: int
    Dimensions: str
    Weight: int
    Certifications: str
    cost: float
    profit: float

class MountingStructure(BaseModel):
    Structure_Type: str
    Material: str
    Brand: str
    Specifications: str
    GSM_Rating: int
    Wind_Speed_Rating: int
    Tilt_Angle: str
    Coating_Type: str
    Warranty: int
    cost: float
    profit: float

class BOSComponent(BaseModel):
    Component_Type: str
    Brand: str
    Specifications: str
    Quality_Grade: str
    Warranty: int
    cost: float
    profit: float

class ProtectionEquipment(BaseModel):
    Component_Type: str
    Brand: str
    Model: str
    Specifications: str
    Application: str
    IP_Rating: str
    Certifications: str
    Warranty: int
    cost: float
    profit: float

class EarthingSystem(BaseModel):
    Type: str
    Brand: str
    Material: str
    Specifications: str
    Application: str
    Warranty: int
    cost: float
    profit: float

class NetMetering(BaseModel):
    Meter_Type: str
    Brand: str
    Model: str
    Specifications: str
    Communication: str
    Certifications: str
    Warranty: int
    Additional_Hardware: str
    cost: float
    profit: float

# Union type for all component types
ComponentType = Union[
    SolarPanel, 
    Inverter, 
    MountingStructure, 
    BOSComponent, 
    ProtectionEquipment, 
    EarthingSystem, 
    NetMetering
]

class ComponentSelection(BaseModel):
    component_type: str  # "solar_panel", "inverter", etc.
    components: List[ComponentType]

class QuotationRequest(BaseModel):
    components: List[ComponentSelection]
    user_id: Optional[str] = None
    save_to_db: bool = True

async def generate_quotations(request: QuotationRequest = Body(...)):
    from db import db_manager
    
    # Validate input data
    if not request.components:
        raise HTTPException(status_code=400, detail="No components provided")
    
    # Prepare component options by type
    component_options = {}
    component_types = []
    
    for component_selection in request.components:
        component_type = component_selection.component_type
        component_types.append(component_type)
        
        # Convert components to dictionaries that include all fields
        options = []
        for component in component_selection.components:
            component_dict = component.dict()
            # Ensure we have brand, cost, and profit for each component
            if "cost" not in component_dict or "profit" not in component_dict:
                raise HTTPException(
                    status_code=400, 
                    detail=f"Component of type {component_type} missing cost or profit"
                )
            options.append(component_dict)
        
        component_options[component_type] = options
    
    # Generate all possible combinations of components
    # First, create lists of options for each component type
    component_lists = []
    for component_type in component_types:
        component_lists.append(component_options[component_type])
    
    # Generate all combinations
    all_combinations = []
    for combination in itertools.product(*component_lists):
        combo_dict = {}
        total_cost = 0
        total_profit = 0
        
        for i, component_type in enumerate(component_types):
            component = combination[i]
            
            # Extract identifying information for each component type
            component_info = {
                "cost": component["cost"],
                "profit": component["profit"]
            }
            
            # Add component-specific fields based on type
            if component_type == "solar_panel":
                component_info.update({
                    "brand": component["brand"],
                    "model_number": component["model_number"],
                    "power_w": component["power_w"],
                    "efficiency_percent": component["efficiency_percent"]
                })
            elif component_type == "inverter":
                component_info.update({
                    "brand": component["brand"],
                    "model": component["model"],
                    "Efficiency": component["Efficiency"],
                    "MPPT_Channels": component["MPPT_Channels"]
                })
            elif component_type == "mounting_structure":
                component_info.update({
                    "Brand": component["Brand"],
                    "Structure_Type": component["Structure_Type"],
                    "Material": component["Material"]
                })
            else:
                # Generic handling for other component types
                if "Brand" in component:
                    component_info["Brand"] = component["Brand"]
                elif "brand" in component:
                    component_info["brand"] = component["brand"]
                
                if "Model" in component:
                    component_info["Model"] = component["Model"]
                elif "model" in component:
                    component_info["model"] = component["model"]
            
            combo_dict[component_type] = component_info
            total_cost += component["cost"]
            total_profit += component["profit"]
        
        all_combinations.append({
            "components": combo_dict,
            "total_cost": total_cost,
            "total_profit": total_profit,
            "total_price": total_cost + total_profit,
            "generated_at": datetime.utcnow()
        })
    
    # Sort combinations - primary by total profit (descending), secondary by total cost (ascending)
    all_combinations.sort(key=lambda x: (-x["total_profit"], x["total_cost"]))
    
    # Save to database if requested
    batch_id = None
    config_id = None
    
    if request.save_to_db and request.user_id:
        try:
            # Convert component selections to serializable format
            component_configs = []
            for comp_selection in request.components:
                component_configs.append({
                    "component_type": comp_selection.component_type,
                    "components": [comp.dict() for comp in comp_selection.components]
                })
            
            # Save the component configuration
            config_id = db_manager.save_component_config(
                component_configs, 
                request.user_id
            )
            
            # Save the generated quotations
            batch_id = db_manager.save_quotations(all_combinations, request.user_id)
        except Exception as e:
            # Log the error but return quotations anyway
            print(f"Error saving to database: {e}")
            return {"quotations": all_combinations, "error": str(e)}
    
    response = {"quotations": all_combinations}
    if batch_id:
        response["batch_id"] = batch_id
    if config_id:
        response["config_id"] = config_id
        
    return response