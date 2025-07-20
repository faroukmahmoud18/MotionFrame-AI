import os
import torch
from diffusers import MotionAdapter, AnimateDiffPipeline
from diffusers.utils import export_to_video
from PIL import Image

def generate_animation(image_path: str, prompt: str, duration: int, output_path: str):
    """
    Generates a video animation from a static image using AnimateDiff.

    Args:
        image_path (str): The path to the input image.
        prompt (str): The camera motion prompt.
        duration (int): The duration of the video in seconds.
        output_path (str): The path to save the generated video.
    """
    # Load the motion adapter and pipeline
    adapter = MotionAdapter.from_pretrained("guoyww/animatediff-motion-adapter-v1-5-2")
    pipe = AnimateDiffPipeline.from_pretrained("runwayml/stable-diffusion-v1-5", motion_adapter=adapter)
    pipe.to("cuda")

    # Prepare the input image
    input_image = Image.open(image_path).convert("RGB")
    input_image = input_image.resize((512, 512)) # Resize for the model

    # Calculate the number of frames based on duration (assuming 8 fps)
    num_frames = duration * 8

    # Generate the animation
    output = pipe(
        prompt=prompt,
        negative_prompt="bad quality, worse quality",
        num_frames=num_frames,
        guidance_scale=7.5,
        num_inference_steps=25,
        image=input_image
    )
    frames = output.frames[0]

    # Export the frames to a video
    export_to_video(frames, output_path, fps=8)

    return output_path
