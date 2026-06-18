from dotenv import load_dotenv
import requests
import os
import json

#server URL for backend server
BASE_URL = "http://mmar-server:8000"

#get metamodel
def getMetaModel(token):
    #resquest all sceneTypes (metamodels)
    response = requests.get(f"{BASE_URL}/metamodel/sceneTypes", headers={"Authorization": f"Bearer {token}"})
    metamodels = response.json()
    return metamodels

#----------------------------------Resolve Petri Net and its components----------------------------
def getPetriNetUUID(token):
    #resquest all sceneTypes (metamodels)
    metamodels = getMetaModel(token)

    #search for Petri Net
    scene_types = metamodels.get("sceneTypes", [])
    petri_net = next((item for item in scene_types if item.get("name") == "Petri Net"), None)

    #save petri_net uuid
    petri_net_uuid = petri_net.get("uuid")

    #get classes and relationclasses from Petri net
    classes = petri_net.get("classes", [])
    relations = petri_net.get("relationclasses", [])

    transition_uuid = next((item.get("uuid") for item in classes if item.get("name") == "Transition"), None)
    place_uuid = next((item.get("uuid") for item in classes if item.get("name") == "Place"), None)

    arc_uuid = next((item.get("uuid") for item in relations if item.get("name") == "Arc"), None)

    return{
        "metamodel": petri_net_uuid,
        "place": place_uuid,
        "transition": transition_uuid ,
        "arc": arc_uuid
    }

#----------------------------------Resolve BPMN and its components----------------------------
def getBPMNUUID():
    pass

