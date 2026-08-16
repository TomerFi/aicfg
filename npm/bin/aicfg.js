#!/usr/bin/env node

import { spawn } from "node:child_process";
import { dirname, resolve } from "node:path";
import { fileURLToPath } from "node:url";

const __dirname = dirname(fileURLToPath(import.meta.url));
const SRC_ROOT = resolve(__dirname, "..", "src");

function findPython() {
  const candidates = process.platform === "win32"
    ? ["python", "python.exe"]
    : ["python3", "python"];

  const promises = candidates.map((name) => {
    return new Promise((resolve) => {
      const proc = spawn(name, ["--version"], {
        stdio: ["ignore", "pipe", "pipe"],
      });

      let output = "";
      proc.stdout.on("data", (chunk) => { output += chunk; });
      proc.stderr.on("data", (chunk) => { output += chunk; });

      proc.on("close", (code) => {
        if (code !== 0) {
          return resolve(null);
        }
        const version = parseVersion(output);
        if (version) {
          resolve({ name, version });
        } else {
          resolve(null);
        }
      });

      proc.on("error", () => resolve(null));
    });
  });

  return Promise.all(promises).then((results) =>
    results.find((result) =>
      result && satisfies(result.version, 3, 11)
    ) ?? null
  );
}

function parseVersion(output) {
  const match = /Python (\d+)\.(\d+)/.exec(output);
  if (!match) {
    return null;
  }
  return { major: parseInt(match[1]), minor: parseInt(match[2]) };
}

function satisfies(version, major, minor) {
  return version.major > major || (version.major === major && version.minor >= minor);
}

function importCode() {
  return [
    "import sys",
    "from aicfg.cli import main",
    "try:",
    "    main()",
    "except KeyboardInterrupt:",
    "    sys.exit(130)",
  ].join("\n");
}

async function main() {
  const result = await findPython();
  if (!result) {
    process.stderr.write(
      "aicfg: Python 3.11+ is required but was not found on PATH.\n" +
        "Install Python 3.11+ and ensure it is available on PATH.\n"
    );
    process.exit(1);
  }

  if (!satisfies(result.version, 3, 11)) {
    process.stderr.write(
      `aicfg: Python ${result.version.major}.${result.version.minor} found, but 3.11+ is required.\n`
    );
    process.exit(1);
  }

  const env = { ...process.env, PYTHONPATH: SRC_ROOT };

  const proc = spawn(result.name, ["-c", importCode(), ...process.argv.slice(2)], {
    env,
    stdio: "inherit",
  });

  proc.on("close", (code) => {
    process.exit(code ?? 1);
  });
}

main().catch((err) => {
  process.stderr.write(`aicfg: ${err.message}\n`);
  process.exit(1);
});
