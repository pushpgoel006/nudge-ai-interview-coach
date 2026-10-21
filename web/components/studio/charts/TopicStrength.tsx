"use client";

import { useState } from "react";
import { TipView, useChartTip } from "./Tooltip";

export type TopicScore = { topic: string; average_score: number; count: number };
export type TopicKind = "theory" | "dsa";

const SIZE = 340;
const CX = SIZE / 2;
const RADIUS = 106;

function tipLines(t: TopicScore) {
  return [`Average ${t.average_score.toFixed(1)}/10`, `${t.count} ${t.count === 1 ? "score" : "scores"}`];
}

/**
 * Average score per topic, as bars or as a radar. Click (or press Enter on) a topic to select it; the page shows
 * what you can do with it. The three weakest topics are marked.
 */
export function TopicStrength({
  theory,
  dsa,
  selected,
  onSelect,
}: {
  theory: TopicScore[];
  dsa: TopicScore[];
  selected: { kind: TopicKind; topic: string } | null;
  onSelect: (pick: { kind: TopicKind; topic: string } | null) => void;
}) {
  const [kind, setKind] = useState<TopicKind>(theory.length || !dsa.length ? "theory" : "dsa");
  const [view, setView] = useState<"bars" | "radar">("bars");
  const { wrapRef, tip, show, hide } = useChartTip();

  const items = [...(kind === "theory" ? theory : dsa)].sort((a, b) => a.average_score - b.average_score);
  const weakest = new Set(items.slice(0, 3).map((t) => t.topic));
  const radarOk = items.length >= 3;
  const showRadar = view === "radar" && radarOk;
  const isSelected = (topic: string) => selected?.kind === kind && selected.topic === topic;
  const pick = (topic: string) => onSelect(isSelected(topic) ? null : { kind, topic });

  // Radar geometry: topics around the circle, starting at the top.
  const angle = (i: number) => (-Math.PI / 2) + (i * 2 * Math.PI) / items.length;
  const point = (i: number, score: number) => {
    const r = (score / 10) * RADIUS;
    return { x: CX + r * Math.cos(angle(i)), y: CX + r * Math.sin(angle(i)) };
  };

  return (
    <div>
      <div className="toolbar">
        <div className="seg" role="group" aria-label="Which scores">
          {(["theory", "dsa"] as const).map((k) => (
            <button key={k} type="button" aria-pressed={kind === k} className={kind === k ? "is-on" : undefined} onClick={() => setKind(k)}>
              {k === "theory" ? "Theory topics" : "DSA topics"}
            </button>
          ))}
        </div>
        <div className="seg" role="group" aria-label="Chart type">
          {(["bars", "radar"] as const).map((v) => (
            <button key={v} type="button" aria-pressed={view === v} className={view === v ? "is-on" : undefined} onClick={() => setView(v)}>
              {v === "bars" ? "Bars" : "Radar"}
            </button>
          ))}
        </div>
      </div>

      {items.length === 0 ? (
        <p className="empty">
          {kind === "theory" ? "Set a topic in the theory round and answer a few questions to see this." : "Submit a DSA solution to see how each topic is going."}
        </p>
      ) : (
        <div ref={wrapRef} className="chartwrap" onKeyDown={(e) => e.key === "Escape" && hide()}>
          {view === "radar" && !radarOk && <p className="help">Radar needs at least 3 topics, so here are the bars.</p>}

          {!showRadar && (
            <ul className="tbars" aria-label="Average score per topic, weakest first">
              {items.map((t) => (
                <li key={t.topic}>
                  <button
                    type="button"
                    className={`tbar${isSelected(t.topic) ? " is-selected" : ""}`}
                    aria-pressed={isSelected(t.topic)}
                    onClick={() => pick(t.topic)}
                    onMouseEnter={(e) => show(e.currentTarget.querySelector(".tbar__fill") ?? e.currentTarget, t.topic, tipLines(t))}
                    onMouseLeave={hide}
                    onFocus={(e) => show(e.currentTarget.querySelector(".tbar__fill") ?? e.currentTarget, t.topic, tipLines(t))}
                    onBlur={hide}
                  >
                    <span className="tbar__name">
                      {t.topic}
                      {weakest.has(t.topic) && items.length > 3 && <span className="pill pill--warn">Weak spot</span>}
                    </span>
                    <span className="tbar__track">
                      <span className="tbar__fill" style={{ width: `${Math.max(2, t.average_score * 10)}%` }} />
                    </span>
                    <span className="tbar__val">{t.average_score.toFixed(1)}</span>
                  </button>
                </li>
              ))}
            </ul>
          )}

          {showRadar && (
            <svg viewBox={`0 0 ${SIZE} ${SIZE}`} className="radar" role="group" aria-label="Radar of average score per topic">
              {[2.5, 5, 7.5, 10].map((ring) => (
                <polygon key={ring} className="radar__ring" points={items.map((_, i) => { const p = point(i, ring); return `${p.x},${p.y}`; }).join(" ")} />
              ))}
              {items.map((t, i) => {
                const end = point(i, 10);
                const label = point(i, 11.9);
                const anchor = Math.abs(label.x - CX) < 8 ? "middle" : label.x > CX ? "start" : "end";
                return (
                  <g key={t.topic}>
                    <line x1={CX} y1={CX} x2={end.x} y2={end.y} className="radar__axis" />
                    <text x={label.x} y={label.y + 4} textAnchor={anchor} className="axis">
                      {t.topic.length > 16 ? `${t.topic.slice(0, 15)}…` : t.topic}
                    </text>
                  </g>
                );
              })}
              <polygon className="radar__shape" points={items.map((t, i) => { const p = point(i, t.average_score); return `${p.x},${p.y}`; }).join(" ")} />
              {items.map((t, i) => {
                const p = point(i, t.average_score);
                return (
                  <circle
                    key={t.topic}
                    cx={p.x}
                    cy={p.y}
                    r={isSelected(t.topic) ? 8 : 6}
                    className={`marker marker--theory${isSelected(t.topic) ? " is-selected" : ""}`}
                    tabIndex={0}
                    role="button"
                    aria-pressed={isSelected(t.topic)}
                    aria-label={`${t.topic}, average ${t.average_score.toFixed(1)} out of 10 over ${t.count} scores`}
                    onClick={() => pick(t.topic)}
                    onKeyDown={(e) => (e.key === "Enter" || e.key === " ") && (e.preventDefault(), pick(t.topic))}
                    onMouseEnter={(e) => show(e.currentTarget, t.topic, tipLines(t))}
                    onMouseLeave={hide}
                    onFocus={(e) => show(e.currentTarget, t.topic, tipLines(t))}
                    onBlur={hide}
                  />
                );
              })}
            </svg>
          )}
          <TipView tip={tip} />
        </div>
      )}
    </div>
  );
}
