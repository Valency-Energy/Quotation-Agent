import uuid
from services.schemas import ComponentQuotation, MountingQuotation, QuotationOption


async def create_inverter_quotations(
    inverter: dict, inverter_cost, inverter_profit, inverter_total
) -> ComponentQuotation:
    inverter_quotation = ComponentQuotation(
        id=inverter.get("id", str(uuid.uuid4())),
        brand=inverter.get("brand", ""),
        model=inverter.get("model", ""),
        specifications=f"{inverter.get('Efficiency', 0)}% efficiency, {inverter.get('MPPT_Channels', 0)} MPPT channels",
        warranty=inverter.get("Warranty", 0),
        cost=inverter_cost,
        profit=inverter_profit,
        total_price=inverter_total,
    )

    return inverter_quotation


async def create_panel_quotations(
    panel: dict, panel_cost, panel_profit, panel_total, required_panels
) -> ComponentQuotation:
    panel_quotations = ComponentQuotation(
        id=panel.get("id", str(uuid.uuid4())),
        brand=panel.get("brand", ""),
        model=panel.get("model_number", ""),
        specifications=f"{panel.get('power_w', 0)}W, {panel.get('efficiency_percent', 0)}% efficiency, {required_panels} panels",
        warranty=panel.get("Warranty", 0),
        cost=panel_cost,
        profit=panel_profit,
        total_price=panel_total,
    )

    return panel_quotations


async def create_mounting_quotations(
    mount: dict, mount_cost, mount_profit, mount_total
) -> MountingQuotation:
    mounting_quotations = MountingQuotation(
        id=mount.get("id", str(uuid.uuid4())),
        material=mount.get("Material", ""),
        coating_type=mount.get("Coating_Type", ""),
        brand=mount.get("Brand", ""),
        specifications=mount.get("Specifications", ""),
        warranty=mount.get("Warranty", 0),
        cost=mount_cost,
        profit=mount_profit,
        total_price=mount_total,
    )

    return mounting_quotations


async def create_bos_quotations(
    bos: dict, bos_cost, bos_profit, bos_total
) -> ComponentQuotation:
    bos_quotations = ComponentQuotation(
        id=bos.get("id", str(uuid.uuid4())),
        brand=bos.get("Brand", ""),
        model=bos.get("Component_Type", ""),
        specifications=bos.get("Specifications", ""),
        warranty=bos.get("Warranty", 0),
        cost=bos_cost,
        profit=bos_profit,
        total_price=bos_total,
    )

    return bos_quotations


async def create_protection_quotations(
    protection: dict, protection_cost, protection_profit, protection_total
) -> ComponentQuotation:
    protection_quotation = ComponentQuotation(
        id=protection.get("id", str(uuid.uuid4())),
        brand=protection.get("Brand", ""),
        model=protection.get("Model", ""),
        specifications=protection.get("Specifications", ""),
        warranty=protection.get("Warranty", 0),
        cost=protection_cost,
        profit=protection_profit,
        total_price=protection_total,
    )
    return protection_quotation


async def create_quotation_options(
    inverter_quotation,
    panel_quotation,
    mounting_quotation,
    bos_quotations,
    protection_quotations,
    total_system_cost,
    total_profit,
    total_price,
    idx,
) -> QuotationOption:
    quotation_option = QuotationOption(
        quotation_id=f"QT-{idx + 1}-{uuid.uuid4().hex[:6]}",
        inverter=inverter_quotation,
        solar_panel=panel_quotation,
        mounting_structure=mounting_quotation,
        bos_components=bos_quotations,
        protection_equipment=protection_quotations,
        total_system_cost=total_system_cost,
        total_profit=total_profit,
        total_price=total_price,
    )

    return quotation_option
