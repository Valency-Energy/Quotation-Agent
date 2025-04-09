import jwt
import uvicorn
import logging
from fastapi import FastAPI, Body, HTTPException, Query
from typing import List, Dict, Optional, Any
from datetime import datetime
from pydantic import BaseModel, Field, validator
from fastapi.middleware.cors import CORSMiddleware
import uuid
from itertools import product
from fastapi import Depends
import bcrypt

# Import your component models
from models import (
    SolarPanel, Inverter, MountingStructure, BOSComponent, 
    ProtectionEquipment, EarthingSystem, NetMetering, Inventory
)
from db import db_manager
from auth import JWT_ALGORITHM, JWT_SECRET, create_access_token, create_refresh_token, decode_token, register_user, authenticate_user, oauth2_scheme, get_current_user, admin_only_route

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

from pydantic import BaseModel

class UserAuth(BaseModel):
    username: str
    password: str

class UserRegister(UserAuth):
    role: str
    @validator("role")
    def validate_role(cls, v):
        allowed_roles = ["admin", "user"]
        if v not in allowed_roles:
            raise ValueError("Role must be either 'admin' or 'user'")
        return v
    
class ChangePasswordModel(BaseModel):
    old_password: str
    new_password: str

@app.post("/register")
def register(user: UserRegister):
    success = register_user(user.username, user.password, user.role)
    if not success:
        raise HTTPException(status_code=400, detail="Username already exists")
    return {"message": "User registered successfully"}

@app.post("/login")
def login(user: UserAuth):
    token_data = authenticate_user(user.username, user.password)
    if not token_data:
        raise HTTPException(status_code=401, detail="Invalid credentials")

    db_manager.store_refresh_token(user.username, token_data["refresh_token"])

    return {
        "access_token": token_data["access_token"],
        "refresh_token": token_data["refresh_token"],
    }

@app.post("/change-password")
def change_password(
    password_data: ChangePasswordModel,
    user: dict = Depends(get_current_user)
):
    users = db_manager.collections["users"]
    user_data = users.find_one({"username": user["username"]})

    if not user_data or not bcrypt.checkpw(password_data.old_password.encode(), user_data["password"]):
        raise HTTPException(status_code=400, detail="Invalid old password")

    new_hashed = bcrypt.hashpw(password_data.new_password.encode(), bcrypt.gensalt())

    users.update_one(
        {"username": user["username"]},
        {"$set": {
            "password": new_hashed,
            "updated_at": datetime.utcnow()
        }}
    )

    return {"message": "Password changed successfully"}

class RefreshTokenModel(BaseModel):
    refresh_token: str

@app.post("/refresh")
def refresh_token(model: RefreshTokenModel):
    refresh_token = model.refresh_token
    try:
        # Decode the refresh token
        payload = decode_token(refresh_token)
        username = payload.get("username")

        if not username:
            raise HTTPException(status_code=401, detail="Invalid refresh token")

        # Validate the refresh token using db_manager function
        if not db_manager.is_valid_refresh_token(username, refresh_token):
            raise HTTPException(status_code=401, detail="Refresh token invalid or reused")

        # Invalidate old refresh token
        db_manager.delete_refresh_token(username)

        # Get user details
        user_data = db_manager.collections["users"].find_one({"username": username})
        if not user_data:
            raise HTTPException(status_code=404, detail="User not found")

        # Generate new tokens
        new_access_token = create_access_token({
            "username": username,
            "role": user_data["role"]
        })
        new_refresh_token = create_refresh_token({"username": username})

        # Store new refresh token
        db_manager.store_refresh_token(username, new_refresh_token)

        return {
            "access_token": new_access_token,
            "refresh_token": new_refresh_token
        }

    except ValueError as e:
        raise HTTPException(status_code=401, detail=str(e))

    
@app.post("/logout")
def logout(token: str = Depends(oauth2_scheme)):
    try:
        payload = decode_token(token)
        username = payload.get("username")

        db_manager.blacklist_token(token)
        db_manager.delete_refresh_token(username)

        return {"message": "Successfully logged out"}

    except Exception as e:
        raise HTTPException(status_code=401, detail="Invalid token")


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

