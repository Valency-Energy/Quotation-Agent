from pymongo import MongoClient, ASCENDING
from typing import Dict, List, Optional
import os
from datetime import datetime
import bcrypt
import dotenv

dotenv.load_dotenv()

class MongoDBManager:
    def __init__(self):
        mongo_uri = os.environ.get("MONGO_URI")
        if not mongo_uri:
            raise ValueError("MONGO_URI environment variable not set")
        self.client = MongoClient(mongo_uri)
        self.db = self.client["solar_quotation_system"]

        self.collections = {
            "solar_panel": self.db["solar_panels"],
            "inverter": self.db["inverters"],
            "mounting_structure": self.db["mounting_structures"],
            "bos_component": self.db["bos_components"],
            "protection_equipment": self.db["protection_equipments"],
            "earthing_system": self.db["earthing_systems"],
            "net_metering": self.db["net_meterings"],
            "quotations": self.db["quotations"],
            "inventories": self.db["inventories"],
            "users": self.db["users"],
            "blacklisted_tokens": self.db["blacklisted_tokens"],
            "refresh_tokens": self.db["refresh_tokens"],
            "access_tokens": self.db["access_tokens"],
        }

        self._ensure_ttl_index()

    def _ensure_ttl_index(self):
        self.collections["blacklisted_tokens"].create_index(
            [("created_at", ASCENDING)],
            expireAfterSeconds=900  # 15 minutes
        )
        self.collections["access_tokens"].create_index(
            [("created_at", ASCENDING)],
            expireAfterSeconds=900  # 15 minutes
        )

        # TTL for refresh tokens (e.g., 7 days = 604800 seconds)
        self.collections["refresh_tokens"].create_index(
            [("created_at", ASCENDING)],
            expireAfterSeconds=604800
        )

    # ------------------ BLACKLIST FUNCTIONS ------------------

    def blacklist_token(self, token: str):
        self.collections["blacklisted_tokens"].insert_one({
            "token": token,
            "created_at": datetime.utcnow()
        })

    def is_token_blacklisted(self, token: str) -> bool:
        return self.collections["blacklisted_tokens"].find_one({"token": token}) is not None

    # ------------------ ACCESS TOKEN FUNCTIONS ------------------_
    def update_access_token(self, username: str, new_token: str):
        old_token_doc = self.collections["access_tokens"].find_one({"username": username})

        # Blacklist the old token if exists
        if old_token_doc:
            self.blacklist_token(old_token_doc["token"])
            self.collections["access_tokens"].delete_one({"username": username})

        # Store new token
        self.collections["access_tokens"].insert_one({
            "username": username,
            "token": new_token,
            "created_at": datetime.utcnow()
        })

    # ------------------ REFRESH TOKEN FUNCTIONS ------------------

    def store_refresh_token(self, username: str, refresh_token: str):
        self.collections["refresh_tokens"].delete_many({"username": username})
        self.collections["refresh_tokens"].insert_one({
            "username": username,
            "refresh_token": refresh_token,
            "created_at": datetime.utcnow()
        })

    def get_refresh_token(self, username: str) -> str:
        token_doc = self.collections["refresh_tokens"].find_one({"username": username})
        return token_doc["refresh_token"] if token_doc else None

    def delete_refresh_token(self, username: str):
        self.collections["refresh_tokens"].delete_one({"username": username})

    def is_valid_refresh_token(self, username: str, refresh_token: str) -> bool:
        stored_token = self.get_refresh_token(username)
        return stored_token == refresh_token

    def clear_all_refresh_tokens(self, username: str):
        self.collections["refresh_tokens"].delete_many({"username": username})

    # ------------------ MATERIAL FUNCTIONS ------------------

    def add_material(self, material_type: str, material_data: Dict) -> str:
        if material_type not in self.collections:
            raise ValueError(f"Invalid material type: {material_type}")
        material_data["created_at"] = datetime.now()
        result = self.collections[material_type].insert_one(material_data)
        return str(result.inserted_id)

    def get_all_materials(self, material_type: str, user_id: Optional[str] = None) -> List[Dict]:
        if material_type not in self.collections:
            raise ValueError(f"Invalid material type: {material_type}")
        query = {"user_id": user_id} if user_id else {}
        materials = list(self.collections[material_type].find(query))
        for material in materials:
            material["_id"] = str(material["_id"])
        return materials

    def get_quotation_batch(self, batch_id: str) -> List[Dict]:
        quotations = list(self.collections["quotations"].find({"batch_id": batch_id}))
        for quotation in quotations:
            quotation["_id"] = str(quotation["_id"])
        return quotations

    def user_inventories(self, user_id: str) -> List[Dict]:
        inventories = list(self.collections["inventories"].find({"user_id": user_id}))
        for inventory in inventories:
            inventory["_id"] = str(inventory["_id"])
        return inventories

    def get_user_inventory(self, user_id: str) -> Optional[Dict]:
        inventory = self.collections["inventories"].find_one({"user_id": user_id})
        if inventory:
            inventory["_id"] = str(inventory["_id"])
        return inventory

    def register_user(self, username: str, full_name: str, role: str) -> bool:
        if self.collections["users"].find_one({"email": username}):
            return False

        self.collections["users"].insert_one({
            "email": username,
            "full_name": full_name,
            "role": role,
            "created_at": datetime.utcnow(),
            "updated_at": datetime.utcnow()
        })
        return True

    def get_user(self, username: str) -> Optional[Dict]:
        return self.collections["users"].find_one({"email": username})


# Create a single instance of the database manager
db_manager = MongoDBManager()