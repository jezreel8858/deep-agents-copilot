"use client";

import { Suspense, useState } from "react";
import { useRouter, useSearchParams } from "next/navigation";

/**
 * /login — formulario do codigo de acesso (substitui o ACCESS_CODE do
 * Lobe Chat). Fora do grupo de rotas (chat), portanto sem o provider
 * `<CopilotKit>` montado.
 */
export default function LoginPage() {
  return (
    <Suspense fallback={null}>
      <LoginForm />
    </Suspense>
  );
}

function LoginForm() {
  const router = useRouter();
  const searchParams = useSearchParams();
  const [codigo, setCodigo] = useState("");
  const [erro, setErro] = useState<string | null>(null);
  const [enviando, setEnviando] = useState(false);

  async function onSubmit(e: React.FormEvent) {
    e.preventDefault();
    setEnviando(true);
    setErro(null);
    try {
      const resposta = await fetch("/api/login", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ codigo }),
      });
      if (!resposta.ok) {
        setErro("Codigo de acesso invalido");
        return;
      }
      router.replace(searchParams.get("next") ?? "/");
    } finally {
      setEnviando(false);
    }
  }

  return (
    <div className="login-page">
      <form className="login-card" onSubmit={onSubmit}>
        <h1>Deep Agents Chat</h1>
        <input
          type="password"
          placeholder="Codigo de acesso"
          value={codigo}
          onChange={(e) => setCodigo(e.target.value)}
          autoFocus
        />
        {erro && <span style={{ color: "crimson" }}>{erro}</span>}
        <button type="submit" disabled={enviando || !codigo}>
          {enviando ? "Entrando…" : "Entrar"}
        </button>
      </form>
    </div>
  );
}

