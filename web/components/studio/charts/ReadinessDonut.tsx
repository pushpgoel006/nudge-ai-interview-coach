"use client";

import { useEffect, useState } from "react";
import { TipView, useChartTip } from "./Tooltip";

type Segment = { key: string; label: string; short: string; points: number; max: number; detail: string; fill: string; stroke: string };

const R = 74;
const C = 2 * Math.PI * R;

/**
 * Readiness as a donut. With both a theory score and a resume check, the ring is split the way the score is
 * computed (60% theory, 40% resume fit) and the empty part is "room to grow". Hover or focus a slice, or click
 * its legend entry, to see its share.
 */
export function ReadinessDonut({
  readiness,
  theoryAverage,
  resumeFit,
}: {
  readiness: number | null;
  theoryAverage: number | null;
  resumeFit: number | null;
}) {
  const [grown, setGrown] = useState(false);
  const [hover, setHover] = useState<string | null>(null);
  const [locked, setLocked] = useState<string | null>(null);
  const { wrapRef, tip, show, hide } = useChartTip();

  useEffect(() => {
    const frame = requestAnimationFrame(() => setGrown(true));
    return () => cancelAnimationFrame(frame);
  }, []);

  if (readiness === null) {
    return <p className="empty">Run a resume check or answer a theory question to see your readiness.</p>;
  }

  const both = theoryAverage !== null && resumeFit !== null;
  const segments: Segment[] = both
    ? [
        {
          key: "theory",
          label: "Theory",
          short: "Theory",
          points: Math.round(0.6 * theoryAverage * 10),
          max: 60,
          detail: `${theoryAverage.toFixed(1)}/10 average, worth up to 60`,
          fill: "#111111",
          stroke: "#111111",
        },
        {
          key: "resume",
          label: "Resume fit",
          short: "Resume",
          points: Math.round(0.4 * resumeFit),
          max: 40,
          detail: `${resumeFit}/100 fit, worth up to 40`,
          fill: "#f9bb5f",
          stroke: "#111111",
        },
      ]
    : [
        {
          key: theoryAverage !== null ? "theory" : "resume",
          label: theoryAverage !== null ? "Theory only" : "Resume fit only",
          short: theoryAverage !== null ? "Theory" : "Resume",
          points: readiness,
          max: 100,
          detail: theoryAverage !== null ? `${theoryAverage.toFixed(1)}/10 average (no resume check yet)` : `${resumeFit}/100 fit (no theory answers yet)`,
          fill: theoryAverage !== null ? "#111111" : "#f9bb5f",
          stroke: "#111111",
        },
      ];

  const used = segments.reduce((sum, s) => sum + s.points, 0);
  const active = segments.find((s) => s.key === (hover ?? locked)) ?? null;
  let offset = 0;

  return (
    <div ref={wrapRef} className="chartwrap donut" onKeyDown={(e) => e.key === "Escape" && hide()}>
      <svg viewBox="0 0 200 200" role="group" aria-label={`Readiness ${readiness} out of 100`}>
        <circle cx="100" cy="100" r={R} className="donut__track" />
        {segments.map((s) => {
          const length = grown ? (s.points / 100) * C : 0;
          const start = (offset / 100) * C;
          offset += s.points;
          const dim = active && active.key !== s.key;
          return (
            <circle
              key={s.key}
              cx="100"
              cy="100"
              r={R}
              className={`donut__arc${dim ? " is-dim" : ""}`}
              style={{ stroke: s.fill, strokeDasharray: `${length} ${C - length}`, strokeDashoffset: -start }}
              tabIndex={0}
              role="img"
              aria-label={`${s.label}: ${s.points} of ${s.max} points. ${s.detail}`}
              onMouseEnter={(e) => {
                setHover(s.key);
                show(e.currentTarget, s.label, [`${s.points} of ${s.max} points`, s.detail]);
              }}
              onMouseLeave={() => {
                setHover(null);
                hide();
              }}
              onFocus={(e) => {
                setHover(s.key);
                show(e.currentTarget, s.label, [`${s.points} of ${s.max} points`, s.detail]);
              }}
              onBlur={() => {
                setHover(null);
                hide();
              }}
              onClick={() => setLocked((k) => (k === s.key ? null : s.key))}
            />
          );
        })}
        <text x="100" y="98" textAnchor="middle" className="donut__num">
          {active ? active.points : readiness}
        </text>
        <text x="100" y="120" textAnchor="middle" className="donut__sub">
          {active ? `of ${active.max} · ${active.short}` : "readiness / 100"}
        </text>
      </svg>

      <ul className="legend" aria-label="Readiness breakdown">
        {segments.map((s) => (
          <li key={s.key}>
            <button
              type="button"
              className={`legend__btn${locked === s.key ? " is-on" : ""}`}
              aria-pressed={locked === s.key}
              onClick={() => setLocked((k) => (k === s.key ? null : s.key))}
              onMouseEnter={() => setHover(s.key)}
              onMouseLeave={() => setHover(null)}
            >
              <i className="swatch" style={{ background: s.fill, borderColor: s.stroke }} aria-hidden="true" />
              <span>
                <b>
                  {s.label}: {s.points}
                </b>
                <small>{s.detail}</small>
              </span>
            </button>
          </li>
        ))}
        {both && (
          <li>
            <span className="legend__btn legend__btn--static">
              <i className="swatch swatch--empty" aria-hidden="true" />
              <span>
                <b>Room to grow: {Math.max(0, 100 - used)}</b>
                <small>points still available</small>
              </span>
            </span>
          </li>
        )}
      </ul>
      <TipView tip={tip} />
    </div>
  );
}
