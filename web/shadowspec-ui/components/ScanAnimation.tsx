import { useEffect, useState } from "react";

// Minimal achromatic running state: white card, hairline border, a thin
// sweeping progress line in ink. No glow, no glyph grid, no chromatic accents.
export default function ScanAnimation({
  label = "Replaying precomputed verdict…",
  running = true,
  onComplete,
}: {
  label?: string;
  running?: boolean;
  onComplete?: () => void;
}) {
  const [dots, setDots] = useState(0);
  useEffect(() => {
    const t = setInterval(() => setDots((d) => (d + 1) % 4), 400);
    return () => clearInterval(t);
  }, []);
  useEffect(() => {
    if (!running || !onComplete) return;
    const t = setTimeout(onComplete, 2200);
    return () => clearTimeout(t);
  }, [running, onComplete]);
  return (
    <div
      style={{
        background: "#ffffff",
        border: "1px solid #e5e5e5",
        borderRadius: 24,
        padding: "48px 20px",
        display: "flex",
        flexDirection: "column",
        alignItems: "center",
        gap: 16,
        boxShadow:
          "0 0 0 1px rgba(23,23,23,0.05), 0 1px 3px rgba(0,0,0,0.1), 0 1px 2px -1px rgba(0,0,0,0.1)",
      }}
    >
      <div
        style={{
          width: 180,
          height: 2,
          background: "#e5e5e5",
          borderRadius: 1,
          overflow: "hidden",
          position: "relative",
        }}
      >
        <div
          style={{
            position: "absolute",
            top: 0,
            left: 0,
            height: "100%",
            width: "40%",
            background: "#171717",
            borderRadius: 1,
            animation: "sweep 1.1s cubic-bezier(.23,1,.32,1) infinite",
          }}
        />
      </div>
      <span style={{ fontSize: 13, color: "#737373", fontWeight: 400 }}>
        {label.replace(/…$/, "") + ".".repeat(dots || 1)}
      </span>
      <style jsx>{`
        @keyframes sweep {
          0% { left: -40%; }
          100% { left: 100%; }
        }
      `}</style>
    </div>
  );
}
