from pm4py.objects.log.obj import EventLog
from pm4py.objects.petri_net.obj import PetriNet, Marking
from pm4py.algo.discovery.alpha import algorithm as alpha_miner_algorithm
from exporters.petri_net import createPetriNet

#alpha miner can be executed as classic or plus version; returns a petri net, marking and final_marking
#reference pm4py package: https://pm4py-source.readthedocs.io/en/stable/pm4py.algo.discovery.alpha.html last visited 11.06.26

def alpha_miner(eventlog: EventLog):
    #apply alpha algorithm
    net, im, fm = alpha_miner_algorithm.apply(eventlog)

    #call converter to save PetriNet to MM-AR
    result = createPetriNet(net, im, fm)

    #return result from create PetriNet
    return result
