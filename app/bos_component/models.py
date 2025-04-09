from pydantic import BaseModel


class BOSComponent(BaseModel):
    Component_Type: str
    Brand: str
    Specifications: str
    Quality_Grade: str
    Warranty: int
    cost: float
    profit: float
