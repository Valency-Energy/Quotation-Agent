from itertools import product
from fastapi import APIRouter, HTTPException, Query, Body
from typing import Dict, List
from .models import InventoryQuotation
from datetime import datetime

from services.db import db_manager
from services.schemas import ComponentResponse

inventory_routes = APIRouter()


@inventory_routes.post("/", response_model=ComponentResponse)
async def add_to_inventory(
    user_id: str,
    items: Dict[str, List[List[str]]] = Body(...),  # Updated to List[List[str]]
):
    try:
        inventory = db_manager.get_user_inventory(user_id)

        # Use correct collection name
        inventory_collection = db_manager.collections["inventories"]

        if not inventory:
            inventory_data = {
                "user_id": user_id,
                "SolarPanels": [],
                "Inverters": [],
                "MountingStructures": [],
                "BOSComponents": [],
                "ProtectionEquipment": [],
                "EarthingSystems": [],
                "NetMetering": [],
                "created_at": datetime.now(),
                "updated_at": datetime.now(),
            }

            for category, components in items.items():
                if category in inventory_data:
                    inventory_data[category] = components

            insert_result = inventory_collection.insert_one(inventory_data)

            return {
                "id": str(insert_result.inserted_id),
                "message": "Inventory created successfully",
            }

        else:
            update_data = {"$set": {"updated_at": datetime.now()}, "$push": {}}

            for category, components in items.items():
                if category in inventory:
                    update_data["$push"][category] = {"$each": components}

            # Clean up if there's no $push data
            if not update_data["$push"]:
                update_data.pop("$push")

            inventory_collection.update_one({"user_id": user_id}, update_data)

            updated_inventory = db_manager.get_user_inventory(user_id)
            return {
                "id": str(updated_inventory["_id"]),
                "message": "Inventory updated successfully",
            }

    except Exception as e:
        raise HTTPException(
            status_code=500, detail=f"Failed to update inventory: {str(e)}"
        )


@inventory_routes.get("/{user_id}", response_model=Dict)
async def get_user_inventory(user_id: str):
    try:
        inventory = db_manager.get_user_inventory(user_id)

        if not inventory:
            raise HTTPException(
                status_code=404, detail=f"No inventory found for user ID: {user_id}"
            )

        # Convert ObjectId to string for JSON serialization
        inventory["_id"] = str(inventory["_id"])

        return inventory

    except Exception as e:
        if isinstance(e, HTTPException):
            raise e
        raise HTTPException(
            status_code=500, detail=f"Failed to retrieve inventory: {str(e)}"
        )


