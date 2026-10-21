"use client";

import { useCallback, useEffect, useId, useState, type FormEvent } from "react";
import { api, ApiError } from "@/lib/api";

type Usage = { used_today: number; limit_today: number };

export function AccountSection({ refreshKey, onDeleted }: { refreshKey: number; onDeleted: () => void }) {
  const id = useId();
  const [usage, setUsage] = useState<Usage | null>(null);
  const [confirming, setConfirming] = useState(false);
  const [password, setPassword] = useState("");
  const [busy, setBusy] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const load = useCallback(async () => {
    try {
      setUsage(await api.get<Usage>("/me/usage"));
    } catch {
      /* the meter is optional */
    }
  }, []);

  useEffect(() => {
    // Refresh the meter whenever something that spends AI calls has just run.
    // eslint-disable-next-line react-hooks/set-state-in-effect
    void load();
  }, [load, refreshKey]);

  async function remove(e: FormEvent) {
    e.preventDefault();
    setError(null);
    setBusy(true);
    try {
      await api.post("/me/delete", { password });
      onDeleted();
    } catch (err) {
      setError(err instanceof ApiError ? err.message : "Could not delete the account.");
    } finally {
      setBusy(false);
    }
  }

  return (
    <section className="account" id="account" aria-labelledby={`${id}-h`}>
      <h2 className="panel__title" id={`${id}-h`}>
        Account and privacy
      </h2>
      {usage && (
        <p>
          AI actions used in the last 24 hours:{" "}
          <strong>
            {usage.used_today} of {usage.limit_today}
          </strong>
          . Chat, resume checks, theory questions and answers, and DSA reviews each count as one.
        </p>
      )}
      <p className="help">
        This is a portfolio demo. Your documents are turned into searchable text for your own sessions only. Uploaded PDF files are not kept on the server
        after indexing. Deleting your account removes every session, document, answer, review and score tied to it.
      </p>

      {!confirming ? (
        <div className="row">
          <button type="button" className="sbtn sbtn--danger" onClick={() => setConfirming(true)}>
            Delete my account and data
          </button>
        </div>
      ) : (
        <form className="panel form" onSubmit={remove}>
          <p>
            <strong>This cannot be undone.</strong> Enter your password to delete your account and everything in it.
          </p>
          <div className="field">
            <label htmlFor={`${id}-pw`}>Password</label>
            <input id={`${id}-pw`} type="password" value={password} onChange={(e) => setPassword(e.target.value)} autoComplete="current-password" maxLength={128} required />
          </div>
          {error && (
            <p className="notice notice--error" role="alert">
              {error}
            </p>
          )}
          <div className="row">
            <button type="submit" className="sbtn sbtn--danger" disabled={busy || !password}>
              {busy ? "Deleting…" : "Delete everything"}
            </button>
            <button type="button" className="sbtn sbtn--quiet" onClick={() => { setConfirming(false); setPassword(""); setError(null); }}>
              Cancel
            </button>
          </div>
        </form>
      )}
    </section>
  );
}
