import os
import uuid
from fastapi import FastAPI, File, UploadFile, Form, HTTPException
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel
import uvicorn

import sys
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from ai.animatediff import generate_animation

def generate_video_from_image(image_path: str, prompt: str, duration: int) -> str:
    """
    Generates a video from an image using the AnimateDiff AI engine.
    """
    video_filename = f"{uuid.uuid4()}.mp4"
    video_path = os.path.join("../storage/videos", video_filename)

    generate_animation(image_path, prompt, duration, video_path)

    return video_path


app = FastAPI()

# Mount the frontend and storage directories
app.mount("/frontend", StaticFiles(directory="../frontend", html=True), name="frontend")
app.mount("/storage", StaticFiles(directory="../storage"), name="storage")

class VideoRequest(BaseModel):
    prompt: str
    duration: int

from sse_starlette.sse import EventSourceResponse
import asyncio

@app.post("/api/generate-video")
async def generate_video(
    image: UploadFile = File(...),
    prompt: str = Form(...),
    duration: int = Form(...)
):
    try:
        # Save the uploaded image
        image_ext = os.path.splitext(image.filename)[1]
        if image_ext.lower() not in [".jpg", ".jpeg", ".png"]:
            raise HTTPException(status_code=400, detail="Invalid image format. Only JPG and PNG are allowed.")

        image_filename = f"{uuid.uuid4()}{image_ext}"
        image_path = os.path.join("../storage/uploads", image_filename)
        with open(image_path, "wb") as f:
            f.write(await image.read())

        # Generate the video
        video_path = generate_video_from_image(image_path, prompt, duration)
        video_url = f"/storage/videos/{os.path.basename(video_path)}"

        return {"video_url": video_url}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

async def video_generator(image_path: str, prompt: str, duration: int):
    video_filename = f"{uuid.uuid4()}.mp4"
    video_path = os.path.join("../storage/videos", video_filename)

    queue = asyncio.Queue()
    loop = asyncio.get_event_loop()

    def progress_callback(step, timestep, latents=None):
        progress = int((step / 25) * 100)
        loop.call_soon_threadsafe(queue.put_nowait, f"data: {progress}\n\n")

    loop.run_in_executor(None, generate_animation, image_path, prompt, duration, video_path, progress_callback)

    while True:
        progress = await queue.get()
        yield progress
        if "100" in progress:
            break

    yield f"data: {{\"video_url\": \"/storage/videos/{video_filename}\"}}\n\n"

@app.post("/api/upload-image")
async def upload_image(image: UploadFile = File(...)):
    try:
        image_ext = os.path.splitext(image.filename)[1]
        if image_ext.lower() not in [".jpg", ".jpeg", ".png"]:
            raise HTTPException(status_code=400, detail="Invalid image format. Only JPG and PNG are allowed.")

        image_filename = f"{uuid.uuid4()}{image_ext}"
        image_path = os.path.join("../storage/uploads", image_filename)
        with open(image_path, "wb") as f:
            f.write(await image.read())

        return {"filename": image_filename}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/generate-video-sse")
async def generate_video_sse(
    image_filename: str,
    prompt: str,
    duration: int
):
    try:
        image_path = os.path.join("../storage/uploads", image_filename)
        if not os.path.exists(image_path):
            raise HTTPException(status_code=404, detail="Image not found.")

        return EventSourceResponse(video_generator(image_path, prompt, duration))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)
