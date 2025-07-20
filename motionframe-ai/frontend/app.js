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

    const eventSource = new EventSource('/api/generate-video-sse', {
        method: 'POST',
        body: formData,
    });

    eventSource.onmessage = (event) => {
        const data = JSON.parse(event.data);

        if (data.video_url) {
            video.src = data.video_url;
            downloadBtn.href = data.video_url;
            videoContainer.classList.remove('hidden');
            loading.classList.add('hidden');
            eventSource.close();
        } else {
            const progress = parseInt(data);
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
});
