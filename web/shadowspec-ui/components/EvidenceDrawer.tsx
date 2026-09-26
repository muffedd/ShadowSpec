"use client";
import { motion, AnimatePresence } from "framer-motion";
import { useState } from "react";
import { VerdictData } from "@/types/verdict";

interface EvidenceDrawerProps {
  verdict: VerdictData;
  open: boolean;
  onToggle: () => void;
}

type Tab = "diff" | "hashes" | "raw";

function DiffView({ diff }: { diff: string }) {
  if (!diff) {
    return (
      <div
        style={{
          padding: "20px",
          color: "#737373",
          fontSize: "12px",
          fontFamily: "Menlo, monospace",
          textAlign: "center",
        }}
      >
        No diff — this is the unchanged baseline.
      </div>
    );
  }

  const lines = diff.split("\n");
  return (
    <pre
      style={{
        margin: 0,
        padding: "12px 0",
        fontSize: "11.5px",
        fontFamily: "Menlo, monospace",
        lineHeight: 1.7,
        overflowX: "auto",
      }}
    >
      {lines.map((line, i) => {
        let cls = "";
        if (line.startsWith("+++") || line.startsWith("---")) {
          cls = "diff-header";
        } else if (line.startsWith("+")) {
          cls = "diff-add";
        } else if (line.startsWith("-")) {
          cls = "diff-remove";
        } else if (line.startsWith("@@")) {
          cls = "diff-header";
        }

        return (
          <div
            key={i}
            className={cls}
            style={{
              padding: "0 16px",
              display: "block",
              whiteSpace: "pre",
            }}
          >
            {line || "\u00A0"}
          </div>
        );
      })}
    </pre>
  );
}

function HashesView({ verdict }: { verdict: VerdictData }) {
  const hashes = [
    {
      label: "candidate_sha256",
      value: verdict.source_sha256,
      desc: `${verdict.candidate}.py`,
    },
    {
      label: "baseline_sha256",
      value: verdict.baseline_sha256,
      desc: "baseline.py",
    },
    {
      label: "validator_sha256",
      value: verdict.validator_sha256,
      desc: "validator.py",
    },
    {
      label: "runner_sha256",
      value: verdict.runner_sha256,
      desc: "embedded runner",
    },
  ];

  return (
    <div style={{ padding: "12px 16px", display: "flex", flexDirection: "column", gap: "8px" }}>
      {hashes.map((h) => (
        <div
          key={h.label}
          style={{
            padding: "10px 12px",
            background: "#fafafa",
            borderRadius: "6px",
            border: "1px solid #fafafa",
          }}
        >
          <div
            style={{
              display: "flex",
              justifyContent: "space-between",
              gap: "8px",
              marginBottom: "4px",
            }}
          >
            <code
              style={{
                fontFamily: "Menlo, monospace",
                fontSize: "10px",
                color: "#171717",
                letterSpacing: "0.02em",
              }}
            >
              {h.label}
            </code>
            <span style={{ fontSize: "10px", color: "#737373" }}>{h.desc}</span>
          </div>
          <code
            style={{
              fontFamily: "Menlo, monospace",
              fontSize: "10.5px",
              color: "#737373",
              wordBreak: "break-all",
              display: "block",
              lineHeight: 1.5,
            }}
          >
            {h.value}
          </code>
        </div>
      ))}
    </div>
  );
}

function RawView({ verdict }: { verdict: VerdictData }) {
  let parsed: unknown = null;
  try {
    parsed = JSON.parse(verdict.output);
  } catch {
    parsed = verdict.output;
  }

  return (
    <pre
      style={{
        margin: 0,
        padding: "12px 16px",
        fontSize: "10.5px",
        fontFamily: "Menlo, monospace",
        color: "#737373",
        lineHeight: 1.7,
        overflowX: "auto",
        whiteSpace: "pre-wrap",
        wordBreak: "break-word",
      }}
    >
      {JSON.stringify(parsed, null, 2)}
    </pre>
  );
}

function buildMarkdownEvidence(verdict: VerdictData): string {
  const checks = verdict.checks
    .map((c) => `- [${c.passed ? "x" : " "}] **${c.kind}**: ${c.name}`)
    .join("\n");

  return `# ShadowSpec evidence pack

**Run ID:** \`${verdict.run_id}\`
**Candidate:** \`${verdict.candidate}\`
**Verdict:** **${verdict.verdict.toUpperCase()}**
**Source SHA-256:** \`${verdict.source_sha256}\`
**Baseline SHA-256:** \`${verdict.baseline_sha256}\`
**Validator SHA-256:** \`${verdict.validator_sha256}\`
**Runner SHA-256:** \`${verdict.runner_sha256}\`

## Provenance

\`\`\`json
${JSON.stringify(
  {
    candidate: verdict.candidate,
    candidate_sha256: verdict.source_sha256,
    baseline: "baseline",
    baseline_sha256: verdict.baseline_sha256,
    validator_sha256: verdict.validator_sha256,
    runner_sha256: verdict.runner_sha256,
  },
  null,
  2
)}
\`\`\`

## Verdict reason

${verdict.reason}

## Named checks

${checks}

## Diff

\`\`\`diff
${verdict.diff || "(no changes from baseline)"}
\`\`\`

## Raw validation output

\`\`\`json
${verdict.output}
\`\`\`
`;
}

