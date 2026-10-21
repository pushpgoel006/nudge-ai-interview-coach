import type { ReactNode } from "react";

/** Shared chrome for one studio page: a heading, an optional one-line lead, and the body. */
export function Section({
  id,
  title,
  lead,
  children,
}: {
  id: string;
  title: string;
  lead?: string;
  children: ReactNode;
}) {
  return (
    <section className="ssec" id={id} aria-labelledby={`${id}-h`}>
      <div className="ssec__head">
        <h1 className="ssec__title" id={`${id}-h`}>
          {title}
        </h1>
        {lead && <p className="ssec__lead">{lead}</p>}
      </div>
      <div className="ssec__body">{children}</div>
    </section>
  );
}
