"use client";
import { CandidateKey, CANDIDATE_META, VerdictData } from "@/types/verdict";

interface CandidateRailProps {
  selected: CandidateKey;
  onSelect: (candidate: CandidateKey) => void;
  verdicts: Record<CandidateKey, VerdictData>;
}

const CANDIDATES: CandidateKey[] = ["baseline", "bad", "narrow"];

function VerdictBadge({ verdict }: { verdict: "accepted" | "rejected" | "error" }) {
  if (verdict === "accepted") {
    return (
      <span
        style={{
          fontSize: "10px",
          fontFamily: "Menlo, monospace",
          fontWeight: 600,
          letterSpacing: "0.04em",
          padding: "2px 6px",
          borderRadius: "4px",
          background: "rgba(42,184,112,0.15)",
          color: "#2ab870",
          border: "1px solid rgba(42,184,112,0.25)",
          textTransform: "uppercase",
          lineHeight: 1,
        }}
      >
        PASS
      </span>
    );
  }
  return (
    <span
      style={{
        fontSize: "10px",
        fontFamily: "Menlo, monospace",
        fontWeight: 600,
        letterSpacing: "0.04em",
        padding: "2px 6px",
        borderRadius: "4px",
        background: "rgba(240,64,64,0.15)",
        color: "#f04040",
        border: "1px solid rgba(240,64,64,0.25)",
        textTransform: "uppercase",
        lineHeight: 1,
      }}
    >
      FAIL
    </span>
  );
}

export default function CandidateRail({
  selected,
  onSelect,
  verdicts,
}: CandidateRailProps) {
  return (
    <aside
      style={{
        width: "var(--pc-rail-w)",
        minWidth: "var(--pc-rail-w)",
        background: "#141210",
        borderRight: "1px solid #2e2a26",
        display: "flex",
        flexDirection: "column",
        height: "100%",
        overflow: "hidden",
      }}
    >
      {/* Rail header */}
      <div
        style={{
          padding: "16px 16px 12px",
          borderBottom: "1px solid #2e2a26",
        }}
      >
        <div
          style={{
            fontSize: "10px",
            fontWeight: 600,
            letterSpacing: "0.08em",
            color: "#6b6358",
            textTransform: "uppercase",
            fontFamily: "Menlo, monospace",
          }}
        >
          Candidates
        </div>
        <div
          style={{
            fontSize: "11px",
            color: "#5a5248",
            marginTop: "4px",
            lineHeight: 1.4,
          }}
        >
          legacy_orders fixture
        </div>
      </div>

      {/* Candidate list */}
      <div style={{ flex: 1, overflowY: "auto", padding: "8px 0" }}>
        {CANDIDATES.map((key) => {
          const meta = CANDIDATE_META[key];
          const verdict = verdicts[key];
          const isSelected = selected === key;

          return (
            <button
              key={key}
              onClick={() => onSelect(key)}
              className="btn-press"
              style={{
                display: "flex",
                flexDirection: "column",
                gap: "4px",
                width: "100%",
                padding: "10px 16px",
                textAlign: "left",
                background: isSelected
                  ? "rgba(249,70,18,0.08)"
                  : "transparent",
                border: "none",
                borderLeft: isSelected
                  ? "2px solid #F94612"
                  : "2px solid transparent",
                cursor: "pointer",
                transition: "background 150ms ease, border-color 150ms ease",
              }}
              onMouseEnter={(e) => {
                if (!isSelected) {
                  (e.currentTarget as HTMLButtonElement).style.background =
                    "rgba(255,255,255,0.04)";
                }
              }}
              onMouseLeave={(e) => {
                if (!isSelected) {
                  (e.currentTarget as HTMLButtonElement).style.background =
                    "transparent";
                }
              }}
            >
              <div
                style={{
                  display: "flex",
                  alignItems: "center",
                  justifyContent: "space-between",
                  gap: "8px",
                }}
              >
                <span
                  style={{
                    fontFamily: "Menlo, monospace",
                    fontSize: "13px",
                    fontWeight: isSelected ? 600 : 400,
                    color: isSelected ? "#f0ece8" : "#b0a89e",
                    letterSpacing: "-0.01em",
                  }}
                >
                  {meta.title}
                </span>
                <VerdictBadge verdict={verdict.verdict} />
              </div>
              <span
                style={{
                  fontSize: "11px",
                  color: "#5a5248",
                  lineHeight: 1.4,
                }}
              >
                {meta.subtitle}
              </span>
            </button>
          );
        })}
      </div>

      {/* Rail footer */}
      <div
        style={{
          padding: "12px 16px",
          borderTop: "1px solid #2e2a26",
        }}
      >
        <div
          style={{
            fontSize: "10px",
            color: "#4a4440",
            fontFamily: "Menlo, monospace",
            lineHeight: 1.5,
          }}
        >
          <div>ShadowSpec v2.0</div>
          <div>Build-time verdicts</div>
        </div>
      </div>
    </aside>
  );
}
