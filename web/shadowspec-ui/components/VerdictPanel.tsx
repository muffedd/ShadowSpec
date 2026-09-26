"use client";
import { motion, AnimatePresence } from "framer-motion";
import { CheckResult, VerdictData } from "@/types/verdict";

interface VerdictPanelProps {
  verdict: VerdictData;
  visible: boolean;
}

function CheckRow({ check }: { check: CheckResult }) {
  return (
    <motion.div
      initial={{ opacity: 0, x: -6 }}
      animate={{ opacity: 1, x: 0 }}
      transition={{ duration: 0.22, ease: [0.23, 1, 0.32, 1] }}
      style={{
        display: "flex",
        alignItems: "flex-start",
        gap: "10px",
        padding: "8px 16px",
        borderBottom: "1px solid #1e1b18",
      }}
    >
      {/* Status icon */}
      <div
        style={{
          width: "16px",
          height: "16px",
          borderRadius: "50%",
          display: "flex",
          alignItems: "center",
          justifyContent: "center",
          flexShrink: 0,
          marginTop: "1px",
          background: check.passed
            ? "rgba(42,184,112,0.18)"
            : "rgba(240,64,64,0.18)",
          border: check.passed
            ? "1px solid rgba(42,184,112,0.4)"
            : "1px solid rgba(240,64,64,0.4)",
        }}
      >
        {check.passed ? (
          <svg width="8" height="6" viewBox="0 0 8 6" fill="none">
            <path
              d="M1 3L3 5L7 1"
              stroke="#2ab870"
              strokeWidth="1.5"
              strokeLinecap="round"
              strokeLinejoin="round"
            />
          </svg>
        ) : (
          <svg width="7" height="7" viewBox="0 0 7 7" fill="none">
            <path
              d="M1.5 1.5L5.5 5.5M5.5 1.5L1.5 5.5"
              stroke="#f04040"
              strokeWidth="1.5"
              strokeLinecap="round"
            />
          </svg>
        )}
      </div>

      {/* Check content */}
      <div style={{ flex: 1 }}>
        <div
          style={{
            fontSize: "12.5px",
            color: check.passed ? "#d0cac4" : "#f09090",
            lineHeight: 1.4,
            fontWeight: check.passed ? 400 : 500,
          }}
        >
          {check.name}
        </div>
        <div
          style={{
            fontSize: "10px",
            color: "#5a5248",
            marginTop: "2px",
            fontFamily: "Menlo, monospace",
            letterSpacing: "0.03em",
          }}
        >
          {check.kind}
        </div>
      </div>
    </motion.div>
  );
}

