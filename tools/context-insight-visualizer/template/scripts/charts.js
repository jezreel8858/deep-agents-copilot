/**
 * charts.js — Renderização de Gráficos SVG e Heatmap de Horário
 */

function formatBytesDisplay(bytes) {
  if (!bytes || bytes === 0) return "0 B";
  if (bytes >= 1024 * 1024) return (bytes / (1024 * 1024)).toFixed(1) + " MB";
  if (bytes >= 1024) return (bytes / 1024).toFixed(1) + " KB";
  return bytes + " B";
}

function renderWhenYouCode() {
  var container = document.getElementById("whenYouCodeBars");
  if (!container) return;

  var hourly = AppState.getHourlyPattern();
  var peakHourObj = null;
  var maxCount = 0;
  var activeHoursCount = 0;

  for (var i = 0; i < hourly.length; i++) {
    var c = hourly[i].count;
    if (c > 0) activeHoursCount++;
    if (c > maxCount) {
      maxCount = c;
      peakHourObj = hourly[i];
    }
  }

  // Atualiza mini-stats
  var elPeakHour = document.getElementById("statPeakHour");
  var elPeakEvents = document.getElementById("statPeakEvents");
  var elActiveHours = document.getElementById("statActiveHours");

  if (elPeakHour) elPeakHour.innerText = peakHourObj ? (String(peakHourObj.hour).padStart(2, "0") + ":00") : "--";
  if (elPeakEvents) elPeakEvents.innerText = peakHourObj ? peakHourObj.count : "0";
  if (elActiveHours) elActiveHours.innerText = activeHoursCount;

  // Monta as 24 barras
  var html = "";
  for (var h = 0; h < 24; h++) {
    var hData = hourly.find(function(item) { return item.hour === h; });
    var count = hData ? hData.count : 0;
    var pct = maxCount > 0 ? (count / maxCount) : 0;
    var heightPx = Math.max(Math.round(pct * 65), count > 0 ? 4 : 2);
    var opacity = count > 0 ? (0.25 + 0.75 * pct).toFixed(2) : "0.08";
    var bgStyle = count > 0 ? "rgba(6, 182, 212, " + opacity + ")" : "var(--md-sys-color-surface-container-highest)";

    html += '<div class="heatmap-bar-col" title="' + String(h).padStart(2, "0") + ':00 — ' + count + ' eventos">' +
              '<div class="heatmap-bar-fill" style="height: ' + heightPx + 'px; background: ' + bgStyle + ';"></div>' +
              (h % 4 === 0 ? '<span class="heatmap-bar-label">' + h + '</span>' : '<span class="heatmap-bar-label" style="opacity:0;">-</span>') +
            '</div>';
  }
  container.innerHTML = html;
}

