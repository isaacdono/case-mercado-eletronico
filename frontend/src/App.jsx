import { useEffect, useState } from "react";
import RequisitionCard from "./components/RequisitionCard.jsx";

const API_BASE_URL =
  import.meta.env.VITE_API_URL || "http://localhost:8000";

const QUICK_PROMPTS = [
  "3 laptops de até US$ 2.000 cada",
  "2 smartphones para equipe comercial",
  "1 laptop com teto de US$ 300",
];

function MeLogo() {
  return (
    <svg
      className="brand-logo"
      xmlns="http://www.w3.org/2000/svg"
      viewBox="0 0 158 53"
      fill="none"
      aria-label="Mercado Eletrônico"
    >
      <path
        d="M85.6653 22.5765V51.729H70.9636V24.8501C70.9636 16.6129 67.2895 12.8271 61.3516 12.8271C54.7563 12.8271 50.1385 17.0868 50.1385 26.1707V51.7236H35.4368V24.8448C35.4368 16.6076 31.9482 12.8218 25.8247 12.8218C19.3248 12.8218 14.7017 17.0815 14.7017 26.1653V51.7183H0V0.798702H14.0443V6.66646C17.8138 2.3109 23.4707 0.0426025 29.9707 0.0426025C37.0379 0.0426025 43.0712 2.79012 46.6499 8.37035C50.7004 3.16285 57.3011 0.0426025 64.9356 0.0426025C76.997 0.0426025 85.6706 7.04451 85.6706 22.5712L85.6653 22.5765Z"
        fill="#0A0A93"
      />
      <path
        d="M129.384 9.12645C124.426 3.3279 117.221 0 109.619 0C102.451 0 95.8183 2.77946 90.9354 7.82723C86.185 12.7366 83.5713 19.2273 83.5713 26.1014C83.5713 32.9755 86.185 39.5089 90.9354 44.4289C95.813 49.4819 102.445 52.2614 109.619 52.2614C121.15 52.2614 131.107 45.0625 134.388 34.344L134.6 33.6518H120.63L120.477 33.9287C118.351 37.7837 114.168 40.1798 109.555 40.1798C103.06 40.1798 97.6845 36.0106 96.534 30.1748H135.226L135.295 29.7222C136.419 22.3475 134.261 14.8451 129.378 9.13177L129.384 9.12645ZM109.497 12.268C115.074 12.268 119.83 15.3936 121.574 20.1165H97.377C99.2485 15.3936 104.02 12.268 109.497 12.268Z"
        fill="#0A0A93"
      />
      <path
        d="M147.43 52.2613C142.208 52.2613 137.659 48.369 137.659 42.448C137.659 36.527 142.208 32.6346 147.43 32.6346C152.652 32.6346 157.201 36.527 157.201 42.448C157.201 48.369 152.652 52.2613 147.43 52.2613Z"
        fill="#0A0A93"
      />
    </svg>
  );
}

