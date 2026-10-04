(() => {
  const storageKey = "goodtogo.private.answers.v1";
  const form = document.getElementById("private-workbook");
  const saveToggle = document.getElementById("device-save");
  const taskList = document.getElementById("task-list");
  const summary = document.getElementById("take-home-summary");
  const answeredCount = document.getElementById("answered-count");
  const questionCount = document.getElementById("question-count");
  const progressBar = document.getElementById("progress-bar");
  let catalog;

  const getAnswers = () => Object.fromEntries(new FormData(form).entries());

  const loadSavedAnswers = () => {
    const saved = localStorage.getItem(storageKey);
    if (!saved) return;
    try {
      const answers = JSON.parse(saved);
      Object.entries(answers).forEach(([name, value]) => {
        const input = form.querySelector(`input[name="${CSS.escape(name)}"][value="${CSS.escape(value)}"]`);
        if (input) input.checked = true;
      });
      saveToggle.checked = true;
    } catch {
      localStorage.removeItem(storageKey);
    }
  };

  const saveIfEnabled = (answers) => {
    if (saveToggle.checked) localStorage.setItem(storageKey, JSON.stringify(answers));
  };

  const updateProgress = (answers) => {
    const total = form.querySelectorAll(".question-card").length;
    const answered = Object.keys(answers).length;
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
        if (!question.task || !question.task.when_values.includes(answers[question.id])) return;
        tasks.push({ ...question.task, questionId: question.id, section: section.title });
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
      meta.textContent = `${task.priority} priority · ${task.section}`;
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
    const answers = getAnswers();
    saveIfEnabled(answers);
    updateProgress(answers);
    renderTasks(answers);
  };

  form.addEventListener("change", refresh);
  saveToggle.addEventListener("change", () => {
    if (saveToggle.checked) {
      localStorage.setItem(storageKey, JSON.stringify(getAnswers()));
    } else {
      localStorage.removeItem(storageKey);
    }
  });

  document.getElementById("clear-answers").addEventListener("click", () => {
    form.reset();
    saveToggle.checked = false;
    localStorage.removeItem(storageKey);
    refresh();
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
      refresh();
    })
    .catch(() => {
      summary.textContent = "The take-home task catalog could not be loaded. Your answers remain in this browser.";
      loadSavedAnswers();
      updateProgress(getAnswers());
    });
})();
