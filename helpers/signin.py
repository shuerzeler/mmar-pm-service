from dotenv import load_dotenv
import requests
import os

#Helper function to get token from mmar_server

#server URL for backend server
BASE_URL = "http://mmar-server:8000"
#for local development; in Docker, env vars should be injected via docker-compose
load_dotenv() 
#get login, or use default admin
USERNAME = os.getenv("MMAR_USERNAME", "admin")
PASSWORD = os.getenv("MMAR_PASSWORD", "admin")

#login call to mmar_server
def login():
    response = requests.post(f"{BASE_URL}/login/signin", json={
        "username": USERNAME,
        "password": PASSWORD
    })
    #raise expection if 400er or 500er response
    response.raise_for_status() 
    return response.json()