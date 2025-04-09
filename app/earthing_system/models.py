from pydantic import BaseModel


class EarthingSystem(BaseModel):
    Type: str
    Brand: str
    Material: str
    Specifications: str
    Application: str
    Warranty: int
    cost: float
    profit: float
