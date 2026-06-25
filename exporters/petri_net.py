from helpers.uuid_resolver import getPetriNetUUID
import uuid
from helpers.signin import login
from datetime import datetime
import requests
import json
from pm4py.objects.petri_net.obj import PetriNet, Marking


BASE_URL = "http://mmar-server:8000"

def createPetriNet(net, im, fm):
    #get token for API calls
    token = login()

    #get uuids needed to create petri net, its classes and relation
    petri_net_uuids = getPetriNetUUID(token)
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
            "coordinates_2d": {"x": i * 2, "y": 0, "z": 0}
        })

    #analogus to places for transitions
    for i, transition in enumerate(net.transitions):
        transition_uuid = str(uuid.uuid4())
        transition_uuid_map[transition] = transition_uuid
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
            "coordinates_2d": {"x": i * 2, "y": 3, "z": 0}
        })


    #create payload
    payload = {
        "uuid": instance_uuid,
        "uuid_scene_type": petri_net_uuids["metamodel"],
        "name": f"PM_PetriNet_{datetime.now().strftime('%Y%m%d_%H%M%S')}",
        "class_instances": class_instances,
        "relationclasses_instances": []
    }

    print(class_instances)

    #make call to save petri net
    response = requests.post(f"{BASE_URL}/instances/sceneInstances/{instance_uuid}", headers={"Authorization": f"Bearer {token}"}, json=payload)
    print("Status code:", response.status_code)
    print("Response text:", response.text)

    return response.json()




#saves Petri Net to MM-AR; takes as input a net object, marking and final marking
#??? do i really need final marking? because transitioning could/should be already impemlelmtned for the metamodel

#use uuid resolver to get uuid of Petri net, transition, places and marking

#create net and inital marking

#return OK or throw error