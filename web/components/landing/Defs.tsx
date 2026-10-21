/** Shared SVG defs (patterns, gradients, grain) used by every drawn figure. */
export function Defs() {
  return (
    <svg className="defs" width="0" height="0" aria-hidden="true" focusable="false">
      <defs>
        <pattern id="p-stripes" width="14" height="14" patternUnits="userSpaceOnUse">
          <rect width="14" height="14" fill="#f2efe8" />
          <rect width="14" height="7" fill="#111" />
        </pattern>
        <pattern id="p-dots" width="17" height="17" patternUnits="userSpaceOnUse">
          <rect width="17" height="17" fill="#f2efe8" />
          <circle cx="8.5" cy="8.5" r="3.2" fill="#111" />
        </pattern>
        <radialGradient id="g-bg" cx="50%" cy="42%" r="75%">
          <stop offset="0" stopColor="#dedbd3" />
          <stop offset="1" stopColor="#aaa69b" />
        </radialGradient>
        <radialGradient id="g-shade" cx="35%" cy="30%" r="80%">
          <stop offset="0" stopColor="#fff" stopOpacity=".55" />
          <stop offset=".55" stopColor="#fff" stopOpacity="0" />
          <stop offset="1" stopColor="#000" stopOpacity=".45" />
        </radialGradient>
        <filter id="f-grain" x="0" y="0" width="100%" height="100%">
          <feTurbulence type="fractalNoise" baseFrequency=".85" numOctaves="2" stitchTiles="stitch" />
          <feColorMatrix type="saturate" values="0" />
        </filter>
      </defs>
    </svg>
  );
}
