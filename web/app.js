const state = {
  sessionId: null,
  busy: false,
  plots: [],
};

const elements = {
  sessionStatus: document.querySelector("#sessionStatus"),
  cwdText: document.querySelector("#cwdText"),
  sourceEditor: document.querySelector("#sourceEditor"),
  runButton: document.querySelector("#runButton"),
  helpButton: document.querySelector("#helpButton"),
  newSessionButton: document.querySelector("#newSessionButton"),
  clearWorkspaceButton: document.querySelector("#clearWorkspaceButton"),
  clearConsoleButton: document.querySelector("#clearConsoleButton"),
  commandInput: document.querySelector("#commandInput"),
  commandButton: document.querySelector("#commandButton"),
  consoleOutput: document.querySelector("#consoleOutput"),
  workspaceBody: document.querySelector("#workspaceBody"),
  workspaceCount: document.querySelector("#workspaceCount"),
  plotPanel: document.querySelector("#plotPanel"),
  plotCount: document.querySelector("#plotCount"),
};

document.addEventListener("DOMContentLoaded", () => {
  elements.runButton.addEventListener("click", runSource);
  elements.helpButton.addEventListener("click", openHelpPage);
  elements.commandButton.addEventListener("click", runCommand);
  elements.newSessionButton.addEventListener("click", createSession);
  elements.clearWorkspaceButton.addEventListener("click", clearWorkspace);
  elements.clearConsoleButton.addEventListener("click", clearConsole);
  elements.commandInput.addEventListener("keydown", (event) => {
    if (event.key === "Enter") {
      runCommand();
    }
  });

  createSession();
});

function openHelpPage() {
  const target = state.sessionId
    ? `/help?session=${encodeURIComponent(state.sessionId)}`
    : "/help";

  window.open(target, "_blank", "noopener");
}

async function createSession() {
  setBusy(true);

  try {
    const session = await request("/sessions", {
      method: "POST",
    });

    state.sessionId = session.id;
    state.plots = [];
    elements.sessionStatus.textContent = `Session ${shortId(session.id)}`;
    elements.cwdText.textContent = session.cwd;
    clearConsole();
    renderWorkspace({ variables: [] });
    renderPlots([]);
    appendConsole(`Session created: ${session.id}`);
  } catch (error) {
    showError(error);
  } finally {
    setBusy(false);
  }
}

async function runSource() {
  if (!state.sessionId) {
    return;
  }

  setBusy(true);
  appendConsole(">> run");

  try {
    const payload = await request(`/sessions/${state.sessionId}/execute`, {
      method: "POST",
      body: JSON.stringify({
        source: elements.sourceEditor.value,
        include_workspace: true,
        include_plots: true,
      }),
    });

    applyExecutionPayload(payload);
  } catch (error) {
    showError(error);
  } finally {
    setBusy(false);
  }
}

async function runCommand() {
  if (!state.sessionId) {
    return;
  }

  const source = elements.commandInput.value.trim();

  if (!source) {
    return;
  }

  setBusy(true);
  appendConsole(`>> ${source}`);

  try {
    const payload = await request(`/sessions/${state.sessionId}/command`, {
      method: "POST",
      body: JSON.stringify({
        source,
        include_workspace: true,
        include_plots: true,
      }),
    });

    if (payload.clear_output) {
      clearConsole();
    }

    applyExecutionPayload(payload);
  } catch (error) {
    showError(error);
  } finally {
    setBusy(false);
  }
}

async function clearWorkspace() {
  if (!state.sessionId) {
    return;
  }

  setBusy(true);

  try {
    const workspace = await request(
      `/sessions/${state.sessionId}/workspace/clear`,
      {
        method: "POST",
      },
    );

    renderWorkspace(workspace);
    appendConsole("Workspace cleared");
  } catch (error) {
    showError(error);
  } finally {
    setBusy(false);
  }
}

