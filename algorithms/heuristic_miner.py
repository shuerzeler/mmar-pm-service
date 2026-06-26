from pm4py.objects.log.obj import EventLog
from pm4py.objects.petri_net.obj import PetriNet, Marking
from pm4py import discover_petri_net_heuristics
from exporters.petri_net import createPetriNet

def heuristic_miner(eventlog: EventLog):
    #apply inductive algorithm
    net, im, fm = discover_petri_net_heuristics(eventlog)

    #call exporter to save net to database
    result = createPetriNet(net, im, fm)

    #just return sth to test
    return result