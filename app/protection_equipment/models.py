from pydantic import BaseModel


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
