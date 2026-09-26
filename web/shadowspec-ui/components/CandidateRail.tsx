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
          borderRadius: "18px",
          background: "#f5f5f5",
          color: "#171717",
          border: "1px solid #e5e5e5",
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
        borderRadius: "18px",
        background: "#fdecec",
        color: "#e7000b",
        border: "1px solid #e7000b",
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
        background: "#fafafa",
        borderRight: "1px solid #e5e5e5",
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
          borderBottom: "1px solid #e5e5e5",
        }}
      >
        <div
          style={{
            fontSize: "10px",
            fontWeight: 600,
            letterSpacing: "0.08em",
            color: "#737373",
            textTransform: "uppercase",
            fontFamily: "Menlo, monospace",
          }}
        >
          Candidates
        </div>
        <div
          style={{
            fontSize: "11px",
            color: "#737373",
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
                  ? "#f5f5f5"
                  : "transparent",
                border: "none",
                borderLeft: isSelected
                  ? "2px solid #171717"
                  : "2px solid transparent",
                cursor: "pointer",
                transition: "background 150ms ease, border-color 150ms ease",
              }}
              onMouseEnter={(e) => {
                if (!isSelected) {
                  (e.currentTarget as HTMLButtonElement).style.background =
                    "transparent";
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
                    color: isSelected ? "#0a0a0a" : "#b0a89e",
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
                  color: "#737373",
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
          borderTop: "1px solid #e5e5e5",
        }}
      >
        <div
          style={{
            fontSize: "10px",
            color: "#d4d4d4",
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
