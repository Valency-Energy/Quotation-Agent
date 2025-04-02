import uvicorn
import logging
from fastapi import FastAPI, HTTPException, Body, Depends
from pydantic import BaseModel
from typing import Optional, List, Dict, Union
from starlette.config import Config
from starlette.requests import Request
from starlette.middleware.sessions import SessionMiddleware
from starlette.responses import RedirectResponse
from authlib.integrations.starlette_client import OAuth
from fastapi.middleware.cors import CORSMiddleware
from google.oauth2 import id_token
from google.auth.transport import requests

# Import the component models and quotation generator
from quotation import (
    generate_quotations, QuotationRequest, 
    SolarPanel, Inverter, MountingStructure, BOSComponent, 
    ProtectionEquipment, EarthingSystem, NetMetering,
    ComponentSelection, ComponentType
)
from db import db_manager

app = FastAPI(docs_url="/docs", redoc_url="/redoc")
app.add_middleware(SessionMiddleware, secret_key='!secret')
config = Config('.env')
oauth = OAuth(config)
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

CONF_URL = 'https://accounts.google.com/.well-known/openid-configuration'
oauth.register(
    name='google',
    server_metadata_url=CONF_URL,
    client_kwargs={
        'scope': 'openid email profile'
    },
    authorize_params={
        'access_type': 'offline',
        'prompt': 'consent'
    }
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/")
async def root():
    return {"message": "Solar System Quotation Generator API"}


# Updated routes for component-based quotation generation
@app.post("/generate-quotations/", tags=['quotation'])
async def quotation_endpoint(request: QuotationRequest = Body(...)):
    """
    Generate all possible quotations based on the combinations of provided components
    """
    return await generate_quotations(request)

@app.get("/quotations/{batch_id}", tags=['quotation'])
async def get_quotation_batch(batch_id: str):
    """
    Retrieve a specific batch of quotations by ID
    """
    batch = db_manager.get_quotation_batch(batch_id)
    if not batch:
        raise HTTPException(status_code=404, detail="Quotation batch not found")
    return batch

if __name__ == "__main__":
    uvicorn.run(app, host="127.0.0.1", port=8000)