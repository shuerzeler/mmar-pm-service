import requests
import os
import json

#server URL for backend serverand login
BASE_URL = "http://mmar-server:8000"
USERNAME = os.getenv("MMAR_USERNAME")
PASSWORD = os.getenv("MMAR_PASSWORD")

#login
def login():
    response = requests.post(f"{BASE_URL}/login/signin", json={
        "username": USERNAME,
        "password": PASSWORD
    })
    print("Login response:", response.json())  # add this
    return response.json()

#get metamodel
def getMetaModel():
    #login
    token = login()
    #resquest all sceneTypes (metamodels)
    response = requests.get(f"{BASE_URL}/metamodel/sceneTypes", headers={"Authorization": f"Bearer {token}"})
    metamodels = response.json()
    return metamodels

#----------------------------------Resolve Petri Net and its components----------------------------
def getPetriNetUUID():
    #resquest all sceneTypes (metamodels)
    metamodels = getMetaModel()

    print(metamodels)
    
    #search for Petri Net
    petriNet = next(m for m in metamodels if m["name"] == "Petri Net")
    petriNetUUID = petriNet["uuid"]

    #get classes UUIDs
    placeUUID = next(c["uuid"] for c in petriNet["classes"] if c["name"] == "Place")
    transitionUUID = next(c["uuid"] for c in petriNet["classes"] if c["name"] == "Transition")
    arcUUID = next(rc["uuid"] for rc in petriNet["relationclasses"] if rc["name"] == "Arc")

    return{
        "metamodel": petriNetUUID,
        "place": placeUUID,
        "transition": transitionUUID,
        "arc": arcUUID
    }

#----------------------------------Resolve BPMN and its components----------------------------
def getBPMNUUID():
    pass

