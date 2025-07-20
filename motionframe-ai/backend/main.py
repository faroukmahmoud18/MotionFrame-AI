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
app.mount("/", StaticFiles(directory="../frontend", html=True), name="frontend")
app.mount("/storage", StaticFiles(directory="../storage"), name="storage")

class VideoRequest(BaseModel):
    prompt: str
    duration: int

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

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)
