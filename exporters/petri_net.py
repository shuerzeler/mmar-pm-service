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
    place_layout, transition_layout = compute_layout(net, im, fm)

    #create random uuid for new scene instance
    instance_uuid = str(uuid.uuid4())

    #create dict for places uuid mapping (needed to create arcs)
    place_uuid_map = {}
    
    #create dict for transition uuid mapping (needed to create arcs)
    transition_uuid_map = {}

    #create object to save class instances for payload
    class_instances = []

    start_place = list(im.keys())[0]
    end_place = list(fm.keys())[0]

    #for each place in net.places first create uuid, then create and add place to class instance object 
    for i, place in enumerate(net.places):
        place_uuid = str(uuid.uuid4())
        place_uuid_map[place] = place_uuid
        coords = place_layout.get(place.name, {"x": 0, "y": 0, "z": 0})

        #enumerate transitions but keep start and end
        if place == start_place:
            label = "start"
        elif place == end_place:
            label = "end"
        else:
            label = f"p{i+1}"

        #set token for start places
        tokens = "1" if place == start_place else "0"

        class_instances.append({
            "uuid": place_uuid,
            "uuid_class": petri_net_uuids["place"],
            "name": "Place",
            "attribute_instance": [
            {
                "uuid": str(uuid.uuid4()),
                "uuid_attribute": petri_net_uuids["place_name_attr"],
                "name": "Name",
                "value": label
            },
            {
                "uuid": str(uuid.uuid4()),
                "uuid_attribute": petri_net_uuids["place_tokens_attr"],
                "name": "Tokens",
                "value": tokens
            }
            ],
            "coordinates_2d": coords
        })

    #analogus to places for transitions
    for transition in net.transitions:
        transition_uuid = str(uuid.uuid4())
        transition_uuid_map[transition] = transition_uuid
        coords = transition_layout.get(transition.name, {"x": 0, "y": 0, "z": 0})
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
            ],
            "attribute_instance": [
                {
                    "uuid": str(uuid.uuid4()),
                    "uuid_attribute": petri_net_uuids["arc_weight_attr"],
                    "name": "Weight",
                    "value": "1"
                }
            ],
        })

    #create sceneinstance
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

def compute_layout(net, im, fm, x_scale=0.003, y_scale=0.015):
    G = nx.DiGraph()
    
    for place in net.places:
        G.add_node(f"place_{place.name}")
    for transition in net.transitions:
        G.add_node(f"transition_{transition.name}")
    for arc in net.arcs:
        G.add_edge(f"place_{arc.source.name}" if isinstance(arc.source, PetriNet.Place) else f"transition_{arc.source.name}",
                   f"place_{arc.target.name}" if isinstance(arc.target, PetriNet.Place) else f"transition_{arc.target.name}")
    
    start_place = list(im.keys())[0]
    end_place = list(fm.keys())[0]
    
    A = nx.nx_agraph.to_agraph(G)
    A.graph_attr["rankdir"] = "LR"
    A.graph_attr["ranksep"] = "1.5"
    A.graph_attr["nodesep"] = "0.8"
    
    A.add_subgraph([f"place_{start_place.name}"], rank="min")
    A.add_subgraph([f"place_{end_place.name}"], rank="max")
    
    A.layout(prog="dot")

    pos = {}
    for node in A.nodes():
        x, y = node.attr["pos"].split(",")
        pos[str(node)] = (float(x), float(y))

    mid_x = (min(x for x, y in pos.values()) + max(x for x, y in pos.values())) / 2
    mid_y = (min(y for x, y in pos.values()) + max(y for x, y in pos.values())) / 2
    
    place_pos = {
        name[len("place_"):]: {"x": float(x - mid_x) * x_scale, "y": float(y - mid_y) * y_scale, "z": 0}
        for name, (x, y) in pos.items() if name.startswith("place_")
    }
    transition_pos = {
        name[len("transition_"):]: {"x": float(x - mid_x) * x_scale, "y": float(y - mid_y) * y_scale, "z": 0}
        for name, (x, y) in pos.items() if name.startswith("transition_")
    }

    return place_pos, transition_pos
