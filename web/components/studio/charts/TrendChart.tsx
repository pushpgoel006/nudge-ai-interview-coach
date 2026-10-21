"use client";

import { useState } from "react";
import { TipView, useChartTip } from "./Tooltip";

export type TrendPoint = { date: string | null; topic: string | null; score: number };
type Kind = "theory" | "dsa";
type Event = TrendPoint & { kind: Kind; at: number };

const W = 620;
const H = 240;
const PAD = { l: 34, r: 16, t: 14, b: 30 };

const dateLabel = (iso: string | null) =>
  iso ? new Date(iso.endsWith("Z") ? iso : iso + "Z").toLocaleDateString(undefined, { day: "numeric", month: "short" }) : "";
const stamp = (iso: string | null) => (iso ? new Date(iso.endsWith("Z") ? iso : iso + "Z").getTime() : Number.MAX_SAFE_INTEGER);

/**
 * Scores over time, oldest to newest. Theory answers are solid with round markers, DSA attempts are dashed with
 * square markers, so the two stay distinguishable without colour. Toggle a series with its button; hover or focus a
 * marker for the topic, score and date.
 */
export function TrendChart({ theory, dsa }: { theory: TrendPoint[]; dsa: TrendPoint[] }) {
  const [shown, setShown] = useState<Record<Kind, boolean>>({ theory: true, dsa: true });
  const { wrapRef, tip, show, hide } = useChartTip();

  const events: Event[] = [
    ...theory.map((p) => ({ ...p, kind: "theory" as const, at: stamp(p.date) })),
    ...dsa.map((p) => ({ ...p, kind: "dsa" as const, at: stamp(p.date) })),
  ]
    .filter((e) => shown[e.kind])
    .sort((a, b) => a.at - b.at);

  const n = events.length;
  const x = (i: number) => (n <= 1 ? (W + PAD.l - PAD.r) / 2 : PAD.l + (i * (W - PAD.l - PAD.r)) / (n - 1));
  const y = (score: number) => PAD.t + (1 - score / 10) * (H - PAD.t - PAD.b);

  const line = (kind: Kind) =>
    events
      .map((e, i) => ({ e, i }))
      .filter(({ e }) => e.kind === kind)
      .map(({ e, i }) => `${x(i)},${y(e.score)}`)
      .join(" ");

  const toggles: { kind: Kind; label: string; count: number }[] = [
    { kind: "theory", label: "Theory answers", count: theory.length },
    { kind: "dsa", label: "DSA attempts", count: dsa.length },
  ];

  return (
    <div>
      <div className="legend legend--row" role="group" aria-label="Series">
        {toggles.map((t) => (
          <button
            key={t.kind}
            type="button"
            className={`legend__btn${shown[t.kind] ? " is-on" : ""}`}
            aria-pressed={shown[t.kind]}
            disabled={t.count === 0}
            onClick={() => setShown((s) => ({ ...s, [t.kind]: !s[t.kind] }))}
          >
            <svg width="26" height="14" viewBox="0 0 26 14" aria-hidden="true">
              {t.kind === "theory" ? (
                <>
                  <line x1="0" y1="7" x2="26" y2="7" stroke="#111" strokeWidth="2" />
                  <circle cx="13" cy="7" r="4.5" fill="#111" />
                </>
              ) : (
                <>
                  <line x1="0" y1="7" x2="26" y2="7" stroke="#111" strokeWidth="2" strokeDasharray="5 3" />
                  <rect x="8.5" y="2.5" width="9" height="9" fill="#de8fc6" stroke="#111" strokeWidth="1.5" />
                </>
              )}
            </svg>
            <span>
              <b>{t.label}</b>
              <small>{t.count} so far</small>
            </span>
          </button>
        ))}
      </div>

      <div ref={wrapRef} className="chartwrap" onKeyDown={(e) => e.key === "Escape" && hide()}>
        {n === 0 ? (
          <p className="empty">Nothing to plot. Turn a series back on, or practise a round.</p>
        ) : (
          <svg viewBox={`0 0 ${W} ${H}`} className="linechart" role="group" aria-label={`Score trend, ${n} points, oldest to newest`}>
            {[0, 5, 10].map((g) => (
              <g key={g}>
                <line x1={PAD.l} x2={W - PAD.r} y1={y(g)} y2={y(g)} className="grid" />
                <text x={PAD.l - 8} y={y(g) + 4} textAnchor="end" className="axis">
                  {g}
                </text>
              </g>
            ))}
            <text x={PAD.l} y={H - 8} className="axis">
              Oldest
            </text>
            <text x={W - PAD.r} y={H - 8} textAnchor="end" className="axis">
              Newest
            </text>

            {shown.theory && theory.length > 1 && <polyline points={line("theory")} className="series series--theory" />}
            {shown.dsa && dsa.length > 1 && <polyline points={line("dsa")} className="series series--dsa" />}

            {events.map((e, i) => {
              const label = `${e.kind === "theory" ? "Theory" : "DSA"}, ${e.topic ?? "no topic"}, ${e.score} out of 10`;
              const lines = [`${e.score}/10`, dateLabel(e.date)].filter(Boolean);
              const common = {
                tabIndex: 0,
                role: "img" as const,
                "aria-label": label,
                onMouseEnter: (ev: React.MouseEvent<SVGElement>) => show(ev.currentTarget, `${e.kind === "theory" ? "Theory" : "DSA"} · ${e.topic ?? "no topic"}`, lines),
                onFocus: (ev: React.FocusEvent<SVGElement>) => show(ev.currentTarget, `${e.kind === "theory" ? "Theory" : "DSA"} · ${e.topic ?? "no topic"}`, lines),
                onMouseLeave: hide,
                onBlur: hide,
              };
              return e.kind === "theory" ? (
                <circle key={`${e.kind}-${i}`} cx={x(i)} cy={y(e.score)} r={6} className="marker marker--theory" {...common} />
              ) : (
                <rect key={`${e.kind}-${i}`} x={x(i) - 6} y={y(e.score) - 6} width={12} height={12} className="marker marker--dsa" {...common} />
              );
            })}
          </svg>
        )}
        <TipView tip={tip} />
      </div>

      <details className="numbers">
        <summary className="help">Show the numbers</summary>
        <table>
          <thead>
            <tr>
              <th scope="col">#</th>
              <th scope="col">Type</th>
              <th scope="col">Topic</th>
              <th scope="col">Score</th>
              <th scope="col">Date</th>
            </tr>
          </thead>
          <tbody>
            {events.map((e, i) => (
              <tr key={`${e.kind}-${i}`}>
                <td>{i + 1}</td>
                <td>{e.kind === "theory" ? "Theory" : "DSA"}</td>
                <td>{e.topic ?? "—"}</td>
                <td>{e.score}/10</td>
                <td>{dateLabel(e.date)}</td>
              </tr>
            ))}
          </tbody>
        </table>
      </details>
    </div>
  );
}
