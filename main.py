from fastapi import FastAPI, File, UploadFile, Form
from helpers.validators import validate_event_log
from helpers.parser import parse_event_log
from algorithms.router import execute_algorithm
from helpers.uuid_resolver import getPetriNetUUID
from helpers.uuid_resolver import getBPMNUUID
from helpers.signin import login
from fastapi.middleware.cors import CORSMiddleware
from typing import Optional

app = FastAPI()

# To allow cross-origin resource sharing; if client does not run on 8080, allow_origins must be changed
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:8080"], 
    allow_methods=["*"],
    allow_headers=["*"],
)

#-------------------------------Health Check-------------------------------
@app.get("/health")
async def health():
    return {"status": "ok"}

#-------------------------------Run Mining Algorithm-------------------------------
@app.post("/run")
async def run(algorithm: str, file: UploadFile = File(...), 
    case_id: Optional[str] = Form(None),
    activity_name: Optional[str] = Form(None),
    timestamp: Optional[str] = Form(None)
    ):
    validate_event_log(file)
    event_log = parse_event_log(file, case_id, activity_name, timestamp)
    result = execute_algorithm(algorithm, event_log)
    return result

#-------------------------------Testing routes------------------------------------
@app.get("/test-petrinet-uuids")
async def test_petrinet_uuids():
    token = login()
    return getPetriNetUUID(token)

@app.get("/test-bpmn-uuids")
async def test_bpmn_uuids():
    token = login()
    return getBPMNUUID(token)
