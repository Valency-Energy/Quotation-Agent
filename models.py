from pydantic import BaseModel, Field, field_validator
from typing import List, Dict, Optional, Union, Type
from fastapi import HTTPException

def validate_type(value: any, expected_type: Type, field_name: str) -> None:
    if not isinstance(value, expected_type):
        raise HTTPException(
            status_code=400,
            detail=f"Type mismatch for {field_name}: expected {expected_type.__name__}, got {type(value).__name__}"
        )

def validate_positive_number(value: Union[int, float], field_name: str) -> None:
    if value <= 0:
        raise HTTPException(
            status_code=400,
            detail=f"{field_name} must be positive, got {value}"
        )

def validate_percentage(value: float, field_name: str) -> None:
    if not 0 <= value <= 100:
        raise HTTPException(
            status_code=400,
            detail=f"{field_name} must be between 0 and 100, got {value}"
        )

def validate_required_fields(data: Dict, required_fields: List[str], component_type: str) -> None:
    missing_fields = [field for field in required_fields if field not in data]
    if missing_fields:
        raise HTTPException(
            status_code=400,
            detail=f"Missing required fields for {component_type}: {', '.join(missing_fields)}"
        )

class SolarPanel(BaseModel):
    model_number: str = Field(..., strict=True)
    technology: str = Field(..., strict=True)
    power_w: int = Field(..., strict=True)
    efficiency_percent: float = Field(..., strict=True)
    dimensions_mm: str = Field(..., strict=True)
    weight_kg: float = Field(..., strict=True)
    cell_configuration: str = Field(..., strict=True)

    @field_validator('power_w')
    @classmethod
    def validate_power_w(cls, v):
        validate_type(v, int, 'power_w')
        validate_positive_number(v, 'power_w')
        return v

    @field_validator('efficiency_percent', 'weight_kg')
    @classmethod
    def validate_float_fields(cls, v, info):
        validate_type(v, float, info.field_name)
        if info.field_name == 'efficiency_percent':
            validate_percentage(v, info.field_name)
        else:
            validate_positive_number(v, info.field_name)
        return v

    @field_validator('technology')
    @classmethod
    def validate_technology(cls, v):
        valid_technologies = ['mono', 'poly', 'thin-film']
        if v not in valid_technologies:
            raise HTTPException(
                status_code=400,
                detail=f"Invalid technology type. Must be one of: {', '.join(valid_technologies)}"
            )
        return v

class Inverter(BaseModel):
    Efficiency: float = Field(..., strict=True)
    MPPT_Channels: int = Field(..., strict=True)
    Input_Voltage_Range: str = Field(..., strict=True)
    Output_Voltage: str = Field(..., strict=True)
    IP_Rating: str = Field(..., strict=True)
    Cooling_Method: str = Field(..., strict=True)
    Communication: str = Field(..., strict=True)
    Warranty: int = Field(..., strict=True)
    Dimensions: str = Field(..., strict=True)
    Weight: int = Field(..., strict=True)
    Certifications: str = Field(..., strict=True)

    @field_validator('Efficiency')
    @classmethod
    def validate_efficiency(cls, v):
        validate_type(v, float, 'Efficiency')
        validate_percentage(v, 'Efficiency')
        return v

    @field_validator('MPPT_Channels', 'Warranty', 'Weight')
    @classmethod
    def validate_int_fields(cls, v, info):
        validate_type(v, int, info.field_name)
        validate_positive_number(v, info.field_name)
        return v

class MountingStructure(BaseModel):
    Structure_Type: str = Field(..., strict=True)
    Material: str = Field(..., strict=True)
    Specifications: str = Field(..., strict=True)
    GSM_Rating: int = Field(..., strict=True)
    Wind_Speed_Rating: int = Field(..., strict=True)
    Tilt_Angle: str = Field(..., strict=True)
    Coating_Type: str = Field(..., strict=True)
    Warranty: int = Field(..., strict=True)

    @field_validator('GSM_Rating', 'Wind_Speed_Rating', 'Warranty')
    @classmethod
    def validate_int_fields(cls, v):
        validate_type(v, int, 'GSM_Rating' if v == 'GSM_Rating' else 'Wind_Speed_Rating' if v == 'Wind_Speed_Rating' else 'Warranty')
        return v

class BOSComponent(BaseModel):
    Component_Type: str = Field(..., strict=True)
    Specifications: str = Field(..., strict=True)
    Quality_Grade: str = Field(..., strict=True)
    Warranty: int = Field(..., strict=True)

    @field_validator('Warranty')
    @classmethod
    def validate_warranty(cls, v):
        validate_type(v, int, 'Warranty')
        return v

class ProtectionEquipment(BaseModel):
    Component_Type: str = Field(..., strict=True)
    Model: str = Field(..., strict=True)
    Specifications: str = Field(..., strict=True)
    Application: str = Field(..., strict=True)
    IP_Rating: str = Field(..., strict=True)
    Certifications: str = Field(..., strict=True)
    Warranty: int = Field(..., strict=True)

    @field_validator('Warranty')
    @classmethod
    def validate_warranty(cls, v):
        validate_type(v, int, 'Warranty')
        return v

