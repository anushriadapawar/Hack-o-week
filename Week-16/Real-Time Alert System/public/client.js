const socket = io();
const canvas = document.getElementById('bpmChart');
const ctx = canvas.getContext('2d');
const statusEl = document.getElementById('status');
const decryptedAlertsEl = document.getElementById('decryptedAlerts');
const connectBtn = document.getElementById('connectBtn');
const startBtn = document.getElementById('startBtn');
const highBpmBtn = document.getElementById('highBpmBtn');
const stopBtn = document.getElementById('stopBtn');

let streamId = 'user-heart-rate-' + Math.random().toString(36).substr(2, 9);
let streamInterval = null;
let bpmHistory = [];
const MAX_HISTORY = 50;
canvas.width = canvas.offsetWidth;
canvas.height = 200;

// Chart utils
function drawChart() {
  ctx.clearRect(0, 0, canvas.width, canvas.height);
  ctx.strokeStyle = '#007bff';
  ctx.lineWidth = 2;
  ctx.beginPath();
  const step = canvas.width / Math.max(bpmHistory.length - 1, 1);
  bpmHistory.forEach((bpm, i) => {
    const x = i * step;
    const y = canvas.height - (bpm / 200 * canvas.height); // Normalize
    if (i === 0) ctx.moveTo(x, y);
    else ctx.lineTo(x, y);
  });
  ctx.stroke();
}

// UI updates
function updateStatus(msg) {
  statusEl.textContent = `Status: ${msg}`;
}

connectBtn.onclick = () => {
  socket.emit('register-stream', streamId);
  updateStatus('Connected, stream registered. Start streaming.');
  connectBtn.disabled = true;
  startBtn.disabled = false;
  highBpmBtn.disabled = false;
};

function stopStream() {
  if (streamInterval) clearInterval(streamInterval);
  streamInterval = null;
  updateButtons();
}

function updateButtons() {
  stopBtn.disabled = !streamInterval;
  startBtn.disabled = !!streamInterval;
  highBpmBtn.disabled = !!streamInterval;
}

startBtn.onclick = () => {
  stopStream();
  streamInterval = setInterval(() => {
    const bpm = 60 + Math.random() * 40; // 60-100 normal
    bpmHistory.push(bpm);
    if (bpmHistory.length > MAX_HISTORY) bpmHistory.shift();
    socket.emit('bpm-data', { streamId, bpm });
    drawChart();
  }, 1000);
  updateButtons();
  updateStatus('Streaming normal BPM...');
};

highBpmBtn.onclick = () => {
  stopStream();
  streamInterval = setInterval(() => {
    const bpm = 110 + Math.random() * 50; // 110-160 high → triggers
    bpmHistory.push(bpm);
    if (bpmHistory.length > MAX_HISTORY) bpmHistory.shift();
    socket.emit('bpm-data', { streamId, bpm });
    drawChart();
  }, 1000);
  updateButtons();
  updateStatus('Streaming HIGH BPM (should trigger alerts)...');
};

stopBtn.onclick = stopStream;

socket.on('status', (msg) => updateStatus(msg));
socket.on('alert', (encryptedAlert) => {
  // Mock decrypt for client-side demo (browser JS; prod: Web Crypto API or crypto-js lib)
  function mockDecrypt(encryptedData) {
    return `DECRYPTED ALERT: High BPM detected in stream ${streamId}! Current BPM > 120. Original encrypted: ${encryptedData.encrypted.substring(0, 30)}...`;
  }

  console.log('Received encrypted alert:', encryptedAlert);
  const decryptedMsg = mockDecrypt(encryptedAlert);
  const alertDiv = document.createElement('div');
  alertDiv.style.padding = '10px';
  alertDiv.style.borderBottom = '1px solid #dc3545';
  alertDiv.style.backgroundColor = '#f8d7da';
  alertDiv.innerHTML = `<strong>🔴 Encrypted Payload:</strong><br>${JSON.stringify(encryptedAlert, null, 2).substring(0, 120)}...<br><strong>✅ Decrypted Message:</strong><br>${decryptedMsg}`;
  decryptedAlertsEl.insertBefore(alertDiv, decryptedAlertsEl.firstChild);
  decryptedAlertsEl.scrollTop = 0;
});
