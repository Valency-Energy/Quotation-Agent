from pydantic import BaseModel
from typing import List, Dict, Any


class InventoryQuotation(BaseModel):
    user_id: str
    inventory_id: str
    quotation: List[List[Dict[str, Any]]]
    total_cost: float
    total_profit: float


class Inventory(BaseModel):
    user_id: str
    SolarPanels: List[List[str]]
    Inverters: List[List[str]]
    MountingStructures: List[List[str]]
    BOSComponents: List[List[str]]
    ProtectionEquipment: List[List[str]]
    EarthingSystems: List[List[str]]
    NetMetering: List[List[str]]
