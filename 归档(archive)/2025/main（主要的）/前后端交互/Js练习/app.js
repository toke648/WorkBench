document.addEventListener('DOMContentLoaded', function() {
    const recordButton = document.getElementById('record');
    const stopButton = document.getElementById('stop');
    const transcriptionArea = document.getElementById('transcription');
    let mediaRecorder;
    let audioChunks = [];
    let socket;

    recordButton.addEventListener('click', async () => {
        try {
            const stream = await navigator.mediaDevices.getUserMedia({ audio: true });
            mediaRecorder = new MediaRecorder(stream);

            mediaRecorder.ondataavailable = event => {
                audioChunks.push(event.data);
            };

            mediaRecorder.onstop = () => {
                const audioBlob = new Blob(audioChunks, { type: 'audio/wav' });
                const formData = new FormData();
                formData.append('audio', audioBlob, 'recording.wav');

                // 使用axios发送POST请求
                axios.post('/api/upload-audio', formData, {
                    headers: {
                        'Content-Type': 'multipart/form-data'
                    }
                })
                .then(function (response) {
                    console.log('Success:', response.data);
                })
                .catch(function (error) {
                    console.error('Error:', error);
                });

                audioChunks = [];
            };

            mediaRecorder.start();
            recordButton.disabled = true;
            stopButton.disabled = false;

            // WebSocket连接到后端进行实时转录
            socket = new WebSocket('ws://localhost:3000');

            socket.onopen = () => {
                console.log('WebSocket connection established');
            };

            socket.onmessage = (event) => {
                const data = JSON.parse(event.data);
                transcriptionArea.value += data.transcription + ' ';
            };

            socket.onclose = () => {
                console.log('WebSocket connection closed');
            };

            socket.onerror = (error) => {
                console.error('WebSocket error:', error);
            };
        } catch (err) {
            console.error('Error accessing microphone:', err);
        }
    });

    stopButton.addEventListener('click', () => {
        mediaRecorder.stop();
        recordButton.disabled = false;
        stopButton.disabled = true;

        if (socket) {
            socket.close();
        }
    });
});
