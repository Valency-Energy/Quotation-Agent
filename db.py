# db.py
import uuid
from datetime import datetime
from typing import List, Dict, Any, Optional
import logging
from pymongo import MongoClient
from bson.objectid import ObjectId

logger = logging.getLogger(__name__)

class DatabaseManager:
    def __init__(self, connection_string="mongodb+srv://rkapoorbe23:La1YcgqAGSHLK7XL@blumi.r2bw9.mongodb.net/?retryWrites=true&w=majority&appName=Blumi"):
        # Connect to MongoDB
        self.client = MongoClient(connection_string)
        self.db = self.client["solar_quotation_system"]
        
        # Initialize collections
        self.users_collection = self.db["users"]
        self.quotation_batches_collection = self.db["quotation_batches"]
        self.material_configs_collection = self.db["material_configs"]
        self.component_configs_collection = self.db["component_configs"]
        
        # Component collections
        self.components_collections = {
            "solar_panel": self.db["solar_panel"],
            "inverter": self.db["inverter"],
            "mounting_structure": self.db["mounting_structure"],
            "bos_component": self.db["bos_component"],
            "protection_equipment": self.db["protection_equipment"],
            "earthing_system": self.db["earthing_system"],
            "net_metering": self.db["net_metering"]
        }
        
        # Admin users
        self.admin_users_collection = self.db["admin_users"]
    
    def create_or_update_user(self, user_info: Dict[str, Any]) -> Dict[str, Any]:
        user_id = user_info.get('sub')
        if not user_id:
            raise ValueError("User ID (sub) is required")
        
        # Set timestamps
        now = datetime.utcnow()
        
        # Find user or create new one
        existing_user = self.users_collection.find_one({"id": user_id})
        
        if not existing_user:
            user_data = {
                "id": user_id,
                "email": user_info.get('email'),
                "name": user_info.get('name'),
                "created_at": now,
                "updated_at": now
            }
            result = self.users_collection.insert_one(user_data)
            user_data["_id"] = result.inserted_id
            return user_data
        else:
            # Update existing user
            self.users_collection.update_one(
                {"id": user_id},
                {"$set": {
                    "email": user_info.get('email'),
                    "name": user_info.get('name'),
                    "updated_at": now
                }}
            )
            
            # Get updated user data
            updated_user = self.users_collection.find_one({"id": user_id})
            return updated_user
    
    def is_admin(self, user_id: str) -> bool:
        admin = self.admin_users_collection.find_one({"user_id": user_id})
        return admin is not None
    
    def save_material_config(self, materials: List[Dict[str, Any]], user_id: Optional[str] = None) -> str:
        config_data = {
            "user_id": user_id,
            "materials": materials,
            "created_at": datetime.utcnow()
        }
        
        result = self.material_configs_collection.insert_one(config_data)
        return str(result.inserted_id)
    
    def save_component_config(self, components: List[Dict[str, Any]], user_id: Optional[str] = None) -> str:
        config_data = {
            "user_id": user_id,
            "components": components,
            "created_at": datetime.utcnow()
        }
        
        result = self.component_configs_collection.insert_one(config_data)
        return str(result.inserted_id)
    
    def save_quotations(self, quotations: List[Dict[str, Any]], user_id: Optional[str] = None) -> str:
        batch_data = {
            "user_id": user_id,
            "quotations": quotations,
            "created_at": datetime.utcnow()
        }
        
        result = self.quotation_batches_collection.insert_one(batch_data)
        return str(result.inserted_id)
    
    def get_quotation_batch(self, batch_id: str) -> Optional[Dict[str, Any]]:
        try:
            batch = self.quotation_batches_collection.find_one({"_id": ObjectId(batch_id)})
            if batch:
                # Convert ObjectId to string for JSON serialization
                batch["id"] = str(batch["_id"])
                del batch["_id"]
                return batch
            return None
        except:
            # Handle invalid ObjectId format
            return None
    
    def get_user_quotation_batches(self, user_id: str) -> List[Dict[str, Any]]:
        user_batches = []
        
        cursor = self.quotation_batches_collection.find({"user_id": user_id})
        
        for batch in cursor:
            # Calculate price range
            quotations = batch.get("quotations", [])
            price_range = self._calculate_price_range(quotations)
            
            # Format result
            user_batches.append({
                "id": str(batch["_id"]),
                "created_at": batch.get("created_at"),
                "quotation_count": len(quotations),
                "price_range": price_range
            })
        
        return user_batches
    
    def _calculate_price_range(self, quotations: List[Dict[str, Any]]) -> Dict[str, float]:
        if not quotations:
            return {"min": 0, "max": 0, "avg": 0}
        
        prices = [q.get("total_price", 0) for q in quotations]
        return {
            "min": min(prices),
            "max": max(prices),
            "avg": sum(prices) / len(prices)
        }
    
    def add_component(self, component_type: str, component_data: Dict[str, Any]) -> str:
        if component_type not in self.components_collections:
            raise ValueError(f"Invalid component type: {component_type}")
        
        component_data["created_at"] = datetime.utcnow()
        
        result = self.components_collections[component_type].insert_one(component_data)
        return str(result.inserted_id)
    
    def get_components(self, component_type: str) -> List[Dict[str, Any]]:
        if component_type not in self.components_collections:
            return []
        
        components = []
        cursor = self.components_collections[component_type].find({})
        
        for component in cursor:
            # Convert ObjectId to string for JSON serialization
            component["id"] = str(component["_id"])
            del component["_id"]
            components.append(component)
        
        return components
    
    def get_component(self, component_type: str, component_id: str) -> Optional[Dict[str, Any]]:
        if component_type not in self.components_collections:
            return None
        
        try:
            component = self.components_collections[component_type].find_one({"_id": ObjectId(component_id)})
            if component:
                # Convert ObjectId to string for JSON serialization
                component["id"] = str(component["_id"])
                del component["_id"]
                return component
            return None
        except:
            # Handle invalid ObjectId format
            return None

# Create a singleton instance
db_manager = DatabaseManager()