from pydantic import BaseModel
from typing import List


# Response models with ID field
class ComponentResponse(BaseModel):
    id: str
    message: str = "Component added successfully"


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
