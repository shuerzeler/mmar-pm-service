from fastapi import FastAPI, File, UploadFile
from helpers.validators import validate_event_log

app = FastAPI()

#health check
@app.get("/health")
async def health():
    return {"status": "ok"}

#-------------------------------Run Mining Algorithm-------------------------------
@app.post("/run")
async def run(algorithm: str, file: UploadFile = File(...)):
    validate_event_log(file)
    #call algorithm
    return{}