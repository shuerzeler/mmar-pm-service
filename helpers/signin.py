from dotenv import load_dotenv
import requests
import os

#server URL for backend serverand login
BASE_URL = "http://mmar-server:8000"
load_dotenv()
USERNAME = os.getenv("MMAR_USERNAME")
PASSWORD = os.getenv("MMAR_PASSWORD")

#login
def login():
    response = requests.post(f"{BASE_URL}/login/signin", json={
        "username": USERNAME,
        "password": PASSWORD
    })
    return response.json()