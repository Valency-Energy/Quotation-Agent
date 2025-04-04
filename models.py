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
