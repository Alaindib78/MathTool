const helpState = {
  sessionId: null,
  searchRequestId: 0,
};

const helpElements = {
  sessionStatus: document.querySelector("#helpSessionStatus"),
  homeButton: document.querySelector("#helpHomeButton"),
  search: document.querySelector("#helpSearch"),
  tabs: Array.from(document.querySelectorAll(".doc-tab")),
  panels: Array.from(document.querySelectorAll(".doc-panel")),
  resultsPanel: document.querySelector("#resultsPanel"),
  indexPanel: document.querySelector("#indexPanel"),
  categoriesPanel: document.querySelector("#categoriesPanel"),
  examplesPanel: document.querySelector("#examplesPanel"),
  title: document.querySelector("#docTitle"),
  meta: document.querySelector("#docMeta"),
  content: document.querySelector("#docContent"),
};

document.addEventListener("DOMContentLoaded", () => {
  helpElements.homeButton.addEventListener("click", showHome);
  helpElements.search.addEventListener("input", () => {
    runHelpSearch(helpElements.search.value);
  });
  helpElements.content.addEventListener("click", handleContentClick);

  for (const tab of helpElements.tabs) {
    tab.addEventListener("click", () => {
      activatePanel(tab.dataset.panel);
    });
  }

  startHelpPage();
});

async function startHelpPage() {
  try {
    helpState.sessionId = sessionIdFromUrl() || await createHelpSession();
    helpElements.sessionStatus.textContent = `Session ${shortId(helpState.sessionId)}`;

    const [home, index, categories, examples] = await Promise.all([
      helpRequest("/help/home"),
      helpRequest("/help/index"),
      helpRequest("/help/categories"),
      helpRequest("/help/examples"),
    ]);

    renderIndex(index.letters || []);
    renderCategories(categories.categories || []);
    renderExamples(examples.examples || []);
    await runHelpSearch("");
    renderHtmlDocument(home.html);
    helpElements.title.textContent = "Help Home";
    helpElements.meta.textContent = `${home.categories.length} categories`;
  } catch (error) {
    renderError(error);
  }
}

function sessionIdFromUrl() {
  return new URLSearchParams(window.location.search).get("session");
}

async function createHelpSession() {
  const session = await request("/sessions", {
    method: "POST",
  });

  return session.id;
}

async function runHelpSearch(query) {
  if (!helpState.sessionId) {
    return;
  }

  const requestId = helpState.searchRequestId + 1;
  helpState.searchRequestId = requestId;

  try {
    const payload = await helpRequest(
      `/help/search?q=${encodeURIComponent(query)}&limit=80`,
    );

    if (requestId !== helpState.searchRequestId) {
      return;
    }

    renderTopicList(
      helpElements.resultsPanel,
      payload.results || [],
      "No matching topics",
    );
  } catch (error) {
    if (requestId === helpState.searchRequestId) {
      renderPanelMessage(helpElements.resultsPanel, error.message);
    }
  }
}

async function showHome() {
  try {
    const home = await helpRequest("/help/home");

    renderHtmlDocument(home.html);
    helpElements.title.textContent = "Help Home";
    helpElements.meta.textContent = `${home.categories.length} categories`;
  } catch (error) {
    renderError(error);
  }
}

async function openTopic(topicId) {
  try {
    const topic = await helpRequest(
      `/help/topic/${encodeURIComponent(topicId)}?include_html=true`,
    );

    renderHtmlDocument(topic.html);
    helpElements.title.textContent = topic.title;
    helpElements.meta.textContent = [
      topic.category,
      topic.kind,
      topic.is_builtin ? "builtin" : "",
    ].filter(Boolean).join(" / ");
  } catch (error) {
    renderError(error);
  }
}

function renderIndex(letters) {
  const fragment = document.createDocumentFragment();

  for (const group of letters) {
    const details = document.createElement("details");
    details.open = ["A", "B", "C", "P"].includes(group.letter);

    const summary = document.createElement("summary");
    summary.textContent = group.letter;
    details.appendChild(summary);

    details.appendChild(topicButtonList(group.topics || []));
    fragment.appendChild(details);
  }

  helpElements.indexPanel.replaceChildren(fragment);
}

