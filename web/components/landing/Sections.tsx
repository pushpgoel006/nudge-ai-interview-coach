import Image from "next/image";
import Link from "next/link";
import type { ReactNode } from "react";
import { Chars, Words } from "./Text";
import { Figure, type FigureName } from "./Figure";

/** Where "Launch app" points. Set NEXT_PUBLIC_APP_URL to override. */
export const APP_HREF = process.env.NEXT_PUBLIC_APP_URL || "/studio";
const APP_IS_EXTERNAL = APP_HREF.startsWith("http");

function AppLink({ className, children }: { className: string; children: ReactNode }) {
  return APP_IS_EXTERNAL ? (
    <a className={className} href={APP_HREF} target="_blank" rel="noopener noreferrer">
      {children}
    </a>
  ) : (
    <Link className={className} href={APP_HREF}>
      {children}
    </Link>
  );
}

export function Loader() {
  return (
    <div className="loader" id="loader" aria-hidden="true">
      <span className="loader__c tl">Nudge</span>
      <span className="loader__c tr">Overture</span>
      <span className="loader__c ml">Interview coach</span>
      <span className="loader__c mr">2026</span>
      <div className="loader__meter" id="loaderMeter">
        {Array.from({ length: 10 }, (_, i) => (
          <i key={i} />
        ))}
      </div>
      <span className="loader__c bl">Setting the stage</span>
      <span className="loader__c br">
        <span id="count">000</span>
      </span>
    </div>
  );
}

export function Bar() {
  return (
    <header className="bar" id="bar">
      <a className="bar__brand" href="#top" aria-label="Nudge, back to top">
        <span className="sq" aria-hidden="true" />
        Nudge
      </a>
      <p className="bar__act" id="barAct">
        Overture
      </p>
      <AppLink className="bar__cta">Launch app</AppLink>
    </header>
  );
}

export function Hero() {
  return (
    <section className="hero" id="top" data-act="Overture">
      <div className="hero__shape hero__shape--a" aria-hidden="true" />
      <div className="hero__shape hero__shape--b" aria-hidden="true" />
      <h1 className="hero__title" aria-label="Nudge">
        <span className="line">
          <Chars text="NUDGE" />
        </span>
      </h1>
      <p className="hero__cap">The AI coach that practises with your JD and resume.</p>
      <div className="hero__row" aria-hidden="true">
        <span id="heroL">THREE</span>
        <span id="heroR">ROUNDS</span>
      </div>
    </section>
  );
}

export function Manifesto() {
  return (
    <section className="manifesto" data-act="Overture">
      <p className="lbl manifesto__lbl">■ Nudge</p>
      <p className="big reveal">
        <Words text="Your documents. Your answers. Your code. One score." />
      </p>
    </section>
  );
}

export type ActImage = { src: string; width: number; height: number; alt: string };

export function Act({
  id,
  tone,
  label,
  n,
  title,
  image,
  steps,
  statement,
  children,
}: {
  id: string;
  tone: "yellow" | "rose" | "black";
  label: string;
  n: 1 | 2 | 3;
  title: string;
  image: ActImage;
  steps: { word: string; cap: string }[];
  statement: string;
  children: ReactNode;
}) {
  const num = `0${n}`;
  return (
    <section className={`act act--${tone}`} id={id} data-act={label}>
      <div className={`stage stage--${tone}`}>
        <div className="stage__in">
          <span className="lbl stage__tl">(Act {num})</span>
          <Image
            className="cut stage__img"
            src={image.src}
            width={image.width}
            height={image.height}
            alt={image.alt}
            sizes="(max-width: 900px) 80vw, 45vw"
          />
          <div className="stage__row">
            <h2 className="stage__title" aria-label={title}>
              <Chars text={title.toUpperCase()} />
            </h2>
            <span className="stage__n">ACT {n}</span>
          </div>
        </div>
      </div>
      <div className="act__body">
        <ol className="steps" aria-label="How it works">
          {steps.map((s, i) => (
            <li key={s.word}>
              <span className="lbl">(0{i + 1})</span>
              <strong>{s.word}</strong>
              <span className="cap">{s.cap}</span>
            </li>
          ))}
        </ol>
        <div className="demo">{children}</div>
        <div className="statement">
          <span className="lbl">({num})</span>
          <p className="big reveal">
            <Words text={statement} />
          </p>
        </div>
      </div>
    </section>
  );
}

type Tool = { name: string; line: string; image?: ActImage; figure?: FigureName };

const TOOLS: Tool[] = [
  { name: "Grounded chat", line: "Ask your documents. Answers cite file and page.", image: { src: "/images/orb.webp", width: 666, height: 1448, alt: "Performer in a polka-dot sphere costume and a tall black cone hat" } },
  { name: "Resume check", line: "Every requirement judged against your resume.", image: { src: "/images/pages.webp", width: 910, height: 1422, alt: "Performer in a costume of stacked white pages, holding out a blank panel" } },
  { name: "Theory round", line: "Questions from your material, graded with feedback.", figure: "disc" },
  { name: "Follow-ups", line: "Up to three probes on whatever stayed vague.", image: { src: "/images/pair.webp", width: 1169, height: 1199, alt: "Two costumed performers facing each other, one leaning in to ask, one listening" } },
  { name: "DSA round", line: "Real problems, judged code review.", figure: "abstrakt" },
  { name: "Readiness score", line: "Theory and resume fit blended into one number.", image: { src: "/images/rings.webp", width: 550, height: 1425, alt: "Performer in a target-ring costume standing on a three-step pedestal" } },
];

export function Ensemble() {
  return (
    <section className="gallery" id="ensemble" data-act="The ensemble">
      <div className="gallery__head">
        <p className="lbl">■ Nudge</p>
        <h2 className="big">
          Six tools.
          <br />
          One coach.
        </h2>
      </div>
      <div className="gallery__track" id="galleryTrack">
        {TOOLS.map((t) => (
          <figure className="g" key={t.name}>
            <div className="card">
              {t.image ? (
                <div className="fig fig--img">
                  <Image src={t.image.src} width={t.image.width} height={t.image.height} alt={t.image.alt} sizes="(max-width: 900px) 70vw, 24vw" />
                </div>
              ) : (
                <Figure name={t.figure as FigureName} />
              )}
            </div>
            <figcaption>
              <b>{t.name}</b>
              {t.line}
            </figcaption>
          </figure>
        ))}
      </div>
    </section>
  );
}

export function Finale() {
  return (
    <section className="finale" id="finale" data-act="Finale">
      <p className="lbl">(Finale)</p>
      <h2 className="finale__t">
        <span className="reveal">
          <Words text="Ready when you are." />
        </span>
      </h2>
      <p className="finale__p">Bring your JD. Leave ready.</p>
      <AppLink className="btn">
        Launch the app<span aria-hidden="true"> →</span>
      </AppLink>
    </section>
  );
}

export function Footer() {
  return (
    <footer className="foot">
      <div>
        <p className="lbl">Disclaimer</p>
        <p>Illustrations are original. Interface mock-ups use sample data.</p>
      </div>
      <div>
        <p className="lbl">Credits</p>
        <p>Typography: Inter Tight.</p>
      </div>
      <div>
        <p className="lbl">Project</p>
        <p>
          <a href="https://github.com/pushpgoel006/AI-coding-interview-and-learning-coach">Source on GitHub</a>
        </p>
      </div>
      <div>
        <p className="lbl">Legal</p>
        <p>© 2026</p>
      </div>
    </footer>
  );
}
