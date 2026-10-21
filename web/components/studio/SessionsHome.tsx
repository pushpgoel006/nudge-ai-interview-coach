"use client";

import { useRouter } from "next/navigation";
import { useId, useState, type FormEvent } from "react";
import { api, ApiError, type PrepSession } from "@/lib/api";
import { AccountSection } from "./AccountSection";
import { useStudioRoot } from "./StudioContext";

function when(iso: string | null) {
  if (!iso) return "";
  const d = new Date(iso.endsWith("Z") ? iso : iso + "Z");
  return d.toLocaleDateString(undefined, { day: "numeric", month: "short", year: "numeric" });
}

/** /studio: choose a prep session or start a new one, then head into the workspace. */
export function SessionsHome() {
  const router = useRouter();
  const root = useStudioRoot();
  const { sessions, session, selectSession, sessionCreated, sessionRemoved, accountDeleted, dataVersion, user } = root;
  const id = useId();

  // Open by default only for someone with no sessions yet; once they toggle it, their choice wins.
  const [manualCreating, setManualCreating] = useState<boolean | null>(null);
  const creating = manualCreating ?? sessions.length === 0;
  const [company, setCompany] = useState("");
  const [role, setRole] = useState("");
  const [jd, setJd] = useState("");
  const [busy, setBusy] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [confirming, setConfirming] = useState<string | null>(null);

  async function create(e: FormEvent) {
    e.preventDefault();
    setError(null);
    setBusy(true);
    try {
      const made = await api.post<PrepSession>("/sessions", { company_name: company, role, jd_text: jd });
      setCompany("");
      setRole("");
      setJd("");
      setManualCreating(false);
      sessionCreated(made);
      router.push("/studio/documents"); // step 1: add documents
    } catch (err) {
      setError(err instanceof ApiError ? err.message : "Could not create the session.");
    } finally {
      setBusy(false);
    }
  }

  async function remove(target: PrepSession) {
    setError(null);
    setBusy(true);
    try {
      await api.del(`/sessions/${target.id}`);
      setConfirming(null);
      sessionRemoved(target.id);
    } catch (err) {
      setError(err instanceof ApiError ? err.message : "Could not remove the session.");
    } finally {
      setBusy(false);
    }
  }

  function open(target: PrepSession) {
    selectSession(target.id);
    router.push("/studio/chat");
  }

  return (
    <div className="home">
      <header className="home__head">
        <p className="lbl">■ Nudge Studio</p>
        <h1 className="big home__title">Hi {user.display_name.split(" ")[0]}.</h1>
        <p className="ssec__lead">
          {sessions.length === 0
            ? "Start by naming the company and role you are preparing for. Then add your documents and practise."
            : "Pick up where you left off, or start a new prep session."}
        </p>
      </header>

      {sessions.length > 0 && (
        <ul className="cards" aria-label="Your prep sessions">
          {sessions.map((s) => {
            const current = session?.id === s.id;
            return (
              <li key={s.id} className={current ? "card2 is-current" : "card2"}>
                <div>
                  <p className="card2__co">{s.company_name}</p>
                  <p className="card2__role">{s.role}</p>
                  <p className="help">
                    {current && <span className="pill">Current</span>} Started {when(s.created_at)}
                  </p>
                </div>
                <div className="row">
                  <button type="button" className="sbtn sbtn--primary" onClick={() => open(s)}>
                    Open
                  </button>
                  {confirming === s.id ? (
                    <>
                      <button type="button" className="sbtn sbtn--danger" onClick={() => remove(s)} disabled={busy}>
                        Remove it
                      </button>
                      <button type="button" className="sbtn sbtn--quiet" onClick={() => setConfirming(null)}>
                        Keep
                      </button>
                    </>
                  ) : (
                    <button type="button" className="sbtn sbtn--quiet" onClick={() => setConfirming(s.id)} aria-label={`Remove ${s.company_name} ${s.role}`}>
                      Remove
                    </button>
                  )}
                </div>
              </li>
            );
          })}
        </ul>
      )}

      <section className="panel" aria-label="New prep session" style={{ maxWidth: 760 }}>
        <div className="row" style={{ alignItems: "center", justifyContent: "space-between" }}>
          <h2 className="panel__title">New prep session</h2>
          {sessions.length > 0 && (
            <button type="button" className="sbtn sbtn--small" onClick={() => setManualCreating(!creating)} aria-expanded={creating}>
              {creating ? "Cancel" : "New session"}
            </button>
          )}
        </div>
        {creating && (
          <form className="form" onSubmit={create}>
            <div className="form__grid">
              <div className="field">
                <label htmlFor={`${id}-co`}>Company</label>
                <input id={`${id}-co`} value={company} onChange={(e) => setCompany(e.target.value)} maxLength={100} required />
              </div>
              <div className="field">
                <label htmlFor={`${id}-role`}>Role</label>
                <input id={`${id}-role`} value={role} onChange={(e) => setRole(e.target.value)} maxLength={100} required />
              </div>
            </div>
            <div className="field">
              <label htmlFor={`${id}-jd`}>Job description (optional)</label>
              <textarea id={`${id}-jd`} rows={4} value={jd} onChange={(e) => setJd(e.target.value)} maxLength={20000} />
              <p className="help">You can paste it now or upload it as a PDF on the next page.</p>
            </div>
            <button type="submit" className="sbtn sbtn--primary" disabled={busy || !company.trim() || !role.trim()}>
              {busy ? "Creating…" : "Create session and add documents →"}
            </button>
          </form>
        )}
      </section>

      {error && (
        <p className="notice notice--error" role="alert">
          {error}
        </p>
      )}

      <AccountSection refreshKey={dataVersion} onDeleted={accountDeleted} />
    </div>
  );
}