function renderCategories(categories) {
  const fragment = document.createDocumentFragment();

  for (const group of categories) {
    const details = document.createElement("details");
    details.open = ["Plotting", "Language Basics"].includes(group.category);

    const summary = document.createElement("summary");
    summary.textContent = `${group.category} (${group.count})`;
    details.appendChild(summary);

    details.appendChild(topicButtonList(group.topics || []));
    fragment.appendChild(details);
  }

  helpElements.categoriesPanel.replaceChildren(fragment);
}

function renderExamples(examples) {
  if (!examples.length) {
    renderPanelMessage(helpElements.examplesPanel, "No examples");
    return;
  }

  const fragment = document.createDocumentFragment();

  for (const example of examples) {
    const button = topicButton(example.topic);
    button.appendChild(countBadge((example.items || []).length));
    fragment.appendChild(button);
  }

  helpElements.examplesPanel.replaceChildren(fragment);
}

function renderTopicList(container, topics, emptyMessage) {
  if (!topics.length) {
    renderPanelMessage(container, emptyMessage);
    return;
  }

  container.replaceChildren(topicButtonList(topics));
}

function topicButtonList(topics) {
  const list = document.createElement("div");
  list.className = "doc-list";

  for (const topic of topics) {
    list.appendChild(topicButton(topic));
  }

  return list;
}

function topicButton(topic) {
  const button = document.createElement("button");
  button.className = "doc-topic";
  button.type = "button";
  button.dataset.topic = topic.id;
  button.addEventListener("click", () => openTopic(topic.id));

  const title = document.createElement("span");
  title.className = "doc-topic-title";
  title.textContent = topic.title || topic.id;

  const summary = document.createElement("span");
  summary.className = "doc-topic-summary";
  summary.textContent = topic.summary || topic.category || "";

  button.append(title, summary);
  return button;
}

function countBadge(count) {
  const badge = document.createElement("span");
  badge.className = "doc-count";
  badge.textContent = String(count);
  return badge;
}

function renderHtmlDocument(html) {
  const parsed = new DOMParser().parseFromString(html || "", "text/html");
  const nodes = Array.from(parsed.body.childNodes).map((node) => {
    return document.importNode(node, true);
  });

  helpElements.content.replaceChildren(...nodes);
}

function handleContentClick(event) {
  const link = event.target.closest("a");

  if (!link) {
    return;
  }

  const href = link.getAttribute("href") || "";

  if (href.startsWith("topic:")) {
    event.preventDefault();
    openTopic(href.slice("topic:".length));
    return;
  }

  if (href.startsWith("category:")) {
    event.preventDefault();
    const category = href.slice("category:".length);
    activatePanel("categoriesPanel");
    helpElements.search.value = category;
    runHelpSearch(category);
    return;
  }

  if (href.startsWith("http://") || href.startsWith("https://")) {
    event.preventDefault();
    window.open(href, "_blank", "noopener");
  }
}

function activatePanel(panelId) {
  for (const tab of helpElements.tabs) {
    tab.classList.toggle("active", tab.dataset.panel === panelId);
  }

  for (const panel of helpElements.panels) {
    panel.classList.toggle("active", panel.id === panelId);
  }
}

function renderPanelMessage(container, message) {
  const empty = document.createElement("div");
  empty.className = "empty-state";
  empty.textContent = message;
  container.replaceChildren(empty);
}

function renderError(error) {
  helpElements.title.textContent = "Help";
  helpElements.meta.textContent = "";
  const message = document.createElement("div");
  message.className = "empty-state error-text";
  message.textContent = `Error: ${error.message}`;
  helpElements.content.replaceChildren(message);
}

async function helpRequest(path, options = {}) {
  return request(`/sessions/${helpState.sessionId}${path}`, options);
}

async function request(path, options = {}) {
  const response = await fetch(path, {
    headers: {
      "Content-Type": "application/json",
      ...(options.headers || {}),
    },
    ...options,
  });

  const contentType = response.headers.get("content-type") || "";
  const body = contentType.includes("application/json")
    ? await response.json()
    : await response.text();

  if (!response.ok) {
    const detail = typeof body === "object" && body.detail
      ? body.detail
      : response.statusText;
    throw new Error(detail);
  }

  return body;
}

function shortId(value) {
  return value ? value.slice(0, 8) : "";
}