@app.get("/api/solar-panels/")
@admin_only_route
async def get_solar_panels(user: dict = Depends(get_current_user)):
    try:
        panels = db_manager.get_all_materials("solar_panel")
        return {"solar_panels": panels}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to retrieve solar panels: {str(e)}")

# Inverter Endpoints
from auth import admin_only_route

@app.post("/api/inverters/", response_model=ComponentResponse)
@admin_only_route
async def add_inverter(inverter: Inverter = Body(...), user: dict = Depends(get_current_user)):
    inverter_data = prepare_component_data(inverter)
    inserted_id = db_manager.add_material("inverter", inverter_data)
    return {"id": inserted_id, "message": "Inverter added successfully"}

@app.get("/api/inverters/")
@admin_only_route
async def get_inverters(user: dict = Depends(get_current_user)):
    inverters = db_manager.get_all_materials("inverter")
    return {"inverters": inverters}

# Mounting Structure Endpoints
@app.post("/api/mounting-structures/", response_model=ComponentResponse)
@admin_only_route
async def add_mounting_structure(structure: MountingStructure = Body(...), user: dict = Depends(get_current_user)):
    structure_data = prepare_component_data(structure)
    inserted_id = db_manager.add_material("mounting_structure", structure_data)
    return {"id": inserted_id, "message": "Mounting structure added successfully"}

@app.get("/api/mounting-structures/")
@admin_only_route
async def get_mounting_structures(user: dict = Depends(get_current_user)):
    structures = db_manager.get_all_materials("mounting_structure")
    return {"mounting_structures": structures}


# BOS Component Endpoints
@app.post("/api/bos-components/", response_model=ComponentResponse)
@admin_only_route
async def add_bos_component(component: BOSComponent = Body(...), user: dict = Depends(get_current_user)):
    component_data = prepare_component_data(component)
    inserted_id = db_manager.add_material("bos_component", component_data)
    return {"id": inserted_id, "message": "BOS component added successfully"}

@app.get("/api/bos-components/")
@admin_only_route
async def get_bos_components(user: dict = Depends(get_current_user)):
    components = db_manager.get_all_materials("bos_component")
    return {"bos_components": components}


# Protection Equipment Endpoints
@app.post("/api/protection-equipment/", response_model=ComponentResponse)
@admin_only_route
async def add_protection_equipment(equipment: ProtectionEquipment = Body(...), user: dict = Depends(get_current_user)):
    equipment_data = prepare_component_data(equipment)
    inserted_id = db_manager.add_material("protection_equipment", equipment_data)
    return {"id": inserted_id, "message": "Protection equipment added successfully"}

@app.get("/api/protection-equipment/")
@admin_only_route
async def get_protection_equipment(user: dict = Depends(get_current_user)):
    equipment = db_manager.get_all_materials("protection_equipment")
    return {"protection_equipment": equipment}


# Earthing System Endpoints
@app.post("/api/earthing-systems/", response_model=ComponentResponse)
@admin_only_route
async def add_earthing_system(system: EarthingSystem = Body(...), user: dict = Depends(get_current_user)):
    system_data = prepare_component_data(system)
    inserted_id = db_manager.add_material("earthing_system", system_data)
    return {"id": inserted_id, "message": "Earthing system added successfully"}

@app.get("/api/earthing-systems/")
@admin_only_route
async def get_earthing_systems(user: dict = Depends(get_current_user)):
    systems = db_manager.get_all_materials("earthing_system")
    return {"earthing_systems": systems}


# Net Metering Endpoints
@app.post("/api/net-metering/", response_model=ComponentResponse)
@admin_only_route
async def add_net_metering(metering: NetMetering = Body(...), user: dict = Depends(get_current_user)):
    metering_data = prepare_component_data(metering)
    inserted_id = db_manager.add_material("net_metering", metering_data)
    return {"id": inserted_id, "message": "Net metering added successfully"}

@app.get("/api/net-metering/")
@admin_only_route
async def get_net_metering(user: dict = Depends(get_current_user)):
    metering = db_manager.get_all_materials("net_metering")
    return {"net_metering": metering}

