from pydantic import BaseModel, Field
from typing import Any, List, Dict, Optional, Union
import datetime

class User(BaseModel):
    email: str
    full_name: str
    picture: Optional[str] = None
    role: str
    gstin: Optional[str] = None
    phone: Optional[str] = None
    company_name: Optional[str] = None
    company_address: Optional[str] = None


class ComponentResponse(BaseModel):
    id: str
    message: str = "Component added successfully"


# Component models
class SolarPanel(BaseModel):
    brand: str
    model_number: str
    technology: str
    power_w: str
    efficiency_percent: str
    dimensions_mm: str
    weight_kg: float
    cell_configuration: str
    quantity: int
    rate: float
    profit: float

class Inverter(BaseModel):
    brand: str
    model_number: str
    efficiency_percent: float
    mppt_channels: int
    input_voltage_range: str
    output_voltage: str
    ip_rating: str
    cooling_method: str
    communication: str
    warranty: int
    dimensions: str
    weight_kg: int
    certifications: str
    quantity: int
    rate: float
    profit: float

class MountingStructure(BaseModel):
    structure_type: str
    material: str
    brand: str
    specifications: str
    gsm_rating: int
    wind_speed_rating: int
    warranty: int
    quantity: int
    rate: float
    profit: float

class BOSComponent(BaseModel):
    component_type: str
    brand: str
    specifications: str
    quality_grade: str
    warranty: int
    quantity: int
    rate: float
    profit: float

class ProtectionEquipment(BaseModel):
    component_type: str
    brand: str
    model: str
    specifications: str
    application: str
    ip_rating: str
    certifications: str
    warranty: int
    quantity: int
    rate: float
    profit: float

class EarthingSystem(BaseModel):
    type: str
    brand: str
    material: str
    specifications: str
    application: str
    warranty: int
    quantity: int
    rate: float
    profit: float

class NetMetering(BaseModel):
    meter_type: str
    brand: str
    model: str
    specifications: str
    communication: str
    certifications: str
    warranty: int
    additional_hardware: str
    quantity: int
    rate: float
    profit: float

class Inventory(BaseModel):
    user_id: str    
    SolarPanels: List[List[Union[str, int]]]  # [model, quantity, rate, profit]
    Inverters: List[List[Union[str, int]]]
    MountingStructures: List[List[Union[str, int]]]
    BOSComponents: List[List[Union[str, int]]]
    ProtectionEquipment: List[List[Union[str, int]]]
    EarthingSystems: List[List[Union[str, int]]]
    NetMetering: List[List[Union[str, int]]]


# Updated Quotation model
class InventoryQuotation(BaseModel):
    user_id: str
    inventory_id: str
    quotation: Dict[str, Any]  # model numbers for components - some are strings, some are lists
    total_cost: float
    total_profit: float

ComponentType = Union[
    SolarPanel, 
    Inverter, 
    MountingStructure, 
    BOSComponent, 
    ProtectionEquipment, 
    EarthingSystem, 
    NetMetering
]


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