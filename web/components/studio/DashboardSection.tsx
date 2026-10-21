"use client";

import Link from "next/link";
import { useRouter } from "next/navigation";
import { useCallback, useEffect, useState } from "react";
import { api, ApiError, type Source } from "@/lib/api";
import { ReadinessDonut } from "./charts/ReadinessDonut";
import { TopicStrength, type TopicKind, type TopicScore } from "./charts/TopicStrength";
import { TrendChart, type TrendPoint } from "./charts/TrendChart";
import { CountUp } from "./CountUp";
import { DOC_TYPES } from "./DocumentsSection";
import { Markdown } from "./Markdown";
import { Section } from "./Section";
import { useSlot, useStudio } from "./StudioContext";

type Dash = {
  readiness: number | null;
  theory_average: number | null;
  resume_fit: number | null;
  dsa_average: number | null;
  theory_count: number;
  dsa_attempts: number;
  trend: TrendPoint[];
  dsa_trend: TrendPoint[];
  by_topic: TopicScore[];
  weakest: TopicScore[];
  dsa_topics: TopicScore[];
};
type Advice = { advice: string; sources: Source[] };

function Kpi({
  href,
  title,
  value,
  suffix,
  caption,
  decimals = 0,
}: {
  href: string;
  title: string;
  value: number | null;
  suffix: string;
  caption: string;
  decimals?: number;
}) {
  return (
    <Link href={href} className="kpi kpi--link">
      <span>{title}</span>
      <strong>
        {value === null ? "—" : <CountUp value={value} decimals={decimals} />}
        {value !== null && <small>{suffix}</small>}
      </strong>
      <span>{caption}</span>
    </Link>
  );
}