function renderAgentInvocations() {
  var container = document.getElementById("agentInvocationsBars");
  if (!container) return;

  var agents = AppState.getAgentInvocations();
  var elTopAgent = document.getElementById("statTopAgent");
  var elTotalInvocations = document.getElementById("statTotalAgentInvocations");
  var elSubagentInvocations = document.getElementById("statSubagentInvocations");
  var elDistinctLabel = document.getElementById("statDistinctAgentsLabel");

  if (!agents || agents.length === 0) {
    container.innerHTML = '<div style="display:flex;align-items:center;justify-content:center;height:100%;color:var(--md-sys-color-on-surface-variant);font-size:12px;">Nenhuma invocação de agente registrada</div>';
    if (elTopAgent) elTopAgent.innerText = "--";
    if (elTotalInvocations) elTotalInvocations.innerText = "0";
    if (elSubagentInvocations) elSubagentInvocations.innerText = "0";
    if (elDistinctLabel) elDistinctLabel.innerText = "0 agentes";
    return;
  }

  var maxTotal = 0;
  var sumTotal = 0;
  var sumSubagents = 0;
  var topAgentObj = agents[0];

  for (var i = 0; i < agents.length; i++) {
    var a = agents[i];
    var tot = a.total != null ? a.total : ((a.direct || 0) + (a.subagent || 0));
    sumTotal += tot;
    sumSubagents += (a.subagent || 0);
    if (tot > maxTotal) {
      maxTotal = tot;
      topAgentObj = a;
    }
  }

  // Atualiza mini-stats
  if (elTopAgent) {
    elTopAgent.innerText = topAgentObj ? ("@" + topAgentObj.agent) : "--";
    elTopAgent.title = topAgentObj ? ("@" + topAgentObj.agent) : "";
  }
  if (elTotalInvocations) elTotalInvocations.innerText = sumTotal;
  if (elSubagentInvocations) elSubagentInvocations.innerText = sumSubagents;
  if (elDistinctLabel) elDistinctLabel.innerText = agents.length + " agentes";

  // Monta as barras para os agentes (até 24 agentes como no When You Code)
  var displayAgents = agents.slice(0, 24);
  var html = "";

  for (var j = 0; j < displayAgents.length; j++) {
    var item = displayAgents[j];
    var totCount = item.total != null ? item.total : ((item.direct || 0) + (item.subagent || 0));
    var dirCount = item.direct || 0;
    var subCount = item.subagent || 0;

    var pct = maxTotal > 0 ? (totCount / maxTotal) : 0;
    var totalHeightPx = Math.max(Math.round(pct * 65), totCount > 0 ? 4 : 2);

    // Divisão proporcional entre chamadas diretas e via subagente
    var subHeightPx = totCount > 0 ? Math.round((subCount / totCount) * totalHeightPx) : 0;
    var dirHeightPx = totalHeightPx - subHeightPx;
    if (totCount > 0 && dirCount > 0 && dirHeightPx < 2) dirHeightPx = 2;
    if (totCount > 0 && subCount > 0 && subHeightPx < 2) subHeightPx = 2;

    var opacity = totCount > 0 ? (0.35 + 0.65 * pct).toFixed(2) : "0.08";
    var directBg = "rgba(6, 182, 212, " + opacity + ")";
    var subBg = "rgba(168, 85, 247, " + opacity + ")";

    var tooltip = "@" + item.agent + " — " + totCount + " invocações (" + dirCount + " diretas, " + subCount + " via subagente)";

    // Rótulo curto
    var shortName = item.agent;
    if (shortName.length > 8) {
      shortName = shortName.substring(0, 7) + "…";
    }

    html += '<div class="agent-bar-col" title="' + tooltip + '">' +
              '<div class="agent-bar-fill-wrap" style="height: ' + totalHeightPx + 'px;">' +
                (dirHeightPx > 0 ? '<div class="agent-bar-fill-direct" style="height: ' + dirHeightPx + 'px; background: ' + directBg + ';"></div>' : '') +
                (subHeightPx > 0 ? '<div class="agent-bar-fill-subagent" style="height: ' + subHeightPx + 'px; background: ' + subBg + ';"></div>' : '') +
              '</div>' +
              '<span class="agent-bar-label" title="@' + item.agent + '">' + shortName + '</span>' +
            '</div>';
  }

  container.innerHTML = html;
}

