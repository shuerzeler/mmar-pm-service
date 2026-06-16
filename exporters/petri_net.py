from helpers.uuid_resolver import getPetriNetUUID
import uuid


def createPetriNet():
    #get uuids needed to create petri net, its classes and relation
    petri_net_uuids = getPetriNetUUID()
    random_uuid = str(uuid.uuid4())

    #create random uuid for new scene instance


#saves Petri Net to MM-AR; takes as input a net object, marking and final marking
#??? do i really need final marking? because transitioning could/should be already impemlelmtned for the metamodel

#use uuid resolver to get uuid of Petri net, transition, places and marking

#create net and inital marking

#return OK or throw error