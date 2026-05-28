#Helper functions to validate
from fastapi import UploadFile, HTTPException

#Validate event log file format
def validate_event_log(file: UploadFile) -> None:
    allowed_extensions = [".xes", ".csv"]
    filename = file.filename.lower()
    
    if not any(filename.endswith(ext) for ext in allowed_extensions):
        raise HTTPException(
            status_code=400,
            detail=f"Unsupported file format. Allowed formats: {allowed_extensions}"
        )