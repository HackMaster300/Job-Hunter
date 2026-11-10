#!/usr/bin/env node
"use strict";
// Instalador npx do Job Hunter. Sem dependências: delega em scripts/*.py (Python 3.9+).
const { spawnSync } = require("node:child_process");
const path = require("node:path");

const ROOT = path.resolve(__dirname, "..");
const VERSION = require(path.join(ROOT, "package.json")).version;
const JH = path.join(ROOT, "scripts", "jh.py");

const HELP = `Job Hunter v${VERSION}

Uso: npx job-hunter-skill <comando> [opções]

  install [--target claude-code|opencode|both] [--scope project|user]
          [--workspace DIR] [--force] [--deps]
        Instala a skill e os 6 subagentes revisores (por omissão: claude-code, project).
        --deps  instala também python-docx (pip)
  doctor          verifica Python, dependências e instalação
  selftest        teste automático de ponta a ponta (dados fictícios)
  jh <comando>    qualquer comando do jh.py (scan, eval, tracker, stories, build, check, gate...)
  version         mostra a versão

Exemplos:
  npx job-hunter-skill install
  npx job-hunter-skill install --target both --scope user
  npx job-hunter-skill jh scan run --root candidaturas
`;

function findPython() {
  for (const cmd of process.platform === "win32" ? ["python", "py", "python3"] : ["python3", "python"]) {
    const r = spawnSync(cmd, ["-c", "import sys;print(sys.version_info>=(3,9))"], { encoding: "utf8" });
    if (r.status === 0 && r.stdout.trim() === "True") return cmd;
  }
  return null;
}

function py(python, args) {
  const r = spawnSync(python, args, { stdio: "inherit" });
  return r.status === null ? 1 : r.status;
}

function option(args, name, fallback) {
  const i = args.indexOf(name);
  return i >= 0 && args[i + 1] ? args[i + 1] : fallback;
}

function install(python, args) {
  if (args.includes("--deps") && py(python, ["-m", "pip", "install", "python-docx"]) !== 0) {
    console.error("Falhou a instalação de python-docx. Corre manualmente: pip install python-docx");
  }
  const forward = ["--target", option(args, "--target", "claude-code"), "--scope", option(args, "--scope", "project"),
    "--workspace", option(args, "--workspace", process.cwd())];
  if (args.includes("--force")) forward.push("--force");
  const code = py(python, [path.join(ROOT, "scripts", "install.py"), ...forward]);
  if (code === 0 && !args.includes("--deps")) {
    console.log("\nSe faltar python-docx: pip install python-docx   (ou repetir com --deps)");
  }
  return code;
}

function main() {
  const [cmd, ...rest] = process.argv.slice(2);
  if (!cmd || ["help", "-h", "--help"].includes(cmd)) return console.log(HELP);
  if (["version", "-v", "--version"].includes(cmd)) return console.log(VERSION);
  const python = findPython();
  if (!python) {
    console.error("Python 3.9+ não encontrado. Instala em https://www.python.org/downloads/ e tenta de novo.");
    process.exit(1);
  }
  const table = {
    install: () => install(python, rest),
    doctor: () => py(python, [JH, "doctor"]),
    selftest: () => py(python, [JH, "selftest"]),
    jh: () => py(python, [JH, ...rest]),
  };
  if (!table[cmd]) {
    console.error(`Comando desconhecido: ${cmd}\n`);
    console.log(HELP);
    process.exit(1);
  }
  process.exit(table[cmd]());
}

main();
