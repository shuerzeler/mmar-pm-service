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

    #get uuids for arcs
    arc_class = next((item for item in relations if item.get("name") == "Arc"), None)
    arc_uuid = arc_class.get("uuid") if arc_class else None
    arc_role_from_uuid = arc_class.get("role_from", {}).get("uuid") if arc_class else None
    arc_role_to_uuid = arc_class.get("role_to", {}).get("uuid") if arc_class else None
    arc_weight_attr_uuid = next((a.get("uuid") for a in arc_class.get("attributes", []) if a.get("name") == "Weight"), None) if arc_class else None

    #getname attribute for places and transitions
    place_class = next((item for item in classes if item.get("name") == "Place"), None)
    place_name_attr_uuid = next((a.get("uuid") for a in place_class.get("attributes", []) if a.get("name") == "Name"), None)

    transition_class = next((item for item in classes if item.get("name") == "Transition"), None)
    transition_name_attr_uuid = next((a.get("uuid") for a in transition_class.get("attributes", []) if a.get("name") == "Name"), None)

    #get uuid for tokens
    place_tokens_attr_uuid = next((a.get("uuid") for a in place_class.get("attributes", []) if a.get("name") == "Tokens"), None)

    return{
        "metamodel": petri_net_uuid,
        "place": place_uuid,
        "transition": transition_uuid ,
        "arc": arc_uuid,
        "arc_role_from": arc_role_from_uuid,
        "arc_role_to": arc_role_to_uuid,
        "arc_weight_attr": arc_weight_attr_uuid,
        "place_name_attr": place_name_attr_uuid,
        "transition_name_attr": transition_name_attr_uuid,
        "place_tokens_attr": place_tokens_attr_uuid  
    }

#----------------------------------Resolve BPMN and its components----------------------------
def getBPMNUUID(token):
    #resquest all sceneTypes (metamodels)
    metamodels = getMetaModel(token)

    #search for bpmn
    scene_types = metamodels.get("sceneTypes", [])
    bpmn = next((item for item in scene_types if item.get("name") == "Business Process Model and Notation"), None)

    #save bpmn uuid
    bpmn_uuid = bpmn.get("uuid")

    #get classes and realtions
    classes = bpmn.get("classes", [])
    relations = bpmn.get("relationclasses", [])
    
    task_uuid = next((item.get("uuid") for item in classes if item.get("name") == "Task"), None)
    start_event_uuid = next((item.get("uuid") for item in classes if item.get("name") == "Start Event"), None)
    end_event_uuid = next((item.get("uuid") for item in classes if item.get("name") == "End Event"), None)
    exclusive_gateway_uuid = next((item.get("uuid") for item in classes if item.get("name") == "Exclusive Gateway"), None)
    parallel_gateway_uuid = next((item.get("uuid") for item in classes if item.get("name") == "Parallel Gateway"), None)
    
    sequence_flow_class = next((item for item in relations if item.get("name") == "Sequence Flow"), None)
    sequence_flow_uuid = sequence_flow_class.get("uuid") if sequence_flow_class else None
    sequence_flow_role_from_uuid = sequence_flow_class.get("role_from", {}).get("uuid") if sequence_flow_class else None
    sequence_flow_role_to_uuid = sequence_flow_class.get("role_to", {}).get("uuid") if sequence_flow_class else None
    
    # get name attribute for task
    task_class = next((item for item in classes if item.get("name") == "Task"), None)
    task_name_attr_uuid = next((a.get("uuid") for a in task_class.get("attributes", []) if a.get("name") == "Name"), None)

    return{
        "metamodel": bpmn_uuid,
        "task": task_uuid,
        "start_event": start_event_uuid,
        "end_event": end_event_uuid,
        "exclusive_gateway": exclusive_gateway_uuid,
        "parallel_gateway": parallel_gateway_uuid,
        "sequence_flow": sequence_flow_uuid,
        "sequence_flow_role_from": sequence_flow_role_from_uuid,
        "sequence_flow_role_to": sequence_flow_role_to_uuid,
        "task_name_attr": task_name_attr_uuid
    }

