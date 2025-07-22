document.getElementById('upload-form').addEventListener('submit', async (e) => {
    e.preventDefault();

    const form = e.target;
    const formData = new FormData(form);
    const loading = document.getElementById('loading');
    const progressBar = document.getElementById('progress-bar');
    const videoContainer = document.getElementById('video-container');
    const video = document.getElementById('video');
    const downloadBtn = document.getElementById('download-btn');

    loading.classList.remove('hidden');
    videoContainer.classList.add('hidden');
    progressBar.style.width = '0%';
    progressBar.textContent = '0%';

    try {
        // 1. Upload the image
        const uploadResponse = await fetch('/api/upload-image', {
            method: 'POST',
            body: formData,
        });

        if (!uploadResponse.ok) {
            throw new Error('Failed to upload image');
        }

        const uploadData = await uploadResponse.json();
        const imageFilename = uploadData.filename;

        // 2. Start the SSE connection
        const prompt = formData.get('prompt');
        const duration = formData.get('duration');
        const url = `/api/generate-video-sse?image_filename=${imageFilename}&prompt=${prompt}&duration=${duration}`;
        alert(`Connecting to: ${url}`);
        const eventSource = new EventSource(url);

        eventSource.onmessage = (event) => {
            try {
                const data = JSON.parse(event.data);

                if (data.video_url) {
                    video.src = data.video_url;
                    downloadBtn.href = data.video_url;
                    videoContainer.classList.remove('hidden');
                    loading.classList.add('hidden');
                    eventSource.close();
                }
            } catch (e) {
                const progress = parseInt(event.data);
                progressBar.style.width = `${progress}%`;
                progressBar.textContent = `${progress}%`;
            }
        };

        eventSource.onerror = (error) => {
            console.error('EventSource failed:', error);
            alert('An error occurred while generating the video. Please try again.');
            loading.classList.add('hidden');
            eventSource.close();
        };
    } catch (error) {
        console.error(error);
        alert('An error occurred. Please try again.');
        loading.classList.add('hidden');
    }
});
