import { Fragment } from "react";

/** Letters wrapped for the rise-in animation. The parent heading carries the accessible label. */
export function Chars({ text }: { text: string }) {
  return (
    <span className="chars" aria-hidden="true">
      {[...text].map((c, i) => (c === " " ? " " : <span className="ch" key={i}>{c}</span>))}
    </span>
  );
}

/** Words wrapped for the scroll-linked reveal. */
export function Words({ text }: { text: string }) {
  const words = text.trim().split(/\s+/);
  return (
    <>
      {words.map((w, i) => (
        <Fragment key={i}>
          <span className="w">{w}</span>
          {i < words.length - 1 ? " " : null}
        </Fragment>
      ))}
    </>
  );
}
