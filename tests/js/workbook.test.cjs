// Exercise the shipped browser script with a small DOM fixture, without dependencies.
const assert = require("node:assert/strict");
const fs = require("node:fs");
const vm = require("node:vm");
const { test } = require("node:test");

class Element {
  constructor(tag = "div") {
    this.tag = tag;
    this.children = [];
    this.dataset = {};
    this.listeners = {};
    this.value = "";
    this.textContent = "";
    this.checked = false;
  }
  append(...nodes) {
    nodes.forEach((node) => { node.parent = this; this.children.push(node); });
  }
  replaceChildren(...nodes) { this.children = []; this.append(...nodes); }
  addEventListener(type, listener) { this.listeners[type] = listener; }
  closest(selector) {
    if (selector === "[data-task-control]" && this.dataset.taskControl) return this;
    if (selector === ".task-item" && this.className?.split(" ").includes("task-item")) return this;
    return this.parent?.closest(selector);
  }
  querySelector(selector) {
    return this.children.find((node) => node.className?.split(" ").includes(selector.slice(1)))
      || this.children.map((node) => node.querySelector(selector)).find(Boolean);
  }
}

async function setup(saved) {
  const elements = {};
  const ids = ["private-workbook", "device-save", "task-list", "take-home-summary",
    "answered-count", "question-count", "progress-bar", "device-save-status",
    "inactivity-status", "clear-answers", "print-tasks", "print-workbook", "source-appendix-list"];
  ids.forEach((id) => { elements[id] = new Element(); });
  elements["progress-bar"].style = {};
  const form = elements["private-workbook"];
  const answer = new Element("input");
  answer.name = "test.question";
  answer.value = "not_started";
  form.querySelectorAll = (selector) => {
    if (selector.includes("radio")) return answer.checked ? [answer] : [];
    if (selector.includes(":not([hidden])")) return [{ dataset: { questionId: answer.name } }];
    return [];
  };
  form.querySelector = (selector) => selector.includes('value="not_started"') ? answer : null;
  form.reset = () => { answer.checked = false; };
  const storage = new Map(saved ? [["goodtogo.private.answers.v1", saved]] : []);
  const timers = new Map();
  const classes = new Set();
  const requests = [];
  const catalog = {
    workbook: { sections: [{ title: "Test section", questions: [{ id: answer.name,
      task: { title: "Test task", details: "Next step", priority: "high",
        when_values: ["not_started"], resource_ids: ["source"] } }] }] },
    resources: [{ id: "source", provider: "Official", title: "Guide", url: "https://example.org/",
      jurisdiction: "US", last_verified: "2026-09-11" }],
  };
  const context = {
    document: { getElementById: (id) => elements[id], createElement: (tag) => new Element(tag),
      addEventListener() {}, body: { classList: {
        add: (value) => classes.add(value), remove: (value) => classes.delete(value),
      } } },
    localStorage: { getItem: (key) => storage.get(key), setItem: (key, value) => storage.set(key, value),
      removeItem: (key) => storage.delete(key) },
    CSS: { escape: (value) => value },
    window: { setTimeout: (fn, ms) => { timers.set(ms, fn); return ms; },
      clearTimeout: (ms) => timers.delete(ms), addEventListener() {}, print() {} },
    fetch: async (...args) => { requests.push(args); return { ok: true, json: async () => catalog }; },
  };
  vm.runInNewContext(fs.readFileSync("app/static/js/workbook.js", "utf8"), context);
  await new Promise(setImmediate);
  const changeAnswer = (checked) => { answer.checked = checked; form.listeners.change(); };
  const task = () => elements["task-list"].children[0];
  const controls = (node) => node.children.flatMap((child) => [child, ...controls(child)]);
  const edit = (key, value, type = "input") => {
    const control = controls(task()).find((node) => node.dataset.taskControl === key);
    if (key === "included") control.checked = value;
    else control.value = value;
    elements["task-list"].listeners[type]({ target: control, type });
    return control;
  };
  return { elements, storage, timers, requests, changeAnswer, task, edit };
}

test("assignments stay local, retain focus, survive regeneration and opt-in reload", async () => {
  const page = await setup();
  page.changeAnswer(true);
  const original = page.task();
  page.edit("responsiblePerson", "Morgan <script>");
  page.edit("targetDate", "2026-12-01");
  assert.equal(page.task(), original, "typing must not replace the focused field");
  assert.match(page.task().querySelector(".task-assignment-print").textContent, /Morgan <script>.*2026-12-01/);
  assert.equal(page.storage.size, 0, "save is off by default");
  page.changeAnswer(false);
  page.changeAnswer(true);
  assert.match(page.task().querySelector(".task-assignment-print").textContent, /Morgan <script>/);
  page.elements["device-save"].checked = true;
  page.elements["device-save"].listeners.change();
  const saved = [...page.storage.values()][0];
  const reloaded = await setup(saved);
  assert.match(reloaded.task().querySelector(".task-assignment-print").textContent, /Morgan <script>.*2026-12-01/);
  reloaded.elements["device-save"].checked = false;
  reloaded.elements["device-save"].listeners.change();
  assert.equal(reloaded.storage.size, 0);
  assert.equal(page.requests.length, 1);
  assert.equal(page.requests[0][0], "/api/v1/catalog");
  assert.equal(page.requests[0][1].body, undefined);
});

test("selection and priority preserve assignments; appendix follows selected tasks", async () => {
  const page = await setup();
  page.changeAnswer(true);
  page.edit("responsiblePerson", "Morgan");
  page.edit("priority", "low", "change");
  assert.match(page.task().querySelector(".task-assignment-print").textContent, /Morgan/);
  assert.equal(page.elements["source-appendix-list"].children.length, 1);
  const source = page.elements["source-appendix-list"].children[0];
  assert.match(source.children[1].textContent, /US.*2026-09-11/);
  page.edit("included", false, "change");
  assert.equal(page.elements["source-appendix-list"].children.length, 0);
  assert.match(page.task().className, /excluded/);
});

test("manual and inactivity clearing remove assignments and source appendix", async () => {
  for (const idle of [false, true]) {
    const page = await setup();
    page.changeAnswer(true);
    page.edit("responsiblePerson", "Private name");
    page.edit("targetDate", "2026-12-01");
    if (idle) page.timers.get(30 * 60 * 1000)();
    else page.elements["clear-answers"].listeners.click();
    assert.equal(page.elements["task-list"].children.length, 0);
    assert.equal(page.elements["source-appendix-list"].children.length, 0);
    assert.equal(page.storage.size, 0);
    page.changeAnswer(true);
    assert.doesNotMatch(page.task().querySelector(".task-assignment-print").textContent, /Private name|2026-12-01/);
  }
});
