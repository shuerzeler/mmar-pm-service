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
    random_uuid = str(uuid.uuid4())

    #create payload
    payload = {
        "uuid": random_uuid,
        "uuid_scene_type": petri_net_uuids["metamodel"],
        "name": f"PM_PetriNet_{datetime.now().strftime('%Y%m%d_%H%M%S')}",
        "class_instances": [],
        "relationclasses_instances": []
    }

    #make call to save petri net
    response = requests.post(f"{BASE_URL}/instances/sceneInstances/{random_uuid}", headers={"Authorization": f"Bearer {token}"}, json=payload)
    print(net)
    print(im)
    print(fm)

    return response.json()




#saves Petri Net to MM-AR; takes as input a net object, marking and final marking
#??? do i really need final marking? because transitioning could/should be already impemlelmtned for the metamodel

#use uuid resolver to get uuid of Petri net, transition, places and marking

#create net and inital marking

#return OK or throw error