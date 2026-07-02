from pm4py.objects.log.obj import EventLog
from pm4py.objects.bpmn.obj import BPMN
from pm4py import discover_bpmn_inductive

def inductive_miner(eventlog: EventLog):
    #apply inductive miner that directly produces a bpmn
    bpmn = discover_bpmn_inductive(eventlog)

    #call exporter to save net to database
    result = createBPMN(bpmn)

    return result