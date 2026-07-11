from pm4py.objects.log.obj import EventLog
from pm4py import discover_bpmn_inductive
from exporters.bpmn import createBPMN

#uses the inductive miner to discover a BPMN; parameter noise_threshold, default is 0.0 
#reference pm4py package: https://pm4py-source.readthedocs.io/en/stable/pm4py.html?highlight=discover%20bpmn%20inductive#pm4py.discovery.discover_bpmn_inductive last visited 11.07.2026

def bpmn_inductive_miner(event_log: EventLog):
    #apply inductive miner that directly produces a bpmn
    bpmn = discover_bpmn_inductive(event_log)

    #call exporter to save bpmn model to database
    result = createBPMN(bpmn)

    #return result from createBPMN
    return result