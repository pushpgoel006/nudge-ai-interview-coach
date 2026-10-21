"use client";

import { useEffect, useId, useRef, useState, type FormEvent } from "react";
import { api, ApiError, type Source } from "@/lib/api";
import { DOC_TYPES } from "./DocumentsSection";
import { Markdown } from "./Markdown";
import { NeedDocs } from "./RequireSession";
import { Section } from "./Section";
import { useSlot, useStudio } from "./StudioContext";

type Reply = {
  answer: string;
  sources: Source[];
  retrieved_count: number;
  kept_count: number;
  retry_count: number;
  sub_questions: string[];
};
type YouMessage = { role: "you"; text: string };
type AiMessage = { role: "ai"; text: string } & Omit<Reply, "answer">;
type Message = YouMessage | AiMessage;

function sourceLabel(s: Source) {
  const type = s.doc_type ? DOC_TYPES[s.doc_type] ?? s.doc_type : null;
  return `${s.file_name} · p.${s.page}${type ? ` · ${type}` : ""}`;
}

export function ChatSection() {
  const { session, docCount, bumpData } = useStudio();
  const id = useId();
  const [messages, setMessages] = useSlot<Message[]>("chat:messages", []);
  const [question, setQuestion] = useSlot("chat:draft", "");
  const [busy, setBusy] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const endRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    endRef.current?.scrollIntoView({ block: "nearest", behavior: "smooth" });
  }, [messages, busy]);

  async function ask(e: FormEvent) {
    e.preventDefault();
    const q = question.trim();
    if (q.length < 2 || busy) return;
    setError(null);
    setMessages((m) => [...m, { role: "you", text: q }]);
    setQuestion("");
    setBusy(true);
    try {
      const r = await api.post<Reply>(`/sessions/${session.id}/chat`, { question: q });
      const { answer, ...rest } = r;
      setMessages((m) => [...m, { role: "ai", text: answer, ...rest }]);
      bumpData();
    } catch (err) {
      setError(err instanceof ApiError ? err.message : "Something went wrong.");
    } finally {
      setBusy(false);
    }
  }

  const noDocs = docCount === 0;

  return (
    <Section id="chat" title="Chat" lead="Ask about the role, the company or your own background. Facts come from your documents, connected across all of them.">
      <NeedDocs />

      <div className="chat panel">
        <div className="chat__log" role="log" aria-live="polite" aria-label="Conversation">
          {messages.length === 0 && !busy && <p className="help">Try: “Where do I fall short of this role?” or “Compare the job requirements with my resume in a table.”</p>}
          {messages.map((m, i) =>
            m.role === "you" ? (
              <p key={i} className="bubble bubble--you">
                {m.text}
              </p>
            ) : (
              <div key={i} className="bubble bubble--ai">
                <Markdown>{m.text}</Markdown>
                <p className="steps-trace">
                  {m.sub_questions.length > 1 && <span>Split into {m.sub_questions.length} parts</span>}
                  <span>
                    Kept {m.kept_count} of {m.retrieved_count} passages
                  </span>
                  {m.retry_count > 0 && <span>Searched again {m.retry_count}×</span>}
                </p>
                {m.sources.length > 0 && (
                  <ul className="sources" aria-label="Sources">
                    {m.sources.map((s) => (
                      <li key={`${s.file_name}-${s.page}`}>{sourceLabel(s)}</li>
                    ))}
                  </ul>
                )}
              </div>
            ),
          )}
          {busy && (
            <p className="help" role="status">
              <span className="spin" aria-hidden="true" /> Searching your documents…
            </p>
          )}
          <div ref={endRef} />
        </div>

        {error && (
          <p className="notice notice--error" role="alert">
            {error}
          </p>
        )}

        <form className="chat__form" onSubmit={ask}>
          <div className="field">
            <label htmlFor={`${id}-q`}>Your question</label>
            <input
              id={`${id}-q`}
              value={question}
              onChange={(e) => setQuestion(e.target.value)}
              maxLength={1000}
              placeholder="Ask something about your documents…"
              disabled={noDocs}
              autoComplete="off"
            />
          </div>
          <button type="submit" className="sbtn sbtn--primary" disabled={busy || noDocs || question.trim().length < 2}>
            {busy ? "Thinking…" : "Ask"}
          </button>
        </form>
      </div>
    </Section>
  );
}
