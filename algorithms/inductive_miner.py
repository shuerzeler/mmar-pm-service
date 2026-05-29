from fastapi import UploadFile, HTTPException


def inductive_miner():
    #just return sth to test
    return {
        "algorithm": "alpha_miner",
        "places": len(net.places),
        "transitions": len(net.transitions),
        "arcs": len(net.arcs)
    }