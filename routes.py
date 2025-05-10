import itertools
import os
from fastapi import APIRouter, Body, HTTPException, Query, status
from typing import List, Dict, Union
from datetime import datetime
from fastapi import Depends
from fastapi.responses import HTMLResponse
import httpx
from pymongo import UpdateOne

# Import your component models
from models import (
    ComponentResponse, InventoryQuotation, SolarPanel, Inverter, MountingStructure, BOSComponent, 
    ProtectionEquipment, EarthingSystem, NetMetering,
)
from db import db_manager
from auth import create_access_token, create_refresh_token, oauth2_scheme, get_current_user, admin_only_route

router = APIRouter()


GOOGLE_CLIENT_ID = os.getenv("GOOGLE_CLIENT_ID")
GOOGLE_CLIENT_SECRET = os.getenv("GOOGLE_CLIENT_SECRET")
REDIRECT_URI = os.getenv("REDIRECT_URI")

@router.get("/")
async def root():
    return {"message": "Valency Energy:---- Solar Quotation System API"}


@router.get("/auth/")
async def google_login(data: Dict = Body(...)):
    role = data.get("role", "user") 
    if role not in ("user", "admin"):
        raise HTTPException(status_code=400, detail="Invalid role")

    state_param = role
    return {
        "url": f"https://accounts.google.com/o/oauth2/v2/auth?response_type=code&client_id={GOOGLE_CLIENT_ID}&redirect_uri={REDIRECT_URI}&scope=openid%20email%20profile&state={state_param}"
    }


@router.get("/auth/callback", response_class=HTMLResponse)
async def auth_callback(code: str, state: str = Query(...)):
    token_url = "https://oauth2.googleapis.com/token"
    data = {
        "client_id": GOOGLE_CLIENT_ID,
        "client_secret": GOOGLE_CLIENT_SECRET,
        "code": code,
        "redirect_uri": REDIRECT_URI,
        "grant_type": "authorization_code",
    }

    async with httpx.AsyncClient() as client:
        token_response = await client.post(token_url, data=data)
        token_data = token_response.json()

        user_info_response = await client.get(
            "https://www.googleapis.com/oauth2/v1/userinfo",
            headers={"Authorization": f"Bearer {token_data['access_token']}"},
        )
        user_info = user_info_response.json()

    desired_role = state
    existing_user = db_manager.get_user(user_info["email"])
    role = existing_user["role"] if existing_user else desired_role

    user = {
        "email": user_info["email"],
        "full_name": user_info["name"],
        "picture": user_info.get("picture"),
        "role": role,
        "updated_at": datetime.utcnow(),
    }

    db_manager.collections["users"].update_one({"email": user["email"]}, {"$set": user}, upsert=True)

    access_token = create_access_token(data={"sub": user["email"], "role": role})
    refresh_token = create_refresh_token(data={"sub": user["email"], "role": role})

    db_manager.store_refresh_token(user["email"], refresh_token)
    db_manager.update_access_token(user["email"], access_token)

    html_content = f"""
        <script>
            localStorage.setItem('access_token', '{access_token}');
            localStorage.setItem('refresh_token', '{refresh_token}');
            console.log('Access Token:', '{access_token}');
            console.log('Refresh Token:', '{refresh_token}');
            window.location.href = '/';
        </script>
    """
    return HTMLResponse(content=html_content)


@router.post("/refresh_token", summary="Refresh access token")
async def refresh_access_token(data: Dict = Body(...)):
    refresh_token = data.get("refresh_token")
    if not refresh_token:
        raise HTTPException(status_code=400, detail="refresh_token is required")

    from auth import decode_token

    try:
        payload = decode_token(refresh_token)
        email = payload.get("sub")
        role = payload.get("role")

        if not email:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST, detail="Invalid refresh token"
            )

        user = db_manager.get_user(email)
        if not user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, detail="User not found"
            )

        stored_refresh_token = db_manager.get_refresh_token(email)

        if not stored_refresh_token or stored_refresh_token != refresh_token:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid or expired refresh token",
            )

        access_token = create_access_token(data={"sub": email, "role": role})
        db_manager.update_access_token(email, access_token)

        return {"access_token": access_token, "token_type": "bearer"}

    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail=str(e)
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Could not refresh token: {str(e)}",
        )