export default function EvidenceDrawer({
  verdict,
  open,
  onToggle,
}: EvidenceDrawerProps) {
  const [tab, setTab] = useState<Tab>("diff");

  function handleExport() {
    const md = buildMarkdownEvidence(verdict);
    const blob = new Blob([md], { type: "text/markdown;charset=utf-8" });
    const url = URL.createObjectURL(blob);
    const a = document.createElement("a");
    a.href = url;
    a.download = `shadowspec-evidence-${verdict.candidate}-${verdict.run_id}.md`;
    document.body.appendChild(a);
    a.click();
    document.body.removeChild(a);
    URL.revokeObjectURL(url);
  }

  const tabs: { id: Tab; label: string }[] = [
    { id: "diff", label: "Diff" },
    { id: "hashes", label: "Hashes" },
    { id: "raw", label: "Raw JSON" },
  ];

  return (
    <div
      style={{
        borderTop: "1px solid #e5e5e5",
        background: "#fafafa",
        flexShrink: 0,
      }}
    >
      {/* Drawer toggle header */}
      <button
        onClick={onToggle}
        className="btn-press"
        style={{
          display: "flex",
          alignItems: "center",
          justifyContent: "space-between",
          width: "100%",
          padding: "10px 20px",
          background: "transparent",
          border: "none",
          cursor: "pointer",
          color: "#737373",
        }}
      >
        <div style={{ display: "flex", alignItems: "center", gap: "8px" }}>
          <svg
            width="12"
            height="12"
            viewBox="0 0 12 12"
            fill="none"
            style={{
              transform: open ? "rotate(180deg)" : "rotate(0deg)",
              transition: "transform 200ms ease",
            }}
          >
            <path
              d="M2 4.5L6 8L10 4.5"
              stroke="currentColor"
              strokeWidth="1.5"
              strokeLinecap="round"
              strokeLinejoin="round"
            />
          </svg>
          <span
            style={{
              fontSize: "11px",
              fontWeight: 600,
              letterSpacing: "0.06em",
              textTransform: "uppercase",
              color: "#737373",
            }}
          >
            Evidence
          </span>
          <span
            style={{
              fontSize: "10px",
              color: "#d4d4d4",
              fontFamily: "Menlo, monospace",
            }}
          >
            {verdict.candidate} · {verdict.run_id}
          </span>
        </div>

        {/* Export button */}
        <button
          onClick={(e) => {
            e.stopPropagation();
            handleExport();
          }}
          className="btn-press"
          style={{
            display: "flex",
            alignItems: "center",
            gap: "5px",
            padding: "4px 10px",
            background: "#ffffff",
            border: "1px solid #e5e5e5",
            borderRadius: "6px",
            cursor: "pointer",
            color: "#737373",
            fontSize: "11px",
            fontWeight: 500,
            transition: "background 150ms ease, border-color 150ms ease",
          }}
          onMouseEnter={(e) => {
            (e.currentTarget as HTMLButtonElement).style.background = "#e5e5e5";
            (e.currentTarget as HTMLButtonElement).style.borderColor = "#171717";
          }}
          onMouseLeave={(e) => {
            (e.currentTarget as HTMLButtonElement).style.background = "#ffffff";
            (e.currentTarget as HTMLButtonElement).style.borderColor = "#e5e5e5";
          }}
        >
          <svg width="11" height="11" viewBox="0 0 11 11" fill="none">
            <path
              d="M5.5 1v6M2.5 4.5L5.5 7.5L8.5 4.5M2 9.5h7"
              stroke="currentColor"
              strokeWidth="1.2"
              strokeLinecap="round"
              strokeLinejoin="round"
            />
          </svg>
          Export .md
        </button>
      </button>

      {/* Animated drawer body */}
      <AnimatePresence initial={false}>
        {open && (
          <motion.div
            initial={{ height: 0, opacity: 0 }}
            animate={{ height: 320, opacity: 1 }}
            exit={{ height: 0, opacity: 0 }}
            transition={{ duration: 0.28, ease: [0.23, 1, 0.32, 1] }}
            style={{ overflow: "hidden" }}
          >
            <div style={{ height: 320, display: "flex", flexDirection: "column" }}>
              {/* Tab bar */}
              <div
                style={{
                  display: "flex",
                  gap: "2px",
                  padding: "0 16px",
                  borderBottom: "1px solid #e5e5e5",
                }}
              >
                {tabs.map((t) => (
                  <button
                    key={t.id}
                    onClick={() => setTab(t.id)}
                    style={{
                      padding: "7px 12px",
                      background: "transparent",
                      border: "none",
                      borderBottom:
                        tab === t.id
                          ? "2px solid #171717"
                          : "2px solid transparent",
                      cursor: "pointer",
                      fontSize: "11px",
                      fontWeight: tab === t.id ? 600 : 400,
                      color: tab === t.id ? "#0a0a0a" : "#737373",
                      transition: "color 150ms ease, border-color 150ms ease",
                      marginBottom: "-1px",
                    }}
                  >
                    {t.label}
                  </button>
                ))}
              </div>

              {/* Tab content */}
              <div style={{ flex: 1, overflowY: "auto" }}>
                {tab === "diff" && <DiffView diff={verdict.diff} />}
                {tab === "hashes" && <HashesView verdict={verdict} />}
                {tab === "raw" && <RawView verdict={verdict} />}
              </div>
            </div>
          </motion.div>
        )}
      </AnimatePresence>
    </div>
  );
}
