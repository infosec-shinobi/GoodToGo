/* Browser-local resume format v1. Specification: docs/private-resume-format.md. */
(() => {
  "use strict";
  const MAX_FILE_BYTES = 2 * 1024 * 1024;
  const MAX_PLAIN_BYTES = 1024 * 1024;
  const encoder = new TextEncoder();
  const aad = encoder.encode("goodtogo.private-resume/v1");
  const fail = () => { throw new Error("Invalid or unsupported resume file."); };
  const object = (value) => value !== null && typeof value === "object" && !Array.isArray(value);
  const keys = (value, allowed) => object(value) && Object.keys(value).every((key) => allowed.includes(key));
  const text = (value, max) => typeof value === "string" && value.length <= max;
  const base64 = (bytes) => {
    let binary = "";
    for (const byte of bytes) binary += String.fromCharCode(byte);
    return btoa(binary);
  };
  const unbase64 = (value, length) => {
    if (typeof value !== "string" || value.length > MAX_FILE_BYTES || !/^(?:[A-Za-z0-9+/]{4})*(?:[A-Za-z0-9+/]{2}==|[A-Za-z0-9+/]{3}=)?$/.test(value)) fail();
    const bytes = Uint8Array.from(atob(value), (char) => char.charCodeAt(0));
    if (base64(bytes) !== value || (length && bytes.length !== length)) fail();
    return bytes;
  };

  const passwordWarning = (password) => {
    if (!text(password, 1024) || password.length < 16) return "Use at least 16 characters; prefer 5–7 randomly chosen words.";
    if (new Set(password).size < 8) return "Avoid repeated characters. Use an unpredictable passphrase, preferably 5–7 random words.";
    return "Length check passed, not a strength guarantee. Avoid quotes, names, and reused passwords; prefer 5–7 random words.";
  };
  const canExport = (password) => text(password, 1024) && password.length >= 16 && new Set(password).size >= 8;

  // Treat decrypted files as untrusted input. No HTML, selectors, or extra state keys.
  const validateState = (state, workbook) => {
    if (!object(state)) fail();
    const questions = new Map(workbook.sections.flatMap((section) => section.questions.map((q) => [q.id, q])));
    const result = {};
    for (const [key, value] of Object.entries(state)) {
      if (key === "__tasks") continue;
      const note = key.endsWith("__note");
      const question = questions.get(note ? key.slice(0, -6) : key);
      if (!question || !text(value, note ? 4000 : 32)) fail();
      const choices = question.response_type === "applicability"
        ? ["yes", "no", "not_sure"]
        : ["complete", "in_progress", "not_started", "not_sure", "professional_help", "not_applicable"];
      if (!note && !choices.includes(value)) fail();
      result[key] = value;
    }
    if (state.__tasks !== undefined && !object(state.__tasks)) fail();
    result.__tasks = {};
    for (const [id, task] of Object.entries(state.__tasks || {})) {
      if (!questions.get(id)?.task || !keys(task, ["included", "priority", "responsiblePerson", "targetDate"])) fail();
      if (task.included !== undefined && typeof task.included !== "boolean") fail();
      if (task.priority !== undefined && !["critical", "high", "medium", "low"].includes(task.priority)) fail();
      if (task.responsiblePerson !== undefined && !text(task.responsiblePerson, 120)) fail();
      if (task.targetDate !== undefined && (!text(task.targetDate, 10) || (task.targetDate !== "" &&
        (!/^\d{4}-\d{2}-\d{2}$/.test(task.targetDate) || !Number.isFinite(Date.parse(task.targetDate)) ||
          new Date(task.targetDate).toISOString().slice(0, 10) !== task.targetDate)))) fail();
      result.__tasks[id] = { ...task };
    }
    return result;
  };

  const deriveKey = async (password, salt, signal) => {
    if (!globalThis.crypto?.subtle || !globalThis.scrypt) throw new Error("Resume files require HTTPS or localhost and a supported browser.");
    if (!text(password, 1024) || !password.length) throw new Error("Enter the file's passphrase.");
    const bytes = encoder.encode(password);
    let raw;
    try {
      if (signal?.aborted) throw new Error("Cancelled.");
      const fallback = () => globalThis.scrypt.scrypt(bytes, salt, 131072, 8, 1, 32, () => signal?.aborted === true);
      if (globalThis.Worker && globalThis.navigator?.onLine !== false) {
        try {
          raw = await new Promise((resolve, reject) => {
            const worker = new Worker("/static/js/resume-worker.js");
            const finish = (key) => {
              worker.terminate();
              signal?.removeEventListener("abort", abort);
              if (key instanceof Uint8Array && key.length === 32) resolve(key);
              else reject(new Error("Key derivation failed or was cancelled."));
            };
            const abort = () => finish(null);
            signal?.addEventListener("abort", abort, { once: true });
            worker.onmessage = ({ data }) => finish(data);
            worker.onerror = () => finish(null);
            try { worker.postMessage({ password: bytes, salt }); }
            catch { finish(null); }
          });
        } catch (error) {
          if (signal?.aborted) throw error;
          // Already-loaded local JS also works if the server/worker is unavailable.
          raw = await fallback();
        }
      } else {
        raw = await fallback();
      }
      if (signal?.aborted) throw new Error("Cancelled.");
      return await crypto.subtle.importKey("raw", raw, "AES-GCM", false, ["encrypt", "decrypt"]);
    } finally {
      bytes.fill(0);
      raw?.fill(0);
    }
  };

  const seal = async (state, password, workbook, signal) => {
    if (!canExport(password)) throw new Error(passwordWarning(password));
    const payload = encoder.encode(JSON.stringify({
      schema: 1, pack: { id: workbook.id, version: workbook.version },
      createdAt: new Date().toISOString(), state: validateState(state, workbook),
    }));
    if (payload.length > MAX_PLAIN_BYTES) fail();
    try {
      const salt = crypto.getRandomValues(new Uint8Array(16));
      const iv = crypto.getRandomValues(new Uint8Array(12));
      const key = await deriveKey(password, salt, signal);
      const ciphertext = await crypto.subtle.encrypt({ name: "AES-GCM", iv, additionalData: aad, tagLength: 128 }, key, payload);
      return JSON.stringify({ format: "goodtogo.private-resume", version: 1,
        kdf: { name: "scrypt", N: 131072, r: 8, p: 1, salt: base64(salt) },
        cipher: { name: "AES-256-GCM", iv: base64(iv) }, ciphertext: base64(new Uint8Array(ciphertext)) });
    } finally {
      payload.fill(0);
    }
  };

  const open = async (fileText, password, workbook, signal) => {
    if (!text(fileText, MAX_FILE_BYTES) || encoder.encode(fileText).length > MAX_FILE_BYTES) fail();
    let envelope;
    try { envelope = JSON.parse(fileText); } catch { fail(); }
    if (!keys(envelope, ["format", "version", "kdf", "cipher", "ciphertext"]) ||
        envelope.format !== "goodtogo.private-resume" || envelope.version !== 1 ||
        !keys(envelope.kdf, ["name", "N", "r", "p", "salt"]) ||
        envelope.kdf.name !== "scrypt" || envelope.kdf.N !== 131072 || envelope.kdf.r !== 8 || envelope.kdf.p !== 1 ||
        !keys(envelope.cipher, ["name", "iv"]) || envelope.cipher.name !== "AES-256-GCM") fail();
    // Check cost/size/encoding before running the memory-hard KDF.
    const salt = unbase64(envelope.kdf.salt, 16);
    const iv = unbase64(envelope.cipher.iv, 12);
    const ciphertext = unbase64(envelope.ciphertext);
    if (ciphertext.length < 16 || ciphertext.length > MAX_PLAIN_BYTES + 16) fail();
    const key = await deriveKey(password, salt, signal);
    let plaintext;
    try {
      plaintext = new Uint8Array(await crypto.subtle.decrypt({ name: "AES-GCM", iv, additionalData: aad, tagLength: 128 }, key, ciphertext));
    } catch {
      throw new Error("Could not unlock the file. The passphrase is incorrect or the file is damaged.");
    }
    try {
      const payload = JSON.parse(new TextDecoder("utf-8", { fatal: true }).decode(plaintext));
      if (!keys(payload, ["schema", "pack", "createdAt", "state"]) || payload.schema !== 1 ||
          !keys(payload.pack, ["id", "version"]) || !text(payload.createdAt, 40) ||
          !Number.isFinite(Date.parse(payload.createdAt))) fail();
      if (payload.pack.id !== workbook.id || payload.pack.version !== workbook.version) {
        throw new Error("This file uses a different content pack or version. Use its matching GoodToGo release; no answers were changed.");
      }
      return validateState(payload.state, workbook);
    } finally {
      plaintext.fill(0);
    }
  };

  globalThis.GoodToGoResume = Object.freeze({ seal, open, validateState, canExport, passwordWarning, MAX_FILE_BYTES });
})();
