"use client";

import ReactMarkdown from "react-markdown";
import remarkGfm from "remark-gfm";

/** Markdown from the AI (bullets, bold, tables), rendered safely: raw HTML in the text is never executed. */
export function Markdown({ children, compact = false }: { children: string; compact?: boolean }) {
  // Older answers carried reference markers in special brackets; drop them so they don't clutter the text.
  const text = children.replace(/【[^】]*】/g, "").trim();
  return (
    <div className={compact ? "md md--compact" : "md"}>
      <ReactMarkdown
        remarkPlugins={[remarkGfm]}
        components={{
          // Wide tables scroll sideways inside their own box instead of breaking the layout.
          // eslint-disable-next-line @typescript-eslint/no-unused-vars
          table: ({ node: _node, ...props }) => (
            <div className="md__table" role="region" aria-label="Table" tabIndex={0}>
              <table {...props} />
            </div>
          ),
          // eslint-disable-next-line @typescript-eslint/no-unused-vars
          a: ({ node: _node, ...props }) => <a {...props} target="_blank" rel="noopener noreferrer" />,
        }}
      >
        {text}
      </ReactMarkdown>
    </div>
  );
}
