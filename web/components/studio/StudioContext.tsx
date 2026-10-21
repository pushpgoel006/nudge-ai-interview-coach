"use client";

import { createContext, useCallback, useContext } from "react";
import type { PrepSession, User } from "@/lib/api";

export type DocItem = {
  id: number;
  file_name: string;
  doc_type: string | null;
  chunk_count: number;
  indexed: boolean | null;
};

export type StudioRoot = {
  user: User;
  sessions: PrepSession[];
  /** The session the workspace pages work on; null until one is created or chosen. */
  session: PrepSession | null;
  /** Documents in the current session (null while loading). */
  docs: DocItem[] | null;
  refreshDocs: () => Promise<void>;
  docCount: number | null;
  /** Call after something that changes dashboard numbers (answer scored, review run, ...). */
  bumpData: () => void;
  /** Increments each time bumpData is called; pages that show saved data re-fetch on change. */
  dataVersion: number;
  /** Topic chosen from the dashboard's "Practise this"; the theory round picks it up. */
  practiceTopic: string;
  setPracticeTopic: (t: string) => void;
  selectSession: (id: string) => void;
  sessionCreated: (s: PrepSession) => void;
  sessionRemoved: (id: string) => void;
  signOut: () => Promise<void>;
  accountDeleted: () => void;
  /** Per-session memory for each tool (chat history, drafts, ...), kept while you move between pages. */
  slotGet: <T>(key: string, initial: T) => T;
  slotSet: <T>(key: string, next: T | ((prev: T) => T), initial: T) => void;
};

export const StudioContext = createContext<StudioRoot | null>(null);

/** Everything, with the session possibly missing. Used by the shell and the sessions page. */
export function useStudioRoot(): StudioRoot {
  const value = useContext(StudioContext);
  if (!value) throw new Error("Studio hooks must be used inside the studio layout");
  return value;
}

/** For workspace pages: the session is guaranteed (they render inside <RequireSession>). */
export function useStudio(): StudioRoot & { session: PrepSession } {
  const root = useStudioRoot();
  if (!root.session) throw new Error("useStudio needs an active session; wrap the page in <RequireSession>");
  return root as StudioRoot & { session: PrepSession };
}

/** Like useState, but the value survives navigating to another studio page and back (per session). */
export function useSlot<T>(key: string, initial: T): [T, (next: T | ((prev: T) => T)) => void] {
  const { slotGet, slotSet } = useStudioRoot();
  const value = slotGet(key, initial);
  // The update is applied inside the provider with a functional state update, so several quick updates
  // (for example a message added before a reply arrives) never overwrite each other.
  const set = useCallback((next: T | ((prev: T) => T)) => slotSet(key, next, initial), [key, initial, slotSet]);
  return [value, set];
}
