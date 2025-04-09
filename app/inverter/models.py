from pydantic import BaseModel


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
