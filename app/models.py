from typing import Union

from app.bos_component.models import BOSComponent
from app.earthing_system.models import EarthingSystem
from app.inverter.models import Inverter
from app.mounting_structure.models import MountingStructure
from app.net_metering.models import NetMetering
from app.protection_equipment.models import ProtectionEquipment
from app.solar_panel.models import SolarPanel


ComponentType = Union[
    SolarPanel,
    Inverter,
    MountingStructure,
    BOSComponent,
    ProtectionEquipment,
    EarthingSystem,
    NetMetering,
]
