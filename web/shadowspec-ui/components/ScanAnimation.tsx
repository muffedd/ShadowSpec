"use client";
import { useEffect, useRef } from "react";

interface ScanAnimationProps {
  running: boolean;
  onComplete: () => void;
}

// Glyph pool for the grid
const GLYPHS = "ABCDEF0123456789#$%&@!?".split("");
const COLS = 16;
const ROWS = 12;
const CELL = 24; // px per cell

function randomGlyph() {
  return GLYPHS[Math.floor(Math.random() * GLYPHS.length)];
}

export default function ScanAnimation({ running, onComplete }: ScanAnimationProps) {
  const canvasRef = useRef<HTMLCanvasElement>(null);
  const animRef = useRef<number | null>(null);
  const startRef = useRef<number | null>(null);
  const glyphGrid = useRef<string[][]>([]);

  // Initialise glyph grid once
  useEffect(() => {
    glyphGrid.current = Array.from({ length: ROWS }, () =>
      Array.from({ length: COLS }, () => randomGlyph())
    );
  }, []);

  useEffect(() => {
    if (!running) {
      if (animRef.current) cancelAnimationFrame(animRef.current);
      startRef.current = null;
      return;
    }

    const canvas = canvasRef.current;
    if (!canvas) return;
    const ctx = canvas.getContext("2d");
    if (!ctx) return;

    const W = COLS * CELL;
    const H = ROWS * CELL;
    canvas.width = W;
    canvas.height = H;

    const DURATION = 2200; // ms for scan to travel full height

    // Shuffle some glyphs each frame for a shimmer effect
    let frameCount = 0;

    function draw(timestamp: number) {
      if (!ctx || !canvas) return;
      if (startRef.current === null) startRef.current = timestamp;
      const elapsed = timestamp - startRef.current;
      const progress = Math.min(elapsed / DURATION, 1);
      const scanY = progress * H;

      ctx.clearRect(0, 0, W, H);

      // Background
      ctx.fillStyle = "#0f0e0d";
      ctx.fillRect(0, 0, W, H);

      // Shimmer: randomly update a few glyphs
      frameCount++;
      if (frameCount % 3 === 0) {
        for (let i = 0; i < 6; i++) {
          const r = Math.floor(Math.random() * ROWS);
          const c = Math.floor(Math.random() * COLS);
          glyphGrid.current[r][c] = randomGlyph();
        }
      }

      // Draw glyph grid
      ctx.font = `600 ${CELL - 8}px Menlo, monospace`;
      ctx.textBaseline = "middle";
      ctx.textAlign = "center";

      for (let row = 0; row < ROWS; row++) {
        for (let col = 0; col < COLS; col++) {
          const x = col * CELL + CELL / 2;
          const y = row * CELL + CELL / 2;
          const glyphY = row * CELL;

          // Determine color based on scan position
          const distFromScan = glyphY - scanY;

          if (distFromScan < 0 && distFromScan > -CELL * 3) {
            // Just-scanned: orange glow fade
            const fade = 1 + distFromScan / (CELL * 3); // 1..0 as it recedes
            const alpha = 0.4 + fade * 0.6;
            ctx.fillStyle = `rgba(249, 70, 18, ${alpha})`;
          } else if (distFromScan >= 0 && distFromScan < CELL * 2) {
            // Just-ahead of scan: bright lead glow
            const lead = 1 - distFromScan / (CELL * 2);
            const alpha = 0.15 + lead * 0.45;
            ctx.fillStyle = `rgba(249, 70, 18, ${alpha})`;
          } else if (distFromScan < 0) {
            // Already scanned: dim green
            ctx.fillStyle = "rgba(42, 184, 112, 0.55)";
          } else {
            // Unscanned: dark gray
            ctx.fillStyle = "rgba(255,255,255,0.10)";
          }

          ctx.fillText(glyphGrid.current[row][col], x, y);
        }
      }

      // Draw scan line glow
      const glowGradient = ctx.createLinearGradient(0, scanY - 20, 0, scanY + 8);
      glowGradient.addColorStop(0, "rgba(249, 70, 18, 0)");
      glowGradient.addColorStop(0.6, "rgba(249, 70, 18, 0.55)");
      glowGradient.addColorStop(1, "rgba(249, 70, 18, 0.85)");
      ctx.fillStyle = glowGradient;
      ctx.fillRect(0, scanY - 20, W, 28);

      // Sharp scan line
      ctx.fillStyle = "rgba(249, 70, 18, 0.95)";
      ctx.fillRect(0, scanY, W, 1.5);

      if (progress < 1) {
        animRef.current = requestAnimationFrame(draw);
      } else {
        // Hold for a moment then call onComplete
        setTimeout(onComplete, 300);
      }
    }

    startRef.current = null;
    animRef.current = requestAnimationFrame(draw);

    return () => {
      if (animRef.current) cancelAnimationFrame(animRef.current);
    };
  }, [running, onComplete]);

  const W = COLS * CELL;
  const H = ROWS * CELL;

  return (
    <canvas
      ref={canvasRef}
      width={W}
      height={H}
      style={{
        display: "block",
        borderRadius: "8px",
        border: "1px solid rgba(249,70,18,0.2)",
        boxShadow: running ? "0 0 32px rgba(249,70,18,0.15)" : "none",
      }}
    />
  );
}