@inventory_routes.get("/{user_id}/quotations")
async def generate_user_quotations(
    user_id: str,
    max_quotations: int = Query(
        10, description="Maximum number of quotations to generate"
    ),
):
    try:
        inventory = db_manager.get_user_inventory(user_id)

        if not inventory:
            raise HTTPException(
                status_code=404, detail=f"No inventory found for user ID: {user_id}"
            )

        # Get components from inventory
        solar_panels = inventory.get("SolarPanels", [])
        inverters = inventory.get("Inverters", [])
        mounting_structures = inventory.get("MountingStructures", [])
        earthing_systems = inventory.get("EarthingSystems", [])

        # These will be included in all quotations
        bos_components = inventory.get("BOSComponents", [])
        protection_equipment = inventory.get("ProtectionEquipment", [])
        net_metering = inventory.get("NetMetering", [])

        # Generate permutations of configurable components
        # Limit the number of combinations to avoid excessive processing
        permutations = list(
            product(
                solar_panels[:3] if solar_panels else [[]],
                inverters[:3] if inverters else [[]],
                mounting_structures[:2] if mounting_structures else [[]],
                earthing_systems[:2] if earthing_systems else [[]],
            )
        )

        # Limit the number of quotations
        permutations = permutations[:max_quotations]

        quotations = []

        for idx, (panel, inverter, mount, earth) in enumerate(permutations):
            # Skip invalid combinations (empty components)
            if not panel or not inverter or not mount or not earth:
                continue

            # Calculate costs and profits (example calculation)
            # In a real system, you would have more sophisticated pricing logic
            panel_cost = float(panel[2]) if len(panel) > 2 else 0
            inverter_cost = float(inverter[2]) if len(inverter) > 2 else 0
            mount_cost = 200  # Example fixed cost
            earth_cost = 100  # Example fixed cost

            # Calculate BOS and protection costs
            bos_cost = sum(
                float(comp[2]) if len(comp) > 2 and comp[2] != "N/A" else 50
                for comp in bos_components
            )
            protection_cost = sum(
                float(comp[2]) if len(comp) > 2 and comp[2] != "N/A" else 75
                for comp in protection_equipment
            )
            metering_cost = sum(
                float(comp[2]) if len(comp) > 2 and comp[2] != "N/A" else 150
                for comp in net_metering
            )

            # Calculate total cost and profit
            total_cost = (
                panel_cost
                + inverter_cost
                + mount_cost
                + earth_cost
                + bos_cost
                + protection_cost
                + metering_cost
            )
            profit_margin = 0.25  # 25% profit margin
            total_profit = total_cost * profit_margin

            # Create quotation structure
            quotation = [
                [
                    {
                        "type": "Solar Panel",
                        "model": panel[0],
                        "quantity": panel[1],
                        "unit_cost": panel_cost / float(panel[1])
                        if float(panel[1]) > 0
                        else 0,
                    }
                ],
                [
                    {
                        "type": "Inverter",
                        "model": inverter[0],
                        "quantity": inverter[1],
                        "unit_cost": inverter_cost / float(inverter[1])
                        if float(inverter[1]) > 0
                        else 0,
                    }
                ],
                [
                    {
                        "type": "Mounting Structure",
                        "model": mount[0],
                        "quantity": mount[1],
                        "unit_cost": mount_cost / float(mount[1])
                        if float(mount[1]) > 0
                        else 0,
                    }
                ],
                [
                    {
                        "type": "Earthing System",
                        "model": earth[0],
                        "quantity": earth[1],
                        "unit_cost": earth_cost / float(earth[1])
                        if float(earth[1]) > 0
                        else 0,
                    }
                ],
                [
                    {
                        "type": comp[0],
                        "model": "BOS Component",
                        "quantity": comp[1],
                        "unit_cost": float(comp[2])
                        if len(comp) > 2 and comp[2] != "N/A"
                        else 50 / float(comp[1])
                        if float(comp[1]) > 0
                        else 0,
                    }
                    for comp in bos_components
                ],
                [
                    {
                        "type": comp[0],
                        "model": "Protection Equipment",
                        "quantity": comp[1],
                        "unit_cost": float(comp[2])
                        if len(comp) > 2 and comp[2] != "N/A"
                        else 75 / float(comp[1])
                        if float(comp[1]) > 0
                        else 0,
                    }
                    for comp in protection_equipment
                ],
                [
                    {
                        "type": comp[0],
                        "model": "Net Metering",
                        "quantity": comp[1],
                        "unit_cost": float(comp[2])
                        if len(comp) > 2 and comp[2] != "N/A"
                        else 150 / float(comp[1])
                        if float(comp[1]) > 0
                        else 0,
                    }
                    for comp in net_metering
                ],
            ]

            quotation_obj = InventoryQuotation(
                user_id=user_id,
                inventory_id=str(inventory["_id"]),
                quotation=quotation,
                total_cost=total_cost,
                total_profit=total_profit,
            )

            quotations.append(quotation_obj.dict())

        return {"quotations": quotations, "count": len(quotations)}

    except Exception as e:
        if isinstance(e, HTTPException):
            raise e
        raise HTTPException(
            status_code=500, detail=f"Failed to generate quotations: {str(e)}"
        )
