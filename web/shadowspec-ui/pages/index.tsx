import { useState, useCallback } from "react";
import Head from "next/head";
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
    <>
      <Head>
        <title>ShadowSpec - behavior firewall for legacy code changes</title>
        <meta
          name="description"
          content="Reject the broad patch. Accept the narrow one. Export the proof. ShadowSpec freezes observed legacy behavior, rejects an over-broad patch, accepts the minimal patch, and exports reviewer-ready evidence."
        />
        <meta property="og:title" content="ShadowSpec - behavior firewall for legacy code changes" />
        <meta
          property="og:description"
          content="Reject the broad patch. Accept the narrow one. Export the proof. A zero-key evidence workbench for legacy maintenance, built with IBM Bob."
        />
        <meta property="og:type" content="website" />
        <meta property="og:url" content="https://shadowspec-demo.pages.dev/" />
        <meta name="twitter:card" content="summary" />
      </Head>
    <div
      style={{
        display: "flex",
        flexDirection: "column",
        height: "100vh",
        background: "#f5f5f5",
        overflow: "hidden",
      }}
    >
      {/* Top bar */}
      <header
        style={{
          height: "44px",
          background: "#fafafa",
          borderBottom: "1px solid #e5e5e5",
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
          <rect width="18" height="18" rx="4" fill="#171717" />
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
            color: "#0a0a0a",
            letterSpacing: "-0.01em",
          }}
        >
          ShadowSpec
        </span>

        <span
          style={{
            fontSize: "11px",
            color: "#d4d4d4",
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
                  ? "#f5f5f5"
                  : "#fdecec",
                border: isAccepted
                  ? "1px solid rgba(23,23,23,0.25)"
                  : "1px solid rgba(231,0,11,0.25)",
              }}
            >
              <div
                style={{
                  width: "6px",
                  height: "6px",
                  borderRadius: "50%",
                  background: isAccepted ? "#171717" : "#e7000b",
                }}
              />
              <code
                style={{
                  fontFamily: "Menlo, monospace",
                  fontSize: "11px",
                  fontWeight: 600,
                  color: isAccepted ? "#171717" : "#e7000b",
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
            background: "#f5f5f5",
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
                    color: "#737373",
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
                    color: "#0a0a0a",
                    letterSpacing: "-0.02em",
                    margin: 0,
                  }}
                >
                  {selected}
                </h1>
              </div>

              {/* Replay verdict button — replays the animation over the precomputed build-time verdict */}
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
                  background: phase === "scanning" ? "#ffffff" : "#171717",
                  border: "none",
                  borderRadius: "18px",
                  cursor: phase === "scanning" ? "not-allowed" : "pointer",
                  color: phase === "scanning" ? "#737373" : "#fff",
                  fontSize: "13px",
                  fontWeight: 600,
                  opacity: phase === "scanning" ? 0.5 : 1,
                  transition: "background 150ms ease, opacity 150ms ease",
                }}
                onMouseEnter={(e) => {
                  if (phase !== "scanning") {
                    (e.currentTarget as HTMLButtonElement).style.background =
                      "#0a0a0a";
                  }
                }}
                onMouseLeave={(e) => {
                  if (phase !== "scanning") {
                    (e.currentTarget as HTMLButtonElement).style.background =
                      "#171717";
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
                {phase === "scanning" ? "Replaying…" : "Replay verdict"}
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
                      color: "#171717",
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
                        background: "#171717",
                      }}
                    />
                    Replaying precomputed verdict…
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
    </>
  );
}
