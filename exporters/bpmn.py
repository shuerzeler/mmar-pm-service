from pm4py.objects.bpmn.obj import BPMN

def createBPMN(bpmn):
    #get token for API calls
    token = login()

    #get uuids needed to create petri net, its classes and relation
    bpmn_uuids = getBPMNUUID(token)

    #calculate coordinates for bpmn
    

    #create random uuid for new scene instance
    instance_uuid = str(uuid.uuid4())

    #create payload

    #make call

    return 1