function renderActivityChart() {
  var svgWrap = document.getElementById("activityChartContainer");
  if (!svgWrap) return;

  var dateData = AppState.getSessionsByDate();
  if (!dateData || dateData.length === 0) {
    svgWrap.innerHTML = '<div style="display:flex;align-items:center;justify-content:center;height:100%;color:var(--md-sys-color-on-surface-variant);font-size:12px;">Sem dados de atividade no período</div>';
    return;
  }

  // Pega os últimos 30 dias para visualização limpa
  var sliceData = dateData.slice(-30);
  var maxEvents = 1;
  for (var i = 0; i < sliceData.length; i++) {
    if (sliceData[i].events > maxEvents) maxEvents = sliceData[i].events;
  }

  var width = 600;
  var height = 150;
  var padX = 35;
  var padY = 20;
  var graphW = width - padX * 2;
  var graphH = height - padY * 2;

  var points = [];
  var stepX = sliceData.length > 1 ? (graphW / (sliceData.length - 1)) : graphW;

  for (var j = 0; j < sliceData.length; j++) {
    var x = padX + (j * stepX);
    var y = height - padY - ((sliceData[j].events / maxEvents) * graphH);
    points.push({ x: x, y: y, item: sliceData[j] });
  }

  // Gera path SVG
  var pathD = "";
  var areaD = "";
  for (var k = 0; k < points.length; k++) {
    if (k === 0) {
      pathD += "M " + points[k].x + " " + points[k].y;
      areaD += "M " + points[k].x + " " + (height - padY) + " L " + points[k].x + " " + points[k].y;
    } else {
      pathD += " L " + points[k].x + " " + points[k].y;
      areaD += " L " + points[k].x + " " + points[k].y;
    }
  }
  if (points.length > 0) {
    areaD += " L " + points[points.length - 1].x + " " + (height - padY) + " Z";
  }

  var svgHtml = '<svg class="activity-svg" viewBox="0 0 ' + width + ' ' + height + '" preserveAspectRatio="none">' +
    '<defs>' +
      '<linearGradient id="activityGrad" x1="0" y1="0" x2="0" y2="1">' +
        '<stop offset="0%" stop-color="var(--md-sys-color-primary)" stop-opacity="0.35" />' +
        '<stop offset="100%" stop-color="var(--md-sys-color-primary)" stop-opacity="0.0" />' +
      '</linearGradient>' +
    '</defs>' +
    '<!-- Linhas de grade -->' +
    '<line x1="' + padX + '" y1="' + (height - padY) + '" x2="' + (width - padX) + '" y2="' + (height - padY) + '" stroke="var(--md-sys-color-outline-variant)" stroke-width="1" />' +
    '<line x1="' + padX + '" y1="' + (height - padY - graphH / 2) + '" x2="' + (width - padX) + '" y2="' + (height - padY - graphH / 2) + '" stroke="var(--md-sys-color-outline-variant)" stroke-dasharray="3,3" stroke-width="1" />' +
    '<!-- Área preenchida -->' +
    '<path d="' + areaD + '" fill="url(#activityGrad)" />' +
    '<!-- Linha principal -->' +
    '<path d="' + pathD + '" fill="none" stroke="var(--md-sys-color-primary)" stroke-width="2.5" stroke-linecap="round" stroke-linejoin="round" />' +
    '<!-- Pontos -->' +
    points.map(function(p) {
      return '<circle cx="' + p.x + '" cy="' + p.y + '" r="3.5" fill="var(--md-sys-color-surface-container)" stroke="var(--md-sys-color-primary)" stroke-width="2">' +
             '<title>' + p.item.date + ' — ' + p.item.events + ' eventos (' + p.item.count + ' sessões)</title>' +
             '</circle>';
    }).join("") +
    '</svg>' +
    '<div class="heatmap-footer-labels">' +
      '<span>' + (sliceData[0] ? sliceData[0].date : "") + '</span>' +
      '<span>' + (sliceData[sliceData.length - 1] ? sliceData[sliceData.length - 1].date : "") + '</span>' +
    '</div>';

  svgWrap.innerHTML = svgHtml;
}

function renderToolUsage() {
  var container = document.getElementById("toolUsageContainer");
  if (!container) return;

  var tools = AppState.getToolUsage();
  if (!tools || tools.length === 0) {
    container.innerHTML = '<div style="font-size:12px;color:var(--md-sys-color-on-surface-variant);">Nenhum evento registrado</div>';
    return;
  }

  var maxCount = tools[0] ? tools[0].count : 1;
  var html = '<div class="tool-usage-list">';

  tools.slice(0, 8).forEach(function(t) {
    var pct = Math.max(Math.round((t.count / maxCount) * 100), 2);
    html += '<div class="tool-usage-row">' +
              '<div class="tool-usage-info">' +
                '<span class="tool-name">' + t.tool + '</span>' +
                '<span class="tool-count">' + t.count + '</span>' +
              '</div>' +
              '<div class="tool-bar-bg">' +
                '<div class="tool-bar-fill" style="width: ' + pct + '%;"></div>' +
              '</div>' +
            '</div>';
  });

  html += '</div>';
  container.innerHTML = html;
}

function renderMcpTools() {
  var container = document.getElementById("mcpToolsContainer");
  if (!container) return;

  var mcpTools = AppState.getMcpTools();
  if (!mcpTools || mcpTools.length === 0) {
    container.innerHTML = '<div style="font-size:12px;color:var(--md-sys-color-on-surface-variant);">Nenhuma chamada MCP registrada</div>';
    return;
  }

  var maxCount = mcpTools[0] ? mcpTools[0].count : 1;
  var html = '<div class="tool-usage-list">';

  mcpTools.slice(0, 8).forEach(function(m) {
    var pct = Math.max(Math.round((m.count / maxCount) * 100), 2);
    var bytesStr = m.bytes ? (" (" + formatBytesDisplay(m.bytes) + ")") : "";
    html += '<div class="tool-usage-row">' +
              '<div class="tool-usage-info">' +
                '<span class="tool-name" style="color:var(--md-sys-color-cyan);">' + m.tool + '</span>' +
                '<span class="tool-count">' + m.count + bytesStr + '</span>' +
              '</div>' +
              '<div class="tool-bar-bg">' +
                '<div class="tool-bar-fill" style="width: ' + pct + '%; background-color: var(--md-sys-color-cyan);"></div>' +
              '</div>' +
            '</div>';
  });

  html += '</div>';
  container.innerHTML = html;
}

