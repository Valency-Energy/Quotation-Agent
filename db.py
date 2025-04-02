from pymongo import MongoClient
from typing import Dict, List
from datetime import datetime
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
    
    def create_or_update_user(self, user_info: Dict):
        try:
            user_filter = {'google_sub': user_info['sub']}
            
            user_document = {
                'google_sub': user_info['sub'],
                'email': user_info['email'],
                'name': user_info['name'],
                'last_login': datetime.utcnow(),
                'created_at': datetime.utcnow()
            }
            
            result = self.users_collection.replace_one(
                user_filter, 
                user_document, 
                upsert=True
            )

            user = self.users_collection.find_one(user_filter)
            
            if user:
                logger.info(f"User processed: {user['email']}")
                return user
            else:
                logger.error("Failed to create/find user document")
                return None
        
        except Exception as e:
            logger.error(f"User creation error: {e}", exc_info=True)
            raise
    
    def save_quotations(self, quotations: List[Dict], user_id: str = None):
        """
        Save generated quotations to the database
        """
        try:
            quotation_batch = {
                'quotations': quotations,
                'created_at': datetime.utcnow(),
                'user_id': user_id
            }
            
            result = self.quotations_collection.insert_one(quotation_batch)
            logger.info(f"Saved quotation batch with ID: {result.inserted_id}")
            return str(result.inserted_id)
        except Exception as e:
            logger.error(f"Error saving quotations: {e}", exc_info=True)
            raise
    
    def get_quotation_batch(self, batch_id: str):
        """
        Retrieve a specific quotation batch
        """
        try:
            quotation_batch = self.quotations_collection.find_one({"_id": ObjectId(batch_id)})
            return quotation_batch
        except Exception as e:
            logger.error(f"Error retrieving quotation batch: {e}", exc_info=True)
            raise
    
    def get_user_quotation_batches(self, user_id: str):
        """
        Retrieve all quotation batches for a specific user
        """
        try:
            batches = list(self.quotations_collection.find({"user_id": user_id}))
            return batches
        except Exception as e:
            logger.error(f"Error retrieving user quotation batches: {e}", exc_info=True)
            raise
    
    def save_material_config(self, material_config: Dict, user_id: str = None):
        """
        Save material configuration for later use
        """
        try:
            config = {
                'materials': material_config,
                'created_at': datetime.utcnow(),
                'user_id': user_id
            }
            
            result = self.materials_collection.insert_one(config)
            logger.info(f"Saved material configuration with ID: {result.inserted_id}")
            return str(result.inserted_id)
        except Exception as e:
            logger.error(f"Error saving material configuration: {e}", exc_info=True)
            raise

import os
from dotenv import load_dotenv
load_dotenv()
uri = os.environ.get('MONGO_URI')
db_manager = DatabaseManager(uri)