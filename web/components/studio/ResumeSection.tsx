"use client";

import { useCallback, useEffect, useState } from "react";
import { api, ApiError } from "@/lib/api";
import { CountUp } from "./CountUp";
import { Markdown } from "./Markdown";
import { NeedDocs } from "./RequireSession";
import { Section } from "./Section";
import { useStudio } from "./StudioContext";

type Verdict = { requirement: string; verdict: string; evidence: string | null };
type Review = {
  overall_score: number;
  matched_skills: string[];
  missing_skills: string[];
  suggestions: string;
  created_at: string | null;
  verdicts: Verdict[] | null;
};

export function ResumeSection() {
  const { session, docCount, bumpData } = useStudio();
  const [review, setReview] = useState<Review | null | undefined>(undefined);
  const [busy, setBusy] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const load = useCallback(async () => {
    try {
      setReview(await api.get<Review | null>(`/sessions/${session.id}/resume`));
    } catch {
      setReview(null);
    }
  }, [session.id]);

  useEffect(() => {
    // Load the last saved review for this session; state is set after the request resolves.
    // eslint-disable-next-line react-hooks/set-state-in-effect
    void load();
  }, [load]);

  async function run() {
    setError(null);
    setBusy(true);
    try {
      setReview(await api.post<Review>(`/sessions/${session.id}/resume/check`));
      bumpData();
    } catch (err) {
      setError(err instanceof ApiError ? err.message : "Something went wrong running the check.");
    } finally {
      setBusy(false);
    }
  }

  const matches = (review?.verdicts ?? []).filter((v) => v.verdict !== "not demonstrated");
  const gaps = (review?.verdicts ?? []).filter((v) => v.verdict === "not demonstrated");

  return (
    <Section
      id="resume"
      title="Resume check"
      lead="Your resume, judged against the job description, requirement by requirement. Needs both documents."
    >
      <NeedDocs needs={["jd", "resume"]} />

      <div className="row">
        <button type="button" className="sbtn sbtn--primary" onClick={run} disabled={busy || docCount === 0}>
          {busy ? "Checking…" : review ? "Run it again" : "Run resume check"}
        </button>
        {busy && (
          <span className="help" role="status">
            <span className="spin" aria-hidden="true" /> Reading both documents. This takes a few seconds.
          </span>
        )}
      </div>

      {error && (
        <p className="notice notice--error" role="alert">
          {error}
        </p>
      )}

      {review === undefined && <p className="help">Loading…</p>}
      {review === null && !busy && <p className="empty">No check yet. Add your resume and the JD above, then run it.</p>}

      {review && (
        <div className="panel">
          <div className="bigscore" aria-label={`Fit score ${review.overall_score} out of 100`}>
            <strong>
              <CountUp key={review.created_at ?? review.overall_score} value={review.overall_score} />
            </strong>
            <span>/100 job fit</span>
          </div>

          {review.verdicts ? (
            <div className="verdicts2">
              <div>
                <h3>What matches ({matches.length})</h3>
                {matches.length === 0 && <p className="help">Nothing in your resume lines up with this role yet.</p>}
                <ul>
                  {matches.map((v) => (
                    <li key={v.requirement}>
                      <span className="vtitle">
                        {v.requirement}
                        {v.verdict === "partially demonstrated" && <span className="pill">Partly</span>}
                      </span>
                      {v.evidence && <span className="ev">{v.evidence}</span>}
                    </li>
                  ))}
                </ul>
              </div>
              <div>
                <h3>What doesn&apos;t ({gaps.length})</h3>
                {gaps.length === 0 && <p className="help">No gaps found. Your resume covers every requirement.</p>}
                <ul>
                  {gaps.map((v) => (
                    <li key={v.requirement}>
                      <span className="vtitle">{v.requirement}</span>
                    </li>
                  ))}
                </ul>
              </div>
            </div>
          ) : (
            <>
              <p className="help">Showing your last saved review. Run it again to see the evidence lines.</p>
              <div className="verdicts2">
                <div>
                  <h3>What matches ({review.matched_skills.length})</h3>
                  <ul>
                    {review.matched_skills.map((s) => (
                      <li key={s}>
                        <span className="vtitle">{s}</span>
                      </li>
                    ))}
                  </ul>
                </div>
                <div>
                  <h3>What doesn&apos;t ({review.missing_skills.length})</h3>
                  <ul>
                    {review.missing_skills.map((s) => (
                      <li key={s}>
                        <span className="vtitle">{s}</span>
                      </li>
                    ))}
                  </ul>
                </div>
              </div>
            </>
          )}

          {review.suggestions && (
            <div>
              <h3 className="panel__title">Suggestions</h3>
              <Markdown>{review.suggestions}</Markdown>
            </div>
          )}
        </div>
      )}
    </Section>
  );
}