@router.post("/logout")
async def logout(token: str = Depends(oauth2_scheme)):
    from auth import decode_token

    try:
        user_data = decode_token(token)
        username = user_data.get("sub")
        db_manager.blacklist_token(token)
        db_manager.clear_all_refresh_tokens(username)
        return {"message": "Logged out successfully"}
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Logout failed: {str(e)}",
        )


# Convert Pydantic models to dict with additional fields
def prepare_component_data(component):
    component_dict = component.dict()
    component_dict["created_at"] = datetime.now()
    return component_dict

# Solar Panel Endpoints
@router.post("/api/solar-panels/", response_model=ComponentResponse)
@admin_only_route
async def add_solar_panel(
    panel: SolarPanel = Body(...),
    user: dict = Depends(get_current_user)
):
    try:
        panel_data = prepare_component_data(panel)
        inserted_id = db_manager.add_material("solar_panel", panel_data)
        return {"id": inserted_id, "message": "Solar panel added successfully"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to add solar panel: {str(e)}")

@router.get("/api/solar-panels/")
@admin_only_route
async def get_solar_panels(user: dict = Depends(get_current_user)):
    try:
        panels = db_manager.get_all_materials("solar_panel")
        return {"solar_panels": panels}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to retrieve solar panels: {str(e)}")

@router.post("/api/inverters/", response_model=ComponentResponse)
@admin_only_route
async def add_inverter(inverter: Inverter = Body(...), user: dict = Depends(get_current_user)):
    inverter_data = prepare_component_data(inverter)
    inserted_id = db_manager.add_material("inverter", inverter_data)
    return {"id": inserted_id, "message": "Inverter added successfully"}

@router.get("/api/inverters/")
@admin_only_route
async def get_inverters(user: dict = Depends(get_current_user)):
    inverters = db_manager.get_all_materials("inverter")
    return {"inverters": inverters}

# Mounting Structure Endpoints
@router.post("/api/mounting-structures/", response_model=ComponentResponse)
@admin_only_route
async def add_mounting_structure(structure: MountingStructure = Body(...), user: dict = Depends(get_current_user)):
    structure_data = prepare_component_data(structure)
    inserted_id = db_manager.add_material("mounting_structure", structure_data)
    return {"id": inserted_id, "message": "Mounting structure added successfully"}

@router.get("/api/mounting-structures/")
@admin_only_route
async def get_mounting_structures(user: dict = Depends(get_current_user)):
    structures = db_manager.get_all_materials("mounting_structure")
    return {"mounting_structures": structures}


# BOS Component Endpoints
@router.post("/api/bos-components/", response_model=ComponentResponse)
@admin_only_route
async def add_bos_component(component: BOSComponent = Body(...), user: dict = Depends(get_current_user)):
    component_data = prepare_component_data(component)
    inserted_id = db_manager.add_material("bos_component", component_data)
    return {"id": inserted_id, "message": "BOS component added successfully"}

@router.get("/api/bos-components/")
@admin_only_route
async def get_bos_components(user: dict = Depends(get_current_user)):
    components = db_manager.get_all_materials("bos_component")
    return {"bos_components": components}


# Protection Equipment Endpoints
@router.post("/api/protection-equipment/", response_model=ComponentResponse)
@admin_only_route
async def add_protection_equipment(equipment: ProtectionEquipment = Body(...), user: dict = Depends(get_current_user)):
    equipment_data = prepare_component_data(equipment)
    inserted_id = db_manager.add_material("protection_equipment", equipment_data)
    return {"id": inserted_id, "message": "Protection equipment added successfully"}

@router.get("/api/protection-equipment/")
@admin_only_route
async def get_protection_equipment(user: dict = Depends(get_current_user)):
    equipment = db_manager.get_all_materials("protection_equipment")
    return {"protection_equipment": equipment}


# Earthing System Endpoints
@router.post("/api/earthing-systems/", response_model=ComponentResponse)
@admin_only_route
async def add_earthing_system(system: EarthingSystem = Body(...), user: dict = Depends(get_current_user)):
    system_data = prepare_component_data(system)
    inserted_id = db_manager.add_material("earthing_system", system_data)
    return {"id": inserted_id, "message": "Earthing system added successfully"}

@router.get("/api/earthing-systems/")
@admin_only_route
async def get_earthing_systems(user: dict = Depends(get_current_user)):
    systems = db_manager.get_all_materials("earthing_system")
    return {"earthing_systems": systems}


# Net Metering Endpoints
@router.post("/api/net-metering/", response_model=ComponentResponse)
@admin_only_route
async def add_net_metering(metering: NetMetering = Body(...), user: dict = Depends(get_current_user)):
    metering_data = prepare_component_data(metering)
    inserted_id = db_manager.add_material("net_metering", metering_data)
    return {"id": inserted_id, "message": "Net metering added successfully"}

@router.get("/api/net-metering/")
@admin_only_route
async def get_net_metering(user: dict = Depends(get_current_user)):
    metering = db_manager.get_all_materials("net_metering")
    return {"net_metering": metering}


#------------------------these are the routes for the quotation generation 
# Add to Inventory (Admin Only)
# saving the inventory to the database 
@router.post("/api/inventory/", response_model=ComponentResponse)
@admin_only_route
async def add_to_inventory(
    items: Dict[str, List[List[Union[str, int]]]] = Body(...),
    user: dict = Depends(get_current_user)
):
    try:
        user_id = user.get("sub")
        inventory = db_manager.get_user_inventory(user_id)
        inventory_collection = db_manager.collections["inventories"]

        if not inventory:
            # If no inventory exists, create a new one with all items
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
                    # Convert string numbers to integers for cost and profit
                    processed_components = []
                    for component in components:
                        processed_component = component.copy()  # Create a copy to avoid modifying the original
                        
                        # Convert cost (index 1) to integer if it exists
                        if len(processed_component) > 1 and processed_component[1] not in ["", "N/A"]:
                            try:
                                processed_component[1] = int(processed_component[1])
                            except (ValueError, TypeError):
                                pass
                        
                        # Convert profit (index 2) to integer if it exists
                        if len(processed_component) > 2 and processed_component[2] not in ["", "N/A"]:
                            try:
                                processed_component[2] = int(processed_component[2])
                            except (ValueError, TypeError):
                                pass
                        
                        processed_components.append(processed_component)
                    
                    inventory_data[category] = processed_components

            insert_result = inventory_collection.insert_one(inventory_data)
            return {"id": str(insert_result.inserted_id), "message": "Inventory created successfully"}

        else:
            # For existing inventory, we need to update selectively
            update_operations = []
            new_items_added = False
            
            for category, new_components in items.items():
                if category in inventory:
                    existing_components = inventory[category]
                    components_to_add = []
                    
                    for new_component in new_components:
                        # Process the new component (convert strings to integers)
                        processed_component = new_component.copy()
                        
                        # Convert cost (index 1) to integer
                        if len(processed_component) > 1 and processed_component[1] not in ["", "N/A"]:
                            try:
                                processed_component[1] = int(processed_component[1])
                            except (ValueError, TypeError):
                                pass
                        
                        # Convert profit (index 2) to integer
                        if len(processed_component) > 2 and processed_component[2] not in ["", "N/A"]:
                            try:
                                processed_component[2] = int(processed_component[2])
                            except (ValueError, TypeError):
                                pass
                        
                        # Check if this component already exists in inventory
                        # We compare based on the model name (first element)
                        if len(processed_component) > 0:
                            model_exists = False
                            for existing_component in existing_components:
                                if len(existing_component) > 0 and existing_component[0] == processed_component[0]:
                                    model_exists = True
                                    break
                            
                            if not model_exists:
                                components_to_add.append(processed_component)
                                new_items_added = True
                    
                    # Only update if we have new components to add
                    if components_to_add:
                        update_operations.append(
                            UpdateOne(
                                {"user_id": user_id},
                                {"$push": {category: {"$each": components_to_add}}}
                            )
                        )
            
            # Always update the timestamp
            update_operations.append(
                UpdateOne(
                    {"user_id": user_id},
                    {"$set": {"updated_at": datetime.now()}}
                )
            )
            
            # Execute the bulk write if we have operations
            if update_operations:
                inventory_collection.bulk_write(update_operations)
                
            # Return appropriate message based on whether new items were added
            if new_items_added:
                return {"id": str(inventory["_id"]), "message": "Inventory updated with new components"}
            else:
                return {"id": str(inventory["_id"]), "message": "No new components to add - inventory unchanged"}

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to update inventory: {str(e)}")
    

# Get Inventory (User and Admin)
@router.get("/api/inventory/", response_model=Dict)
async def get_user_inventory(user: dict = Depends(get_current_user)):
    try:
        user_id = user.get("sub")
        inventory = db_manager.get_user_inventory(user_id)

        if not inventory:
            raise HTTPException(
                status_code=404,
                detail=f"No inventory found for user: {user_id}"
            )

        inventory["_id"] = str(inventory["_id"])
        return inventory

    except Exception as e:
        if isinstance(e, HTTPException):
            raise e
        raise HTTPException(
            status_code=500,
            detail=f"Failed to retrieve inventory: {str(e)}"
        )
        
#this will help in generating the quotations for the user by permuting the components in the inventory
@router.get("/api/inventory/quotations")
async def generate_user_quotations(max_quotations: int = Query(None, description="Maximum number of quotations to generate"), user: dict = Depends(get_current_user)):
    try:
        user_id = user.get("sub")
        inventory = db_manager.get_user_inventory(user_id)
        
        if not inventory:
            raise HTTPException(status_code=404, detail=f"No inventory found for user ID: {user_id}")
        
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
        permutations = list(itertools.product(
            solar_panels if solar_panels else [[]],
            inverters if inverters else [[]],
            mounting_structures if mounting_structures else [[]],
            earthing_systems if earthing_systems else [[]]
        ))
        
        # Apply max_quotations limit if specified
        if max_quotations is not None:
            permutations = permutations[:max_quotations]
        
        quotations = []
        
        for idx, (panel, inverter, mount, earth) in enumerate(permutations):
            # Skip invalid combinations (empty components)
            if not panel or not inverter or not mount or not earth:
                continue
            
            # Extract costs and profits using correct indices [model, cost, profit]
            panel_cost = int(panel[1]) if len(panel) > 1 and panel[1] not in ["", "N/A"] else 0
            panel_profit = int(panel[2]) if len(panel) > 2 and panel[2] not in ["", "N/A"] else 0
            
            inverter_cost = int(inverter[1]) if len(inverter) > 1 and inverter[1] not in ["", "N/A"] else 0
            inverter_profit = int(inverter[2]) if len(inverter) > 2 and inverter[2] not in ["", "N/A"] else 0
            
            mount_cost = int(mount[1]) if len(mount) > 1 and mount[1] not in ["", "N/A"] else 0
            mount_profit = int(mount[2]) if len(mount) > 2 and mount[2] not in ["", "N/A"] else 0
            
            earth_cost = int(earth[1]) if len(earth) > 1 and earth[1] not in ["", "N/A"] else 0
            earth_profit = int(earth[2]) if len(earth) > 2 and earth[2] not in ["", "N/A"] else 0
            
            # Calculate costs and profits for additional components using correct indices
            bos_cost = sum(int(comp[1]) if len(comp) > 1 and comp[1] not in ["", "N/A"] else 0 for comp in bos_components)
            bos_profit = sum(int(comp[2]) if len(comp) > 2 and comp[2] not in ["", "N/A"] else 0 for comp in bos_components)
            
            protection_cost = sum(int(comp[1]) if len(comp) > 1 and comp[1] not in ["", "N/A"] else 0 for comp in protection_equipment)
            protection_profit = sum(int(comp[2]) if len(comp) > 2 and comp[2] not in ["", "N/A"] else 0 for comp in protection_equipment)
            
            metering_cost = sum(int(comp[1]) if len(comp) > 1 and comp[1] not in ["", "N/A"] else 0 for comp in net_metering)
            metering_profit = sum(int(comp[2]) if len(comp) > 2 and comp[2] not in ["", "N/A"] else 0 for comp in net_metering)
            
            # Calculate total cost and profit
            total_cost = panel_cost + inverter_cost + mount_cost + earth_cost + bos_cost + protection_cost + metering_cost
            total_profit = panel_profit + inverter_profit + mount_profit + earth_profit + bos_profit + protection_profit + metering_profit
            
            # Create simple quotation with just model numbers
            quotation = {
                "SolarPanel": panel[0],
                "Inverter": inverter[0],
                "MountingStructure": mount[0],
                "EarthingSystem": earth[0],
                "BOSComponents": [comp[0] for comp in bos_components],
                "ProtectionEquipment": [comp[0] for comp in protection_equipment],
                "NetMetering": [comp[0] for comp in net_metering]
            }
            
            quotation_obj = InventoryQuotation(
                user_id=user_id,
                inventory_id=str(inventory["_id"]),
                quotation=quotation,
                total_cost=total_cost,
                total_profit=total_profit
            )
            
            quotations.append(quotation_obj.dict())
        
        return {"quotations": quotations, "count": len(quotations)}
        
    except Exception as e:
        if isinstance(e, HTTPException):
            raise e
        raise HTTPException(status_code=500, detail=f"Failed to generate quotations: {str(e)}")
    
    
# @router.post("/api/quotations/", response_model=QuotationResponse)
# async def get_quotation(request: QuotationFilterRequest = Body(...), user: dict = Depends(get_current_user)):
#     try:
#         # Fetch all components
#         inverters = db_manager.get_all_materials("inverter")
#         solar_panels = db_manager.get_all_materials("solar_panel")
#         mounting_structures = db_manager.get_all_materials("mounting_structure")
#         bos_components = db_manager.get_all_materials("bos_component")
#         protection_equipment = db_manager.get_all_materials("protection_equipment")
        
#         # Apply filters if provided
#         if request.inverter_brands:
#             inverters = [inv for inv in inverters if inv.get("brand") in request.inverter_brands]
        
#         if request.panel_brands:
#             solar_panels = [panel for panel in solar_panels if panel.get("brand") in request.panel_brands]
        
#         if request.mounting_material:
#             mounting_structures = [mount for mount in mounting_structures 
#                                   if mount.get("Material") in request.mounting_material]
        
#         if request.mounting_coating:
#             mounting_structures = [mount for mount in mounting_structures 
#                                   if mount.get("Coating_Type") in request.mounting_coating]
        
#         # Generate all permutations
#         permutations = list(product(inverters, solar_panels, mounting_structures))
        
#         # Create quotation options
#         quotation_options = []
        
#         for i, (inverter, panel, mount) in enumerate(permutations):
#             # Calculate required number of panels based on system capacity
#             panel_capacity_kw = panel.get("power_w", 0) / 1000
#             required_panels = max(1, round(request.system_capacity_kw / panel_capacity_kw))
            
#             # Calculate costs for components
#             inverter_cost = inverter.get("cost", 0)
#             inverter_profit = inverter.get("profit", 0)
#             inverter_total = inverter_cost * (1 + inverter_profit)
            
#             panel_cost = panel.get("cost", 0) * required_panels
#             panel_profit = panel.get("profit", 0)
#             panel_total = panel_cost * (1 + panel_profit)
            
#             mount_cost = mount.get("cost", 0)
#             mount_profit = mount.get("profit", 0)
#             mount_total = mount_cost * (1 + mount_profit)
            
#             # Calculate BOS and protection equipment costs
#             bos_total_cost = sum(item.get("cost", 0) for item in bos_components)
#             bos_total_profit = sum(item.get("cost", 0) * item.get("profit", 0) for item in bos_components)
            
#             protection_total_cost = sum(item.get("cost", 0) for item in protection_equipment)
#             protection_total_profit = sum(item.get("cost", 0) * item.get("profit", 0) for item in protection_equipment)
            
#             # Calculate total system cost and profit
#             total_system_cost = inverter_cost + panel_cost + mount_cost + bos_total_cost + protection_total_cost
#             total_profit = inverter_cost * inverter_profit + panel_cost * panel_profit + mount_cost * mount_profit + bos_total_profit + protection_total_profit
#             total_price = total_system_cost + total_profit
            
#             # Create component quotations
#             inverter_quotation = ComponentQuotation(
#                 id=inverter.get("id", str(uuid.uuid4())),
#                 brand=inverter.get("brand", ""),
#                 model=inverter.get("model", ""),
#                 specifications=f"{inverter.get('Efficiency', 0)}% efficiency, {inverter.get('MPPT_Channels', 0)} MPPT channels",
#                 warranty=inverter.get("Warranty", 0),
#                 cost=inverter_cost,
#                 profit=inverter_profit,
#                 total_price=inverter_total
#             )
            
#             panel_quotation = ComponentQuotation(
#                 id=panel.get("id", str(uuid.uuid4())),
#                 brand=panel.get("brand", ""),
#                 model=panel.get("model_number", ""),
#                 specifications=f"{panel.get('power_w', 0)}W, {panel.get('efficiency_percent', 0)}% efficiency, {required_panels} panels",
#                 warranty=panel.get("Warranty", 0),
#                 cost=panel_cost,
#                 profit=panel_profit,
#                 total_price=panel_total
#             )
            
#             mounting_quotation = MountingQuotation(
#                 id=mount.get("id", str(uuid.uuid4())),
#                 material=mount.get("Material", ""),
#                 coating_type=mount.get("Coating_Type", ""),
#                 brand=mount.get("Brand", ""),
#                 specifications=mount.get("Specifications", ""),
#                 warranty=mount.get("Warranty", 0),
#                 cost=mount_cost,
#                 profit=mount_profit,
#                 total_price=mount_total
#             )
            
#             # Create BOS component quotations
#             bos_quotations = []
#             for bos in bos_components:
#                 bos_cost = bos.get("cost", 0)
#                 bos_profit = bos.get("profit", 0)
#                 bos_total = bos_cost * (1 + bos_profit)
                
#                 bos_quotations.append(ComponentQuotation(
#                     id=bos.get("id", str(uuid.uuid4())),
#                     brand=bos.get("Brand", ""),
#                     model=bos.get("Component_Type", ""),
#                     specifications=bos.get("Specifications", ""),
#                     warranty=bos.get("Warranty", 0),
#                     cost=bos_cost,
#                     profit=bos_profit,
#                     total_price=bos_total
#                 ))
            
#             # Create protection equipment quotations
#             protection_quotations = []
#             for protection in protection_equipment:
#                 protection_cost = protection.get("cost", 0)
#                 protection_profit = protection.get("profit", 0)
#                 protection_total = protection_cost * (1 + protection_profit)
                
#                 protection_quotations.append(ComponentQuotation(
#                     id=protection.get("id", str(uuid.uuid4())),
#                     brand=protection.get("Brand", ""),
#                     model=protection.get("Model", ""),
#                     specifications=protection.get("Specifications", ""),
#                     warranty=protection.get("Warranty", 0),
#                     cost=protection_cost,
#                     profit=protection_profit,
#                     total_price=protection_total
#                 ))
                
#             # Create quotation option
#             quotation_option = QuotationOption(
#                 quotation_id=f"QT-{i+1}-{uuid.uuid4().hex[:6]}",
#                 inverter=inverter_quotation,
#                 solar_panel=panel_quotation,
#                 mounting_structure=mounting_quotation,
#                 bos_components=bos_quotations,
#                 protection_equipment=protection_quotations,
#                 total_system_cost=total_system_cost,
#                 total_profit=total_profit,
#                 total_price=total_price
#             )
            
#             quotation_options.append(quotation_option)
        
#         # Create and return the response
#         response = QuotationResponse(
#             quotation_options=quotation_options,
#             total_options=len(quotation_options),
#             system_capacity_kw=request.system_capacity_kw
#         )
        
#         return response
        
#     except Exception as e:
#         print(f"Error generating quotation: {str(e)}")
#         raise HTTPException(status_code=500, detail=f"Failed to generate quotation: {str(e)}")

@router.get("/")
async def root():
    return {"message": "Solar System Quotation Generator API"}