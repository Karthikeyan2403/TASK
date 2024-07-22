from fastapi import FastAPI, File, UploadFile, HTTPException
from pydantic import BaseModel
from fastapi.staticfiles import StaticFiles
from app.celery import celery_app
from app.tasks import combine_videos
import os

app = FastAPI()

# Serve static files
if not os.path.exists("static"):
    os.makedirs("static")
app.mount("/static", StaticFiles(directory="static"), name="static")

class JobStatus(BaseModel):
    job_id: str

@app.get("/")
async def root():
    return {"message": "Welcome to the video processing API!"}

@app.post("/upload")
async def upload_files(files: list[UploadFile] = File(...)):
    # Validate number of files
    if len(files) != 3:
        raise HTTPException(status_code=400, detail="Please upload exactly 3 files.")
    
    # Read files
    video_data = []
    for file in files:
        try:
            content = await file.read()  # Use await to read asynchronously
            video_data.append(content)
        except Exception as e:
            raise HTTPException(status_code=400, detail=f"Error reading file: {str(e)}")
    
    # Call Celery task
    job = combine_videos.delay(video_data)
    return {"job_id": job.id}

@app.get("/jobs/{job_id}")
async def get_job_status(job_id: str):
    result = celery_app.AsyncResult(job_id)
    if result.state == 'PENDING':
        return {"status": "Pending"}
    elif result.state == 'SUCCESS':
        download_url = f"/static/{job_id}.mp4"
        if os.path.exists(os.path.join("static", f"{job_id}.mp4")):
            return {"status": "Completed", "download_url": download_url}
        else:
            return {"status": "Completed", "download_url": None}
    elif result.state == 'FAILURE':
        return {"status": "Failed"}
    else:
        return {"status": result.state}