export default function App() {
  const [messages, setMessages] = useState([
    {
      id: "welcome",
      role: "agent",
      status: "info",
      text: "Informe os itens, quantidades e limites de orçamento desejados para consultar o catálogo e emitir uma requisição corporativa.",
      requisicao: null,
    },
  ]);
  const [input, setInput] = useState("");
  const [loading, setLoading] = useState(false);
  const [history, setHistory] = useState([]);

  const fetchRequisicoes = async () => {
    try {
      const res = await fetch(`${API_BASE_URL}/requisicoes`);
      if (res.ok) {
        const data = await res.json();
        setHistory(data);
      }
    } catch {
      // Backend iniciando
    }
  };

  useEffect(() => {
    fetchRequisicoes();
  }, []);

  const sendMessage = async (textToSend) => {
    const trimmed = (textToSend ?? input).trim();
    if (!trimmed || loading) return;

    const historico = messages
      .filter((m) => m.id !== "welcome")
      .map((m) => ({
        role: m.role === "user" ? "user" : "assistant",
        content: m.text,
      }));

    setMessages((prev) => [
      ...prev,
      { id: Date.now().toString(), role: "user", text: trimmed },
    ]);
    setInput("");
    setLoading(true);

    try {
      const res = await fetch(`${API_BASE_URL}/requisicoes`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ mensagem: trimmed, historico }),
      });

      if (!res.ok) {
        throw new Error(`HTTP ${res.status}`);
      }

      const data = await res.json();

      setMessages((prev) => [
        ...prev,
        {
          id: `${Date.now()}-agent`,
          role: "agent",
          status: data.requisicao ? "approved" : "info",
          text: data.mensagem,
          requisicao: data.requisicao,
        },
      ]);

      if (data.requisicao) {
        fetchRequisicoes();
      }
    } catch {
      setMessages((prev) => [
        ...prev,
        {
          id: `${Date.now()}-err`,
          role: "agent",
          status: "error",
          text: "Serviço de requisições indisponível no momento. Verifique a conexão com o backend e tente novamente.",
          requisicao: null,
        },
      ]);
    } finally {
      setLoading(false);
    }
  };

  const handleSubmit = (e) => {
    e.preventDefault();
    sendMessage();
  };

  return (
    <div className="app-shell">
      <header className="topbar">
        <div className="topbar-inner">
          <div className="brand">
            <MeLogo />
            <span className="brand-sep" />
            <span className="brand-module">E-Procurement &amp; Requisições B2B</span>
          </div>
        </div>
      </header>

      <main className="workspace">
        <section className="panel">
          <div className="panel-header">
            <h1>Nova Requisição de Compra</h1>
            <span>Consulta automatizada de catálogo</span>
          </div>

          <div className="quick-bar">
            {QUICK_PROMPTS.map((prompt) => (
              <button
                key={prompt}
                type="button"
                className="quick-chip"
                disabled={loading}
                onClick={() => sendMessage(prompt)}
              >
                {prompt}
              </button>
            ))}
          </div>

          <div className="messages-stream">
            {messages.map((msg) => (
              <div
                key={msg.id}
                className={`msg-item ${msg.role} ${msg.status || ""}`}
              >
                <span className="msg-meta">
                  {msg.role === "user" ? "Solicitante" : "Mercado Eletrônico"}
                </span>
                <div className="msg-card">
                  {msg.status === "error" && (
                    <span className="status-tag error">Erro de Conexão</span>
                  )}
                  {msg.status === "approved" && (
                    <span className="status-tag approved">Requisição Emitida</span>
                  )}
                  <div>{msg.text}</div>
                  {msg.requisicao && (
                    <RequisitionCard requisicao={msg.requisicao} />
                  )}
                </div>
              </div>
            ))}

            {loading && (
              <div className="msg-item agent">
                <span className="msg-meta">Mercado Eletrônico</span>
                <div className="msg-card">
                  Consultando catálogo e validando parâmetros da solicitação...
                </div>
              </div>
            )}
          </div>

          <form className="composer" onSubmit={handleSubmit}>
            <input
              type="text"
              className="composer-input"
              placeholder="Ex: Preciso de 3 laptops com valor unitário até US$ 2.000..."
              value={input}
              onChange={(e) => setInput(e.target.value)}
              disabled={loading}
            />
            <button
              type="submit"
              className="composer-btn"
              disabled={loading || !input.trim()}
            >
              {loading ? "Aguarde..." : "Solicitar"}
            </button>
          </form>
        </section>

        <aside className="panel">
          <div className="panel-header">
            <h2>Histórico de Requisições</h2>
            <span>{history.length} emitida(s)</span>
          </div>
          <div className="history-body">
            {history.length === 0 ? (
              <div className="empty-state">
                Nenhuma requisição registrada.
              </div>
            ) : (
              history.map((req) => (
                <RequisitionCard
                  key={req.id}
                  requisicao={req}
                  defaultExpanded={false}
                />
              ))
            )}
          </div>
        </aside>
      </main>
    </div>
  );
}
