document.getElementById('upload-form').addEventListener('submit', async (e) => {
    e.preventDefault();

    const form = e.target;
    const formData = new FormData(form);
    const loading = document.getElementById('loading');
    const videoContainer = document.getElementById('video-container');
    const video = document.getElementById('video');
    const downloadBtn = document.getElementById('download-btn');

    loading.classList.remove('hidden');
    videoContainer.classList.add('hidden');

    try {
        const response = await fetch('/api/generate-video', {
            method: 'POST',
            body: formData,
        });

        if (!response.ok) {
            throw new Error('Failed to generate video');
        }

        const data = await response.json();
        const videoUrl = data.video_url;

        video.src = videoUrl;
        downloadBtn.href = videoUrl;
        videoContainer.classList.remove('hidden');
    } catch (error) {
        console.error(error);
        alert('An error occurred while generating the video. Please try again.');
    } finally {
        loading.classList.add('hidden');
    }
});
