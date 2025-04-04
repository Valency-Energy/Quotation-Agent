import requests
import json
import random
import uuid
from datetime import datetime

# Base URL of your API - change if needed
BASE_URL = "http://127.0.0.1:8000/api"

def print_response(resp, title=None):
    """Helper function to print API responses nicely"""
    if title:
        print(f"\n=== {title} ===")
    print(f"Status Code: {resp.status_code}")
    if resp.status_code == 200:
        print(json.dumps(resp.json(), indent=2))
    else:
        print(f"Error: {resp.text}")

def add_test_components():
    """Add test components to the database"""
    print("\n=== Adding Test Components ===")
    
    # Add a solar panel
    solar_panel_data = {
        "brand": "TestSolar",
        "model_number": "TS-250W",
        "power_w": 250,
        "efficiency": 19.5,
        "warranty_years": 25,
        "cost": 150,
        "profit": 30
    }
    resp = requests.post(f"{BASE_URL}/solar-panels/", json=solar_panel_data)
    print_response(resp, "Added Solar Panel")
    
    # Add an inverter
    inverter_data = {
        "brand": "InverterCo",
        "model": "Inv-1000",
        "capacity_w": 1000,
        "efficiency": 97.5,
        "warranty_years": 10,
        "cost": 500,
        "profit": 100
    }
    resp = requests.post(f"{BASE_URL}/inverters/", json=inverter_data)
    print_response(resp, "Added Inverter")
    
    # Add a mounting structure
    mounting_structure_data = {
        "Structure_Type": "Roof Mount",
        "Brand": "MountCo",
        "Material": "Aluminum",
        "Warranty_Years": 15,
        "cost": 300,
        "profit": 75
    }
    resp = requests.post(f"{BASE_URL}/mounting-structures/", json=mounting_structure_data)
    mounting_id = resp.json()["id"] if resp.status_code == 200 else None
    print_response(resp, "Added Mounting Structure")
    
    # Add earthing system
    earthing_system_data = {
        "Type": "Rod Type",
        "Brand": "EarthSafe",
        "Material": "Copper",
        "Standards": "IEEE-80",
        "cost": 100,
        "profit": 25
    }
    resp = requests.post(f"{BASE_URL}/earthing-systems/", json=earthing_system_data)
    print_response(resp, "Added Earthing System")
    
    # Add net metering
    net_metering_data = {
        "Meter_Type": "Bidirectional",
        "Brand": "MeterTech",
        "Accuracy": 99.5,
        "Features": "Remote Monitoring",
        "cost": 200,
        "profit": 40
    }
    resp = requests.post(f"{BASE_URL}/net-metering/", json=net_metering_data)
    print_response(resp, "Added Net Metering")
    
    # Add BOS component
    bos_component_data = {
        "component_type": "DC Cable",
        "brand": "CableCo",
        "specifications": "6mm² UV resistant",
        "warranty_years": 5,
        "cost": 50,
        "profit": 10
    }
    resp = requests.post(f"{BASE_URL}/bos-components/", json=bos_component_data)
    print_response(resp, "Added BOS Component")
    
    # Add protection equipment
    protection_equipment_data = {
        "equipment_type": "DC Isolator",
        "brand": "SafeSwitch",
        "specifications": "1000V, 32A",
        "warranty_years": 5,
        "cost": 75,
        "profit": 15
    }
    resp = requests.post(f"{BASE_URL}/protection-equipment/", json=protection_equipment_data)
    print_response(resp, "Added Protection Equipment")
    
    return mounting_id

def get_mounting_structure_id():
    """Get an existing mounting structure ID from the API"""
    resp = requests.get(f"{BASE_URL}/mounting-structures/")
    if resp.status_code == 200 and resp.json()["mounting_structures"]:
        return resp.json()["mounting_structures"][0]["_id"]
    return None

def test_quotation_generation(mounting_id):
    """Test the quotation generation endpoint"""
    if not mounting_id:
        print("Error: No mounting structure ID available. Cannot test quotation generation.")
        return
    
    quotation_request = {
        "installation_type": "residential",
        "mounting_structure_id": mounting_id,
        "system_capacity_kw": 3.75,  # 15 * 250W panels
        "location": "Test Location",
        "include_details": True
    }
    
    print("\n=== Testing Quotation Generation ===")
    print(f"Request data: {json.dumps(quotation_request, indent=2)}")
    
    resp = requests.post(f"{BASE_URL}/generate-quotations/", json=quotation_request)
    print_response(resp, "Quotation Generation Response")
    
    # If successful, get the first quotation ID to test the single quotation endpoint
    if resp.status_code == 200 and resp.json()["quotations"]:
        quotation_id = resp.json()["quotations"][0]["quotation_id"]
        batch_id = resp.json()["batch_id"]
        
        # Test getting a single quotation
        print("\n=== Testing Get Single Quotation ===")
        resp = requests.get(f"{BASE_URL}/quotations/single/{quotation_id}")
        print_response(resp, "Single Quotation Response")
        
        # Test filtering quotations
        print("\n=== Testing Filter Quotations ===")
        filter_params = {
            "batch_id": batch_id,
            "installation_type": "residential",
            "min_capacity": 3.0,
            "max_capacity": 5.0
        }
        resp = requests.get(f"{BASE_URL}/quotations/filter/", params=filter_params)
        print_response(resp, "Filtered Quotations Response")

def main():
    print("=== Solar Quotation API Test Script ===")
    
    # First try to get an existing mounting structure ID
    mounting_id = get_mounting_structure_id()
    
    # If no mounting structure exists, add test components
    if not mounting_id:
        print("No existing mounting structure found. Adding test components...")
        mounting_id = add_test_components()
    
    # Test quotation generation
    test_quotation_generation(mounting_id)

if __name__ == "__main__":
    main()