# Add to Inventory (Admin Only)
@app.post("/api/inventory/", response_model=ComponentResponse)
@admin_only_route
async def add_to_inventory(
    user_id: str,
    items: Dict[str, List[List[str]]] = Body(...),  # No more user_id param
    user: dict = Depends(get_current_user)
):
    try:
        ## user_id = user["username"] 
        inventory = db_manager.get_user_inventory(user_id)
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
            return {"id": str(insert_result.inserted_id), "message": "Inventory created successfully"}

        else:
            update_data = {
                "$set": {"updated_at": datetime.now()},
                "$push": {}
            }

            for category, components in items.items():
                if category in inventory:
                    update_data["$push"][category] = {"$each": components}

            if not update_data["$push"]:
                update_data.pop("$push")

            inventory_collection.update_one(
                {"user_id": user_id},
                update_data
            )

            updated_inventory = db_manager.get_user_inventory(user_id)
            return {"id": str(updated_inventory["_id"]), "message": "Inventory updated successfully"}

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to update inventory: {str(e)}")


# Get Inventory (User and Admin)
@app.get("/api/inventory/{user_id}", response_model=Dict)
async def get_user_inventory(user_id : str, user: dict = Depends(get_current_user)):
    try:
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
        

class InventoryQuotation(BaseModel):
    user_id: str
    inventory_id: str
    quotation: List[List[Dict[str, Any]]]
    total_cost: float
    total_profit: float
    
import itertools
from fastapi import Query

@app.get("/api/inventory/{user_id}/quotations")
async def generate_user_quotations(user_id: str, max_quotations: int = Query(10, description="Maximum number of quotations to generate"), user: dict = Depends(get_current_user)):
    try:
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
        # Limit the number of combinations to avoid excessive processing
        permutations = list(itertools.product(
            solar_panels[:3] if solar_panels else [[]],
            inverters[:3] if inverters else [[]],
            mounting_structures[:2] if mounting_structures else [[]],
            earthing_systems[:2] if earthing_systems else [[]]
        ))
        
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
            bos_cost = sum(float(comp[2]) if len(comp) > 2 and comp[2] != "N/A" else 50 for comp in bos_components)
            protection_cost = sum(float(comp[2]) if len(comp) > 2 and comp[2] != "N/A" else 75 for comp in protection_equipment)
            metering_cost = sum(float(comp[2]) if len(comp) > 2 and comp[2] != "N/A" else 150 for comp in net_metering)
            
            # Calculate total cost and profit
            total_cost = panel_cost + inverter_cost + mount_cost + earth_cost + bos_cost + protection_cost + metering_cost
            profit_margin = 0.25  # 25% profit margin
            total_profit = total_cost * profit_margin
            
            # Create quotation structure
            quotation = [
                [{"type": "Solar Panel", "model": panel[0], "quantity": panel[1], "unit_cost": panel_cost / float(panel[1]) if float(panel[1]) > 0 else 0}],
                [{"type": "Inverter", "model": inverter[0], "quantity": inverter[1], "unit_cost": inverter_cost / float(inverter[1]) if float(inverter[1]) > 0 else 0}],
                [{"type": "Mounting Structure", "model": mount[0], "quantity": mount[1], "unit_cost": mount_cost / float(mount[1]) if float(mount[1]) > 0 else 0}],
                [{"type": "Earthing System", "model": earth[0], "quantity": earth[1], "unit_cost": earth_cost / float(earth[1]) if float(earth[1]) > 0 else 0}],
                [{"type": comp[0], "model": "BOS Component", "quantity": comp[1], "unit_cost": float(comp[2]) if len(comp) > 2 and comp[2] != "N/A" else 50 / float(comp[1]) if float(comp[1]) > 0 else 0} for comp in bos_components],
                [{"type": comp[0], "model": "Protection Equipment", "quantity": comp[1], "unit_cost": float(comp[2]) if len(comp) > 2 and comp[2] != "N/A" else 75 / float(comp[1]) if float(comp[1]) > 0 else 0} for comp in protection_equipment],
                [{"type": comp[0], "model": "Net Metering", "quantity": comp[1], "unit_cost": float(comp[2]) if len(comp) > 2 and comp[2] != "N/A" else 150 / float(comp[1]) if float(comp[1]) > 0 else 0} for comp in net_metering]
            ]
            
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
async def get_quotation(request: QuotationFilterRequest = Body(...), user: dict = Depends(get_current_user)):
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