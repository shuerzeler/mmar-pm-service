from fastapi import UploadFile, HTTPException

#Helper function to validate event log filetype

#Validate event log file format
def validate_event_log(file: UploadFile) -> None:
    #defines which filetypes are allowed
    allowed_extensions = [".xes", ".csv"]
    filename = file.filename.lower()
    
    #throw exception if filetype not in allowed
    if not any(filename.endswith(ext) for ext in allowed_extensions):
        raise HTTPException(
            status_code=400,
            detail=f"Unsupported file format. Allowed formats: {allowed_extensions}"
        )