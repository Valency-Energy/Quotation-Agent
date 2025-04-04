import requests
import json
from pprint import pprint

# Base URL of your FastAPI application
BASE_URL = "http://localhost:8000/api"

# Sample data for each component type (3 samples each)

# 1. Solar Panels
solar_panels = [
    {
        "brand": "SunPower",
        "model_number": "SPR-X22-370",
        "technology": "Monocrystalline",
        "power_w": 370,
        "efficiency_percent": 22.7,
        "dimensions_mm": "1690 x 1046 x 40",
        "weight_kg": 18.6,
        "cell_configuration": "96-cell",
        "cost": 250.00,
        "profit": 50.00
    },
    {
        "brand": "LG",
        "model_number": "NeON R",
        "technology": "N-type Monocrystalline",
        "power_w": 380,
        "efficiency_percent": 22.0,
        "dimensions_mm": "1700 x 1016 x 40",
        "weight_kg": 18.0,
        "cell_configuration": "60-cell",
        "cost": 265.00,
        "profit": 55.00
    },
    {
        "brand": "Canadian Solar",
        "model_number": "HiKu CS3W-415",
        "technology": "Poly PERC",
        "power_w": 415,
        "efficiency_percent": 18.8,
        "dimensions_mm": "2108 x 1048 x 40",
        "weight_kg": 24.9,
        "cell_configuration": "144-cell",
        "cost": 180.00,
        "profit": 35.00
    }
]

# 2. Inverters
inverters = [
    {
        "brand": "SolarEdge",
        "model": "SE10000H",
        "Efficiency": 99.0,
        "MPPT_Channels": 2,
        "Input_Voltage_Range": "500-900V",
        "Output_Voltage": "230V/400V",
        "IP_Rating": "IP65",
        "Cooling_Method": "Natural convection",
        "Communication": "RS485, Ethernet, Wifi",
        "Warranty": 12,
        "Dimensions": "540 x 315 x 260 mm",
        "Weight": 33,
        "Certifications": "IEC 61000-6-2, IEC 61000-6-3",
        "cost": 2100.00,
        "profit": 300.00
    },
    {
        "brand": "Fronius",
        "model": "Primo 8.2-1",
        "Efficiency": 98.1,
        "MPPT_Channels": 2,
        "Input_Voltage_Range": "270-800V",
        "Output_Voltage": "230V",
        "IP_Rating": "IP65",
        "Cooling_Method": "Regulated air cooling",
        "Communication": "WLAN/Ethernet LAN",
        "Warranty": 10,
        "Dimensions": "645 x 431 x 204 mm",
        "Weight": 21,
        "Certifications": "CE, IEC 62109",
        "cost": 1800.00,
        "profit": 280.00
    },
    {
        "brand": "Huawei",
        "model": "SUN2000 12KTL",
        "Efficiency": 98.5,
        "MPPT_Channels": 4,
        "Input_Voltage_Range": "160-950V",
        "Output_Voltage": "230V/400V",
        "IP_Rating": "IP65",
        "Cooling_Method": "Natural cooling",
        "Communication": "RS485, WLAN",
        "Warranty": 10,
        "Dimensions": "525 x 470 x 262 mm",
        "Weight": 25,
        "Certifications": "IEC 62109, G83/2",
        "cost": 1950.00,
        "profit": 290.00
    }
]

# 3. Mounting Structures
mounting_structures = [
    {
        "Structure_Type": "Roof Mount",
        "Material": "Aluminum",
        "Brand": "IronRidge",
        "Specifications": "XR100 Rail System",
        "GSM_Rating": 275,
        "Wind_Speed_Rating": 180,
        "Tilt_Angle": "5-45 degrees",
        "Coating_Type": "Anodized",
        "Warranty": 20,
        "cost": 120.00,
        "profit": 30.00
    },
    {
        "Structure_Type": "Ground Mount",
        "Material": "Galvanized Steel",
        "Brand": "UniRac",
        "Specifications": "GroundMount 2.0",
        "GSM_Rating": 350,
        "Wind_Speed_Rating": 200,
        "Tilt_Angle": "15-35 degrees",
        "Coating_Type": "Hot-dip galvanized",
        "Warranty": 25,
        "cost": 180.00,
        "profit": 45.00
    },
    {
        "Structure_Type": "Flat Roof Ballasted",
        "Material": "Aluminum/Steel",
        "Brand": "SunPower",
        "Specifications": "EnergyMax",
        "GSM_Rating": 300,
        "Wind_Speed_Rating": 160,
        "Tilt_Angle": "10 degrees fixed",
        "Coating_Type": "Powder coated",
        "Warranty": 15,
        "cost": 150.00,
        "profit": 40.00
    }
]

# 4. BOS Components
bos_components = [
    {
        "Component_Type": "DC Cable",
        "Brand": "Prysmian",
        "Specifications": "6mm² PV1-F Solar Cable",
        "Quality_Grade": "Class A",
        "Warranty": 10,
        "cost": 1.20,
        "profit": 0.30
    },
    {
        "Component_Type": "AC Cable",
        "Brand": "Havells",
        "Specifications": "4mm² 3-core outdoor cable",
        "Quality_Grade": "Class A",
        "Warranty": 5,
        "cost": 2.30,
        "profit": 0.50
    },
    {
        "Component_Type": "Junction Box",
        "Brand": "ABB",
        "Specifications": "IP67 rated 8-string DC combiner",
        "Quality_Grade": "Premium",
        "Warranty": 7,
        "cost": 85.00,
        "profit": 20.00
    }
]

