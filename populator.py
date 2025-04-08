import requests
import json
import os
from pprint import pprint

# Base URL of your FastAPI application
BASE_URL = "http://localhost:8000/api"

# Path to the output_json folder
OUTPUT_JSON_PATH = "output_json"

# Function to load JSON data from a file
def load_json(file_name):
    file_path = os.path.join(OUTPUT_JSON_PATH, file_name)
    print(file_path)
    with open(file_path, "r") as file:
        return json.load(file)

# Load data from JSON files
solar_panels = load_json("Solar Panels.json")
for i in solar_panels:
    print(i, end='\n')
inverters = load_json("Inverters.json")
mounting_structures = load_json("Mounting Structures.json")
bos_components = load_json("BOS Components.json")
protection_equipment = load_json("Protection Equipment.json")
earthing_systems = load_json("Earthing Systems.json")
net_meterings = load_json("Net Metering.json")

# Function to make POST requests and handle responses
def post_components(endpoint, component_list, component_type):
    print(f"\n===== Adding {component_type} =====")
    
    for i, component in enumerate(component_list, 1):
        try:
            print(f"Payload for {component_type} #{i}:")
            pprint(component)
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
    post_components("bos-components", bos_components, "BOS Component")
    post_components("protection-equipment", protection_equipment, "Protection Equipment")
    post_components("earthing-systems", earthing_systems, "Earthing System")
    post_components("net-metering", net_meterings, "Net Metering")
    
    print("\nCompleted adding all components!")

if __name__ == "__main__":
    main()