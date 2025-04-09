import uvicorn
import logging
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

# Import service routes
from app.bos_component import bos_component_routes
from app.earthing_system import earthing_system_routes
from app.inventory import inventory_routes
from app.inverter import inverter_routes
from app.mounting_structure import mounting_strcture_routes
from app.net_metering import net_metering_routes
from app.protection_equipment import protection_equipment_routes
from app.solar_panel import solar_panel_routes
from app.routes import routes

# Setup logging
logger = logging.getLogger(__name__)

app = FastAPI(title="Solar Quotation System API", docs_url="/docs", redoc_url="/redoc")

# Set up CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Add routers
app.include_router(bos_component_routes, prefix="/api/bos-components")
app.include_router(earthing_system_routes, prefix="/api/earthing-systems")
app.include_router(inventory_routes, prefix="/api/inventory")
app.include_router(inverter_routes, prefix="/api/inverters")
app.include_router(mounting_strcture_routes, prefix="/api/mounting-structures")
app.include_router(net_metering_routes, prefix="/api/net-metering")
app.include_router(protection_equipment_routes, prefix="/api/protection-equipment")
app.include_router(solar_panel_routes, prefix="/api/solar-panels")
app.include_router(routes, prefix="")


if __name__ == "__main__":
    uvicorn.run(app, host="127.0.0.1", port=8000)
