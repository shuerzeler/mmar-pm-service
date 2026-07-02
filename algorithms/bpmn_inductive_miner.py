from pm4py.objects.log.obj import EventLog
from pm4py.objects.bpmn.obj import BPMN
from pm4py import discover_bpmn_inductive
from exporters.bpmn import createBPMN

def bpmn_inductive_miner(eventlog: EventLog):
    #apply inductive miner that directly produces a bpmn
    bpmn = discover_bpmn_inductive(eventlog)

    #call exporter to save net to database
    result = createBPMN(bpmn)

    for node in bpmn.get_nodes():
        print(f"Type: {type(node).__name__}, name: {node.get_name()}, id: {node.get_id()}, x: {node.get_x()}, y: {node.get_y()}")

    for flow in bpmn.get_flows():
        print(f"Flow from: {flow.get_source().get_name()} to: {flow.get_target().get_name()}")

    return {"status": "ok", "message": "BPMN discovered successfully"}