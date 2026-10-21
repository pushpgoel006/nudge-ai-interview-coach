// One command to run Nudge locally: the Next.js site AND the Python API (on throwaway data).
//
//   npm run dev:all
//
// The Python backend is a separate program, so this starts two processes and stops both on Ctrl+C.
// Where the backend lives: NUDGE_BACKEND_DIR, or the ../backend folder next to this one in the repo.

import { spawn, spawnSync } from "node:child_process";
import { existsSync } from "node:fs";
import path from "node:path";
import { fileURLToPath } from "node:url";

const WEB_DIR = path.resolve(path.dirname(fileURLToPath(import.meta.url)), "..");
const BACKEND_DIR = path.resolve(
  process.env.NUDGE_BACKEND_DIR || path.join(WEB_DIR, "..", "backend"),
);
const isWindows = process.platform === "win32";
const PYTHON = path.join(BACKEND_DIR, ".venv", isWindows ? "Scripts/python.exe" : "bin/python");
const API_PORT = process.env.API_PORT || "8000";
const WEB_PORT = process.env.PORT || "3000";

const color = (code, text) => (process.stdout.isTTY ? `\x1b[${code}m${text}\x1b[0m` : text);
const tag = { api: color("35", "[api]"), web: color("36", "[web]"), dev: color("33", "[dev]") };
const say = (message) => console.log(`${tag.dev} ${message}`);

function fail(message) {
  console.error(`${tag.dev} ${message}`);
  process.exit(1);
}

if (!existsSync(path.join(BACKEND_DIR, "api", "dev.py"))) {
  fail(
    `Could not find the backend at ${BACKEND_DIR}\n` +
      `      Set NUDGE_BACKEND_DIR to the folder that contains the "api" directory, for example:\n` +
      `      NUDGE_BACKEND_DIR="C:/path/to/backend" npm run dev:all`,
  );
}
if (!existsSync(PYTHON)) {
  fail(`Could not find the backend's Python at ${PYTHON}\n      Create its virtual environment first (uv sync, or python -m venv .venv).`);
}

async function isUp(url) {
  try {
    const response = await fetch(url, { signal: AbortSignal.timeout(1500) });
    return response.ok;
  } catch {
    return false;
  }
}

const children = [];
let stopping = false;

function pipeWithPrefix(stream, prefix) {
  let pending = "";
  stream.on("data", (chunk) => {
    pending += chunk.toString();
    const lines = pending.split(/\r?\n/);
    pending = lines.pop() ?? "";
    for (const line of lines) if (line.trim()) console.log(`${prefix} ${line}`);
  });
  stream.on("end", () => pending.trim() && console.log(`${prefix} ${pending}`));
}

function start(name, command, args, options) {
  const child = spawn(command, args, { ...options, stdio: ["ignore", "pipe", "pipe"], windowsHide: true });
  children.push(child);
  pipeWithPrefix(child.stdout, tag[name]);
  pipeWithPrefix(child.stderr, tag[name]);
  child.on("exit", (code) => {
    if (!stopping) {
      say(`${name} stopped (exit code ${code}). Stopping everything.`);
      stopAll(code ?? 1);
    }
  });
  return child;
}

function kill(child) {
  if (!child.pid || child.exitCode !== null) return;
  if (isWindows) spawnSync("taskkill", ["/pid", String(child.pid), "/T", "/F"], { stdio: "ignore" });
  else child.kill("SIGTERM");
}

function stopAll(code = 0) {
  if (stopping) return;
  stopping = true;
  children.forEach(kill);
  setTimeout(() => process.exit(code), 400);
}
process.on("SIGINT", () => stopAll(0));
process.on("SIGTERM", () => stopAll(0));

const apiHealth = `http://127.0.0.1:${API_PORT}/api/health`;

if (await isUp(apiHealth)) {
  say(`An API is already running on port ${API_PORT}; using it instead of starting another.`);
} else {
  say(`Starting the API from ${BACKEND_DIR}`);
  say("It uses throwaway data (temporary database, vectors and uploads), never your real database.");
  start("api", PYTHON, ["-m", "api.dev"], { cwd: BACKEND_DIR, env: { ...process.env, PORT: API_PORT, PYTHONUNBUFFERED: "1" } });
}

say(`Starting the site on port ${WEB_PORT}`);
const nextBin = path.join(WEB_DIR, "node_modules", "next", "dist", "bin", "next");
start("web", process.execPath, [nextBin, "dev", "--port", WEB_PORT], { cwd: WEB_DIR, env: { ...process.env, BACKEND_URL: `http://127.0.0.1:${API_PORT}` } });

// Tell the user when everything is ready (the API takes a while to load its AI libraries).
(async () => {
  const started = Date.now();
  while (!stopping && Date.now() - started < 180_000) {
    if (await isUp(apiHealth)) {
      say(`Ready.  Site: http://localhost:${WEB_PORT}   Studio: http://localhost:${WEB_PORT}/studio   API: http://127.0.0.1:${API_PORT}`);
      say("Press Ctrl+C to stop both.");
      // Test hook: DEV_ALL_EXIT_AFTER_MS=5000 shuts everything down by itself once ready.
      if (process.env.DEV_ALL_EXIT_AFTER_MS) setTimeout(() => stopAll(0), Number(process.env.DEV_ALL_EXIT_AFTER_MS));
      return;
    }
    await new Promise((resolve) => setTimeout(resolve, 2000));
  }
  if (!stopping) say("The API is taking unusually long to start. Check the [api] lines above for errors.");
})();
