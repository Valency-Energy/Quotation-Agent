from pydantic import BaseModel


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
