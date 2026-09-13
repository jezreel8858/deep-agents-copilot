-- ==============================================================================
-- Schema Supabase: Tabela de Incidentes e Aprendizado de Workflows (NoSQL/JSONB)
-- Execute este script no SQL Editor do seu projeto Supabase (https://supabase.com)
-- ==============================================================================

-- 1. Criação da Tabela de Incidentes
CREATE TABLE IF NOT EXISTS public.workflow_incidents (
    incident_id UUID PRIMARY KEY,
    workflow_id TEXT NOT NULL,
    workflow_name TEXT NOT NULL,
    session_id TEXT,
    agent_id TEXT NOT NULL,
    step_index INTEGER NOT NULL,
    step_name TEXT NOT NULL,
    severity TEXT NOT NULL CHECK(severity IN ('LOW', 'MEDIUM', 'HIGH', 'CRITICAL')),
    category TEXT NOT NULL CHECK(category IN ('TOOL_FAILURE', 'RUNTIME_EXCEPTION', 'CIRCUIT_BREAKER', 'PARITY_BREAK', 'QUALITY_GATE_FAILURE', 'HUMAN_ESCALATION')),
    status TEXT NOT NULL CHECK(status IN ('OPEN', 'RETRYING', 'MITIGATED', 'RESOLVED', 'LEARNED_AND_PRUNED', 'ESCALATED_TO_HUMAN', 'CIRCUIT_TRIPPED')),
    created_at TIMESTAMPTZ NOT NULL DEFAULT timezone('utc'::text, now()),
    document_payload JSONB NOT NULL -- Documento completo com rootCause, lessonLearned e contexto
);

-- 2. Índices de Alta Performance (Índice GIN para busca profunda em JSONB)
CREATE INDEX IF NOT EXISTS idx_supabase_incidents_payload_gin ON public.workflow_incidents USING GIN (document_payload);
CREATE INDEX IF NOT EXISTS idx_supabase_incidents_workflow ON public.workflow_incidents(workflow_id);
CREATE INDEX IF NOT EXISTS idx_supabase_incidents_agent ON public.workflow_incidents(agent_id);
CREATE INDEX IF NOT EXISTS idx_supabase_incidents_severity ON public.workflow_incidents(severity);
CREATE INDEX IF NOT EXISTS idx_supabase_incidents_created ON public.workflow_incidents(created_at DESC);

-- 3. Habilitação de Row Level Security (RLS)
ALTER TABLE public.workflow_incidents ENABLE ROW LEVEL SECURITY;

-- 4. Política de Acesso para a API (Permite leitura e escrita com Service Role ou Anon Key)
CREATE POLICY "Permitir acesso completo para chaves autenticadas da API"
    ON public.workflow_incidents
    FOR ALL
    USING (true)
    WITH CHECK (true);

-- Comentários de Documentação
COMMENT ON TABLE public.workflow_incidents IS 'Registro central de incidentes e lições aprendidas de workflows de agentes de IA.';
COMMENT ON COLUMN public.workflow_incidents.document_payload IS 'Payload canônico documental validado contra workflow-incident.schema.json.';

