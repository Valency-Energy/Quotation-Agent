from pydantic import BaseModel, ValidationError
from fastapi import HTTPException, Body
from datetime import datetime, UTC
import itertools
from models import (
    SolarPanel, Inverter, MountingStructure, BOSComponent, 
    ProtectionEquipment, EarthingSystem, NetMetering,
    QuotationRequest, MaterialSelection
)

async def generate_quotations(request: QuotationRequest = Body(...)):
    from db import db_manager
    
    try:
        # Validate the request first
        try:
            validated_request = QuotationRequest(**request.model_dump())
        except ValidationError as e:
            raise HTTPException(
                status_code=400,
                detail=f"Validation error: {str(e)}"
            )

        # Prepare material options by type
        material_options = {}
        material_types = []
        
        for material in validated_request.materials:
            try:
                material_type = material.material_type
                material_types.append(material_type)
                options = []
                
                for brand in material.available_brands:
                    if brand not in material.components:
                        raise HTTPException(
                            status_code=400,
                            detail=f"Component details missing for brand: {brand}"
                        )
                    
                    component = material.components[brand]
                    component_dict = component.model_dump() if isinstance(component, BaseModel) else component
                    
                    try:
                        if material_type == 'solar_panel':
                            validated_component = SolarPanel(**component_dict)
                        elif material_type == 'inverter':
                            validated_component = Inverter(**component_dict)
                        elif material_type == 'mounting_structure':
                            validated_component = MountingStructure(**component_dict)
                        elif material_type == 'bos_component':
                            validated_component = BOSComponent(**component_dict)
                        elif material_type == 'protection_equipment':
                            validated_component = ProtectionEquipment(**component_dict)
                        elif material_type == 'earthing_system':
                            validated_component = EarthingSystem(**component_dict)
                        elif material_type == 'net_metering':
                            validated_component = NetMetering(**component_dict)
                        else:
                            raise HTTPException(
                                status_code=400,
                                detail=f"Invalid material type: {material_type}"
                            )
                    except ValidationError as e:
                        raise HTTPException(
                            status_code=400,
                            detail=f"Validation error for {brand} {material_type}: {str(e)}"
                        )
                    
                    if brand not in material.costs or brand not in material.profits:
                        raise HTTPException(
                            status_code=400,
                            detail=f"Missing cost or profit for brand: {brand}"
                        )
                    
                    options.append({
                        "brand": brand,
                        "cost": material.costs[brand],
                        "profit": material.profits[brand],
                        "details": validated_component.model_dump()
                    })
                
                material_options[material_type] = options
                
            except ValidationError as e:
                raise HTTPException(
                    status_code=400,
                    detail=f"Validation error for material type {material_type}: {str(e)}"
                )
        
        # Generate all possible combinations of materials
        material_lists = []
        for material_type in material_types:
            material_lists.append(material_options[material_type])
        
        all_combinations = []
        for combination in itertools.product(*material_lists):
            combo_dict = {}
            total_cost = 0
            total_profit = 0
            
            for i, material_type in enumerate(material_types):
                material_option = combination[i]
                combo_dict[material_type] = {
                    "brand": material_option["brand"],
                    "cost": material_option["cost"],
                    "profit": material_option["profit"],
                    "details": material_option["details"]
                }
                total_cost += material_option["cost"]
                total_profit += material_option["profit"]
            
            all_combinations.append({
                "materials": combo_dict,
                "total_cost": total_cost,
                "total_profit": total_profit,
                "total_price": total_cost + total_profit,
                "generated_at": datetime.now(UTC).isoformat()
            })
        
        # Sort combinations by total profit (descending) and total cost (ascending)
        all_combinations.sort(key=lambda x: (-x["total_profit"], x["total_cost"]))
        
        # Save to database if requested
        if validated_request.save_to_db:
            try:
                material_config_id = db_manager.save_material_config(
                    [material.model_dump() for material in validated_request.materials], 
                    validated_request.user_id
                )
                
                batch_id = db_manager.save_quotations(all_combinations, validated_request.user_id)
                
                return {
                    "quotations": all_combinations,
                    "batch_id": batch_id,
                    "material_config_id": material_config_id
                }
            except Exception as e:
                raise HTTPException(
                    status_code=500,
                    detail=f"Database error: {str(e)}"
                )
        
        return {"quotations": all_combinations}
        
    except HTTPException as he:
        raise he
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error generating quotations: {str(e)}"
        )