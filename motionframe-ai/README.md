# MotionFrame AI

Turn a still image into a realistic animated video (MP4) using a camera movement prompt.

## Features

*   Upload a static image (JPG or PNG).
*   Enter a camera motion prompt in natural language (e.g., “pan left slowly”, “zoom out”, “rotate clockwise”).
*   Select the desired video duration: 5, 10, or 20 seconds.
*   Generate the video using AnimateDiff + Stable Diffusion.
*   Display the generated Full HD (1920x1080) MP4 video on the page.
*   Provide a button to download the video.

## Technical Stack

*   **Frontend:** HTML + Tailwind CSS
*   **Backend:** FastAPI (Python)
*   **AI Engine:** AnimateDiff + Stable Diffusion
*   **Storage:** Local file system
*   **Output Format:** MP4

## Setup

### 1. Clone the repository

```bash
git clone https://github.com/your-username/motionframe-ai.git
cd motionframe-ai
```

### 2. Install Python dependencies

Make sure you have Python 3.8 or higher installed.

```bash
pip install -r backend/requirements.txt
```

### 3. Download the models

You will need to download the Stable Diffusion v1.5 model and the AnimateDiff motion adapter.

*   **Stable Diffusion v1.5:** Download from [runwayml/stable-diffusion-v1-5](https://huggingface.co/runwayml/stable-diffusion-v1-5) and place it in a `models/stable-diffusion-v1-5` directory.
*   **AnimateDiff Motion Adapter:** Download from [guoyww/animatediff-motion-adapter-v1-5-2](https://huggingface.co/guoyww/animatediff-motion-adapter-v1-5-2) and place it in a `models/animatediff-motion-adapter-v1-5-2` directory.

Your `models` directory should look like this:

```
models/
├── stable-diffusion-v1-5/
│   ├── ...
└── animatediff-motion-adapter-v1-5-2/
    └── ...
```

### 4. Update the model paths in the code

In `motionframe-ai/ai/animatediff.py`, update the paths to the models you downloaded:

```python
pipe = AnimateDiffPipeline.from_pretrained("./models/stable-diffusion-v1-5", motion_adapter=adapter)
```

## Usage

1.  **Start the backend server:**

    ```bash
    cd motionframe-ai/backend
    uvicorn main:app --reload
    ```

2.  **Open your browser:**

    Open your web browser and go to `http://localhost:8000`.

3.  **Generate a video:**

    *   Upload an image.
    *   Enter a camera motion prompt.
    *   Select the video duration.
    *   Click "Generate Video".

    The generated video will appear on the page, and you can download it using the "Download Video" button.

## Troubleshooting

*   **`CUDA out of memory`:** If you get a `CUDA out of memory` error, try reducing the `num_frames` in `ai/animatediff.py` or use a smaller image.
*   **Slow generation:** Video generation can be slow, especially on older GPUs. Be patient!
*   **Model loading issues:** Make sure you have downloaded the correct models and placed them in the correct directories.

## Optional Bonus: Google Colab

A Google Colab notebook is available for users who do not have a local GPU. You can find it here: [link-to-colab-notebook]
