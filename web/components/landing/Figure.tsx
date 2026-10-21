/* Original geometric stage figures, drawn in SVG (viewBox 300x400).
   Used as stand-ins until a photographic cut-out exists for a slot. */
const INK = "#111";
const PAPER = "#f2efe8";

const ART = {
  sphere: `
    <rect x="121" y="262" width="22" height="98" fill="url(#p-stripes)" stroke="${INK}" stroke-width="2"/>
    <rect x="157" y="262" width="22" height="98" fill="url(#p-stripes)" stroke="${INK}" stroke-width="2"/>
    <polygon points="121,360 143,360 106,378" fill="${INK}"/>
    <polygon points="157,360 179,360 194,378" fill="${INK}"/>
    <ellipse cx="150" cy="262" rx="50" ry="14" fill="${PAPER}" stroke="${INK}" stroke-width="2"/>
    <ellipse cx="150" cy="198" rx="80" ry="72" fill="url(#p-dots)" stroke="${INK}" stroke-width="2.5"/>
    <ellipse cx="150" cy="198" rx="80" ry="72" fill="url(#g-shade)" style="mix-blend-mode:multiply"/>
    <rect x="140" y="112" width="20" height="18" fill="${PAPER}" stroke="${INK}" stroke-width="2"/>
    <polygon points="150,36 178,112 122,112" fill="${INK}"/>
    <rect x="122" y="96" width="56" height="8" fill="${PAPER}"/>`,
  disc: `
    <g fill="none" stroke="${INK}" stroke-width="3.4">
      <circle cx="150" cy="214" r="96" fill="${PAPER}"/>
      <circle cx="150" cy="214" r="76"/><circle cx="150" cy="214" r="56"/>
      <circle cx="150" cy="214" r="36"/>
    </g>
    <circle cx="150" cy="214" r="17" fill="${INK}"/>
    <circle cx="150" cy="214" r="96" fill="url(#g-shade)" style="mix-blend-mode:multiply"/>
    <circle cx="150" cy="86" r="22" fill="${PAPER}" stroke="${INK}" stroke-width="2.5"/>
    <path d="M128 84 a22 22 0 0 1 44 0z" fill="${INK}"/>
    <rect x="132" y="308" width="14" height="56" fill="url(#p-stripes)" stroke="${INK}" stroke-width="1.8"/>
    <rect x="154" y="308" width="14" height="56" fill="url(#p-stripes)" stroke="${INK}" stroke-width="1.8"/>`,
  abstrakt: `
    <rect x="140" y="40" width="20" height="320" fill="${INK}"/>
    <path d="M52 270 A98 98 0 0 1 248 270 Z" fill="${INK}"/>
    <polygon points="150,70 214,200 86,200" fill="${PAPER}" stroke="${INK}" stroke-width="3"/>
    <circle cx="150" cy="150" r="16" fill="${INK}"/>
    <rect x="86" y="286" width="128" height="14" fill="url(#p-stripes)" stroke="${INK}" stroke-width="2"/>
    <rect x="114" y="300" width="22" height="62" fill="url(#p-stripes)" stroke="${INK}" stroke-width="2"/>
    <rect x="164" y="300" width="22" height="62" fill="url(#p-stripes)" stroke="${INK}" stroke-width="2"/>`,
} as const;

export type FigureName = keyof typeof ART;

export function Figure({ name }: { name: FigureName }) {
  const inner =
    '<rect width="300" height="400" fill="url(#g-bg)"/>' +
    ART[name] +
    '<rect width="300" height="400" filter="url(#f-grain)" opacity=".22" style="mix-blend-mode:multiply"/>';
  return (
    <div className="fig">
      <svg
        viewBox="0 0 300 400"
        preserveAspectRatio="xMidYMid slice"
        aria-hidden="true"
        focusable="false"
        dangerouslySetInnerHTML={{ __html: inner }}
      />
    </div>
  );
}
