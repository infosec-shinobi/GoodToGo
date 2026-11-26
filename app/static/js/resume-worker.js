/* Dedicated, short-lived KDF worker. No answers, storage, logging, or network APIs. */
importScripts("/static/vendor/scrypt-3.0.1.js");
self.onmessage = ({ data }) => {
  let key;
  try {
    key = scrypt.syncScrypt(data.password, data.salt, 131072, 8, 1, 32);
    self.postMessage(key, [key.buffer]);
  } catch {
    self.postMessage(null);
  } finally {
    data.password.fill(0);
    if (key?.byteLength) key.fill(0);
    self.close();
  }
};
