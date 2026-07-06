const form = document.querySelector("#assistantForm");
const input = document.querySelector("#messageInput");
const sendButton = document.querySelector("#sendButton");
const conversation = document.querySelector("#conversation");
const sessionLabel = document.querySelector("#sessionId");
const quickActions = document.querySelectorAll("[data-prompt]");

let sessionId = window.localStorage.getItem("citypulse_session_id");

if (sessionId) {
  sessionLabel.textContent = sessionId;
}

quickActions.forEach((button) => {
  button.addEventListener("click", () => {
    input.value = button.dataset.prompt;
    input.focus();
  });
});

form.addEventListener("submit", async (event) => {
  event.preventDefault();

  const message = input.value.trim();
  if (!message) {
    return;
  }

  appendUserMessage(message);
  input.value = "";
  setLoading(true);

  try {
    const payload = { message };
    if (sessionId) {
      payload.session_id = sessionId;
    }

    const response = await fetch("/assistant", {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
      },
      body: JSON.stringify(payload),
    });

    const data = await response.json();
    if (!response.ok) {
      throw new Error(data.detail || "Assistant request failed.");
    }

    sessionId = data.session_id;
    window.localStorage.setItem("citypulse_session_id", sessionId);
    sessionLabel.textContent = sessionId;
    appendAssistantResponse(data);
  } catch (error) {
    appendErrorMessage(error.message);
  } finally {
    setLoading(false);
  }
});

function setLoading(isLoading) {
  sendButton.disabled = isLoading;
  sendButton.textContent = isLoading ? "Sending" : "Send";
}

function appendUserMessage(message) {
  const article = createMessage("You", message, "user-message");
  conversation.appendChild(article);
  scrollConversation();
}

function appendAssistantResponse(data) {
  const article = document.createElement("article");
  article.className = "message assistant-message";

  const label = document.createElement("div");
  label.className = "message-label";
  label.textContent = `CityPulse · ${data.intent} · ${Math.round(data.confidence * 100)}%`;

  const body = document.createElement("div");
  body.className = "message-body";

  const summary = document.createElement("div");
  summary.textContent = getPrimaryText(data);
  body.appendChild(summary);

  const tags = buildTags(data);
  if (tags.length) {
    body.appendChild(renderTags(tags));
  }

  const gridItems = buildResultItems(data);
  if (gridItems.length) {
    body.appendChild(renderResultGrid(gridItems));
  }

  article.appendChild(label);
  article.appendChild(body);
  conversation.appendChild(article);
  scrollConversation();
}

function appendErrorMessage(message) {
  const article = createMessage("CityPulse", message, "assistant-message");
  article.querySelector(".message-body").classList.add("error");
  conversation.appendChild(article);
  scrollConversation();
}

function createMessage(labelText, message, className) {
  const article = document.createElement("article");
  article.className = `message ${className}`;

  const label = document.createElement("div");
  label.className = "message-label";
  label.textContent = labelText;

  const body = document.createElement("div");
  body.className = "message-body";
  body.textContent = message;

  article.appendChild(label);
  article.appendChild(body);

  return article;
}

function getPrimaryText(data) {
  const result = data.result || {};
  if (typeof result.answer === "string") {
    return result.answer;
  }

  if (typeof result.summary === "string") {
    return result.summary;
  }

  return "The request was processed successfully.";
}

function buildTags(data) {
  const result = data.result || {};
  const tags = [`Intent: ${data.intent}`];

  if (Array.isArray(result.sources)) {
    result.sources.forEach((source) => tags.push(`Source: ${source}`));
  }

  if (result.routing) {
    tags.push(`SLA: ${result.routing.sla}`);
    tags.push(`Officer: ${result.routing.officer}`);
    if (result.routing.escalation_required) {
      tags.push("Escalation required");
    }
  }

  return tags;
}

function buildResultItems(data) {
  const result = data.result || {};
  const items = [];

  if (result.category) {
    items.push(["Category", result.category]);
  }
  if (result.department) {
    items.push(["Department", result.department]);
  }
  if (result.severity) {
    items.push(["Severity", result.severity]);
  }
  if (result.priority) {
    items.push(["Priority", result.priority]);
  }
  if (result.location) {
    items.push(["Location", result.location]);
  }
  if (result.ward) {
    items.push(["Ward", result.ward]);
  }
  if (result.routing) {
    items.push(["Routing department", result.routing.department]);
    items.push(["Escalation", result.routing.escalation_level]);
    items.push(["Routing reason", result.routing.reason]);
  }

  return items;
}

function renderTags(tags) {
  const row = document.createElement("div");
  row.className = "tag-row";

  tags.forEach((tagText) => {
    const tag = document.createElement("span");
    tag.className = "tag";
    if (tagText.includes("Escalation")) {
      tag.classList.add("danger");
    }
    if (tagText.startsWith("SLA")) {
      tag.classList.add("warning");
    }
    tag.textContent = tagText;
    row.appendChild(tag);
  });

  return row;
}

function renderResultGrid(items) {
  const grid = document.createElement("div");
  grid.className = "result-grid";

  items.forEach(([labelText, value]) => {
    const item = document.createElement("div");
    item.className = "result-item";

    const label = document.createElement("span");
    label.textContent = labelText;

    const strong = document.createElement("strong");
    strong.textContent = value;

    item.appendChild(label);
    item.appendChild(strong);
    grid.appendChild(item);
  });

  return grid;
}

function scrollConversation() {
  conversation.scrollTop = conversation.scrollHeight;
}
