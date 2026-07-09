from fastapi import UploadFile, HTTPException
from pm4py.objects.log.importer.xes import importer as xes_importer
from pm4py.objects.conversion.log import converter as log_converter
import pandas as pd 
import io
import tempfile
import os
import pm4py
from typing import Optional


def parse_event_log(file: UploadFile, case_id: Optional[str], activity_name: Optional[str], timestamp: Optional[str]):
    filename = file.filename.lower()
    contents = file.file.read()
    
    if filename.endswith(".csv"):
        df = pd.read_csv(io.BytesIO(contents))
        missing = [col for col in [case_id, activity_name, timestamp] if col not in df.columns]
        if missing:
            raise HTTPException(
                status_code=400,
                detail=f"Missing columns in CSV: {missing}"
            )
        # Rename to PM4Py standard names
        df = df.rename(columns={
            case_id: "case:concept:name",
            activity_name: "concept:name",
            timestamp: "time:timestamp"
        })
        df = pm4py.format_dataframe(df, 
            case_id="case:concept:name", 
            activity_key="concept:name", 
            timestamp_key="time:timestamp"
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