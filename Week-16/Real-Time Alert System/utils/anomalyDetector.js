/**
 * Simple anomaly detection for BPM streams.
 * Alert if BPM > 120 (high heart rate example).
 */

function isAnomaly(bpm, threshold = 120) {
  return bpm > threshold;
}

function getAlertMessage(streamId, bpm) {
  return `ALERT: High BPM detected in stream ${streamId}! Current BPM: ${bpm}`;
}

module.exports = { isAnomaly, getAlertMessage };
