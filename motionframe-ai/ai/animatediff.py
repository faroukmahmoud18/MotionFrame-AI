import os
import torch
import imageio
import logging
import numpy as np
from PIL import Image
from diffusers import MotionAdapter, AnimateDiffPipeline

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class AnimateDiff:
    def __init__(self):
        self.pipe = None

    def load_models(self):
        """
        Loads the AnimateDiff and Stable Diffusion models.
        This function is called once on application startup.
        """
        if self.pipe is None:
            logger.info("Loading AnimateDiff and Stable Diffusion models...")
            adapter = MotionAdapter.from_pretrained("guoyww/animatediff-motion-adapter-v1-5-2")
            self.pipe = AnimateDiffPipeline.from_pretrained("runwayml/stable-diffusion-v1-5", motion_adapter=adapter)
            self.pipe.to("cuda")
            logger.info("Models loaded successfully.")

    def generate_animation(self, image_path: str, prompt: str, duration: int, progress_callback=None) -> bytes:
        """
        Generates a video animation from a static image.

        Args:
            image_path (str): The path to the input image.
            prompt (str): The camera motion prompt.
            duration (int): The duration of the video in seconds.
            progress_callback (function): A function to call with progress updates.

        Returns:
            bytes: The generated video as a byte string.
        """
        # 1. Downscale the input image
        input_image = Image.open(image_path).convert("RGB")
        input_image = input_image.resize((512, 512))
        logger.info(f"Input image resized to {input_image.size}")

        # 2. Set the number of frames and inference steps
        num_frames = duration * 8
        num_inference_steps = 20  # Reduced for faster generation
        logger.info(f"Generating {num_frames} frames with {num_inference_steps} inference steps.")

        # 3. Generate the animation in a batch
        output = self.pipe(
            prompt=prompt,
            negative_prompt="bad quality, worse quality",
            num_frames=num_frames,
            guidance_scale=7.5,
            num_inference_steps=num_inference_steps,
            image=input_image,
            callback=progress_callback,
            callback_steps=1,
        )
        frames = output.frames[0]
        logger.info(f"Generated {len(frames)} frames.")

        # 4. Verify the output frames
        if len(frames) > 0:
            logger.info(f"First frame shape: {np.array(frames[0]).shape}, dtype: {np.array(frames[0]).dtype}")
            # frames[0].save("debug_frame.png") # Uncomment for debugging

        # 5. Convert frames to RGB and create video in memory
        video_frames = []
        for frame in frames:
            video_frames.append(np.array(frame.convert("RGB")))

        # 6. Assemble the video using imageio
        video_bytes = imageio.mimwrite("<bytes>", video_frames, format="mp4", fps=8)
        logger.info("Video created successfully in memory.")

        return video_bytes

def generate_video_from_image(animatediff: AnimateDiff, image_path: str, prompt: str, duration: int) -> str:
    """
    Generates a video from an image using the AnimateDiff AI engine.
    """
    video_bytes = animatediff.generate_animation(image_path, prompt, duration)
    video_filename = f"{os.path.splitext(os.path.basename(image_path))[0]}.mp4"
    video_path = os.path.join("storage/videos", video_filename)

    with open(video_path, "wb") as f:
        f.write(video_bytes)

    return video_path
