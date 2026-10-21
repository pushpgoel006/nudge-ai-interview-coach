"use client";

import Link from "next/link";
import { useId, useRef, useState, type FormEvent } from "react";
import { api, ApiError } from "@/lib/api";
import { PRACTICE } from "./nav";
import { Section } from "./Section";
import { useStudio, type DocItem } from "./StudioContext";

export const DOC_TYPES: Record<string, string> = {
  jd: "Job description",
  resume: "Resume",
  company: "Company",
  notes: "Notes",
  experience: "Experience",
};

const JD_TEXT_NAME = "job-description.txt";
const MAX_MB = 5;

function errorText(err: unknown, fallback: string) {
  return err instanceof ApiError ? err.message : fallback;
}

export function DocumentsSection() {
  const { session, docs, refreshDocs } = useStudio();
  const id = useId();
  const fileRef = useRef<HTMLInputElement>(null);

  const [error, setError] = useState<string | null>(null);
  const [busy, setBusy] = useState<string | null>(null); // what is happening right now
  const [docType, setDocType] = useState("resume");
  const [pasteType, setPasteType] = useState("jd");
  const [pasteName, setPasteName] = useState("");
  const [pasteText, setPasteText] = useState("");

  const base = `/sessions/${session.id}/documents`;

  async function uploadPdf(e: FormEvent) {
    e.preventDefault();
    const file = fileRef.current?.files?.[0];
    if (!file) {
      setError("Choose a PDF first.");
      return;
    }
    if (file.size > MAX_MB * 1024 * 1024) {
      setError(`That file is over ${MAX_MB} MB.`);
      return;
    }
    setError(null);
    setBusy("Indexing your PDF. The first one can take a minute while the model warms up…");
    try {
      const form = new FormData();
      form.append("file", file);
      form.append("doc_type", docType);
      await api.upload(base, form);
      if (fileRef.current) fileRef.current.value = "";
      await refreshDocs();
    } catch (err) {
      setError(errorText(err, "Upload failed."));
    } finally {
      setBusy(null);
    }
  }

  async function addText(e: FormEvent, override?: { doc_type: string; name: string; text: string }) {
    e.preventDefault();
    const payload = override ?? { doc_type: pasteType, name: pasteName, text: pasteText };
    setError(null);
    setBusy("Indexing your text…");
    try {
      await api.post(`${base}/text`, payload);
      if (!override) {
        setPasteText("");
        setPasteName("");
      }
      await refreshDocs();
    } catch (err) {
      setError(errorText(err, "Could not add that text."));
    } finally {
      setBusy(null);
    }
  }

  async function remove(doc: DocItem) {
    setError(null);
    setBusy(`Removing ${doc.file_name}…`);
    try {
      await api.del(`${base}/${doc.id}`);
      await refreshDocs();
    } catch (err) {
      setError(errorText(err, "Could not remove that document."));
    } finally {
      setBusy(null);
    }
  }

  const hasPastedJd = session.jd_text.trim().length >= 20;
  const jdAlreadyIndexed = (docs ?? []).some((d) => d.file_name === JD_TEXT_NAME);
  const offerPastedJd = hasPastedJd && !jdAlreadyIndexed && docs !== null;
  const stale = (docs ?? []).filter((d) => d.indexed === false);
  const ready = (docs?.length ?? 0) > 0;
  const hasJd = (docs ?? []).some((d) => d.doc_type === "jd");
  const hasResume = (docs ?? []).some((d) => d.doc_type === "resume");

  return (
    <Section
      id="documents"
      title="Documents"
      lead="Add the job description and your resume. Everything else answers from these and cites the page."
    >
      <ol className="stepper" aria-label="Setup steps">
        <li className="is-current" aria-current="step">
          <span>1</span> Add documents
        </li>
        <li className={ready ? "is-ready" : undefined}>
          <span>2</span> Pick what to practise
        </li>
      </ol>

      <div className="panel">
        <h2 className="panel__title">In this session</h2>
        {docs === null && <p className="help">Loading…</p>}
        {docs?.length === 0 && <p className="empty">Nothing yet. Add a job description and your resume to begin.</p>}
        {docs && docs.length > 0 && (
          <ul className="list">
            {docs.map((d) => (
              <li key={d.id}>
                <span className="list__name">{d.file_name}</span>
                <span className="pill">{(d.doc_type && DOC_TYPES[d.doc_type]) || d.doc_type}</span>
                <span className="list__meta">{d.chunk_count} chunks</span>
                {d.indexed === false && <span className="pill pill--warn">Needs re-adding</span>}
                <button type="button" className="sbtn sbtn--small sbtn--quiet list__spacer" onClick={() => remove(d)} disabled={!!busy} aria-label={`Remove ${d.file_name}`}>
                  Remove
                </button>
              </li>
            ))}
          </ul>
        )}
        {stale.length > 0 && (
          <p className="notice notice--warn">
            {stale.length === 1 ? "One document is" : `${stale.length} documents are`} no longer in the search index (the
            server may have restarted). Remove and add {stale.length === 1 ? "it" : "them"} again.
          </p>
        )}
      </div>

      {offerPastedJd && (
        <div className="panel">
          <h2 className="panel__title">Job description you pasted</h2>
          <p className="help">You pasted a JD when creating this session. Index it so the resume check and chat can use it.</p>
          <div className="row">
            <button
              type="button"
              className="sbtn sbtn--primary"
              disabled={!!busy}
              onClick={(e) => addText(e, { doc_type: "jd", name: "", text: session.jd_text })}
            >
              Index my JD
            </button>
          </div>
        </div>
      )}

      <div className="dash2">
        <form className="panel form" onSubmit={uploadPdf}>
          <h2 className="panel__title">Upload a PDF</h2>
          <div className="field">
            <label htmlFor={`${id}-type`}>Type</label>
            <select id={`${id}-type`} value={docType} onChange={(e) => setDocType(e.target.value)}>
              {Object.entries(DOC_TYPES).map(([v, label]) => (
                <option key={v} value={v}>
                  {label}
                </option>
              ))}
            </select>
          </div>
          <div className="field">
            <label htmlFor={`${id}-file`}>PDF file</label>
            <input id={`${id}-file`} ref={fileRef} type="file" accept="application/pdf,.pdf" aria-describedby={`${id}-limits`} />
            <p id={`${id}-limits`} className="help">
              PDF only, up to {MAX_MB} MB, 40 pages, 5 files per session. Scanned images are not readable.
            </p>
          </div>
          <button type="submit" className="sbtn sbtn--primary" disabled={!!busy}>
            Upload and index
          </button>
        </form>

        <form className="panel form" onSubmit={(e) => addText(e)}>
          <h2 className="panel__title">Or paste text</h2>
          <div className="form__grid">
            <div className="field">
              <label htmlFor={`${id}-ptype`}>Type</label>
              <select id={`${id}-ptype`} value={pasteType} onChange={(e) => setPasteType(e.target.value)}>
                {Object.entries(DOC_TYPES).map(([v, label]) => (
                  <option key={v} value={v}>
                    {label}
                  </option>
                ))}
              </select>
            </div>
            <div className="field">
              <label htmlFor={`${id}-pname`}>Name (optional)</label>
              <input id={`${id}-pname`} value={pasteName} onChange={(e) => setPasteName(e.target.value)} maxLength={60} placeholder="job-description" />
            </div>
          </div>
          <div className="field">
            <label htmlFor={`${id}-ptext`}>Text</label>
            <textarea id={`${id}-ptext`} rows={6} value={pasteText} onChange={(e) => setPasteText(e.target.value)} maxLength={20000} />
          </div>
          <button type="submit" className="sbtn sbtn--primary" disabled={!!busy || pasteText.trim().length < 20}>
            Add text
          </button>
        </form>
      </div>

      {busy && (
        <p className="notice" role="status">
          <span className="spin" aria-hidden="true" /> {busy}
        </p>
      )}
      {error && (
        <p className="notice notice--error" role="alert">
          {error}
        </p>
      )}

      {ready && (
        <section className="next" aria-labelledby={`${id}-next`}>
          <h2 className="panel__title" id={`${id}-next`}>
            Step 2. What do you want to practise?
          </h2>
          {(!hasJd || !hasResume) && (
            <p className="help">
              Tip: add your {!hasJd && !hasResume ? "job description and resume" : !hasJd ? "job description" : "resume"} for the best results.
              You can go ahead without it.
            </p>
          )}
          <ul className="nextcards">
            {PRACTICE.map((item) => (
              <li key={item.href}>
                <Link href={item.href} className="nextcard">
                  <strong>{item.label}</strong>
                  <span>{item.blurb}</span>
                  <em aria-hidden="true">Open →</em>
                </Link>
              </li>
            ))}
          </ul>
        </section>
      )}
    </Section>
  );
}
