from fastapi import UploadFile, HTTPException
from pm4py.objects.log.importer.xes import importer as xes_importer
from pm4py.objects.conversion.log import converter as log_converter
from typing import Optional
import pandas as pd 
import io
import tempfile
import os
import pm4py

#Helper function to parse .csv and .xes to be used by PM4Py

def parse_event_log(file: UploadFile, case_id: Optional[str], activity_name: Optional[str], timestamp: Optional[str]):
    #read file
    filename = file.filename.lower()
    contents = file.file.read()
    
    #for .csv files
    if filename.endswith(".csv"):
        #create panda dataframe
        df = pd.read_csv(io.BytesIO(contents))
        #check that user mapped columns are in dataframe
        missing = [col for col in [case_id, activity_name, timestamp] if col not in df.columns]
        #throw exception if columns are missing
        if missing:
            raise HTTPException(
                status_code=400,
                detail=f"Missing columns in CSV: {missing}"
            )
        #rename mapped columns to PM4Py standard names
        df = df.rename(columns={
            case_id: "case:concept:name",
            activity_name: "concept:name",
            timestamp: "time:timestamp"
        })
        #ensure correct types
        df = pm4py.format_dataframe(df, 
            case_id="case:concept:name", 
            activity_key="concept:name", 
            timestamp_key="time:timestamp"
        )
        #apply converter to dataframe
        event_log = log_converter.apply(df)
        return event_log   
    #for .xes files
    elif filename.endswith(".xes"):
        #temporarily save to disk for the importer to read 
        with tempfile.NamedTemporaryFile(suffix=".xes", delete=False) as tmp:
            tmp.write(contents)
            tmp_path = tmp.name
        #apply converter
        event_log = xes_importer.apply(tmp_path)
        #remove temporary file
        os.unlink(tmp_path)
        return event_log
    #should already be caught by validator, but throw exception if file is not valid
    else:
        raise HTTPException(
            status_code=400,
            detail=f"File not valid"
        )