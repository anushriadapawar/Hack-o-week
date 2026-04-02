const crypto = require('crypto');

const algorithm = 'aes-256-cbc';
const key = crypto.randomBytes(32); // In production, use env var or key management
const iv = crypto.randomBytes(16); // In production, generate per message

function encrypt(text) {
  const cipher = crypto.createCipher(algorithm, key);
  let encrypted = cipher.update(text, 'utf8', 'hex');
  encrypted += cipher.final('hex');
  return { encrypted, iv: iv.toString('hex') };
}

function decrypt(encryptedData, ivHex) {
  const decipher = crypto.createDecipher(algorithm, key);
  decipher.setAutoPadding(true);
  const ivBuffer = Buffer.from(ivHex, 'hex');
  decipher.setAAD(); // Not used but for completeness
  let decrypted = decipher.update(encryptedData, 'hex', 'utf8');
  decrypted += decipher.final('utf8');
  return decrypted;
}

module.exports = { encrypt, decrypt, key, iv };
