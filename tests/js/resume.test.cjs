const assert = require("node:assert/strict");
const { test } = require("node:test");
const { webcrypto, scryptSync, createHash } = require("node:crypto");
const fs = require("node:fs");
const vm = require("node:vm");
const scrypt = require("../../app/static/vendor/scrypt-3.0.1.js");
const context = { crypto: webcrypto, scrypt, TextEncoder, TextDecoder, Uint8Array, btoa, atob };
vm.runInNewContext(fs.readFileSync("app/static/js/resume-crypto.js", "utf8"), context);
const resume = context.GoodToGoResume;
const workbook = { id: "test", version: "1", sections: [{ questions: [{ id: "q", task: {} }] }] };
const password = "cobalt apricot heron meadow velvet";
const state = { q: "not_sure", q__note: "Safe note 🐾", __tasks: { q: {
  included: false, priority: "low", responsiblePerson: "Morgan", targetDate: "2026-12-01",
} } };

test("vendored scrypt provenance and RFC 7914 vector", () => {
  assert.equal(createHash("sha256").update(fs.readFileSync("app/static/vendor/scrypt-3.0.1.js")).digest("hex"),
    "544292934136527d60acc9e337d8c7b953f412e81314aa551a12d4230afd449d");
  const key = scrypt.syncScrypt([], [], 16, 1, 1, 64);
  assert.equal(Buffer.from(key).toString("hex"),
    "77d6576238657b203b19ca42c18a0497f16b4844e3074ae8dfdffa3fede21442" +
    "fcd0069ded0948f8326a753a0fc81f17e8d3e0fb2e0d3628cf35e20c38d18906");
});

test("roundtrip, random salt/IV, Unicode, wrong password and authenticated tamper rejection", async () => {
  const file = await resume.seal(state, password, workbook);
  const decoded = await resume.open(file, password, workbook);
  assert.equal(JSON.stringify(decoded), JSON.stringify(state));
  assert.ok(!file.includes("Safe note"));
  assert.ok(!file.includes(password));
  const envelope = JSON.parse(file);
  const independent = scryptSync(password, Buffer.from(envelope.kdf.salt, "base64"), 32,
    { N: 131072, r: 8, p: 1, maxmem: 256 * 1024 * 1024 });
  const key = await webcrypto.subtle.importKey("raw", independent, "AES-GCM", false, ["decrypt"]);
  const plaintext = await webcrypto.subtle.decrypt({ name: "AES-GCM",
    iv: Buffer.from(envelope.cipher.iv, "base64"), additionalData: Buffer.from("goodtogo.private-resume/v1") },
    key, Buffer.from(envelope.ciphertext, "base64"));
  assert.equal(JSON.parse(Buffer.from(plaintext).toString()).state.q__note, state.q__note);
  const second = JSON.parse(await resume.seal(state, password, workbook));
  assert.notEqual(second.kdf.salt, envelope.kdf.salt);
  assert.notEqual(second.cipher.iv, envelope.cipher.iv);
  await assert.rejects(resume.open(file, "wrong passphrase", workbook), /incorrect or the file is damaged/);
  const corrupted = Buffer.from(envelope.ciphertext, "base64");
  corrupted[0] ^= 1;
  envelope.ciphertext = corrupted.toString("base64");
  await assert.rejects(resume.open(JSON.stringify(envelope), password, workbook), /incorrect or the file is damaged/);
  await assert.rejects(resume.open(file, password, { ...workbook, version: "2" }), /different content pack/);
});

test("reject malformed state, parameters, size, version and weak export passphrases", async () => {
  for (const bad of [{ q: "bad" }, { foreign: "x" }, { q__note: "x".repeat(4001) },
    { __tasks: { q: { targetDate: "2026-02-30" } } },
    { __tasks: { q: { priority: "urgent" } } }, { __tasks: { q: { included: "yes" } } },
    { __tasks: { q: { responsiblePerson: "x".repeat(121) } } },
    JSON.parse('{"__proto__":{"polluted":true}}')]) {
    assert.throws(() => resume.validateState(bad, workbook), /Invalid/);
  }
  assert.equal(resume.canExport("short"), false);
  assert.equal(resume.canExport("a".repeat(30)), false);
  assert.equal(resume.canExport(password), true);
  for (const file of ["{}", "{", "x".repeat(resume.MAX_FILE_BYTES + 1),
    JSON.stringify({ format: "goodtogo.private-resume", version: 2 }),
    JSON.stringify({ format: "goodtogo.private-resume", version: 1,
      kdf: { name: "scrypt", N: 2 ** 30, r: 8, p: 1 } })]) {
    await assert.rejects(resume.open(file, password, workbook), /Invalid/);
  }
});
