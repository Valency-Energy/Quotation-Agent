from pydantic import BaseModel
from typing import List, Dict, Optional
from fastapi import HTTPException, Body
from datetime import datetime
import itertools

class MaterialSelection(BaseModel):
    material_type: str
    available_brands: List[str]
    costs: Dict[str, float]  # brand -> cost mapping
    profits: Dict[str, float]  # brand -> profit mapping

class QuotationRequest(BaseModel):
    materials: List[MaterialSelection]
    user_id: Optional[str] = None
    save_to_db: bool = True

async def generate_quotations(request: QuotationRequest = Body(...)):
    from db import db_manager
    
    # Validate input data
    if not request.materials:
        raise HTTPException(status_code=400, detail="No materials provided")
    
    # Prepare material options by type
    material_options = {}
    material_types = []
    
    for material in request.materials:
        material_type = material.material_type
        material_types.append(material_type)
        options = []
        
        for brand in material.available_brands:
            if brand in material.costs and brand in material.profits:
                options.append({
                    "brand": brand,
                    "cost": material.costs[brand],
                    "profit": material.profits[brand]
                })
        
        material_options[material_type] = options
    
    # Generate all possible combinations of materials
    # First, create lists of options for each material type
    material_lists = []
    for material_type in material_types:
        material_lists.append(material_options[material_type])
    
    # Generate all combinations
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
                "profit": material_option["profit"]
            }
            total_cost += material_option["cost"]
            total_profit += material_option["profit"]
        
        all_combinations.append({
            "materials": combo_dict,
            "total_cost": total_cost,
            "total_profit": total_profit,
            "total_price": total_cost + total_profit,
            "generated_at": datetime.utcnow().isoformat()
        })
    
    # Sort combinations - primary by total profit (descending), secondary by total cost (ascending)
    # This prioritizes higher profit combinations, and for equal profits, those with lower costs
    all_combinations.sort(key=lambda x: (-x["total_profit"], x["total_cost"]))
    
    # Save materials configuration for future reference if requested
    if request.save_to_db:
        # First save the material configuration
        material_config_id = db_manager.save_material_config(
            [material.dict() for material in request.materials], 
            request.user_id
        )
        
        # Then save the generated quotations
        batch_id = db_manager.save_quotations(all_combinations, request.user_id)
        
        return {
            "quotations": all_combinations,
            "batch_id": batch_id,
            "material_config_id": material_config_id
        }
    
    return {"quotations": all_combinations}