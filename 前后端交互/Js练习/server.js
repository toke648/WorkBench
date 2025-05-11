const express = require('express');
const http = require('http');
const WebSocket = require('ws');
const multer = require('multer');
const path = require('path');
const fs = require('fs');
const { spawn } = require('child_process');

const app = express();
const server = http.createServer(app);
const wss = new WebSocket.Server({ server });
const upload = multer({ dest: 'uploads/' });

app.post('/api/upload-audio', upload.single('audio'), (req, res) => {
    const tempPath = req.file.path;
    const targetPath = path.join(__dirname, 'uploads', req.file.originalname);

    fs.rename(tempPath, targetPath, err => {
        if (err) return res.status(500).send(err);
        res.json({ status: 'success', message: 'Audio uploaded successfully' });
    });
});

wss.on('connection', (ws) => {
    console.log('Client connected');

    ws.on('message', (message) => {
        const audioData = Buffer.from(message);

        // 保存音频数据到临时文件
        const tempFilePath = path.join(__dirname, 'uploads', 'temp_recording.wav');
        fs.writeFileSync(tempFilePath, audioData);

        // 使用Python脚本进行语音转录
        const pythonProcess = spawn('python', ['text_program/audio_record.py', tempFilePath]);

        pythonProcess.stdout.on('data', (data) => {
            const transcription = data.toString().trim();
            ws.send(JSON.stringify({ transcription }));
        });

        pythonProcess.stderr.on('data', (data) => {
            console.error(`Python error: ${data}`);
        });

        pythonProcess.on('close', (code) => {
            console.log(`Python process exited with code ${code}`);
            fs.unlinkSync(tempFilePath); // 删除临时文件
        });
    });

    ws.on('close', () => {
        console.log('Client disconnected');
    });
});

server.listen(3000, () => {
    console.log('Server is running on port 3000');
});