const express = require('express');
const http = require('http');
const { Server } = require('socket.io');
const path = require('path');
const { isAnomaly, getAlertMessage } = require('./utils/anomalyDetector');
const { encrypt } = require('./utils/encryption');

const app = express();
const server = http.createServer(app);
const io = new Server(server, {
  cors: {
    origin: '*',
  }
});

// Serve static files
app.use(express.static(path.join(__dirname, 'public')));

const clientStreams = new Map(); // streamId -> {clientId, recentBPMs: []}

io.on('connection', (socket) => {
  console.log('Client connected:', socket.id);

  socket.on('register-stream', (streamId) => {
    clientStreams.set(streamId, { clientId: socket.id, recentBPMs: [] });
    console.log(`Stream ${streamId} registered by ${socket.id}`);
    socket.emit('status', `Stream ${streamId} registered. Send BPM data.`);
  });

  socket.on('bpm-data', (data) => { // {streamId, bpm}
    const stream = clientStreams.get(data.streamId);
    if (stream && stream.clientId === socket.id) {
      stream.recentBPMs.push(data.bpm);
      if (stream.recentBPMs.length > 10) stream.recentBPMs.shift(); // Keep last 10

      if (isAnomaly(data.bpm)) {
        const alertMsg = getAlertMessage(data.streamId, data.bpm);
        const encryptedAlert = encrypt(alertMsg);
        socket.emit('alert', encryptedAlert); // Encrypted alert to client
        console.log(`Anomaly alert for ${data.streamId}: BPM ${data.bpm}`);
      }
    }
  });

  socket.on('disconnect', () => {
    console.log('Client disconnected:', socket.id);
    // Clean up streams
    for (let [streamId, stream] of clientStreams) {
      if (stream.clientId === socket.id) {
        clientStreams.delete(streamId);
      }
    }
  });
});

const PORT = process.env.PORT || 3000;
server.listen(PORT, () => {
  console.log(`Server running on http://localhost:${PORT}`);
});