export function DashboardSection() {
  const router = useRouter();
  const { session, dataVersion, setPracticeTopic } = useStudio();
  const [, setDsaTopic] = useSlot("dsa:topic", "array");
  const [dash, setDash] = useState<Dash | null>(null);
  const [error, setError] = useState<string | null>(null);
  const [selected, setSelected] = useState<{ kind: TopicKind; topic: string } | null>(null);
  const [advice, setAdvice] = useState<Record<string, Advice>>({});
  const [adviceBusy, setAdviceBusy] = useState(false);
  const [adviceError, setAdviceError] = useState<string | null>(null);

  const load = useCallback(async () => {
    try {
      setDash(await api.get<Dash>(`/sessions/${session.id}/dashboard`));
      setError(null);
    } catch (err) {
      setError(err instanceof ApiError ? err.message : "Could not load the dashboard.");
    }
  }, [session.id]);

  useEffect(() => {
    // Re-fetch whenever a round, review or attempt changes the numbers.
    // eslint-disable-next-line react-hooks/set-state-in-effect
    void load();
  }, [load, dataVersion]);

  async function getAdvice(topic: string) {
    setAdviceError(null);
    setAdviceBusy(true);
    try {
      const a = await api.post<Advice>(`/sessions/${session.id}/dashboard/recommendation`, { topic });
      setAdvice((m) => ({ ...m, [topic]: a }));
    } catch (err) {
      setAdviceError(err instanceof ApiError ? err.message : "Could not get advice.");
    } finally {
      setAdviceBusy(false);
    }
  }

  function practise(kind: TopicKind, topic: string) {
    if (kind === "theory") {
      setPracticeTopic(topic);
      router.push("/studio/theory");
    } else {
      setDsaTopic(topic);
      router.push("/studio/dsa");
    }
  }

  const empty = dash && dash.readiness === null && dash.dsa_average === null && dash.theory_count === 0 && dash.resume_fit === null;
  const chosen = dash && selected ? (selected.kind === "theory" ? dash.by_topic : dash.dsa_topics).find((t) => t.topic === selected.topic) : null;

  return (
    <Section id="dashboard" title="Dashboard" lead="Where you stand. Hover or focus a chart for detail, and click a topic to act on it.">
      {error && (
        <p className="notice notice--error" role="alert">
          {error}
        </p>
      )}
      {!dash && !error && <p className="help">Loading…</p>}

      {dash && (
        <>
          <div className="kpis">
            <Kpi href="/studio/theory" title="Readiness" value={dash.readiness} suffix="/100" caption="60% theory · 40% resume" />
            <Kpi href="/studio/theory" title="Theory average" value={dash.theory_average} suffix="/10" decimals={1} caption={`${dash.theory_count} scored answer${dash.theory_count === 1 ? "" : "s"}`} />
            <Kpi href="/studio/resume" title="Resume fit" value={dash.resume_fit} suffix="/100" caption={dash.resume_fit === null ? "Not checked yet" : "Latest check"} />
            <Kpi href="/studio/dsa" title="DSA" value={dash.dsa_average} suffix="/10" decimals={1} caption={dash.dsa_attempts ? `${dash.dsa_attempts} attempt${dash.dsa_attempts === 1 ? "" : "s"}` : "Not attempted yet"} />
          </div>

          {empty && (
            <p className="empty">
              Nothing to show yet. Run a <Link href="/studio/resume">resume check</Link> or answer a <Link href="/studio/theory">theory question</Link> and your charts appear here.
            </p>
          )}

          {!empty && (
            <>
              <div className="dashgrid">
                <div className="panel">
                  <h2 className="panel__title">Readiness</h2>
                  <ReadinessDonut readiness={dash.readiness} theoryAverage={dash.theory_average} resumeFit={dash.resume_fit} />
                </div>
                <div className="panel">
                  <h2 className="panel__title">Score trend</h2>
                  {dash.trend.length + dash.dsa_trend.length ? (
                    <TrendChart theory={dash.trend} dsa={dash.dsa_trend} />
                  ) : (
                    <p className="empty">Answer a theory question or submit a DSA solution to see a trend.</p>
                  )}
                </div>
              </div>

              <div className="dashgrid dashgrid--even">
                <div className="panel">
                  <h2 className="panel__title">Topic strength</h2>
                  <TopicStrength theory={dash.by_topic} dsa={dash.dsa_topics} selected={selected} onSelect={setSelected} />
                </div>
                <div className="panel" aria-live="polite">
                  <h2 className="panel__title">{selected && chosen ? chosen.topic : "Pick a topic"}</h2>
                  {!selected || !chosen ? (
                    <p className="help">Click a bar (or a point on the radar) to see the detail and what to do next. The weakest topics are marked.</p>
                  ) : (
                    <>
                      <p>
                        <strong>{chosen.average_score.toFixed(1)}/10</strong> average over {chosen.count} {chosen.count === 1 ? "score" : "scores"} ({selected.kind === "theory" ? "theory" : "DSA"}).
                      </p>
                      <div className="row">
                        <button type="button" className="sbtn sbtn--primary" onClick={() => practise(selected.kind, chosen.topic)}>
                          Practise this
                        </button>
                        <button type="button" className="sbtn" onClick={() => getAdvice(chosen.topic)} disabled={adviceBusy}>
                          {adviceBusy ? "Thinking…" : advice[chosen.topic] ? "Refresh advice" : "Get advice"}
                        </button>
                      </div>
                      {advice[chosen.topic] && (
                        <div className="notice">
                          <Markdown compact>{advice[chosen.topic].advice}</Markdown>
                          {advice[chosen.topic].sources.length > 0 && (
                            <ul className="sources" aria-label="Sources">
                              {advice[chosen.topic].sources.map((s) => (
                                <li key={`${s.file_name}-${s.page}`}>
                                  {s.file_name} · p.{s.page}
                                  {s.doc_type ? ` · ${DOC_TYPES[s.doc_type] ?? s.doc_type}` : ""}
                                </li>
                              ))}
                            </ul>
                          )}
                        </div>
                      )}
                      {adviceError && (
                        <p className="notice notice--error" role="alert">
                          {adviceError}
                        </p>
                      )}
                    </>
                  )}
                </div>
              </div>
            </>
          )}
        </>
      )}
    </Section>
  );
}
