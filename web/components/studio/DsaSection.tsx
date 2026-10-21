"use client";

import { useId, useState, type FormEvent } from "react";
import { api, ApiError } from "@/lib/api";
import { CountUp } from "./CountUp";
import { Markdown } from "./Markdown";
import { Section } from "./Section";
import { useSlot, useStudio } from "./StudioContext";

const TOPICS: [string, string][] = [
  ["array", "Array"], ["hash-table", "Hash Table"], ["two-pointers", "Two Pointers"], ["dynamic-programming", "Dynamic Programming"],
  ["binary-search", "Binary Search"], ["tree", "Tree"], ["graph", "Graph"], ["linked-list", "Linked List"], ["stack", "Stack"],
  ["greedy", "Greedy"], ["backtracking", "Backtracking"], ["sorting", "Sorting"], ["string", "String"],
  ["heap-priority-queue", "Heap / Priority Queue"], ["sliding-window", "Sliding Window"],
];
const LANGUAGES: [string, string][] = [["python", "Python"], ["javascript", "JavaScript"], ["java", "Java"], ["cpp", "C++"]];

type Problem = { problem_id: string; title: string; slug: string; statement: string; source: string; topic: string; difficulty: string };
type Review = { score: number; correctness_notes: string; complexity_notes: string; suggestions: string };

export function DsaSection() {
  const { session, bumpData } = useStudio();
  const id = useId();
  const [topic, setTopic] = useSlot("dsa:topic", "array");
  const [difficulty, setDifficulty] = useSlot("dsa:difficulty", "easy");
  const [language, setLanguage] = useSlot("dsa:language", "python");
  const [problem, setProblem] = useSlot<Problem | null>("dsa:problem", null);
  const [code, setCode] = useSlot("dsa:code", "");
  const [review, setReview] = useSlot<Review | null>("dsa:review", null);
  const [busy, setBusy] = useState<"problem" | "submit" | null>(null);
  const [error, setError] = useState<string | null>(null);

  const base = `/sessions/${session.id}/dsa`;

  async function newProblem() {
    setError(null);
    setBusy("problem");
    try {
      setProblem(await api.post<Problem>(`${base}/problem`, { topic, difficulty }));
      setReview(null);
      setCode("");
    } catch (err) {
      setError(err instanceof ApiError ? err.message : "Could not fetch a problem.");
    } finally {
      setBusy(null);
    }
  }

  async function submit(e: FormEvent) {
    e.preventDefault();
    if (!problem || code.trim().length < 5) return;
    setError(null);
    setBusy("submit");
    try {
      setReview(await api.post<Review>(`${base}/${problem.problem_id}/submit`, { code, language }));
      bumpData();
    } catch (err) {
      setError(err instanceof ApiError ? err.message : "Could not review that solution.");
    } finally {
      setBusy(null);
    }
  }

  return (
    <Section id="dsa" title="DSA round" lead="A real problem, your solution, and a review of correctness and complexity.">
      <div className="panel">
        <div className="form__grid">
          <div className="field">
            <label htmlFor={`${id}-topic`}>Topic</label>
            <select id={`${id}-topic`} value={topic} onChange={(e) => setTopic(e.target.value)}>
              {TOPICS.map(([v, l]) => (
                <option key={v} value={v}>
                  {l}
                </option>
              ))}
            </select>
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
          <button type="button" className="sbtn sbtn--primary" onClick={newProblem} disabled={!!busy}>
            {busy === "problem" ? "Fetching…" : problem ? "New problem" : "Get a problem"}
          </button>
        </div>
      </div>

      {problem && (
        <div className="panel">
          <p className="lbl">
            ({problem.topic} · {problem.difficulty})
          </p>
          <h3 className="qa__q">{problem.title}</h3>
          <p className="prose">{problem.statement}</p>
          <p className="help">
            <a href={`https://leetcode.com/problems/${problem.slug}/`} target="_blank" rel="noopener noreferrer">
              View on LeetCode
            </a>
            {problem.source === "fallback" && " · LeetCode could not be reached, so this is a bundled problem."}
          </p>
        </div>
      )}

      {problem && (
        <form className="panel form" onSubmit={submit}>
          <div className="field">
            <label htmlFor={`${id}-lang`}>Language</label>
            <select id={`${id}-lang`} value={language} onChange={(e) => setLanguage(e.target.value)}>
              {LANGUAGES.map(([v, l]) => (
                <option key={v} value={v}>
                  {l}
                </option>
              ))}
            </select>
          </div>
          <div className="field">
            <label htmlFor={`${id}-code`}>Your solution</label>
            <textarea
              id={`${id}-code`}
              className="codearea"
              rows={12}
              value={code}
              onChange={(e) => setCode(e.target.value)}
              maxLength={10000}
              spellCheck={false}
              autoCapitalize="off"
              autoCorrect="off"
            />
            <p className="help">Your code is reviewed by the AI. It is not executed.</p>
          </div>
          <div className="row">
            <button type="submit" className="sbtn sbtn--primary" disabled={!!busy || code.trim().length < 5}>
              {busy === "submit" ? "Reviewing…" : "Submit solution"}
            </button>
            {busy === "submit" && (
              <span className="help" role="status">
                <span className="spin" aria-hidden="true" /> Reading your code…
              </span>
            )}
          </div>
        </form>
      )}

      {review && (
        <div className="panel">
          <div className="bigscore" aria-label={`Score ${review.score} out of 10`}>
            <strong>
              <CountUp value={review.score} />
            </strong>
            <span>/10</span>
          </div>
          <div>
            <h3 className="panel__title">Correctness</h3>
            <Markdown compact>{review.correctness_notes}</Markdown>
          </div>
          <div>
            <h3 className="panel__title">Complexity</h3>
            <Markdown compact>{review.complexity_notes}</Markdown>
          </div>
          <div>
            <h3 className="panel__title">Suggestions</h3>
            <Markdown compact>{review.suggestions}</Markdown>
          </div>
        </div>
      )}

      {error && (
        <p className="notice notice--error" role="alert">
          {error}
        </p>
      )}
    </Section>
  );
}
