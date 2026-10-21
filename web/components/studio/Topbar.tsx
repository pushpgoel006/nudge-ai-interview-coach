"use client";

import Link from "next/link";
import { usePathname } from "next/navigation";
import { NAV } from "./nav";
import { useStudioRoot } from "./StudioContext";

export function Topbar() {
  const pathname = usePathname();
  const { user, session, docCount, signOut } = useStudioRoot();
  const needsDocs = session !== null && docCount === 0;

  return (
    <header className="sbar">
      <div className="sbar__left">
        <Link className="sbar__brand" href="/">
          <span className="sq" aria-hidden="true" />
          Nudge
        </Link>
        <Link className="sbar__session" href="/studio" title="Switch or add a prep session">
          {session ? (
            <>
              <span className="sbar__sessionname">
                {session.company_name} · {session.role}
              </span>
              <span className="sbar__change">Change</span>
            </>
          ) : (
            <span className="sbar__sessionname">Choose a session</span>
          )}
        </Link>
      </div>

      <nav className="sbar__nav" aria-label="Studio pages">
        {NAV.map((item) => {
          const active = pathname === item.href;
          return (
            <Link key={item.href} href={item.href} aria-current={active ? "page" : undefined} className={active ? "is-active" : undefined}>
              {item.label}
              {item.href === "/studio/documents" && needsDocs && <span className="dot" role="img" aria-label="no documents yet" />}
            </Link>
          );
        })}
      </nav>

      <div className="sbar__user">
        <span className="sbar__name">{user.display_name}</span>
        <button type="button" className="sbtn sbtn--small" onClick={signOut}>
          Sign out
        </button>
      </div>
    </header>
  );
}
