
from pymongo import MongoClient
from typing import Dict, List, Optional
import os
from datetime import datetime

class MongoDBManager:
    def __init__(self):
        # Connect to MongoDB
        mongo_uri = "mongodb+srv://rkapoorbe23:La1YcgqAGSHLK7XL@blumi.r2bw9.mongodb.net/?retryWrites=true&w=majority&appName=Blumi"
        self.client = MongoClient(mongo_uri)
        self.db = self.client["solar_quotation_system"]
        
        # Collections for each material type
        self.collections = {
            "solar_panel": self.db["solar_panels"],
            "inverter": self.db["inverters"],
            "mounting_structure": self.db["mounting_structures"],
            "bos_component": self.db["bos_components"],
            "protection_equipment": self.db["protection_equipments"],
            "earthing_system": self.db["earthing_systems"],
            "net_metering": self.db["net_meterings"],
            "quotations": self.db["quotations"],
            "inventories": self.db["inventories"]
        }

    def add_material(self, material_type: str, material_data: Dict) -> str:
        """Add a new material to the database"""
        if material_type not in self.collections:
            raise ValueError(f"Invalid material type: {material_type}")
        
        material_data["created_at"] = datetime.now()
        result = self.collections[material_type].insert_one(material_data)
        return str(result.inserted_id)

    def get_all_materials(self, material_type: str, user_id: Optional[str] = None) -> List[Dict]:
        """Get all materials of a specific type"""
        if material_type not in self.collections:
            raise ValueError(f"Invalid material type: {material_type}")
        
        query = {}
        if user_id:
            query["user_id"] = user_id
            
        materials = list(self.collections[material_type].find(query))
        # Convert ObjectId to string for JSON serialization
        for material in materials:
            material["_id"] = str(material["_id"])
        return materials

    def get_quotation_batch(self, batch_id: str) -> List[Dict]:
        """Get a specific batch of quotations"""
        quotations = list(self.collections["quotations"].find({"batch_id": batch_id}))
        for quotation in quotations:
            quotation["_id"] = str(quotation["_id"])
        return quotations
    def user_inventories(self, user_id: str) -> List[Dict]:
        """Get all inventories for a specific user"""
        inventories = list(self.collections["inventories"].find({"user_id": user_id}))
        for inventory in inventories:
            inventory["_id"] = str(inventory["_id"])
        return inventories
    def get_user_inventory(self, user_id: str) -> Optional[Dict]:
        inventory = self.collections["inventories"].find_one({"user_id": user_id})
        if inventory:
            inventory["_id"] = str(inventory["_id"])
        return inventory


# Create a single instance of the database manager
db_manager = MongoDBManager()