function applyExecutionPayload(payload) {
  for (const line of payload.output || []) {
    appendConsole(line.replace(/\n$/, ""));
  }

  if (payload.value && payload.value.type !== "none") {
    appendConsole(formatValue(payload.value));
  }

  if (payload.workspace) {
    renderWorkspace(payload.workspace);
  }

  if (payload.plots) {
    state.plots = payload.plots;
    renderPlots(state.plots);
  }
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

function renderWorkspace(workspace) {
  const variables = workspace.variables || [];

  elements.workspaceCount.textContent =
    `${variables.length} ${variables.length === 1 ? "variable" : "variables"}`;

  elements.workspaceBody.replaceChildren(
    ...variables.map((variable) => {
      const row = document.createElement("tr");

      row.appendChild(tableCell(variable.name));
      row.appendChild(tableCell(typeLabel(variable.value)));
      row.appendChild(tableCell(variable.preview || formatValue(variable.value)));

      return row;
    }),
  );
}

function renderPlots(plots) {
  elements.plotCount.textContent =
    `${plots.length} ${plots.length === 1 ? "plot" : "plots"}`;

  if (!plots.length) {
    const empty = document.createElement("div");
    empty.className = "empty-state";
    empty.textContent = "No plots";
    elements.plotPanel.replaceChildren(empty);
    return;
  }

  elements.plotPanel.replaceChildren(
    ...plots.map((plot) => {
      const frame = document.createElement("div");
      frame.className = "plot-frame";
      frame.appendChild(renderPlot(plot));
      return frame;
    }),
  );
}

function renderPlot(plot) {
  const trace = (plot.data || [])[0] || {};
  const xAxisType = plot.layout?.xaxis?.type === "log" ? "log" : "linear";
  const pointValues = pairedNumericValues(
    trace.x || [],
    trace.y || [],
    xAxisType,
  );
  const xValues = pointValues.map((point) => point.xPlot);
  const yValues = pointValues.map((point) => point.y);

  if (!pointValues.length) {
    const empty = document.createElement("div");
    empty.className = "empty-state";
    empty.textContent = "Plot data unavailable";
    return empty;
  }

  const width = 720;
  const height = 360;
  const margin = {
    top: 42,
    right: 24,
    bottom: 52,
    left: 62,
  };
  const plotWidth = width - margin.left - margin.right;
  const plotHeight = height - margin.top - margin.bottom;
  const xDomain = paddedDomain(xValues);
  const yDomain = paddedDomain(yValues);
  const points = pointValues.map((point) => {
    const x = point.xPlot;
    const y = point.y;
    return [
      margin.left + ((x - xDomain.min) / (xDomain.max - xDomain.min)) * plotWidth,
      margin.top + plotHeight - ((y - yDomain.min) / (yDomain.max - yDomain.min)) * plotHeight,
    ];
  });
  const path = points
    .map((point, index) => `${index === 0 ? "M" : "L"} ${point[0].toFixed(2)} ${point[1].toFixed(2)}`)
    .join(" ");
  const title = plot.layout?.title?.text || "";
  const xLabel = plot.layout?.xaxis?.title?.text || "";
  const yLabel = plot.layout?.yaxis?.title?.text || "";
  const showGrid = Boolean(plot.layout?.xaxis?.showgrid);

  const svg = svgElement("svg", {
    viewBox: `0 0 ${width} ${height}`,
    role: "img",
  });
  const background = svgElement("rect", {
    x: 0,
    y: 0,
    width,
    height,
    fill: "#171b18",
  });
  svg.appendChild(background);

  if (showGrid) {
    for (let index = 1; index < 5; index += 1) {
      const x = margin.left + (plotWidth / 5) * index;
      const y = margin.top + (plotHeight / 5) * index;
      svg.appendChild(svgElement("line", {
        x1: x,
        y1: margin.top,
        x2: x,
        y2: margin.top + plotHeight,
        stroke: "#2d352f",
      }));
      svg.appendChild(svgElement("line", {
        x1: margin.left,
        y1: y,
        x2: margin.left + plotWidth,
        y2: y,
        stroke: "#2d352f",
      }));
    }
  }

  svg.appendChild(svgElement("line", {
    x1: margin.left,
    y1: margin.top + plotHeight,
    x2: margin.left + plotWidth,
    y2: margin.top + plotHeight,
    stroke: "#8c9a90",
  }));
  svg.appendChild(svgElement("line", {
    x1: margin.left,
    y1: margin.top,
    x2: margin.left,
    y2: margin.top + plotHeight,
    stroke: "#8c9a90",
  }));
  svg.appendChild(svgElement("path", {
    d: path,
    fill: "none",
    stroke: "var(--line)",
    "stroke-width": 2.5,
  }));

  for (const point of points) {
    svg.appendChild(svgElement("circle", {
      cx: point[0],
      cy: point[1],
      r: 3,
      fill: "#d5f7d6",
    }));
  }

  svg.appendChild(svgText(title, width / 2, 24, "middle", "14"));
  svg.appendChild(svgText(xLabel, margin.left + plotWidth / 2, height - 16, "middle", "12"));
  const yAxisLabel = svgText(yLabel, 18, margin.top + plotHeight / 2, "middle", "12");
  yAxisLabel.setAttribute("transform", `rotate(-90 18 ${margin.top + plotHeight / 2})`);
  svg.appendChild(yAxisLabel);
  svg.appendChild(svgText(formatAxisTick(xDomain.min, xAxisType), margin.left, height - 34, "middle", "11"));
  svg.appendChild(svgText(formatAxisTick(xDomain.max, xAxisType), margin.left + plotWidth, height - 34, "middle", "11"));
  svg.appendChild(svgText(formatTick(yDomain.min), margin.left - 10, margin.top + plotHeight + 4, "end", "11"));
  svg.appendChild(svgText(formatTick(yDomain.max), margin.left - 10, margin.top + 4, "end", "11"));

  return svg;
}

function formatValue(value) {
  if (!value) {
    return "";
  }

  switch (value.type) {
    case "none":
      return "";
    case "bool":
    case "string":
      return String(value.value);
    case "number":
      return formatNumberValue(value.value);
    case "complex":
      return `${formatNumberValue(value.real)} ${value.imag >= 0 ? "+" : "-"} ${formatNumberValue(Math.abs(value.imag))}i`;
    case "array":
      return formatArray(value);
    case "symbolic":
      return value.expression;
    case "list":
    case "tuple":
      return `[${(value.items || []).map(formatValue).join(", ")}]`;
    case "struct":
      return Object.entries(value.fields || {})
        .map(([key, fieldValue]) => `${key}: ${formatValue(fieldValue)}`)
        .join("\n");
    default:
      return value.repr || JSON.stringify(value);
  }
}

function formatArray(value) {
  const shape = (value.shape || []).join("x");
  const data = JSON.stringify(value.data);
  return shape ? `${shape} ${value.dtype}\n${data}` : data;
}

function formatNumberValue(value) {
  if (typeof value === "number") {
    return Number.isInteger(value) ? String(value) : value.toPrecision(8).replace(/\.?0+$/, "");
  }

  if (value && value.special) {
    return value.special;
  }

  return String(value);
}

function typeLabel(value) {
  if (!value) {
    return "unknown";
  }

  if (value.type === "array") {
    return `${value.dtype} ${value.shape.join("x")}`;
  }

  if (value.type === "number") {
    return value.kind;
  }

  if (value.type === "symbolic") {
    return value.kind;
  }

  return value.type;
}

function pairedNumericValues(xValues, yValues, xAxisType) {
  const length = Math.min(xValues.length, yValues.length);
  const points = [];

  for (let index = 0; index < length; index += 1) {
    const x = numericValue(xValues[index]);
    const y = numericValue(yValues[index]);

    if (!Number.isFinite(x) || !Number.isFinite(y)) {
      continue;
    }

    if (xAxisType === "log" && x <= 0) {
      continue;
    }

    points.push({
      xPlot: xAxisType === "log" ? Math.log10(x) : x,
      y,
    });
  }

  return points;
}

function numericValue(value) {
  if (typeof value === "number") {
    return value;
  }

  if (value && typeof value.real === "number" && value.imag === 0) {
    return value.real;
  }

  return Number.NaN;
}

function paddedDomain(values) {
  let min = Math.min(...values);
  let max = Math.max(...values);

  if (min === max) {
    min -= 1;
    max += 1;
  }

  const padding = (max - min) * 0.05;

  return {
    min: min - padding,
    max: max + padding,
  };
}

function formatTick(value) {
  return Number(value).toPrecision(4).replace(/\.?0+$/, "");
}

function formatAxisTick(value, axisType) {
  if (axisType === "log") {
    return formatTick(10 ** value);
  }

  return formatTick(value);
}

function svgElement(name, attributes) {
  const element = document.createElementNS("http://www.w3.org/2000/svg", name);

  for (const [key, value] of Object.entries(attributes)) {
    element.setAttribute(key, value);
  }

  return element;
}

function svgText(content, x, y, anchor, size) {
  const text = svgElement("text", {
    x,
    y,
    "text-anchor": anchor,
    fill: "#d6dfd8",
    "font-size": size,
    "font-family": "Segoe UI, Arial, sans-serif",
  });
  text.textContent = content;
  return text;
}

function tableCell(text) {
  const cell = document.createElement("td");
  cell.textContent = text;
  return cell;
}

function appendConsole(text) {
  const current = elements.consoleOutput.textContent;
  elements.consoleOutput.textContent = current
    ? `${current}\n${text}`
    : text;
  elements.consoleOutput.scrollTop = elements.consoleOutput.scrollHeight;
}

function clearConsole() {
  elements.consoleOutput.textContent = "";
}

function showError(error) {
  appendConsole(`Error: ${error.message}`);
}

function setBusy(isBusy) {
  state.busy = isBusy;

  for (const element of [
    elements.runButton,
    elements.commandButton,
    elements.newSessionButton,
    elements.clearWorkspaceButton,
  ]) {
    element.disabled = isBusy;
  }

  elements.sessionStatus.classList.toggle("error-text", false);
}

function shortId(value) {
  return value ? value.slice(0, 8) : "";
}
