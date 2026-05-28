from fastapi import UploadFile, HTTPException

def execute_algorithm(algorithm: str, file: UploadFile):
    if algorithm == "alpha":
        return alpha_miner(file)
    elif algorithm == "inductive":
        return inductive_miner(file)
    else:
        raise HTTPException(status_code=400, detail=f"Unknown algorithm: {algorithm}")