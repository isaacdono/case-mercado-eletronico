import { useState } from "react";

const formatUSD = (val) =>
  `US$ ${new Intl.NumberFormat("en-US", {
    minimumFractionDigits: 2,
    maximumFractionDigits: 2,
  }).format(Number(val || 0))}`;

export default function RequisitionCard({
  requisicao,
  defaultExpanded = true,
}) {
  const [expanded, setExpanded] = useState(defaultExpanded);

  if (!requisicao) return null;

  const reqCode = `REQ #${String(requisicao.id).padStart(4, "0")}`;
  const fretes = [
    ...new Set((requisicao.itens || []).map((i) => i.frete).filter(Boolean)),
  ];

  return (
    <div className={`req-doc ${expanded ? "expanded" : "collapsed"}`}>
      <button
        type="button"
        className="req-doc-top"
        onClick={() => setExpanded((prev) => !prev)}
        aria-expanded={expanded}
      >
        <div className="req-doc-top-left">
          <span className="req-number">{reqCode}</span>
          <span className="req-status-pill">{requisicao.status}</span>
        </div>
        <div className="req-doc-top-right">
          <span className="req-top-total">
            {formatUSD(requisicao.valor_total)}
          </span>
          <svg
            className={`req-chevron ${expanded ? "open" : ""}`}
            width="16"
            height="16"
            viewBox="0 0 24 24"
            fill="none"
            stroke="currentColor"
            strokeWidth="2.5"
            strokeLinecap="round"
            strokeLinejoin="round"
          >
            <polyline points="6 9 12 15 18 9" />
          </svg>
        </div>
      </button>

      {expanded && (
        <div className="req-doc-body">
          <div className="req-items-list">
            {(requisicao.itens || []).map((item) => (
              <div key={item.id} className="req-item-row">
                <div className="req-item-main">
                  <div className="req-item-name">{item.nome_produto}</div>
                  <div className="req-item-sub">
                    {item.categoria && <span>{item.categoria}</span>}
                    {item.frete && <span>• {item.frete}</span>}
                  </div>
                </div>
                <div className="req-item-numbers mono">
                  <span className="req-item-qty">
                    {item.quantidade}x {formatUSD(item.preco_unitario)}
                  </span>
                  <strong className="req-item-subtotal">
                    {formatUSD(item.subtotal)}
                  </strong>
                </div>
              </div>
            ))}
          </div>

          <div className="req-doc-bottom">
            <span className="frete-info">
              {fretes.length > 0 ? (
                <>
                  Frete: <span className="frete-val">{fretes.join(" • ")}</span>
                </>
              ) : (
                <span>{(requisicao.itens || []).length} item(ns)</span>
              )}
            </span>
            <span>
              Total:{" "}
              <strong className="total-val">
                {formatUSD(requisicao.valor_total)}
              </strong>
            </span>
          </div>
        </div>
      )}
    </div>
  );
}
