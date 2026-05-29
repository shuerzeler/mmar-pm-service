from fastapi import HTTPException
from pm4py.objects.log.obj import EventLog
from pm4py.objects.petri_net.obj import PetriNet, Marking
from pm4py.algo.discovery.alpha import algorithm as alpha_miner_algorithm


def alpha_miner(eventlog: EventLog):
    net: PetriNet
    im: Marking
    fm: Marking
    net, im, fm = alpha_miner_algorithm.apply(eventlog)

    #just return sth to test
    return {
        "algorithm": "alpha_miner",
        "places": len(net.places),
        "transitions": len(net.transitions),
        "arcs": len(net.arcs)
    }
