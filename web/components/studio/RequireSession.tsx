"use client";

import Link from "next/link";
import type { ReactNode } from "react";
import { useStudio, useStudioRoot } from "./StudioContext";

/** Renders its children only when there is a current session; otherwise points to the sessions page. */
export function RequireSession({ children }: { children: ReactNode }) {
  const { session } = useStudioRoot();
  if (!session) {
    return (
      <div className="panel" style={{ maxWidth: 560 }}>
        <h1 className="ssec__title">Pick a session</h1>
        <p>Practice happens inside a prep session: the company and role you are preparing for.</p>
        <div className="row">
          <Link className="sbtn sbtn--primary" href="/studio">
            Choose or create a session
          </Link>
        </div>
      </div>
    );
  }
  return <>{children}</>;
}

/**
 * A gentle nudge, never a lock: shown when the session has no documents (or is missing a type this page
 * needs). The page underneath still works.
 */
export function NeedDocs({ needs }: { needs?: ("jd" | "resume")[] }) {
  const { docs } = useStudio();
  if (docs === null) return null;

  let message: string | null = null;
  if (docs.length === 0) {
    message = needs?.length
      ? "This page works from your documents. Add your job description and resume first."
      : "This page works from your documents. Add at least one first (the job description and your resume are the best start).";
  } else if (needs) {
    const missing = needs.filter((type) => !docs.some((d) => d.doc_type === type));
    if (missing.length) {
      message = `Add your ${missing.map((m) => (m === "jd" ? "job description" : "resume")).join(" and ")} for the best result.`;
    }
  }
  if (!message) return null;

  return (
    <p className="notice notice--warn" role="status">
      {message}{" "}
      <Link href="/studio/documents">
        <strong>Add documents →</strong>
      </Link>
    </p>
  );
}
