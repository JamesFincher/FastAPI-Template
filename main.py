import random
import string
from fastapi import FastAPI, HTTPException, Header, Response
from pymongo import MongoClient
from fastapi.encoders import jsonable_encoder
import os

from dotenv import load_dotenv


 
app = FastAPI()
load_dotenv()

if os.getenv('DEVELOPER_MODE') == 'True':
    DEVELOPER_MODE = True
else:
    DEVELOPER_MODE = False
    
database_url = os.getenv('DATABASE_URL')
client = MongoClient(database_url)
db = client.test

collection = db['api_keys']

def generate_api_key(length=20):
    letters_and_digits = string.ascii_letters + string.digits
    return ''.join(random.choice(letters_and_digits) for i in range(length))

def get_api_key_data(api_key):
    api_key_data = collection.find_one({'key': api_key})
    if api_key_data is None:
        return None
    return api_key_data

@app.post("/api-keys")
async def create_api_key(owner: str):
    api_key = generate_api_key()
    api_key_data = {'key': api_key, 'secret_key': generate_api_key(), 'owner': owner, 'usage_limit': 100}
    try:
        collection.insert_one(api_key_data)
    except Exception as e:
        raise HTTPException(status_code=500, detail='Failed to create API key')
    return {'api_key': api_key, 'secret_key': api_key_data['secret_key']}

async def api_key_middleware(request, call_next):
    path = request.url.path

    # Allow requests to the docs path without an API key
    if path.startswith('/docs'):
        response = await call_next(request)
        return response
    
    # Allow requests to the test endpoint without an API key
    if path.startswith('/test'):
        response = await call_next(request)
        return response

    # Check for the x-api-key header and validate the API key
    x_api_key = request.headers.get('x-api-key')
    if DEVELOPER_MODE:
        return await call_next(request)
    api_key_data = get_api_key_data(x_api_key)
    if api_key_data is None:
        raise HTTPException(status_code=401, detail='Invalid API key')

    # Check the API key usage limit
    if api_key_data['usage_limit'] <= 0:
        raise HTTPException(status_code=429, detail='API key usage limit exceeded')

    # Decrement the API key usage limit
    collection.update_one({'key': x_api_key}, {'$inc': {'usage_limit': -1}})
    response = await call_next(request)
    return response

@app.middleware("http")
async def validate_api_key(request, call_next):
    path = request.url.path
    # Allow requests to the docs path without an API key
    if path.startswith('/docs'):
        response = await call_next(request)
        return response
    
    # Allow requests to the test endpoint without an API key
    if path.startswith('/test'):
        response = await call_next(request)
        return response
    if DEVELOPER_MODE:
        response = await call_next(request)
        return response
    x_api_key = request.headers.get('x-api-key')
    api_key_data = get_api_key_data(x_api_key)
    if api_key_data is None:
        raise HTTPException(status_code=401, detail='Invalid API key')
    # Check usage limit
    if api_key_data['usage_limit'] <= 0:
        raise HTTPException(status_code=429, detail='API key usage limit exceeded')
    # Decrement usage limit
    collection.update_one({'key': x_api_key}, {'$inc': {'usage_limit': -1}})
    response = await call_next(request)
    return response

@app.get("/api-lookup/{api_key}")
async def api_lookup(api_key: str):
    api_key_data = get_api_key_data(api_key)
    if api_key_data is None:
        raise HTTPException(status_code=404, detail='API key not found')
    api_object = { 'api_key': api_key_data['key'], 'owner': api_key_data['owner'], 'usage_limit': api_key_data['usage_limit'] }
    return api_object


@app.get("/test")
async def test(x_api_key: str = Header(None)):
    api_key_data = get_api_key_data(x_api_key)

    if x_api_key is None and DEVELOPER_MODE:
        return {'message': 'API UP', 'DEV_MODE': 'ON', 'header api key': 'NOT SUPPLIED', 'api key data': 'None'},
    elif x_api_key is None and not DEVELOPER_MODE:
        return {'message': 'API UP', 'DEV_MODE': 'OFF', 'header api key': 'NOT SUPPLIED', 'api key data': 'None'},
    elif DEVELOPER_MODE:
        return {'message': 'API UP', 'DEV_MODE': 'ON', 'header api key': x_api_key, 'api key data': { 'api_key': api_key_data['key'], 'owner': api_key_data['owner'], 'usage_limit': api_key_data['usage_limit'] }}
    else:
        return {'message': 'API UP', 'DEV_MODE': 'OFF', 'header api key': x_api_key, 'api key data': { 'api_key': api_key_data['key'], 'owner': api_key_data['owner'], 'usage_limit': api_key_data['usage_limit'] }}
    
