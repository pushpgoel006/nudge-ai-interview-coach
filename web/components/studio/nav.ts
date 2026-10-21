export type NavItem = { href: string; label: string; blurb: string };

/** The workspace pages, in the order they appear in the top bar. */
export const NAV: NavItem[] = [
  { href: "/studio/documents", label: "Documents", blurb: "Add the JD, your resume and notes." },
  { href: "/studio/chat", label: "Chat", blurb: "Ask anything. Answers connect your documents." },
  { href: "/studio/resume", label: "Resume check", blurb: "See what matches the job and what doesn't." },
  { href: "/studio/theory", label: "Theory round", blurb: "Concept questions, scored, with follow-ups." },
  { href: "/studio/dsa", label: "DSA round", blurb: "Real problems with a code review." },
  { href: "/studio/dashboard", label: "Dashboard", blurb: "Your readiness, trend and weak spots." },
];

/** The four practice pages (everything except Documents and the Dashboard). */
export const PRACTICE = NAV.filter((n) => ["/studio/chat", "/studio/resume", "/studio/theory", "/studio/dsa"].includes(n.href));
