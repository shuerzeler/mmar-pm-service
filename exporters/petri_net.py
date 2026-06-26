from helpers.uuid_resolver import getPetriNetUUID
import uuid
from helpers.signin import login
from datetime import datetime
import requests
import json
from pm4py.objects.petri_net.obj import PetriNet, Marking
import networkx as nx


BASE_URL = "http://mmar-server:8000"

def createPetriNet(net, im, fm):
    #get token for API calls
    token = login()

    #get uuids needed to create petri net, its classes and relation
    petri_net_uuids = getPetriNetUUID(token)

    #calculate coordinates for net
    layout = compute_layout(net)

    #create random uuid for new scene instance
    instance_uuid = str(uuid.uuid4())

    #create dict for places uuid mapping (needed to create arcs)
    place_uuid_map = {}
    
    #create dict for transition uuid mapping (needed to create arcs)
    transition_uuid_map = {}

    #create object to save class instances for payload
    class_instances = []

    #for each place in net.places first create uuid, then create and add place to class instance object 
    for i, place in enumerate(net.places):
        place_uuid = str(uuid.uuid4())
        place_uuid_map[place] = place_uuid
        coords = layout.get(place.name, {"x": 0, "y": 0, "z": 0})
        class_instances.append({
            "uuid": place_uuid,
            "uuid_class": petri_net_uuids["place"],
            "name": "Place",
            "attribute_instance": [
            {
                "uuid": str(uuid.uuid4()),
                "uuid_attribute": petri_net_uuids["place_name_attr"],
                "name": "Name",
                "value": place.name
            }
            ],
            "coordinates_2d": coords
        })

    #analogus to places for transitions
    for i, transition in enumerate(net.transitions):
        transition_uuid = str(uuid.uuid4())
        transition_uuid_map[transition] = transition_uuid
        coords = layout.get(transition.name, {"x": 0, "y": 0, "z": 0})
        class_instances.append({
            "uuid": transition_uuid,
            "uuid_class": petri_net_uuids["transition"],
            "name": "Transition",
            "attribute_instance": [
            {
                "uuid": str(uuid.uuid4()),
                "name": "Name",
                "uuid_attribute": petri_net_uuids["transition_name_attr"],
                "value": transition.name
            }
            ],
            "coordinates_2d": coords
        })

    relationclasses_instances = []
    for arc in net.arcs:
        source = arc.source
        target = arc.target

        source_uuid = place_uuid_map.get(source) or transition_uuid_map.get(source)
        target_uuid = place_uuid_map.get(target) or transition_uuid_map.get(target)

        source_data = next(ci for ci in class_instances if ci["uuid"] == source_uuid)
        target_data = next(ci for ci in class_instances if ci["uuid"] == target_uuid)

        arc_instance_uuid = str(uuid.uuid4())
        role_from_instance_uuid = str(uuid.uuid4())
        role_to_instance_uuid = str(uuid.uuid4())

        relationclasses_instances.append({
            "uuid": arc_instance_uuid,
            "uuid_relationclass": petri_net_uuids["arc"],
            "uuid_class": petri_net_uuids["arc"],
            "name": "Arc",
            "role_instance_from": {
                "uuid": role_from_instance_uuid,
                "uuid_role": petri_net_uuids["arc_role_from"],
                "uuid_has_reference_class_instance": source_uuid
            },
            "role_instance_to": {
                "uuid": role_to_instance_uuid,
                "uuid_role": petri_net_uuids["arc_role_to"],
                "uuid_has_reference_class_instance": target_uuid
            },
            "uuid_role_instance_from": role_from_instance_uuid,
            "uuid_role_instance_to": role_to_instance_uuid,
            "line_points": [
                {"UUID": source_uuid, "Point": source_data["coordinates_2d"]},
                {"UUID": target_uuid, "Point": target_data["coordinates_2d"]}
            ]
        })
            


    #create payload
    payload = {
        "uuid": instance_uuid,
        "uuid_scene_type": petri_net_uuids["metamodel"],
        "name": f"PM_PetriNet_{datetime.now().strftime('%Y%m%d_%H%M%S')}",
        "class_instances": class_instances,
        "relationclasses_instances": relationclasses_instances
    }

    #make call to save petri net
    response = requests.post(f"{BASE_URL}/instances/sceneInstances/{instance_uuid}", headers={"Authorization": f"Bearer {token}"}, json=payload)

    return response.json()

def compute_layout(net, scale=25.0):
    G = nx.DiGraph()
    
    for place in net.places:
        G.add_node(place.name)
    for transition in net.transitions:
        G.add_node(transition.name)
    for arc in net.arcs:
        G.add_edge(arc.source.name, arc.target.name)
    
    # spring_layout returns values roughly between -1 and 1
    pos = nx.spring_layout(G, seed=42)
    
    return {name: {"x": float(x) * scale, "y": float(y) * scale, "z": 0}
            for name, (x, y) in pos.items()}


#saves Petri Net to MM-AR; takes as input a net object, marking and final marking
#??? do i really need final marking? because transitioning could/should be already impemlelmtned for the metamodel

#use uuid resolver to get uuid of Petri net, transition, places and marking

#create net and inital marking

#return OK or throw error