from pydantic import BaseModel


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
