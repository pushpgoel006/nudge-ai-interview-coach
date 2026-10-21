"use client";

import Link from "next/link";
import { useCallback, useMemo, useState, useEffect, type ReactNode } from "react";
import { api, ApiError, type PrepSession, type User } from "@/lib/api";
import { AuthPanel } from "./AuthPanel";
import { StudioContext, type DocItem, type StudioRoot } from "./StudioContext";
import { Topbar } from "./Topbar";
import "./studio.css";

const ACTIVE_KEY = "nudge.activeSession";

function readActive(): string | null {
  try {
    return sessionStorage.getItem(ACTIVE_KEY);
  } catch {
    return null;
  }
}
function writeActive(id: string | null) {
  try {
    if (id) sessionStorage.setItem(ACTIVE_KEY, id);
    else sessionStorage.removeItem(ACTIVE_KEY);
  } catch {
    /* storage unavailable: fine */
  }
}

/** Owns sign-in, the session list, the current session's documents and each tool's remembered state. */
export function StudioProvider({ children }: { children: ReactNode }) {
  // undefined = still checking, null = signed out
  const [user, setUser] = useState<User | null | undefined>(undefined);
  const [bootError, setBootError] = useState<string | null>(null);
  const [sessions, setSessions] = useState<PrepSession[]>([]);
  const [activeId, setActiveId] = useState<string | null>(null);
  // Documents are stored with the session they belong to, so a slow reply for a session you have left is ignored.
  const [docsState, setDocsState] = useState<{ id: string; list: DocItem[] } | null>(null);
  const [dataVersion, setDataVersion] = useState(0);
  const [practiceTopic, setPracticeTopic] = useState("");

  const [slots, setSlots] = useState<Record<string, unknown>>({});

  const loadDocsFor = useCallback(async (id: string | null) => {
    if (!id) return;
    try {
      setDocsState({ id, list: await api.get<DocItem[]>(`/sessions/${id}/documents`) });
    } catch {
      setDocsState({ id, list: [] });
    }
  }, []);

  const activate = useCallback(
    (id: string | null) => {
      setActiveId(id);
      writeActive(id);
      void loadDocsFor(id);
    },
    [loadDocsFor],
  );

  const loadSessions = useCallback(async () => {
    try {
      const list = await api.get<PrepSession[]>("/sessions");
      setSessions(list);
      const wanted = readActive();
      activate(list.find((s) => s.id === wanted)?.id ?? list[0]?.id ?? null);
    } catch (err) {
      setBootError(err instanceof ApiError ? err.message : "Could not load sessions.");
    }
  }, [activate]);

  useEffect(() => {
    let cancelled = false;
    api
      .get<User>("/auth/me")
      .then((u) => {
        if (cancelled) return;
        setUser(u);
        void loadSessions();
      })
      .catch((err) => {
        if (cancelled) return;
        if (err instanceof ApiError && err.status === 401) setUser(null);
        else {
          setBootError(err instanceof ApiError ? err.message : "Could not load the studio.");
          setUser(null);
        }
      });
    return () => {
      cancelled = true;
    };
  }, [loadSessions]);

  const reset = useCallback(() => {
    setUser(null);
    setSessions([]);
    setSlots({});
    setActiveId(null);
    setDocsState(null);
    writeActive(null);
  }, []);

  const signOut = useCallback(async () => {
    try {
      await api.post("/auth/logout");
    } catch {
      /* cookie may already be gone */
    }
    reset();
  }, [reset]);

  const slotGet = useCallback(
    <T,>(key: string, initial: T): T => {
      const full = `${activeId}:${key}`;
      return full in slots ? (slots[full] as T) : initial;
    },
    [slots, activeId],
  );
  const slotSet = useCallback(
    <T,>(key: string, next: T | ((prev: T) => T), initial: T) => {
      const full = `${activeId}:${key}`;
      setSlots((prev) => {
        const current = full in prev ? (prev[full] as T) : initial;
        const resolved = typeof next === "function" ? (next as (p: T) => T)(current) : next;
        return { ...prev, [full]: resolved };
      });
    },
    [activeId],
  );

  const session = useMemo(() => sessions.find((s) => s.id === activeId) ?? null, [sessions, activeId]);
  const docs = docsState && docsState.id === activeId ? docsState.list : null;

  const refreshDocs = useCallback(() => loadDocsFor(activeId), [loadDocsFor, activeId]);
  const bumpData = useCallback(() => setDataVersion((v) => v + 1), []);
  const sessionCreated = useCallback(
    (s: PrepSession) => {
      setSessions((list) => [s, ...list]);
      activate(s.id);
    },
    [activate],
  );
  const sessionRemoved = useCallback(
    (id: string) => {
      const rest = sessions.filter((s) => s.id !== id);
      setSessions(rest);
      if (activeId === id) activate(rest[0]?.id ?? null);
    },
    [activate, activeId, sessions],
  );

  const value = useMemo<StudioRoot | null>(
    () =>
      user
        ? {
            user,
            sessions,
            session,
            docs,
            refreshDocs,
            docCount: docs === null ? null : docs.length,
            bumpData,
            dataVersion,
            practiceTopic,
            setPracticeTopic,
            selectSession: activate,
            sessionCreated,
            sessionRemoved,
            signOut,
            accountDeleted: reset,
            slotGet,
            slotSet,
          }
        : null,
    [user, sessions, session, docs, dataVersion, practiceTopic, activate, refreshDocs, bumpData, sessionCreated, sessionRemoved, signOut, reset, slotGet, slotSet],
  );

  if (user === undefined) {
    return (
      <main className="studio studio--center" aria-busy="true">
        <p className="lbl">Loading studio…</p>
      </main>
    );
  }

  if (!user || !value) {
    return (
      <main className="studio studio--center">
        <Link className="studio__home" href="/">
          <span className="sq" aria-hidden="true" />
          Nudge
        </Link>
        {bootError && (
          <p className="notice notice--error" role="alert">
            {bootError}
          </p>
        )}
        <AuthPanel
          onAuthed={(u) => {
            setBootError(null);
            setUser(u);
            void loadSessions();
          }}
        />
      </main>
    );
  }

  return (
    <StudioContext.Provider value={value}>
      <div className="studio">
        <Topbar />
        <main className="studio__main" id="studio-main">
          {bootError && (
            <p className="notice notice--error" role="alert">
              {bootError}
            </p>
          )}
          {children}
        </main>
      </div>
    </StudioContext.Provider>
  );
}
