from fastapi import HTTPException
from pm4py.objects.log.obj import EventLog
from algorithms.alpha_miner import alpha_miner
from algorithms.inductive_miner import inductive_miner

def execute_algorithm(algorithm: str, event_log: EventLog):
    if algorithm == "alpha":
        return alpha_miner(event_log)
    elif algorithm == "inductive":
        return inductive_miner(event_log)
    else:
        raise HTTPException(status_code=400, detail=f"Algorithm not  valid: {algorithm}")