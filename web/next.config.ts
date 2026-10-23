import type { NextConfig } from "next";
import path from "node:path";

// Where the Python API runs. Locally: http://127.0.0.1:8000.
// On Vercel, set BACKEND_URL to the Hugging Face Space URL.
const BACKEND_URL = (process.env.BACKEND_URL || "http://127.0.0.1:8000").replace(/\/$/, "");

const nextConfig: NextConfig = {
  // Pin the project root so a stray lockfile higher up the disk is not picked up.
  turbopack: { root: path.resolve(__dirname) },
  // Slow AI answers can take longer than the 30 s default before the proxy gives up with "socket hang up".
  experimental: { proxyTimeout: 180_000 },
  cacheComponents: true,
  partialPrefetching: true,
  // The browser only ever talks to this site; /api/* is forwarded to the backend,
  // so cookies stay first-party and the backend URL is never exposed to the page.
  async rewrites() {
    return [{ source: "/api/:path*", destination: `${BACKEND_URL}/api/:path*` }];
  },
};

export default nextConfig;
