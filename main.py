import uvicorn
import logging
from fastapi import FastAPI, HTTPException, Body
from quotation import generate_quotations, QuotationRequest
from fastapi import FastAPI, HTTPException
from starlette.config import Config
from starlette.requests import Request
from starlette.middleware.sessions import SessionMiddleware
from starlette.responses import RedirectResponse
from authlib.integrations.starlette_client import OAuth
from fastapi.middleware.cors import CORSMiddleware
from db import db_manager
from google.oauth2 import id_token
from google.auth.transport import requests

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
    return {"message": "VEquotation API"}

# oauth enpoints
@app.get('/login', tags=['authentication'])  
async def login(request: Request):
    redirect_uri = request.url_for('auth')
    return await oauth.google.authorize_redirect(request, redirect_uri)



@app.get('/auth', tags=['authentication'])
async def auth(request: Request):
    try:
        code = request.query_params.get('code')
        if not code:
            raise HTTPException(status_code=400, detail="No authorization code")
        token = await oauth.google.authorize_access_token(request)
        
        id_token_string = token.get('id_token')
        if not id_token_string:
            raise HTTPException(status_code=401, detail="No ID token found")

        idinfo = id_token.verify_oauth2_token(
            id_token_string, 
            requests.Request(), 
            oauth.google.client_id
        )

        user_info = {
            'email': idinfo.get('email'),
            'name': idinfo.get('name'),
            'sub': idinfo.get('sub')
        }
        
        try:
            db_user = db_manager.create_or_update_user(user_info)
            request.session['user'] = user_info
            logger.info(f"User processed successfully: {user_info['email']}")
        except Exception as db_error:
            logger.error(f"Database user creation failed: {db_error}")
        return RedirectResponse(url='/')
    
    except Exception as e:
        print(f"Authentication Error: {e}")
        raise HTTPException(status_code=401, detail=f"Authentication failed: {str(e)}")



@app.get('/logout', tags=['authentication'])  
async def logout(request: Request):
    request.session.pop('user', None)
    return RedirectResponse(url='/')

# Register routes
@app.post("/generate-quotations/")
async def quotation_endpoint(request: QuotationRequest = Body(...)):
    return await generate_quotations(request)

@app.get("/quotations/{batch_id}")
async def get_quotation_batch(batch_id: str):
    """
    Retrieve a specific batch of quotations by ID
    """
    batch = db_manager.get_quotation_batch(batch_id)
    if not batch:
        raise HTTPException(status_code=404, detail="Quotation batch not found")
    return batch

@app.get("/user/{user_id}/quotations")
async def get_user_quotations(user_id: str):
    """
    Retrieve all quotation batches for a specific user
    """
    batches = db_manager.get_user_quotation_batches(user_id)
    return {"batches": batches}

@app.get("/")
async def root():
    return {"message": "Quotation Generator API"}


if __name__ == "__main__":
    uvicorn.run(app, host="127.0.0.1", port=8000)
