/**
 * app.js — Inicialização da Aplicação, Event Listeners e Ações Globais
 */

function populateKpis() {
  var kpis = AppState.getKpis();

  var elSessions = document.getElementById("kpiTotalSessions");
  var elRwRatio = document.getElementById("kpiRwRatio");
  var elCompactRate = document.getElementById("kpiCompactRate");
  var elErrorRate = document.getElementById("kpiErrorRate");
  var elPromptsPerSession = document.getElementById("kpiPromptsPerSession");

  if (elSessions) elSessions.innerText = kpis.totalSessions || 0;
  if (elRwRatio) elRwRatio.innerText = (kpis.readWriteRatio || 1.0) + " : 1";
  if (elCompactRate) elCompactRate.innerText = (kpis.compactRate || 0.0) + "%";
  if (elErrorRate) elErrorRate.innerText = (kpis.errorRatePct || 0.0) + "%";
  if (elPromptsPerSession) elPromptsPerSession.innerText = kpis.promptsPerSession || 0.0;

  // Secondary pills
  var elTokensSaved = document.getElementById("pillTokensSaved");
  var elDollarsSaved = document.getElementById("pillDollarsSaved");
  var elTimeSaved = document.getElementById("pillTimeSaved");

  if (elTokensSaved) elTokensSaved.innerText = (kpis.tokensSaved || 0).toLocaleString();
  if (elDollarsSaved) elDollarsSaved.innerText = "$" + (kpis.dollarsSaved || 0).toFixed(2);
  if (elTimeSaved) elTimeSaved.innerText = (kpis.timeSavedMin || 0) + " min";
}

function populateProjectSelect() {
  var select = document.getElementById("projectSelect");
  if (!select) return;

  var projects = AppState.getProjects();
  var html = '<option value="all">Todos os Projetos (' + projects.length + ')</option>';

  projects.forEach(function(p) {
    html += '<option value="' + p.projectDir + '">' + p.projectName + ' (' + p.sessions + ' sessões)</option>';
  });

  select.innerHTML = html;
  select.addEventListener("change", function(e) {
    AppState.activeProject = e.target.value;
    AppState.tablePage = 1;
    renderSessionsTable();
  });
}

function switchView(viewName) {
  AppState.activeNav = viewName;

  // Atualiza sidebar links
  var links = document.querySelectorAll(".nav-link");
  links.forEach(function(l) {
    if (l.getAttribute("data-view") === viewName) {
      l.classList.add("active");
    } else {
      l.classList.remove("active");
    }
  });

  // Atualiza views containers
  var views = document.querySelectorAll(".app-view");
  views.forEach(function(v) {
    if (v.id === "view-" + viewName) {
      v.classList.add("active");
    } else {
      v.classList.remove("active");
    }
  });

  // Renderizadores específicos sob demanda
  if (viewName === "dashboard") {
    renderWhenYouCode();
    renderAgentInvocations();
    renderActivityChart();
    renderToolUsage();
    renderMcpTools();
    renderInsightCards();
  } else if (viewName === "knowledge") {
    renderKnowledgeBase();
  } else if (viewName === "sessions") {
    renderSessionsTable();
    if (activeSessionsSubTab === "decisions") {
      renderDecisionsStream();
    }
  } else if (viewName === "search") {
    renderSearchResults();
  } else if (viewName === "executive") {
    renderExecutiveView();
  }

  window.scrollTo({ top: 0, behavior: "smooth" });
}

function exportInsightsJson() {
  var dataStr = "data:text/json;charset=utf-8," + encodeURIComponent(JSON.stringify(AppState.data, null, 2));
  var downloadAnchor = document.createElement("a");
  downloadAnchor.setAttribute("href", dataStr);
  downloadAnchor.setAttribute("download", "context-mode-insight.json");
  document.body.appendChild(downloadAnchor);
  downloadAnchor.click();
  downloadAnchor.remove();
}

document.addEventListener("DOMContentLoaded", function() {
  populateKpis();
  populateProjectSelect();
  renderWhenYouCode();
  renderAgentInvocations();
  renderActivityChart();
  renderToolUsage();
  renderMcpTools();
  renderInsightCards();
  renderSessionsTable();
  renderKnowledgeBase();
  renderDecisionsStream();
  renderExecutiveView();

  // Fecha modals com tecla ESC
  document.addEventListener("keydown", function(e) {
    if (e.key === "Escape") {
      closeSourceDetailModal();
      closeSessionEventsModal();
    }
  });
});

