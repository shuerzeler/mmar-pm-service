from pm4py.objects.log.obj import EventLog
from pm4py import discover_petri_net_inductive
from exporters.petri_net import createPetriNet

#uses the inductive miner to discover a petri net; parameter noise_threshold, default is 0.0 
#reference pm4py package: https://pm4py-source.readthedocs.io/en/stable/pm4py.html?highlight=discover_petri_net_inductive#pm4py.discovery.discover_petri_net_inductive last visited 11.07.2026

def inductive_miner(event_log: EventLog):
    #apply inductive algorithm
    net, im, fm = discover_petri_net_inductive(event_log)

    #call exporter to save net to database
    result = createPetriNet(net, im, fm)

    #return results
    return result