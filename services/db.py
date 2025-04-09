from pymongo import MongoClient
from typing import Dict, List, Optional
import os
from datetime import datetime

from dotenv import load_dotenv

load_dotenv()


class MongoDBManager:
    def __init__(self):
        # Connect to MongoDB
        # TODO: Change MONGO_URI to environment URI
        mongo_uri = os.getenv("MONGO_URI")
        # mongo_uri = os.environ.get("MONGO_URI")
        if not mongo_uri:
            raise ValueError("MONGO_URI environment variable not set")
        self.client = MongoClient(mongo_uri)
        self.db = self.client.get_database("solar_quotation_system")

        # Collections for each material type
        self.collections = {
            "solar_panel": self.db.get_collection("solar_panels"),
            "inverter": self.db.get_collection("inverters"),
            "mounting_structure": self.db.get_collection("mounting_structures"),
            "bos_component": self.db.get_collection("bos_components"),
            "protection_equipment": self.db.get_collection("protection_equipments"),
            "earthing_system": self.db.get_collection("earthing_systems"),
            "net_metering": self.db.get_collection("net_meterings"),
            "quotations": self.db.get_collection("quotations"),
            "inventories": self.db.get_collection("inventories"),
        }

    def add_material(self, material_type: str, material_data: Dict) -> str:
        """Add a new material to the database"""
        if material_type not in self.collections:
            raise ValueError(f"Invalid material type: {material_type}")

        material_data["created_at"] = datetime.now()
        result = self.collections[material_type].insert_one(material_data)
        return str(result.inserted_id)

    def get_all_materials(
        self, material_type: str, user_id: Optional[str] = None
    ) -> List[Dict]:
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
