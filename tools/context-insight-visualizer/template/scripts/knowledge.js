/**
 * knowledge.js — Gestão da Base de Conhecimento e Visualização de Chunks
 */

function getDateRecencyGroup(dateStr) {
  if (!dateStr) return "Anteriores";
  try {
    var now = new Date();
    var d = new Date(dateStr.replace(" ", "T"));
    var diffHours = (now - d) / (1000 * 60 * 60);
    if (diffHours < 24) return "Hoje";
    if (diffHours < 48) return "Ontem";
    if (diffHours < 168) return "Esta Semana";
    return "Anteriores";
  } catch (e) {
    return "Anteriores";
  }
}

function renderKnowledgeBase() {
  var container = document.getElementById("knowledgeSourcesContainer");
  if (!container) return;

  var sources = AppState.getSources();
  var chunksBySource = AppState.getChunksBySource();

  // KPIs
  var totalSources = sources.length;
  var totalChunks = sources.reduce(function(acc, s) { return acc + ((s.chunkCount || 0) || 0); }, 0);
  var totalCodeChunks = sources.reduce(function(acc, s) { return acc + ((s.codeChunkCount || 0) || 0); }, 0);
  var codePct = totalChunks > 0 ? Math.round((totalCodeChunks / totalChunks) * 100) : 0;
  var freshest = sources[0] ? sources[0].indexedAt.slice(0, 10) : "--";

  var elTotSources = document.getElementById("kbStatTotalSources");
  var elTotChunks = document.getElementById("kbStatTotalChunks");
  var elCodePct = document.getElementById("kbStatCodePct");
  var elFreshest = document.getElementById("kbStatFreshestDate");

  if (elTotSources) elTotSources.innerText = totalSources;
  if (elTotChunks) elTotChunks.innerText = totalChunks.toLocaleString();
  if (elCodePct) elCodePct.innerText = codePct + "%";
  if (elFreshest) elFreshest.innerText = freshest;

  if (sources.length === 0) {
    container.innerHTML = '<div style="padding: 32px; text-align: center; color: var(--md-sys-color-on-surface-variant);">' +
      '<span class="material-symbols-outlined" style="font-size: 40px; opacity: 0.5; margin-bottom: 8px;">folder_off</span>' +
      '<p>Nenhuma fonte de conhecimento indexada localmente.</p>' +
      '</div>';
    return;
  }

  // Agrupamento por recência
  var groups = { "Hoje": [], "Ontem": [], "Esta Semana": [], "Anteriores": [] };
  sources.forEach(function(s) {
    var g = getDateRecencyGroup(s.indexedAt);
    if (!groups[g]) groups[g] = [];
    groups[g].push(s);
  });

  var html = "";
  ["Hoje", "Ontem", "Esta Semana", "Anteriores"].forEach(function(grpName) {
    var grpItems = groups[grpName];
    if (grpItems && grpItems.length > 0) {
      html += '<div class="date-group-title">' +
                '<span class="material-symbols-outlined" style="font-size:16px;">calendar_today</span>' +
                '<span>' + grpName + ' (' + grpItems.length + ')</span>' +
              '</div>' +
              '<div class="sources-grid">';

      grpItems.forEach(function(s) {
        var codeChunksCount = (s.codeChunkCount || 0) || 0;
        var totalC = (s.chunkCount || 0) || 0;
        var codeRatio = totalC > 0 ? Math.round((codeChunksCount / totalC) * 100) : 0;

        html += '<div class="source-card" onclick="openSourceDetailModal(' + s.id + ')">' +
                  '<div class="source-card-header">' +
                    '<h4 class="source-label">' + (s.label || "Fonte sem título") + '</h4>' +
                    '<span class="mat-badge-tag">' + (s.dbHash ? s.dbHash.slice(0, 8) : "db") + '</span>' +
                  '</div>' +
                  '<div class="source-path">' + (s.filePath || "-") + '</div>' +
                  '<div class="source-stats">' +
                    '<span><strong style="color:#f8fafc;">' + totalC + '</strong> chunks</span>' +
                    '<span><strong style="color:var(--md-sys-color-cyan);">' + codeRatio + '%</strong> código</span>' +
                    '<span style="margin-left:auto;">' + (s.indexedAt ? s.indexedAt.slice(0, 16) : "") + '</span>' +
                  '</div>' +
                '</div>';
      });

      html += '</div>';
    }
  });

  container.innerHTML = html;
}

function openSourceDetailModal(sourceId) {
  var modal = document.getElementById("sourceDetailModal");
  var titleEl = document.getElementById("sourceModalTitle");
  var bodyEl = document.getElementById("sourceModalBody");
  if (!modal || !bodyEl) return;

  var sources = AppState.getSources();
  var chunksBySource = AppState.getChunksBySource();

  var s = sources.find(function(item) { return item.id === sourceId; });
  if (titleEl) titleEl.innerText = s ? s.label : "Detalhes da Fonte";

  var chunks = chunksBySource[sourceId] || [];

  if (chunks.length === 0) {
    bodyEl.innerHTML = '<p style="color:var(--md-sys-color-on-surface-variant);text-align:center;padding:24px;">Nenhum chunk disponível para esta fonte.</p>';
  } else {
    var html = '<p style="font-size:12px;color:var(--md-sys-color-on-surface-variant);margin-bottom:12px;">' +
               'Exibindo ' + chunks.length + ' chunks indexados:</p>';

    chunks.forEach(function(c, i) {
      var isCode = c.contentType === "code";
      html += '<div style="background:var(--md-sys-color-surface-container-high);border:1px solid var(--md-sys-color-outline-variant);border-radius:var(--radius-sm);padding:14px;margin-bottom:10px;">' +
                '<div style="display:flex;justify-content:space-between;align-items:center;margin-bottom:6px;">' +
                  '<span style="font-size:12px;font-weight:600;color:#f8fafc;">#' + (i + 1) + ' — ' + (c.title || "Untitled") + '</span>' +
                  '<span class="mat-badge-tag" style="background:' + (isCode ? 'rgba(6,182,212,0.2)' : 'rgba(208,188,255,0.2)') + ';color:' + (isCode ? '#06b6d4' : '#d0bcff') + ';">' + (c.contentType || "text") + ' (' + c.charLen + ' chars)</span>' +
                '</div>' +
                '<pre style="font-family:var(--font-family-mono);font-size:11px;color:var(--md-sys-color-on-surface-variant);background:rgba(0,0,0,0.3);padding:10px;border-radius:4px;overflow-x:auto;white-space:pre-wrap;">' +
                  escapeHtml(c.preview || "(Vazio)") +
                '</pre>' +
              '</div>';
    });
    bodyEl.innerHTML = html;
  }

  modal.classList.add("open");
}

function closeSourceDetailModal() {
  var modal = document.getElementById("sourceDetailModal");
  if (modal) modal.classList.remove("open");
}

function escapeHtml(str) {
  return String(str || "").replace(/&/g, "&amp;").replace(/</g, "&lt;").replace(/>/g, "&gt;");
}

