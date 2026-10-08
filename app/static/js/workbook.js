(() => {
  const storageKey = "goodtogo.private.answers.v1";
  const form = document.getElementById("private-workbook");
  const saveToggle = document.getElementById("device-save");
  const taskList = document.getElementById("task-list");
  const summary = document.getElementById("take-home-summary");
  const answeredCount = document.getElementById("answered-count");
  const questionCount = document.getElementById("question-count");
  const progressBar = document.getElementById("progress-bar");
  const saveStatus = document.getElementById("device-save-status");
  const inactivityStatus = document.getElementById("inactivity-status");
  const idleWarningMs = 25 * 60 * 1000;
  const idleClearMs = 30 * 60 * 1000;
  let idleWarningTimer;
  let idleClearTimer;
  let catalog;

  const getFormState = () => {
    const state = {};
    form.querySelectorAll('input[type="radio"]:checked:not(:disabled), textarea:not(:disabled)').forEach((field) => {
      if (field.value) state[field.name] = field.value;
    });
    return state;
  };

  const getReadinessAnswers = () => {
    const answers = {};
    form.querySelectorAll('input[type="radio"]:checked:not(:disabled)').forEach((input) => {
      answers[input.name] = input.value;
    });
    return answers;
  };

  const applyConditionals = () => {
    form.querySelectorAll(".question-card[data-applies-question]").forEach((card) => {
      const questionId = card.dataset.appliesQuestion;
      const appliesValues = (card.dataset.appliesValues || "").split(",");
      const selected = form.querySelector(`input[name="${CSS.escape(questionId)}"]:checked`);
      const isApplicable = selected && appliesValues.includes(selected.value);
      card.hidden = !isApplicable;
      card.querySelectorAll("input, textarea").forEach((field) => {
        field.disabled = !isApplicable;
      });
    });
  };

  const loadSavedAnswers = () => {
    const saved = localStorage.getItem(storageKey);
    if (!saved) return;
    try {
      const state = JSON.parse(saved);
      Object.entries(state).forEach(([name, value]) => {
        const textarea = form.querySelector(`textarea[name="${CSS.escape(name)}"]`);
        if (textarea) {
          textarea.value = value;
          return;
        }
        const input = form.querySelector(`input[name="${CSS.escape(name)}"][value="${CSS.escape(value)}"]`);
        if (input) input.checked = true;
      });
      saveToggle.checked = true;
    } catch {
      localStorage.removeItem(storageKey);
    }
  };

  const saveIfEnabled = () => {
    if (saveToggle.checked) localStorage.setItem(storageKey, JSON.stringify(getFormState()));
  };

  const updateSaveStatus = () => {
    saveStatus.textContent = saveToggle.checked
      ? "Device saving is on. Answers are remembered only in this browser."
      : "Device saving is off. Answers will be lost when this tab is closed.";
  };

  const clearSession = (message) => {
    form.reset();
    saveToggle.checked = false;
    localStorage.removeItem(storageKey);
    updateSaveStatus();
    inactivityStatus.textContent = message;
    refresh();
  };

  const resetIdleTimers = () => {
    window.clearTimeout(idleWarningTimer);
    window.clearTimeout(idleClearTimer);
    inactivityStatus.textContent = saveToggle.checked
      ? "Inactivity auto-clear is paused while device saving is on."
      : "Inactivity auto-clear is on for unsaved sessions.";

    if (saveToggle.checked) return;

    idleWarningTimer = window.setTimeout(() => {
      inactivityStatus.textContent = "Unsaved answers will clear after 5 more minutes of inactivity.";
    }, idleWarningMs);
    idleClearTimer = window.setTimeout(() => {
      clearSession("Unsaved answers were cleared after 30 minutes of inactivity.");
    }, idleClearMs);
  };

  const updateProgress = (answers) => {
    const visibleCards = form.querySelectorAll(".question-card:not([hidden])");
    const visibleQuestionIds = new Set([...visibleCards].map((card) => card.dataset.questionId));
    const answered = Object.keys(answers).filter((questionId) => visibleQuestionIds.has(questionId)).length;
    const total = visibleCards.length;
    questionCount.textContent = String(total);
    answeredCount.textContent = String(answered);
    progressBar.style.width = `${total ? (answered / total) * 100 : 0}%`;
  };

  const createResourceList = (resourceIds, resourcesById) => {
    if (!resourceIds.length) return null;
    const list = document.createElement("ul");
    list.className = "resource-list";
    resourceIds.forEach((id) => {
      const resource = resourcesById[id];
      if (!resource) return;
      const item = document.createElement("li");
      const link = document.createElement("a");
      link.href = resource.url;
      link.target = "_blank";
      link.rel = "noopener noreferrer";
      link.textContent = `${resource.provider}: ${resource.title}`;
      item.append(link);
      list.append(item);
    });
    return list;
  };

  const renderTasks = (answers) => {
    if (!catalog) return;
    const resourcesById = Object.fromEntries(catalog.resources.map((resource) => [resource.id, resource]));
    const priorityOrder = { critical: 0, high: 1, medium: 2, low: 3 };
    const tasks = [];

    catalog.workbook.sections.forEach((section) => {
      section.questions.forEach((question) => {
        const answer = answers[question.id];
        if (!question.task || (!question.task.when_values.includes(answer) && answer !== "professional_help")) return;
        tasks.push({
          ...question.task,
          needsProfessionalHelp: answer === "professional_help",
          questionId: question.id,
          section: section.title,
        });
      });
    });
    tasks.sort((a, b) => priorityOrder[a.priority] - priorityOrder[b.priority] || a.title.localeCompare(b.title));

    taskList.replaceChildren();
    tasks.forEach((task) => {
      const item = document.createElement("li");
      item.className = "task-item";
      const heading = document.createElement("h3");
      heading.textContent = task.title;
      const meta = document.createElement("p");
      meta.className = `priority ${task.priority}`;
      meta.textContent = `${task.priority} priority · ${task.section}${task.needsProfessionalHelp ? " · professional help flagged" : ""}`;
      const details = document.createElement("p");
      details.textContent = task.details;
      item.append(meta, heading, details);
      const resources = createResourceList(task.resource_ids, resourcesById);
      if (resources) item.append(resources);
      taskList.append(item);
    });

    summary.textContent = tasks.length
      ? `${tasks.length} follow-up task${tasks.length === 1 ? "" : "s"}, ordered by priority.`
      : "No follow-up tasks yet. Items marked ready or not applicable will not appear here.";
  };

  const refresh = () => {
    applyConditionals();
    const answers = getReadinessAnswers();
    saveIfEnabled();
    updateProgress(answers);
    renderTasks(answers);
  };

  form.addEventListener("change", refresh);
  form.addEventListener("input", refresh);
  saveToggle.addEventListener("change", () => {
    if (saveToggle.checked) {
      localStorage.setItem(storageKey, JSON.stringify(getFormState()));
    } else {
      localStorage.removeItem(storageKey);
    }
    updateSaveStatus();
    resetIdleTimers();
  });

  document.getElementById("clear-answers").addEventListener("click", () => {
    clearSession("Session cleared. Inactivity auto-clear is on for unsaved sessions.");
    resetIdleTimers();
  });

  ["pointerdown", "keydown", "input", "change"].forEach((eventName) => {
    document.addEventListener(eventName, resetIdleTimers, { passive: true });
  });

  document.getElementById("print-tasks").addEventListener("click", () => {
    document.body.classList.add("print-take-home-only");
    window.print();
  });
  document.getElementById("print-workbook").addEventListener("click", () => {
    document.body.classList.remove("print-take-home-only");
    window.print();
  });
  window.addEventListener("afterprint", () => document.body.classList.remove("print-take-home-only"));

  fetch("/api/v1/catalog", { credentials: "same-origin" })
    .then((response) => {
      if (!response.ok) throw new Error("Unable to load workbook catalog");
      return response.json();
    })
    .then((value) => {
      catalog = value;
      loadSavedAnswers();
      updateSaveStatus();
      resetIdleTimers();
      refresh();
    })
    .catch(() => {
      summary.textContent = "The take-home task catalog could not be loaded. Your answers remain in this browser.";
      loadSavedAnswers();
      updateSaveStatus();
      resetIdleTimers();
      updateProgress(getReadinessAnswers());
    });
})();