export default function VerdictPanel({ verdict, visible }: VerdictPanelProps) {
  const isAccepted = verdict.verdict === "accepted";

  return (
    <AnimatePresence mode="wait">
      {visible && (
        <motion.div
          key={verdict.candidate}
          initial={{ opacity: 0, y: 18, scale: 0.98 }}
          animate={{ opacity: 1, y: 0, scale: 1 }}
          exit={{ opacity: 0, y: -8, scale: 0.98 }}
          transition={{
            duration: 0.38,
            ease: [0.34, 1.36, 0.64, 1], // --pc-ease-spring
          }}
          style={{
            background: "#1a1815",
            border: "1px solid #2e2a26",
            borderRadius: "10px",
            overflow: "hidden",
          }}
        >
          {/* Verdict header */}
          <div
            style={{
              padding: "20px 20px 16px",
              borderBottom: "1px solid #2e2a26",
              background: isAccepted
                ? "rgba(42,184,112,0.06)"
                : "rgba(240,64,64,0.06)",
            }}
          >
            {/* Verdict badge */}
            <div
              style={{
                display: "flex",
                alignItems: "center",
                gap: "10px",
                marginBottom: "12px",
              }}
            >
              <div
                style={{
                  display: "flex",
                  alignItems: "center",
                  gap: "8px",
                  padding: "5px 12px",
                  borderRadius: "6px",
                  background: isAccepted
                    ? "rgba(42,184,112,0.15)"
                    : "rgba(240,64,64,0.15)",
                  border: isAccepted
                    ? "1px solid rgba(42,184,112,0.3)"
                    : "1px solid rgba(240,64,64,0.3)",
                }}
              >
                <div
                  style={{
                    width: "7px",
                    height: "7px",
                    borderRadius: "50%",
                    background: isAccepted ? "#2ab870" : "#f04040",
                    boxShadow: isAccepted
                      ? "0 0 6px rgba(42,184,112,0.6)"
                      : "0 0 6px rgba(240,64,64,0.6)",
                  }}
                />
                <span
                  style={{
                    fontFamily: "Menlo, monospace",
                    fontSize: "13px",
                    fontWeight: 700,
                    letterSpacing: "0.06em",
                    color: isAccepted ? "#2ab870" : "#f04040",
                    textTransform: "uppercase",
                  }}
                >
                  {verdict.verdict}
                </span>
              </div>

              {/* Candidate name */}
              <code
                style={{
                  fontFamily: "Menlo, monospace",
                  fontSize: "13px",
                  color: "#9a9088",
                  background: "#221f1c",
                  padding: "3px 8px",
                  borderRadius: "5px",
                  border: "1px solid #2e2a26",
                }}
              >
                {verdict.candidate}
              </code>
            </div>

            {/* Run ID + SHA */}
            <div
              style={{
                display: "flex",
                gap: "16px",
                flexWrap: "wrap",
              }}
            >
              <div style={{ display: "flex", gap: "6px", alignItems: "center" }}>
                <span
                  style={{
                    fontSize: "10px",
                    color: "#5a5248",
                    textTransform: "uppercase",
                    letterSpacing: "0.06em",
                    fontWeight: 600,
                  }}
                >
                  Run
                </span>
                <code
                  style={{
                    fontFamily: "Menlo, monospace",
                    fontSize: "11px",
                    color: "#7a7068",
                  }}
                >
                  {verdict.run_id}
                </code>
              </div>
              <div style={{ display: "flex", gap: "6px", alignItems: "center" }}>
                <span
                  style={{
                    fontSize: "10px",
                    color: "#5a5248",
                    textTransform: "uppercase",
                    letterSpacing: "0.06em",
                    fontWeight: 600,
                  }}
                >
                  SHA
                </span>
                <code
                  style={{
                    fontFamily: "Menlo, monospace",
                    fontSize: "11px",
                    color: "#7a7068",
                  }}
                >
                  {verdict.source_sha256.slice(0, 16)}…
                </code>
              </div>
            </div>

            {/* Reason */}
            <p
              style={{
                fontSize: "12px",
                color: "#8a8078",
                marginTop: "10px",
                lineHeight: 1.5,
              }}
            >
              {verdict.reason}
            </p>
          </div>

          {/* Check summary pills */}
          <div
            style={{
              display: "flex",
              gap: "8px",
              padding: "12px 16px",
              borderBottom: "1px solid #2e2a26",
            }}
          >
            <div
              style={{
                display: "flex",
                alignItems: "center",
                gap: "5px",
                padding: "4px 10px",
                borderRadius: "5px",
                background: "rgba(42,184,112,0.10)",
                border: "1px solid rgba(42,184,112,0.20)",
              }}
            >
              <span style={{ fontSize: "11px", color: "#2ab870", fontWeight: 600 }}>
                {verdict.checks.filter((c) => c.passed).length}
              </span>
              <span style={{ fontSize: "10px", color: "#5a7a6a" }}>passed</span>
            </div>
            <div
              style={{
                display: "flex",
                alignItems: "center",
                gap: "5px",
                padding: "4px 10px",
                borderRadius: "5px",
                background:
                  verdict.checks.filter((c) => !c.passed).length > 0
                    ? "rgba(240,64,64,0.10)"
                    : "rgba(255,255,255,0.04)",
                border:
                  verdict.checks.filter((c) => !c.passed).length > 0
                    ? "1px solid rgba(240,64,64,0.20)"
                    : "1px solid #2e2a26",
              }}
            >
              <span
                style={{
                  fontSize: "11px",
                  fontWeight: 600,
                  color:
                    verdict.checks.filter((c) => !c.passed).length > 0
                      ? "#f04040"
                      : "#5a5248",
                }}
              >
                {verdict.checks.filter((c) => !c.passed).length}
              </span>
              <span style={{ fontSize: "10px", color: "#5a5248" }}>failed</span>
            </div>

            {/* Characterization / Acceptance breakdown */}
            <div
              style={{
                marginLeft: "auto",
                display: "flex",
                gap: "6px",
                alignItems: "center",
              }}
            >
              <div
                style={{
                  fontSize: "10px",
                  padding: "3px 8px",
                  borderRadius: "4px",
                  background: verdict.characterization_passed
                    ? "rgba(42,184,112,0.08)"
                    : "rgba(240,64,64,0.08)",
                  color: verdict.characterization_passed ? "#2ab870" : "#f04040",
                  border: verdict.characterization_passed
                    ? "1px solid rgba(42,184,112,0.2)"
                    : "1px solid rgba(240,64,64,0.2)",
                  fontFamily: "Menlo, monospace",
                  letterSpacing: "0.02em",
                }}
              >
                char {verdict.characterization_passed ? "✓" : "✗"}
              </div>
              <div
                style={{
                  fontSize: "10px",
                  padding: "3px 8px",
                  borderRadius: "4px",
                  background: verdict.acceptance_passed
                    ? "rgba(42,184,112,0.08)"
                    : "rgba(240,64,64,0.08)",
                  color: verdict.acceptance_passed ? "#2ab870" : "#f04040",
                  border: verdict.acceptance_passed
                    ? "1px solid rgba(42,184,112,0.2)"
                    : "1px solid rgba(240,64,64,0.2)",
                  fontFamily: "Menlo, monospace",
                  letterSpacing: "0.02em",
                }}
              >
                accept {verdict.acceptance_passed ? "✓" : "✗"}
              </div>
            </div>
          </div>

          {/* Named checks */}
          <div>
            {verdict.checks.map((check, i) => (
              <motion.div
                key={check.name}
                initial={{ opacity: 0, x: -8 }}
                animate={{ opacity: 1, x: 0 }}
                transition={{
                  duration: 0.25,
                  ease: [0.23, 1, 0.32, 1],
                  delay: 0.05 + i * 0.04,
                }}
              >
                <CheckRow check={check} />
              </motion.div>
            ))}
          </div>
        </motion.div>
      )}
    </AnimatePresence>
  );
}
