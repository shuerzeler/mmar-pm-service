from fastapi import FastAPI, File, UploadFile
from helpers.validators import validate_event_log
from helpers.parser import parse_event_log
from algorithms.router import execute_algorithm
from helpers.uuid_resolver import getPetriNetUUID
from helpers.uuid_resolver import getBPMNUUID
from helpers.signin import login
from exporters.petri_net import createPetriNet
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:8080"],  # your client URL
    allow_methods=["*"],
    allow_headers=["*"],
)

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
@app.get("/test-petrinet-uuids")
async def test_uuids():
    token = login()
    return getPetriNetUUID(token)

@app.get("/create-petri-net-test")
async def test_createPetriNet():
    return createPetriNet()

@app.get("/test-bpmn-uuids")
async def test_uuids():
    token = login()
    return getBPMNUUID(token)
