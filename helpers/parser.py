from fastapi import UploadFile, HTTPException
from pm4py.objects.log.importer.xes import importer as xes_importer
from pm4py.objects.conversion.log import converter as log_converter
import pandas as pd 
import io
import tempfile
import os

REQUIRED_CSV_COLUMNS = ["case:concept:name", "concept:name", "time:timestamp"]

def parse_event_log(file: UploadFile):
    filename = file.filename.lower()
    contents = file.file.read()
    
    if filename.endswith(".csv"):
        df = pd.read_csv(io.BytesIO(contents))
        missing = [col for col in REQUIRED_CSV_COLUMNS if col not in df.columns]
        if missing:
            raise HTTPException(
                status_code=400,
                detail=f"Missing required columns: {missing}"
            )
        event_log = log_converter.apply(df)
        return event_log   
    elif filename.endswith(".xes"):
        with tempfile.NamedTemporaryFile(suffix=".xes", delete=False) as tmp:
            tmp.write(contents)
            tmp_path = tmp.name
        event_log = xes_importer.apply(tmp_path)
        os.unlink(tmp_path)
        return event_log
    else:
        raise HTTPException(
            status_code=400,
            detail=f"File not valid"
        )