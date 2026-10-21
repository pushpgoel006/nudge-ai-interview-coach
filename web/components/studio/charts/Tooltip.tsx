"use client";

import { useCallback, useRef, useState } from "react";

export type Tip = { x: number; y: number; title: string; lines: string[] };

/**
 * A tooltip for SVG charts. `show` takes the element being pointed at, so it works for mouse hover AND keyboard
 * focus, and places the tip above that element's centre, relative to the element carrying `wrapRef`.
 *
 * Usage:
 *   const { wrapRef, tip, show, hide } = useChartTip();
 *   <div ref={wrapRef} className="chartwrap" onKeyDown={(e) => e.key === "Escape" && hide()}> ...svg... <TipView tip={tip} /> </div>
 */
export function useChartTip() {
  const wrapRef = useRef<HTMLDivElement>(null);
  const [tip, setTip] = useState<Tip | null>(null);

  const show = useCallback((target: Element, title: string, lines: string[] = []) => {
    const box = wrapRef.current?.getBoundingClientRect();
    if (!box) return;
    const rect = target.getBoundingClientRect();
    setTip({ x: rect.left + rect.width / 2 - box.left, y: rect.top - box.top, title, lines });
  }, []);
  const hide = useCallback(() => setTip(null), []);

  return { wrapRef, tip, show, hide };
}

export function TipView({ tip }: { tip: Tip | null }) {
  if (!tip) return null;
  return (
    <div className="ctip" role="tooltip" style={{ left: tip.x, top: tip.y }}>
      <strong>{tip.title}</strong>
      {tip.lines.map((line) => (
        <span key={line}>{line}</span>
      ))}
    </div>
  );
}
