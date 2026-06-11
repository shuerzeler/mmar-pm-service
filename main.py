from fastapi import FastAPI, File, UploadFile
from helpers.validators import validate_event_log
from helpers.parser import parse_event_log
from algorithms.router import execute_algorithm
from helpers.uuid_resolver import getPetriNetUUID

app = FastAPI()

#health check
@app.get("/health")
async def health():
    return {"status": "ok"}

#-------------------------------Run Mining Algorithm-------------------------------
@app.post("/run")
async def run(algorithm: str, file: UploadFile = File(...)):
    validate_event_log(file)
    event_log = parse_event_log(file)
    result = execute_algorithm(algorithm, event_log)
    return result

#-------------------------------Testing routes------------------------------------
@app.get("/test-uuids")
async def test_uuids():
    return getPetriNetUUID()