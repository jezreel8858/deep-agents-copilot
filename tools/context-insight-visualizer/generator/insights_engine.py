#!/usr/bin/env python3
"""
insights_engine.py — Motor de Cálculo de KPIs e Regras de Negócio de Insights
=============================================================================
Calcula KPIs agregados e avalia deterministicamente regras de insight (cards FYI,
NICE, HEADS UP, FIX THIS) com thresholds definidos e mensagens acionáveis (action + roi).
"""

from typing import Any, Dict, List


class InsightsEngine:
    """Motor de inteligência analítica para métricas do Context Mode."""

    def __init__(self, extracted_data: Dict[str, Any]):
        self.data = extracted_data
        self.sessions: List[Dict[str, Any]] = extracted_data.get("sessions", [])
        self.events_summary: Dict[str, Any] = extracted_data.get("eventsSummary", {})
        self.stats_pid: Dict[str, Any] = extracted_data.get("statsPid", {})
        self.content: Dict[str, Any] = extracted_data.get("content", {})
        self.meta: Dict[str, Any] = extracted_data.get("meta", {})

    def build_payload(self) -> Dict[str, Any]:
        """Calcula os KPIs, time-series, fontes, decisões e cards de insight unificados."""
        kpis = self._compute_kpis()
        insights = self._evaluate_insights(kpis)
        personas = self._build_executive_personas(kpis)

        return {
            "version": "1.0.0",
            "meta": self.meta,
            "kpis": kpis,
            "sessions": self.sessions[:200],  # Limita a 200 sessões mais recentes para evitar payload gigante
            "sessionsByDate": self.events_summary.get("sessionsByDate", []),
            "hourlyPattern": self.events_summary.get("hourlyPattern", [{"hour": h, "count": 0} for h in range(24)]),
            "agentInvocations": self.events_summary.get("agentInvocations", []),
            "toolUsage": self.events_summary.get("toolUsage", []),
            "mcpTools": self.events_summary.get("mcpTools", []),
            "projects": self.events_summary.get("projects", []),
            "subagents": self.events_summary.get("subagents", {}),
            "sources": self.content.get("sources", []),
            "chunksBySource": self.content.get("chunksBySource", {}),
            "decisions": self.events_summary.get("decisions", []),
            "detailedEvents": self.events_summary.get("detailedEvents", []),
            "insightsActions": insights,
            "executivePersonas": personas,
        }

    def _build_executive_personas(self, kpis: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Gera as métricas de visão executiva estruturadas por papel organizacional."""
        decisions_cnt = len(self.events_summary.get("decisions", []))
        sources_cnt = len(self.content.get("sources", []))
        hourly = self.events_summary.get("hourlyPattern", [])
        peak_hour = max(hourly, key=lambda x: x["count"])["hour"] if hourly else 14

        return [
            {
                "role": "CTO / VP Engineering",
                "icon": "domain",
                "colorClass": "persona-blue",
                "badge": "Custos & Escala",
                "metricHeadline": f"${kpis['dollarsSaved']:.2f} economizados em chamadas de IA",
                "insights": [
                    f"{kpis['tokensSaved']:,} tokens mantidos fora de contexto via sandbox seguro",
                    f"Zero lock-in em serviços SaaS proprietários com persistência 100% local",
                ],
                "roi": "Controle absoluto de gastos de tokens e previsibilidade de escala",
            },
            {
                "role": "Engineering Manager",
                "icon": "groups",
                "colorClass": "persona-purple",
                "badge": "Autonomia de Time",
                "metricHeadline": f"{kpis['promptsPerSession']} prompts/sessão — alta autonomia",
                "insights": [
                    f"{kpis['totalSessions']} sessões registradas com relação {kpis['readWriteRatio']}:1 leitura/escrita",
                    f"Roteamento de agentes diminui tempo gasto em refinamentos repetitivos",
                ],
                "roi": "Aceleração do ciclo de entrega com menor tempo de re-explicação de tarefas",
            },
            {
                "role": "DevEx Lead",
                "icon": "auto_awesome",
                "colorClass": "persona-cyan",
                "badge": "Experiência Dev",
                "metricHeadline": f"Apenas {kpis['compactRate']}% de sessões com estouro de contexto",
                "insights": [
                    f"~{kpis['timeSavedMin']} minutos economizados por agentes paralelos em tarefas complexas",
                    f"{sources_cnt} arquivos técnicos indexados para recuperação contextual instantânea",
                ],
                "roi": "Fluxo contínuo sem frustração de 'context window limit reached'",
            },
            {
                "role": "Security / CISO",
                "icon": "security",
                "colorClass": "persona-red",
                "badge": "Auditoria & Compliance",
                "metricHeadline": f"{decisions_cnt} decisões técnicas com rastreabilidade",
                "insights": [
                    "Varreduras e leituras rodando em sandbox subprocess isolado",
                    "Trilha de auditoria cronológica completa com hash e origem por evento",
                ],
                "roi": "Conformidade SOC 2 e zero risco de vazamento acidental em saídas de ferramentas",
            },
            {
                "role": "QA Lead",
                "icon": "science",
                "colorClass": "persona-amber",
                "badge": "Confiabilidade",
                "metricHeadline": f"Taxa de erro de ferramentas de apenas {kpis['errorRatePct']}%",
                "insights": [
                    f"{kpis['totalEvents']} operações de ferramenta auditadas com apenas {kpis['totalErrors']} falhas",
                    "Adapters de governança evitam loops de tentativa e erro",
                ],
                "roi": "Menos retentativas, código gerado mais assertivo e menor taxa de retrabalho",
            },
            {
                "role": "Developer (IC)",
                "icon": "code",
                "colorClass": "persona-emerald",
                "badge": "Foco Pessoal",
                "metricHeadline": f"Horário de pico em {peak_hour:02d}:00h — deep work otimizado",
                "insights": [
                    "Acesso instantâneo à base de conhecimento sem precisar reler arquivos repetidamente",
                    "Histórico unificado de sessões pesquisável e exportável",
                ],
                "roi": "Mais tempo codando a solução real e menos tempo manipulando contexto",
            },
        ]

    def _compute_kpis(self) -> Dict[str, Any]:
        """Calcula as métricas de nível executivo."""
        total_sessions = len(self.sessions)
        total_events = self.events_summary.get("totalEvents", 0)
        total_errors = self.events_summary.get("totalErrors", 0)
        total_prompts = self.events_summary.get("totalPrompts", 0)
        total_reads = self.events_summary.get("totalReads", 0)
        total_writes = self.events_summary.get("totalWrites", 0)

        total_compacts = sum(s.get("compactCount", 0) for s in self.sessions)
        sessions_with_compact = sum(1 for s in self.sessions if s.get("compactCount", 0) > 0)

        # 1. Read to Write ratio
        if total_writes > 0:
            rw_ratio = round(total_reads / total_writes, 1)
        elif total_reads > 0:
            rw_ratio = float(total_reads)
        else:
            rw_ratio = 1.0

        # 2. Compact rate (%)
        compact_rate = round((sessions_with_compact / max(total_sessions, 1)) * 100.0, 1)

        # 3. Error rate (%)
        error_rate_pct = round((total_errors / max(total_events, 1)) * 100.0, 1)

        # 4. Prompts per session
        prompts_per_session = round(total_prompts / max(total_sessions, 1), 1)

        # 5. Tokens e Dólares economizados
        tokens_saved = self.stats_pid.get("tokensSavedLifetime", 0)
        dollars_saved = self.stats_pid.get("dollarsSavedLifetime", 0.0)

        # 6. Tempo economizado por subagentes
        subagent_data = self.events_summary.get("subagents", {})
        time_saved_min = subagent_data.get("timeSavedMin", 0)

        # 7. Métricas de invocações de agentes
        agent_invs = self.events_summary.get("agentInvocations", [])
        total_agent_invocations = sum(a.get("total", 0) for a in agent_invs)
        subagent_invocations = sum(a.get("subagent", 0) for a in agent_invs)
        top_agent = agent_invs[0].get("agent", "") if agent_invs else ""

        return {
            "totalSessions": total_sessions,
            "readWriteRatio": rw_ratio,
            "compactRate": compact_rate,
            "errorRatePct": error_rate_pct,
            "promptsPerSession": prompts_per_session,
            "totalEvents": total_events,
            "totalErrors": total_errors,
            "totalCompacts": total_compacts,
            "totalReads": total_reads,
            "totalWrites": total_writes,
            "tokensSaved": tokens_saved,
            "dollarsSaved": dollars_saved,
            "timeSavedMin": time_saved_min,
            "totalAgentInvocations": total_agent_invocations,
            "subagentInvocations": subagent_invocations,
            "topAgent": top_agent,
        }

    def _evaluate_insights(self, kpis: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Aplica regras determinísticas para gerar os cards Insights & Actions."""
        cards: List[Dict[str, Any]] = []

        # ── Regra 1: Balanço de Leitura vs Escrita ──
        reads = kpis["totalReads"]
        writes = kpis["totalWrites"]
        ratio = kpis["readWriteRatio"]

        if (reads + writes) >= 5:
            if ratio > 4.0:
                cards.append({
                    "id": "rw-high-reads",
                    "severity": "neutral",
                    "badge": "FYI",
                    "icon": "menu_book",
                    "metric": f"Você lê {ratio}x mais arquivos do que escreve",
                    "evidence": f"{reads} leituras de arquivo vs {writes} escritas registradas. O agente investe volume substancial em exploração antes de alterar código.",
                    "action": "Utilize consultas filtradas (ctx_search / grep cirúrgico) em vez de ler arquivos inteiros para inspeção inicial.",
                    "roi": "Reduz drasticamente o consumo de tokens na janela de contexto.",
                })
            elif 0 < ratio <= 4.0:
                cards.append({
                    "id": "rw-healthy",
                    "severity": "positive",
                    "badge": "Nice",
                    "icon": "check_circle",
                    "metric": f"Equilíbrio saudável: proporção de {ratio}:1",
                    "evidence": f"{writes} escritas realizadas com apenas {reads} leituras prévias. O consumo de contexto é focado e cirúrgico.",
                    "action": "Continue mantendo pré-voos concisos e solicitações direcionadas por arquivo.",
                    "roi": "Evita loops de releitura e maximiza a precisão das alterações.",
                })

        # ── Regra 2: Estouro de Contexto / Taxa de Compactação ──
        total_sessions = kpis["totalSessions"]
        compact_rate = kpis["compactRate"]
        total_compacts = kpis["totalCompacts"]

        if total_sessions >= 3:
            if compact_rate > 35.0:
                cards.append({
                    "id": "compact-high",
                    "severity": "warning",
                    "badge": "Heads up",
                    "icon": "psychology",
                    "metric": f"{compact_rate}% das sessões exigiram compactação de memória",
                    "evidence": f"{total_compacts} eventos de compactação em {total_sessions} sessões. Sessões excessivamente longas causam perda de contexto intermediário.",
                    "action": "Inicie uma nova conversa ao trocar de tarefa ou após atingir o objetivo principal da issue.",
                    "roi": "Preserva a fidelidade das instruções e elimina a necessidade de re-explicar contexto antigo.",
                })
            elif compact_rate <= 15.0:
                cards.append({
                    "id": "compact-low",
                    "severity": "positive",
                    "badge": "Nice",
                    "icon": "check_circle",
                    "metric": f"Apenas {compact_rate}% de compactação — sessões bem delimitadas",
                    "evidence": f"{total_compacts} compactações em {total_sessions} sessões. Suas conversas concluem dentro do orçamento de tokens.",
                    "action": "Mantenha o padrão de sessões atômicas com escopo bem definido.",
                    "roi": "Zero degradação de contexto e respostas mais rápidas do modelo.",
                })

        # ── Regra 3: Taxa de Erro de Ferramentas ──
        total_events = kpis["totalEvents"]
        error_rate = kpis["errorRatePct"]
        total_errors = kpis["totalErrors"]

        if total_events >= 10:
            if error_rate > 10.0:
                cards.append({
                    "id": "error-high",
                    "severity": "critical",
                    "badge": "Fix this",
                    "icon": "warning",
                    "metric": f"{error_rate}% das chamadas de ferramentas falharam",
                    "evidence": f"{total_errors} erros em {total_events} chamadas. Pode indicar comandos inexistentes no shell ou caminhos inválidos.",
                    "action": "Revise as instruções do adapter da stack e utilize ferramentas dedicadas (ctx_execute / read_file) em vez de comandos crus.",
                    "roi": f"Elimina retentativas automáticas e economiza ~{round(total_errors * 1.5)} minutos em loops desnecessários.",
                })
            elif error_rate <= 5.0:
                cards.append({
                    "id": "error-low",
                    "severity": "positive",
                    "badge": "Nice",
                    "icon": "shield",
                    "metric": f"Taxa de erro de apenas {error_rate}% — alta precisão de execução",
                    "evidence": f"Apenas {total_errors} erros em {total_events} eventos. O ferramental opera com alta confiabilidade.",
                    "action": "Mantenha a governança de comandos testados e parâmetros estritos.",
                    "roi": "Execução limpa sem desperdício de tokens de recuperação.",
                })

        # ── Regra 4: Paralelismo de Subagentes ──
        subagents = self.events_summary.get("subagents", {})
        bursts = subagents.get("bursts", 0)
        time_saved = subagents.get("timeSavedMin", 0)
        parallel_count = subagents.get("parallelCount", 0)
        max_concurrent = subagents.get("maxConcurrent", 0)

        if bursts > 0 and time_saved > 0:
            cards.append({
                "id": "subagent-parallel",
                "severity": "positive",
                "badge": "Nice",
                "icon": "group",
                "metric": f"Você economizou ~{time_saved} min com subagentes paralelos",
                "evidence": f"{parallel_count} tarefas rodaram concorrentemente em {bursts} rajadas paralelas (pico de {max_concurrent} agentes simultâneos).",
                "action": "Continue delegando pesquisas e análises exploratórias complexas a subagentes.",
                "roi": "Paralelismo acelera a descoberta de código e protege a janela da conversa principal.",
            })
        elif total_events > 30 and bursts == 0:
            cards.append({
                "id": "subagent-sequential",
                "severity": "neutral",
                "badge": "FYI",
                "icon": "bolt",
                "metric": "Oportunidade para acelerar tarefas com subagentes paralelos",
                "evidence": f"{total_events} eventos processados de modo estritamente sequencial sem rajadas paralelas detectadas.",
                "action": "Utilize run_subagent para buscas ou delegue pesquisas concorrentes via ctx_batch_execute.",
                "roi": "Pesquisas paralelas reduzem em até 60% o tempo de espera do desenvolvedor.",
            })

        # ── Regra 5: Eficiência de Prompts ──
        prompts_per_session = kpis["promptsPerSession"]
        if total_sessions >= 2 and prompts_per_session > 0:
            if prompts_per_session <= 3.5:
                cards.append({
                    "id": "prompt-efficient",
                    "severity": "positive",
                    "badge": "Nice",
                    "icon": "tune",
                    "metric": f"{prompts_per_session} prompts por sessão — instruções claras e objetivas",
                    "evidence": "O agente atinge o objetivo com poucas intervenções manuais, evidenciando prompts estruturados.",
                    "action": "Mantenha o padrão de declarar objetivos, restrições e saídas esperadas no primeiro turno.",
                    "roi": "Reduz o overhead cognitivo e o custo total por funcionalidade entregue.",
                })
            else:
                cards.append({
                    "id": "prompt-exploratory",
                    "severity": "neutral",
                    "badge": "FYI",
                    "icon": "tune",
                    "metric": f"{prompts_per_session} prompts por sessão — sessões de exploração",
                    "evidence": "Número elevado de interações por sessão indica diálogos refinados passo a passo.",
                    "action": "Para tarefas de implementação, utilize @prompt-structuring para sintetizar o plano antes de codificar.",
                    "roi": "Encurta o ciclo de entrega e economiza turnos de refinamento.",
                })

        # ── Regra 6: Padrão de Horário (When You Code) ──
        hourly = self.events_summary.get("hourlyPattern", [])
        if hourly:
            peak = max(hourly, key=lambda x: x["count"], default=None)
            if peak and peak["count"] > 0:
                cards.append({
                    "id": "peak-hour",
                    "severity": "neutral",
                    "badge": "FYI",
                    "icon": "schedule",
                    "metric": f"Horário de pico de atividade: {peak['hour']:02d}:00h ({peak['count']} eventos)",
                    "evidence": f"Maior concentração de interações com agentes ocorre por volta das {peak['hour']:02d}:00h.",
                    "action": "Reserve esse horário para tarefas críticas que exigem maior foco e atenção aos detalhes.",
                    "roi": "Melhor alinhamento entre o fluxo de trabalho e momentos de alta produtividade.",
                })

        # ── Regra 7: Economia de Tokens via Context Mode ──
        tokens_saved = kpis["tokensSaved"]
        dollars_saved = kpis["dollarsSaved"]
        if tokens_saved > 1000:
            cards.append({
                "id": "tokens-saved",
                "severity": "positive",
                "badge": "Nice",
                "icon": "savings",
                "metric": f"Economia de ~{tokens_saved:,} tokens via Context Mode",
                "evidence": f"O processamento em sandbox do context-mode manteve bytes fora da conversa, gerando economia acumulada estimada em ${dollars_saved:.2f}.",
                "action": "Continue utilizando ctx_execute e ctx_search para tarefas de leitura e agregação volumosa.",
                "roi": "Menor custo de API e janelas de contexto limpas para raciocínio profundo.",
            })

        return cards


if __name__ == "__main__":
    from extractor import ContextDataExtractor
    extractor = ContextDataExtractor()
    raw = extractor.extract_all()
    engine = InsightsEngine(raw)
    payload = engine.build_payload()
    print("KPIs calculados:")
    for k, v in payload["kpis"].items():
        print(f"  {k}: {v}")
    print(f"\nTotal Insights Cards gerados: {len(payload['insightsActions'])}")
    for card in payload["insightsActions"]:
        print(f"  [{card['badge']}] {card['metric']}")

