from pm4py.objects.log.obj import EventLog
from pm4py import discover_petri_net_heuristics
from exporters.petri_net import createPetriNet

#heuristic miner creating a petri net; dependency_threshold, and_threshold, loop_two_threshold parameters with defaults 0.5, 0.65 and 0.5 respectively
#reference pm4py package: https://pm4py-source.readthedocs.io/en/stable/pm4py.html?highlight=discover_petri_net_heuristics#pm4py.discovery.discover_petri_net_heuristics last visited 11.07.2026

def heuristic_miner(event_log: EventLog):
    #apply heuristic algorithm
    net, im, fm = discover_petri_net_heuristics(event_log)

    #call exporter to save net to database
    result = createPetriNet(net, im, fm)

    #return results
    return result