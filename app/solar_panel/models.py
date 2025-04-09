from pydantic import BaseModel


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
