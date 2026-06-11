from fastapi import HTTPException
from pm4py.objects.log.obj import EventLog
from pm4py.objects.petri_net.obj import PetriNet, Marking
from pm4py.algo.discovery.alpha import algorithm as alpha_miner_algorithm

#alpha miner can be executed as classic or plus version; return a net, marking and final_marking
#reference pm4py package: https://pm4py-source.readthedocs.io/en/stable/pm4py.algo.discovery.alpha.html last visited 11.06.26

def alpha_miner(eventlog: EventLog):
    #initalize variables for return
    net: PetriNet 
    im: Marking
    fm: Marking

    #apply alpha algorithm
    net, im, fm = alpha_miner_algorithm.apply(eventlog)

    #call converter to save PetriNet to MM-AR

    #just return sth to test
    return {
        "algorithm": "alpha_miner",
        "places": len(net.places),
        "transitions": len(net.transitions),
        "arcs": len(net.arcs)
    }