# 5. Protection Equipment
protection_equipment = [
    {
        "Component_Type": "DC Surge Protector",
        "Brand": "Schneider Electric",
        "Model": "PRD40r",
        "Specifications": "1000V DC Type 2",
        "Application": "DC Strings Protection",
        "IP_Rating": "IP20",
        "Certifications": "IEC 61643-11",
        "Warranty": 5,
        "cost": 75.00,
        "profit": 15.00
    },
    {
        "Component_Type": "AC Circuit Breaker",
        "Brand": "ABB",
        "Model": "S200",
        "Specifications": "63A 3-pole",
        "Application": "AC Connection",
        "IP_Rating": "IP20",
        "Certifications": "IEC 60947-2",
        "Warranty": 3,
        "cost": 45.00,
        "profit": 10.00
    },
    {
        "Component_Type": "Fuse Disconnect",
        "Brand": "Suntree",
        "Model": "PV-FSW1000",
        "Specifications": "1000V DC 32A",
        "Application": "String Isolation",
        "IP_Rating": "IP65",
        "Certifications": "IEC 60269-6",
        "Warranty": 5,
        "cost": 35.00,
        "profit": 8.00
    }
]

# 6. Earthing Systems
earthing_systems = [
    {
        "Type": "Grounding Rod",
        "Brand": "Gallagher",
        "Material": "Copper-bonded Steel",
        "Specifications": "1.5m x 14mm diameter",
        "Application": "Main Earthing Terminal",
        "Warranty": 15,
        "cost": 25.00,
        "profit": 5.00
    },
    {
        "Type": "Earthing Cable",
        "Brand": "Polycab",
        "Material": "Copper",
        "Specifications": "16mm² green/yellow",
        "Application": "Equipment Grounding",
        "Warranty": 10,
        "cost": 3.50,
        "profit": 0.80
    },
    {
        "Type": "Lightning Arrester",
        "Brand": "OBO Bettermann",
        "Material": "Aluminum",
        "Specifications": "Air terminal with 30m protection radius",
        "Application": "Lightning Protection",
        "Warranty": 20,
        "cost": 180.00,
        "profit": 45.00
    }
]

# 7. Net Metering
net_meterings = [
    {
        "Meter_Type": "Bidirectional",
        "Brand": "Schneider Electric",
        "Model": "iEM3155",
        "Specifications": "Class 1 accuracy, 3-phase",
        "Communication": "Modbus RTU",
        "Certifications": "MID-approved",
        "Warranty": 5,
        "Additional_Hardware": "CT sensors",
        "cost": 250.00,
        "profit": 50.00
    },
    {
        "Meter_Type": "Smart Meter",
        "Brand": "Itron",
        "Model": "SL7000",
        "Specifications": "Class 0.5S accuracy, import/export",
        "Communication": "GPRS, RS485",
        "Certifications": "IEC 62052-11",
        "Warranty": 7,
        "Additional_Hardware": "Communication gateway",
        "cost": 320.00,
        "profit": 65.00
    },
    {
        "Meter_Type": "Bidirectional",
        "Brand": "Secure Meters",
        "Model": "Elite 440",
        "Specifications": "Class 1 accuracy, single-phase",
        "Communication": "Optical port",
        "Certifications": "IEC 62053-21",
        "Warranty": 5,
        "Additional_Hardware": "None",
        "cost": 180.00,
        "profit": 40.00
    }
]

# Function to make POST requests and handle responses
def post_components(endpoint, component_list, component_type):
    print(f"\n===== Adding {component_type} =====")
    
    for i, component in enumerate(component_list, 1):
        try:
            response = requests.post(
                f"{BASE_URL}/{endpoint}/",
                json=component,
                headers={"Content-Type": "application/json"}
            )
            
            # Check if request was successful
            response.raise_for_status()
            
            # Print response
            print(f"Added {component_type} #{i}:")
            pprint(response.json())
            
        except requests.exceptions.RequestException as e:
            print(f"Error adding {component_type} #{i}: {e}")
            if hasattr(e, 'response') and e.response:
                print(f"Response: {e.response.text}")

# Execute POST requests for each component type
def main():
    print("Starting to add components to the Solar Quotation System...")
    
    # Post all component types
    post_components("solar-panels", solar_panels, "Solar Panel")
    post_components("inverters", inverters, "Inverter")
    post_components("mounting-structures", mounting_structures, "Mounting Structure")
    post_components("bos-components", bos_components, "BOS Component")
    post_components("protection-equipment", protection_equipment, "Protection Equipment")
    post_components("earthing-systems", earthing_systems, "Earthing System")
    post_components("net-metering", net_meterings, "Net Metering")
    
    print("\nCompleted adding all components!")

if __name__ == "__main__":
    main()