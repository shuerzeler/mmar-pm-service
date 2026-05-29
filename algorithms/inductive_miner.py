from fastapi import UploadFile, HTTPException
from pm4py.objects.log.obj import EventLog
from pm4py.objects.petri_net.obj import PetriNet, Marking
from pm4py.algo.discovery.inductive import algorithm as inductive_miner_algorithm
from pm4py.objects.conversion.process_tree import converter as pt_converter


def inductive_miner(eventlog: EventLog):
    process_tree = inductive_miner_algorithm.apply(eventlog)
    net, im, fm = pt_converter.apply(process_tree)

    #just return sth to test
    return {
        "algorithm": "inductive_miner",
        "places": len(net.places),
        "transitions": len(net.transitions),
        "arcs": len(net.arcs)
    }