class EarthingSystem(BaseModel):
    Type: str = Field(..., strict=True)
    Material: str = Field(..., strict=True)
    Specifications: str = Field(..., strict=True)
    Application: str = Field(..., strict=True)
    Warranty: int = Field(..., strict=True)

    @field_validator('Warranty')
    @classmethod
    def validate_warranty(cls, v):
        validate_type(v, int, 'Warranty')
        return v

class NetMetering(BaseModel):
    Meter_Type: str = Field(..., strict=True)
    Model: str = Field(..., strict=True)
    Specifications: str = Field(..., strict=True)
    Communication: str = Field(..., strict=True)
    Certifications: str = Field(..., strict=True)
    Warranty: int = Field(..., strict=True)
    Additional_Hardware: str = Field(..., strict=True)

    @field_validator('Warranty')
    @classmethod
    def validate_warranty(cls, v):
        validate_type(v, int, 'Warranty')
        return v

class MaterialSelection(BaseModel):
    material_type: str = Field(..., strict=True)
    available_brands: List[str] = Field(..., strict=True)
    costs: Dict[str, float] = Field(..., strict=True)
    profits: Dict[str, float] = Field(..., strict=True)
    components: Dict[str, Union[SolarPanel, Inverter, MountingStructure, BOSComponent, ProtectionEquipment, EarthingSystem, NetMetering]] = Field(..., strict=True)

    @field_validator('material_type')
    @classmethod
    def validate_material_type(cls, v):
        validate_type(v, str, 'material_type')
        valid_types = [
            'solar_panel', 'inverter', 'mounting_structure', 
            'bos_component', 'protection_equipment', 
            'earthing_system', 'net_metering'
        ]
        if v not in valid_types:
            raise HTTPException(
                status_code=400,
                detail=f"Invalid material type. Must be one of: {', '.join(valid_types)}"
            )
        return v

    @field_validator('available_brands')
    @classmethod
    def validate_available_brands(cls, v):
        validate_type(v, list, 'available_brands')
        if not v:
            raise HTTPException(
                status_code=400,
                detail="At least one brand must be specified"
            )
        if not all(isinstance(brand, str) for brand in v):
            raise HTTPException(
                status_code=400,
                detail="All brands must be strings"
            )
        return v

    @field_validator('costs', 'profits')
    @classmethod
    def validate_costs_profits(cls, v, info):
        validate_type(v, dict, info.field_name)
        for brand, value in v.items():
            if not isinstance(value, float):
                raise HTTPException(
                    status_code=400,
                    detail=f"Invalid type for {info.field_name} value of brand '{brand}': expected float, got {type(value).__name__}"
                )
            if info.field_name == 'costs' and value <= 0:
                raise HTTPException(
                    status_code=400,
                    detail=f"Cost for brand '{brand}' must be greater than 0, got {value}"
                )
            if info.field_name == 'profits' and value < 0:
                raise HTTPException(
                    status_code=400,
                    detail=f"Profit for brand '{brand}' must be greater than or equal to 0, got {value}"
                )
        if 'available_brands' in info.data:
            for brand in info.data['available_brands']:
                if brand not in v:
                    raise HTTPException(
                        status_code=400,
                        detail=f"Missing {info.field_name} for brand: {brand}"
                    )
        return v

    @field_validator('components')
    @classmethod
    def validate_components(cls, v, info):
        validate_type(v, dict, 'components')
        if 'material_type' not in info.data:
            return v
            
        component_type = info.data['material_type']
        component_mapping = {
            'solar_panel': SolarPanel,
            'inverter': Inverter,
            'mounting_structure': MountingStructure,
            'bos_component': BOSComponent,
            'protection_equipment': ProtectionEquipment,
            'earthing_system': EarthingSystem,
            'net_metering': NetMetering
        }
        
        expected_type = component_mapping.get(component_type)
        if not expected_type:
            raise HTTPException(
                status_code=400,
                detail=f"Invalid component type: {component_type}"
            )
            
        for brand, component in v.items():
            if not isinstance(component, expected_type):
                raise HTTPException(
                    status_code=400,
                    detail=f"Invalid component type for brand {brand}. Expected {expected_type.__name__}"
                )
            if brand not in info.data['available_brands']:
                raise HTTPException(
                    status_code=400,
                    detail=f"Component specified for brand {brand} which is not in available_brands"
                )
        return v

class QuotationRequest(BaseModel):
    materials: List[MaterialSelection] = Field(..., strict=True)
    user_id: Optional[str] = Field(None, strict=True)
    save_to_db: bool = Field(True, strict=True)

    @field_validator('materials')
    @classmethod
    def validate_materials(cls, v):
        validate_type(v, list, 'materials')
        if not v:
            raise HTTPException(
                status_code=400,
                detail="At least one material must be specified"
            )
        if not all(isinstance(material, MaterialSelection) for material in v):
            raise HTTPException(
                status_code=400,
                detail="All materials must be valid MaterialSelection objects"
            )
        return v