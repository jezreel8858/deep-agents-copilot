/**
 * state.js — Estado Reativo e Armazenamento dos Dados Injetados
 */

// Dados brutos injetados pelo gerador Python / TemplateBundler
var rawInsightsData = /* __INJECT_RAW_INSIGHTS__ */ {};

// Estado global reativo da aplicação
var AppState = {
  data: rawInsightsData || {},
  activeNav: "dashboard",
  activeSeverity: "all",
  activeProject: "all",
  searchQuery: "",
  memorySearchQuery: "",
  memorySearchFilter: "all",
  tablePage: 1,
  pageSize: 10,

  getKpis: function() {
    return this.data.kpis || {};
  },

  getInsights: function() {
    return this.data.insightsActions || [];
  },

  getSessions: function() {
    return this.data.sessions || [];
  },

  getHourlyPattern: function() {
    return this.data.hourlyPattern || [];
  },

  getAgentInvocations: function() {
    return this.data.agentInvocations || [];
  },

  getSessionsByDate: function() {
    return this.data.sessionsByDate || [];
  },

  getToolUsage: function() {
    return this.data.toolUsage || [];
  },

  getMcpTools: function() {
    return this.data.mcpTools || [];
  },

  getProjects: function() {
    return this.data.projects || [];
  },

  getSources: function() {
    return this.data.sources || [];
  },

  getChunksBySource: function() {
    return this.data.chunksBySource || {};
  },

  getDecisions: function() {
    return this.data.decisions || [];
  },

  getDetailedEvents: function() {
    return this.data.detailedEvents || [];
  },

  getExecutivePersonas: function() {
    return this.data.executivePersonas || [];
  }
};

