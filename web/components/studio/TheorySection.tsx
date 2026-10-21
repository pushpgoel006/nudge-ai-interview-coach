"use client";

import { useId, useState, type FormEvent } from "react";
import { api, ApiError, type Source } from "@/lib/api";
import { CountUp } from "./CountUp";
import { DOC_TYPES } from "./DocumentsSection";
import { Markdown } from "./Markdown";
import { NeedDocs } from "./RequireSession";
import { Section } from "./Section";
import { useSlot, useStudio } from "./StudioContext";

type Pending = { thread_id: string; question: string; sources: Source[]; followup_number: number; topic?: string | null };
type Turn = {
  followup_number: number;
  question: string;
  answer: string;
  score: number;
  strengths: string;
  weaknesses: string;
  ideal_answer: string;
  grounded: boolean;
  sources: Source[];
};
type AnswerResult = { turn: Turn; next: Omit<Pending, "thread_id"> | null; done: boolean };

const label = (n: number) => (n === 0 ? "Question" : `Follow-up ${n}`);

function Sources({ sources }: { sources: Source[] }) {
  if (!sources.length) return null;
  return (
    <ul className="sources" aria-label="Sources">
      {sources.map((s) => (
        <li key={`${s.file_name}-${s.page}`}>
          {s.file_name} · p.{s.page}
          {s.doc_type ? ` · ${DOC_TYPES[s.doc_type] ?? s.doc_type}` : ""}
        </li>
      ))}
    </ul>
  );
}

export function TheorySection() {
  const { session, docCount, bumpData, practiceTopic, setPracticeTopic } = useStudio();
  const id = useId();
  const [difficulty, setDifficulty] = useSlot("theory:difficulty", "medium");
  const [turns, setTurns] = useSlot<Turn[]>("theory:turns", []);
  const [pending, setPending] = useSlot<Pending | null>("theory:pending", null);
  const [finished, setFinished] = useSlot("theory:finished", false);
  const [answer, setAnswer] = useSlot("theory:answer", "");
  const [busy, setBusy] = useState<"question" | "answer" | null>(null);
  const [error, setError] = useState<string | null>(null);

  const base = `/sessions/${session.id}/theory`;

  async function newQuestion() {
    setError(null);
    setBusy("question");
    try {
      const q = await api.post<Pending>(`${base}/start`, { topic: practiceTopic.trim() || null, difficulty });
      setPending(q);
      setTurns([]);
      setFinished(false);
      setAnswer("");
    } catch (err) {
      setError(err instanceof ApiError ? err.message : "Could not get a question.");
    } finally {
      setBusy(null);
    }
  }

  async function submit(e: FormEvent) {
    e.preventDefault();
    if (!pending || answer.trim().length < 2) return;
    setError(null);
    setBusy("answer");
    try {
      const r = await api.post<AnswerResult>(`${base}/${pending.thread_id}/answer`, { answer });
      setTurns((t) => [...t, r.turn]);
      setAnswer("");
      if (r.next) setPending({ ...r.next, thread_id: pending.thread_id });
      else {
        setPending(null);
        setFinished(true);
      }
      bumpData();
    } catch (err) {
      setError(err instanceof ApiError ? err.message : "Could not evaluate that answer.");
    } finally {
      setBusy(null);
    }
  }

  return (
    <Section
      id="theory"
      title="Theory round"
      lead="Questions drawn from your own material. Answer, get scored, then face up to three follow-ups."
    >
      <NeedDocs />

      <div className="panel">
        <div className="form__grid">
          <div className="field">
            <label htmlFor={`${id}-topic`}>Topic (optional)</label>
            <input id={`${id}-topic`} value={practiceTopic} onChange={(e) => setPracticeTopic(e.target.value)} maxLength={80} placeholder="e.g. PostgreSQL indexing" />
          </div>
          <div className="field">
            <label htmlFor={`${id}-diff`}>Difficulty</label>
            <select id={`${id}-diff`} value={difficulty} onChange={(e) => setDifficulty(e.target.value)}>
              <option value="easy">Easy</option>
              <option value="medium">Medium</option>
              <option value="hard">Hard</option>
            </select>
          </div>
        </div>
        <div className="row">
          <button type="button" className="sbtn sbtn--primary" onClick={newQuestion} disabled={!!busy || docCount === 0}>
            {busy === "question" ? "Writing a question…" : turns.length || pending ? "New question" : "Get a question"}
          </button>
          {docCount === 0 && <span className="help">Add a document first.</span>}
        </div>
      </div>

      {turns.map((t) => (
        <div className="panel" key={t.followup_number}>
          <p className="lbl">({label(t.followup_number)})</p>
          <p className="qa__q">{t.question}</p>
          <p className="prose">
            <em>Your answer:</em> {t.answer}
          </p>
          <div className="bigscore" aria-label={`Score ${t.score} out of 10`}>
            <strong>
              <CountUp value={t.score} />
            </strong>
            <span>/10</span>
          </div>
          <div className="dash2">
            <div>
              <h3 className="panel__title">Strengths</h3>
              <Markdown compact>{t.strengths}</Markdown>
            </div>
            <div>
              <h3 className="panel__title">To work on</h3>
              <Markdown compact>{t.weaknesses}</Markdown>
            </div>
          </div>
          <div>
            <h3 className="panel__title">Ideal answer</h3>
            <Markdown compact>{t.ideal_answer}</Markdown>
          </div>
          {!t.grounded && <p className="notice notice--warn">This ideal answer could not be confirmed against your uploaded material.</p>}
          <Sources sources={t.sources} />
        </div>
      ))}

      {pending && (
        <form className="panel form" onSubmit={submit}>
          <p className="lbl">({label(pending.followup_number)})</p>
          <p className="qa__q">{pending.question}</p>
          <Sources sources={pending.sources} />
          <div className="field">
            <label htmlFor={`${id}-answer`}>Your answer</label>
            <textarea id={`${id}-answer`} rows={6} value={answer} onChange={(e) => setAnswer(e.target.value)} maxLength={4000} />
          </div>
          <div className="row">
            <button type="submit" className="sbtn sbtn--primary" disabled={!!busy || answer.trim().length < 2}>
              {busy === "answer" ? "Scoring…" : "Submit answer"}
            </button>
            {busy === "answer" && (
              <span className="help" role="status">
                <span className="spin" aria-hidden="true" /> Checking your answer against your documents…
              </span>
            )}
          </div>
        </form>
      )}

      {finished && <p className="notice">Round complete. That was the last follow-up. Get a new question to keep going.</p>}
      {error && (
        <p className="notice notice--error" role="alert">
          {error}
        </p>
      )}
    </Section>
  );
}
