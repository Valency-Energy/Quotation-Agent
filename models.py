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
    power_w: str
    efficiency_percent: str
    dimensions_mm: str
    weight_kg: float
    cell_configuration: str
    cost: float
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
    cost: float
    profit: float

class MountingStructure(BaseModel):
    structure_type: str
    material: str
    brand: str
    specifications: str
    gsm_rating: int
    wind_speed_rating: int
    warranty: int
    cost: float
    profit: float

class BOSComponent(BaseModel):
    component_type: str
    brand: str
    specifications: str
    quality_grade: str
    warranty: int
    cost: float
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
    cost: float
    profit: float

class EarthingSystem(BaseModel):
    type: str
    brand: str
    material: str
    specifications: str
    application: str
    warranty: int
    cost: float
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
