"use client";

import { useId, useState, type FormEvent } from "react";
import { api, ApiError, type User } from "@/lib/api";

type Mode = "signin" | "signup";

export function AuthPanel({ onAuthed }: { onAuthed: (user: User) => void }) {
  const [mode, setMode] = useState<Mode>("signin");
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [name, setName] = useState("");
  const [error, setError] = useState<string | null>(null);
  const [busy, setBusy] = useState(false);
  const id = useId();

  const signup = mode === "signup";

  async function submit(e: FormEvent) {
    e.preventDefault();
    setError(null);
    setBusy(true);
    try {
      const user = signup
        ? await api.post<User>("/auth/register", { email, password, display_name: name })
        : await api.post<User>("/auth/login", { email, password });
      onAuthed(user);
    } catch (err) {
      setError(err instanceof ApiError ? err.message : "Something went wrong. Try again.");
    } finally {
      setBusy(false);
    }
  }

  return (
    <section className="auth" aria-labelledby={`${id}-title`}>
      <p className="lbl">■ Nudge Studio</p>
      <h1 id={`${id}-title`} className="big auth__title">
        {signup ? "Create account" : "Sign in"}
      </h1>

      <div className="auth__tabs" role="tablist" aria-label="Account">
        <button type="button" role="tab" aria-selected={!signup} className="auth__tab" onClick={() => { setMode("signin"); setError(null); }}>
          Sign in
        </button>
        <button type="button" role="tab" aria-selected={signup} className="auth__tab" onClick={() => { setMode("signup"); setError(null); }}>
          Create account
        </button>
      </div>

      <form className="form" onSubmit={submit} noValidate>
        {signup && (
          <div className="field">
            <label htmlFor={`${id}-name`}>Display name</label>
            <input id={`${id}-name`} value={name} onChange={(e) => setName(e.target.value)} autoComplete="name" maxLength={60} required />
          </div>
        )}
        <div className="field">
          <label htmlFor={`${id}-email`}>Email</label>
          <input id={`${id}-email`} type="email" value={email} onChange={(e) => setEmail(e.target.value)} autoComplete="email" maxLength={254} required />
        </div>
        <div className="field">
          <label htmlFor={`${id}-pw`}>Password</label>
          <input
            id={`${id}-pw`}
            type="password"
            value={password}
            onChange={(e) => setPassword(e.target.value)}
            autoComplete={signup ? "new-password" : "current-password"}
            minLength={8}
            maxLength={72}
            aria-describedby={signup ? `${id}-pwhelp` : undefined}
            required
          />
          {signup && (
            <p id={`${id}-pwhelp`} className="help">
              At least 8 characters.
            </p>
          )}
        </div>

        {error && (
          <p className="notice notice--error" role="alert">
            {error}
          </p>
        )}

        <button className="sbtn sbtn--primary" type="submit" disabled={busy}>
          {busy ? "Please wait…" : signup ? "Create account" : "Sign in"}
        </button>
      </form>

      <p className="help auth__privacy">
        This is a portfolio demo. Anything you upload is used only to coach you, is limited in size and number, and
        you can delete your account and all its data from the studio at any time.
      </p>
    </section>
  );
}
