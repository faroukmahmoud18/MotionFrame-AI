import os
import torch
from diffusers import MotionAdapter, AnimateDiffPipeline
from diffusers.utils import export_to_video
from PIL import Image

def generate_animation(image_path: str, prompt: str, duration: int, output_path: str, progress_callback=None):
    """
    Generates a 240p vertical video (432x768) animation for TikTok using AnimateDiff.
    """

    # Load model and adapter with float16 precision to save VRAM
    adapter = MotionAdapter.from_pretrained("guoyww/animatediff-motion-adapter-v1-5-2")
    pipe = AnimateDiffPipeline.from_pretrained(
        "../models/stable-diffusion-v1-5",
        motion_adapter=adapter,
        torch_dtype=torch.float16
    )
    pipe.to("cuda")
    pipe.enable_model_cpu_offload()  # Optional: offload unused parts to CPU

    # Resize input image to vertical 432x768 (TikTok ratio)
    input_image = Image.open(image_path).convert("RGB")
    input_image = input_image.resize((432, 768))  # vertical video format

    num_frames = 24  # fixed number of frames

    if progress_callback is None:
        def default_callback(step: int, timestep: int, latents):
            print(f"Step {step}, Timestep {timestep}")
        progress_callback = default_callback

    # Run the animation pipeline
    output = pipe(
        prompt=prompt,
        negative_prompt="bad quality, worse quality",
        num_frames=num_frames,
        guidance_scale=7.5,
        num_inference_steps=25,
        image=input_image,
        callback=progress_callback,
        callback_steps=1,
        height=768,
        width=432
    )

    frames = output.frames[0]
    export_to_video(frames, output_path, fps=8)

    return output_path
