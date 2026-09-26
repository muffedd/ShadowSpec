import { useState, useCallback } from "react";
import { AnimatePresence, motion } from "framer-motion";
import CandidateRail from "@/components/CandidateRail";
import VerdictPanel from "@/components/VerdictPanel";
import EvidenceDrawer from "@/components/EvidenceDrawer";
import ScanAnimation from "@/components/ScanAnimation";
import { CandidateKey, VerdictData } from "@/types/verdict";

// Precomputed verdicts bundled at build time
import baselineVerdict from "@/public/verdicts/baseline.json";
import badVerdict from "@/public/verdicts/bad.json";
import narrowVerdict from "@/public/verdicts/narrow.json";

const VERDICTS: Record<CandidateKey, VerdictData> = {
  baseline: baselineVerdict as VerdictData,
  bad: badVerdict as VerdictData,
  narrow: narrowVerdict as VerdictData,
};

type Phase = "idle" | "scanning" | "done";

export default function WorkbenchPage() {
  const [selected, setSelected] = useState<CandidateKey>("narrow");
  const [phase, setPhase] = useState<Phase>("done");
  const [drawerOpen, setDrawerOpen] = useState(false);

  const handleSelect = useCallback((key: CandidateKey) => {
    if (key === selected && phase === "done") return;
    setSelected(key);
    setPhase("scanning");
    setDrawerOpen(false);
  }, [selected, phase]);

  const handleScanComplete = useCallback(() => {
    setPhase("done");
  }, []);

  const verdict = VERDICTS[selected];
  const isAccepted = verdict.verdict === "accepted";

  return (
    <div
      style={{
        display: "flex",
        flexDirection: "column",
        height: "100vh",
        background: "#0f0e0d",
        overflow: "hidden",
      }}
    >
      {/* Top bar */}
      <header
        style={{
          height: "44px",
          background: "#141210",
          borderBottom: "1px solid #2e2a26",
          display: "flex",
          alignItems: "center",
          padding: "0 20px",
          gap: "12px",
          flexShrink: 0,
          zIndex: 10,
        }}
      >
        {/* Logo mark */}
        <svg width="18" height="18" viewBox="0 0 18 18" fill="none">
          <rect width="18" height="18" rx="4" fill="#F94612" />
          <path
            d="M5 6h8M5 9h5M5 12h7"
            stroke="#fff"
            strokeWidth="1.5"
            strokeLinecap="round"
          />
        </svg>

        <span
          style={{
            fontFamily: "'Suisse Intl Trial', 'Suisse Intl', Satoshi, sans-serif",
            fontSize: "14px",
            fontWeight: 600,
            color: "#f0ece8",
            letterSpacing: "-0.01em",
          }}
        >
          ShadowSpec
        </span>

        <span
          style={{
            fontSize: "11px",
            color: "#4a4440",
            fontFamily: "Menlo, monospace",
            marginLeft: "4px",
          }}
        >
          / judge workbench
        </span>

        <div style={{ flex: 1 }} />

        {/* Current verdict indicator */}
        <AnimatePresence mode="wait">
          {phase === "done" && (
            <motion.div
              key={`${selected}-header`}
              initial={{ opacity: 0, scale: 0.9 }}
              animate={{ opacity: 1, scale: 1 }}
              exit={{ opacity: 0, scale: 0.9 }}
              transition={{ duration: 0.2, ease: [0.23, 1, 0.32, 1] }}
              style={{
                display: "flex",
                alignItems: "center",
                gap: "6px",
                padding: "3px 10px",
                borderRadius: "6px",
                background: isAccepted
                  ? "rgba(42,184,112,0.12)"
                  : "rgba(240,64,64,0.12)",
                border: isAccepted
                  ? "1px solid rgba(42,184,112,0.25)"
                  : "1px solid rgba(240,64,64,0.25)",
              }}
            >
              <div
                style={{
                  width: "6px",
                  height: "6px",
                  borderRadius: "50%",
                  background: isAccepted ? "#2ab870" : "#f04040",
                }}
              />
              <code
                style={{
                  fontFamily: "Menlo, monospace",
                  fontSize: "11px",
                  fontWeight: 600,
                  color: isAccepted ? "#2ab870" : "#f04040",
                  letterSpacing: "0.05em",
                  textTransform: "uppercase",
                }}
              >
                {verdict.verdict}
              </code>
            </motion.div>
          )}
        </AnimatePresence>
      </header>

      {/* Body: rail + main */}
      <div style={{ flex: 1, display: "flex", overflow: "hidden" }}>
        {/* Left rail */}
        <CandidateRail
          selected={selected}
          onSelect={handleSelect}
          verdicts={VERDICTS}
        />

        {/* Main content */}
        <main
          style={{
            flex: 1,
            display: "flex",
            flexDirection: "column",
            overflow: "hidden",
            background: "#0f0e0d",
          }}
        >
          {/* Scrollable verdict area */}
          <div
            style={{
              flex: 1,
              overflowY: "auto",
              padding: "24px",
              display: "flex",
              flexDirection: "column",
              gap: "20px",
            }}
          >
            {/* Panel header */}
            <div
              style={{
                display: "flex",
                alignItems: "center",
                justifyContent: "space-between",
              }}
            >
              <div>
                <div
                  style={{
                    fontSize: "10px",
                    fontWeight: 600,
                    letterSpacing: "0.08em",
                    color: "#5a5248",
                    textTransform: "uppercase",
                    fontFamily: "Menlo, monospace",
                    marginBottom: "4px",
                  }}
                >
                  Verdict
                </div>
                <h1
                  style={{
                    fontSize: "16px",
                    fontWeight: 600,
                    color: "#f0ece8",
                    letterSpacing: "-0.02em",
                    margin: 0,
                  }}
                >
                  {selected}
                </h1>
              </div>

              {/* Re-run button */}
              <button
                onClick={() => {
                  setPhase("scanning");
                  setDrawerOpen(false);
                }}
                disabled={phase === "scanning"}
                className="btn-press"
                style={{
                  display: "flex",
                  alignItems: "center",
                  gap: "6px",
                  padding: "7px 14px",
                  background: phase === "scanning" ? "#221f1c" : "#F94612",
                  border: "none",
                  borderRadius: "8px",
                  cursor: phase === "scanning" ? "not-allowed" : "pointer",
                  color: phase === "scanning" ? "#5a5248" : "#fff",
                  fontSize: "13px",
                  fontWeight: 600,
                  opacity: phase === "scanning" ? 0.5 : 1,
                  transition: "background 150ms ease, opacity 150ms ease",
                }}
                onMouseEnter={(e) => {
                  if (phase !== "scanning") {
                    (e.currentTarget as HTMLButtonElement).style.background =
                      "#D93A0B";
                  }
                }}
                onMouseLeave={(e) => {
                  if (phase !== "scanning") {
                    (e.currentTarget as HTMLButtonElement).style.background =
                      "#F94612";
                  }
                }}
              >
                <svg width="12" height="12" viewBox="0 0 12 12" fill="none">
                  <path
                    d="M2 6a4 4 0 1 1 4 4M2 6l2-2M2 6l2 2"
                    stroke="currentColor"
                    strokeWidth="1.4"
                    strokeLinecap="round"
                    strokeLinejoin="round"
                  />
                </svg>
                {phase === "scanning" ? "Scanning…" : "Re-run"}
              </button>
            </div>

            {/* Scanning state: canvas animation */}
            <AnimatePresence mode="wait">
              {phase === "scanning" && (
                <motion.div
                  key="scanning"
                  initial={{ opacity: 0, scale: 0.97 }}
                  animate={{ opacity: 1, scale: 1 }}
                  exit={{ opacity: 0, scale: 0.97 }}
                  transition={{ duration: 0.22, ease: [0.23, 1, 0.32, 1] }}
                  style={{
                    display: "flex",
                    flexDirection: "column",
                    alignItems: "center",
                    gap: "16px",
                    padding: "32px 0",
                  }}
                >
                  <ScanAnimation
                    running={phase === "scanning"}
                    onComplete={handleScanComplete}
                  />
                  <div
                    style={{
                      display: "flex",
                      alignItems: "center",
                      gap: "8px",
                      color: "#F94612",
                      fontSize: "12px",
                      fontFamily: "Menlo, monospace",
                      letterSpacing: "0.04em",
                    }}
                  >
                    <motion.div
                      animate={{ opacity: [1, 0.3, 1] }}
                      transition={{ duration: 1.2, repeat: Infinity, ease: "easeInOut" }}
                      style={{
                        width: "6px",
                        height: "6px",
                        borderRadius: "50%",
                        background: "#F94612",
                      }}
                    />
                    Running checks…
                  </div>
                </motion.div>
              )}
            </AnimatePresence>

            {/* Verdict panel (springs in after scan) */}
            <VerdictPanel
              verdict={verdict}
              visible={phase === "done"}
            />
          </div>

          {/* Evidence drawer (pinned to bottom) */}
          <EvidenceDrawer
            verdict={verdict}
            open={drawerOpen && phase === "done"}
            onToggle={() => {
              if (phase === "done") setDrawerOpen((v) => !v);
            }}
          />
        </main>
      </div>
    </div>
  );
}
