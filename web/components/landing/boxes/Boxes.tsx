import type { CSSProperties, ReactNode } from "react";

/* Product mock-ups shown in each act. Sample data only for now; in later
   sections these become live components wired to the API. Class names and
   data-count attributes are what the scroll motion hooks into. */

function Frame({
  className,
  label,
  title,
  children,
}: {
  className: string;
  label: string;
  title: string;
  children: ReactNode;
}) {
  return (
    <figure className={`ui ${className}`} aria-label={label}>
      <div className="ui__bar">
        <span className="sqs" aria-hidden="true">
          <i />
          <i />
          <i />
        </span>
        <span>{title}</span>
        <em>Sample</em>
      </div>
      <div className="ui__body">{children}</div>
    </figure>
  );
}

export function ChatBox() {
  return (
    <Frame className="ui--chat" label="Sample document chat" title="Chat">
      <p className="msg msg--you">Where do I fall short of this role?</p>
      <ol className="trace" aria-label="Retrieval steps">
        <li>
          Decompose
          <b>
            <span data-count="2">2</span> parts
          </b>
        </li>
        <li>
          Retrieve
          <b>
            <span data-count="8">8</span> passages
          </b>
        </li>
        <li>
          Grade
          <b>
            <span data-count="5">5</span> relevant
          </b>
        </li>
        <li>
          Answer<b>cited</b>
        </li>
      </ol>
      <p className="msg msg--ai">Strong on REST and PostgreSQL. Missing: Kubernetes and on-call ownership.</p>
      <ul className="chips">
        <li>resume.pdf · p.1</li>
        <li>job-description.pdf · p.2</li>
      </ul>
    </Frame>
  );
}

export function ResumeBox() {
  return (
    <Frame className="ui--resume" label="Sample resume check" title="Resume check">
      <div className="fit">
        <strong data-count="72">72</strong>
        <span>
          /100
          <br />
          job fit
        </span>
      </div>
      <ul className="verdicts">
        <li>
          <span className="tag tag--yes">Clearly shown</span>REST API design
        </li>
        <li>
          <span className="tag tag--part">Partly shown</span>CI/CD pipelines
        </li>
        <li>
          <span className="tag tag--no">Not shown</span>Kubernetes
        </li>
      </ul>
    </Frame>
  );
}

export function TheoryBox() {
  return (
    <Frame className="ui--theory" label="Sample theory round" title="Theory round">
      <div className="theory">
        <div className="theory__q">
          <p className="lbl">(Question)</p>
          <p className="theory__qt">B-tree or hash index for a lookup-heavy table?</p>
          <p className="lbl">(Your answer)</p>
          <p className="theory__a">B-tree by default: it supports range scans. Hash only wins on pure equality…</p>
        </div>
        <div className="theory__eval">
          <div className="score">
            <strong data-count="7">7</strong>
            <span>/10</span>
          </div>
          <div className="meter" aria-hidden="true">
            {Array.from({ length: 10 }, (_, i) => (
              <i key={i} className={i < 7 ? "on" : undefined} />
            ))}
          </div>
          <p className="lbl">(Strengths)</p>
          <p>Names the range-scan trade-off.</p>
          <p className="lbl">(Gaps)</p>
          <p>No mention of write cost.</p>
          <p className="grounded">
            <span className="sq" aria-hidden="true" />
            Checked against your notes
          </p>
          <p className="follow">
            Follow-up 1 of 3: <em>Where did you use a hash index?</em>
          </p>
        </div>
      </div>
    </Frame>
  );
}

export function DsaBox() {
  return (
    <Frame className="ui--dsa" label="Sample DSA round" title="DSA round">
      <p className="lbl">(Problem)</p>
      <p className="dsa__t">Two Sum</p>
      <pre className="code" aria-label="Sample Python solution">
        <span className="k">def</span> two_sum(nums, target):{"\n"}
        {"    "}seen = {"{}"}
        {"\n"}
        {"    "}
        <span className="k">for</span> i, n <span className="k">in</span> enumerate(nums):{"\n"}
        {"        "}
        <span className="k">if</span> target - n <span className="k">in</span> seen:{"\n"}
        {"            "}
        <span className="k">return</span> [seen[target - n], i]{"\n"}
        {"        "}seen[n] = i
      </pre>
      <div className="dsa__r">
        <div className="score score--sm">
          <strong data-count="9">9</strong>
          <span>/10</span>
        </div>
        <p>
          <b>Correct</b> Handles duplicates.
        </p>
        <p>
          <b>Complexity</b> O(n) time.
        </p>
      </div>
    </Frame>
  );
}

const BARS: { label: string; w: string; v: string }[] = [
  { label: "Concurrency", w: "38%", v: "3.8" },
  { label: "Indexing", w: "55%", v: "5.5" },
  { label: "APIs", w: "82%", v: "8.2" },
];

export function DashBox() {
  return (
    <Frame className="ui--dash" label="Sample readiness dashboard" title="Dashboard">
      <div className="ring">
        <svg viewBox="0 0 100 100" aria-hidden="true">
          <circle cx="50" cy="50" r="42" className="ring__bg" />
          <circle cx="50" cy="50" r="42" className="ring__fg" id="ringFg" />
        </svg>
        <div className="ring__n">
          <strong id="ringNum" data-count="78">
            78
          </strong>
          <span>readiness</span>
        </div>
      </div>
      <p className="dash__note">60% theory + 40% resume fit</p>
      <svg className="trend" viewBox="0 0 200 50" role="img" aria-label="Theory scores trending up over six sessions">
        <polyline
          className="trend__line"
          pathLength={1}
          points="0,42 40,36 80,38 120,26 160,20 200,10"
          fill="none"
          stroke="currentColor"
          strokeWidth={2}
        />
        <g fill="currentColor">
          {[
            [0, 42],
            [40, 36],
            [80, 38],
            [120, 26],
            [160, 20],
            [200, 10],
          ].map(([x, y]) => (
            <circle key={x} cx={x} cy={y} r={2.5} />
          ))}
        </g>
      </svg>
      <ul className="bars" aria-label="Weakest topics">
        {BARS.map((b) => (
          <li key={b.label}>
            <span>{b.label}</span>
            <i style={{ "--w": b.w } as CSSProperties} />
            <b data-count={b.v} data-dec="1">
              {b.v}
            </b>
          </li>
        ))}
      </ul>
    </Frame>
  );
}
