from fastapi import APIRouter, Body, HTTPException
from itertools import product
from logging import getLogger

from quotation.create_quotations import (
    create_bos_quotations,
    create_inverter_quotations,
    create_mounting_quotations,
    create_panel_quotations,
    create_protection_quotations,
    create_quotation_options,
)

from services.components import apply_filters, QuotationFilterRequest

from services.db import db_manager
from services.schemas import (
    QuotationResponse,
)

routes = APIRouter()
logger = getLogger(__name__)


@routes.get("/")
async def root():
    return {"message": "Solar System Quotation Generator API"}


@routes.post("/api/quotations/", response_model=QuotationResponse)
async def get_quotation(request: QuotationFilterRequest = Body(...)):
    try:
        # Fetch all components
        inverters = db_manager.get_all_materials("inverter")
        solar_panels = db_manager.get_all_materials("solar_panel")
        mounting_structures = db_manager.get_all_materials("mounting_structure")
        bos_components = db_manager.get_all_materials("bos_component")
        protection_equipment = db_manager.get_all_materials("protection_equipment")

        # Apply filters if provided
        inverters, solar_panels, mounting_structures = await apply_filters(
            inverters, solar_panels, mounting_structures, request
        )
        # Generate all permutations
        permutations = list(product(inverters, solar_panels, mounting_structures))

        # Create quotation options
        quotation_options = []

        for i, (inverter, panel, mount) in enumerate(permutations):
            # Calculate required number of panels based on system capacity
            panel_capacity_kw = panel.get("power_w", 0) / 1000
            required_panels = max(
                1, round(request.system_capacity_kw / panel_capacity_kw)
            )

            # Calculate costs for components
            inverter_cost = inverter.get("cost", 0)
            inverter_profit = inverter.get("profit", 0)
            inverter_total = inverter_cost * (1 + inverter_profit)

            panel_cost = panel.get("cost", 0) * required_panels
            panel_profit = panel.get("profit", 0)
            panel_total = panel_cost * (1 + panel_profit)

            mount_cost = mount.get("cost", 0)
            mount_profit = mount.get("profit", 0)
            mount_total = mount_cost * (1 + mount_profit)

            # Calculate BOS and protection equipment costs
            bos_total_cost = sum(item.get("cost", 0) for item in bos_components)
            bos_total_profit = sum(
                item.get("cost", 0) * item.get("profit", 0) for item in bos_components
            )

            protection_total_cost = sum(
                item.get("cost", 0) for item in protection_equipment
            )
            protection_total_profit = sum(
                item.get("cost", 0) * item.get("profit", 0)
                for item in protection_equipment
            )

            # Calculate total system cost and profit
            total_system_cost = (
                inverter_cost
                + panel_cost
                + mount_cost
                + bos_total_cost
                + protection_total_cost
            )
            total_profit = (
                inverter_cost * inverter_profit
                + panel_cost * panel_profit
                + mount_cost * mount_profit
                + bos_total_profit
                + protection_total_profit
            )
            total_price = total_system_cost + total_profit

            # Create component quotations
            inverter_quotation = await create_inverter_quotations(
                inverter, inverter_cost, inverter_profit, inverter_total
            )
            panel_quotation = await create_panel_quotations(
                panel, panel_cost, panel_profit, panel_total, required_panels
            )
            mounting_quotation = await create_mounting_quotations(
                mount, mount_cost, mount_profit, mount_total
            )

            # Create BOS component quotations
            bos_quotations = []
            for bos in bos_components:
                bos_cost = bos.get("cost", 0)
                bos_profit = bos.get("profit", 0)
                bos_total = bos_cost * (1 + bos_profit)

                bos_quotation = await create_bos_quotations(
                    bos, bos_cost, bos_profit, bos_total
                )
                bos_quotations.append(bos_quotation)

            # Create protection equipment quotations
            protection_quotations = []
            for protection in protection_equipment:
                protection_cost = protection.get("cost", 0)
                protection_profit = protection.get("profit", 0)
                protection_total = protection_cost * (1 + protection_profit)

                protection_quotation = await create_protection_quotations(
                    protection, protection_cost, protection_profit, protection_total
                )
                protection_quotations.append(protection_quotation)

            # Create quotation option
            quotation_option = await create_quotation_options(
                inverter_quotation,
                panel_quotation,
                mounting_quotation,
                bos_quotations,
                protection_quotations,
                total_system_cost,
                total_profit,
                total_price,
                idx=i,
            )
            quotation_options.append(quotation_option)

        # Create and return the response
        response = QuotationResponse(
            quotation_options=quotation_options,
            total_options=len(quotation_options),
            system_capacity_kw=request.system_capacity_kw,
        )

        return response

    except Exception as e:
        logger.error(f"Error generating quotation: {str(e)}")
        raise HTTPException(
            status_code=500, detail=f"Failed to generate quotation: {str(e)}"
        )
