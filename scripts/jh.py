#!/usr/bin/env python3
"""Comando único do job-hunter. Uso: python jh.py <comando> [argumentos]

  init      cria a pasta de uma vaga + regista no tracker        (init_job_folder.py)
  build     gera CV/carta em .docx (--pdf opcional)               (build_docx.py)
  check     verificações mecânicas ATS/carta                      (ats_check.py)
  hash      hash da versão do rascunho (--write grava .hash)      (gate.py hash)
  gate      valida a ronda e aprova/reprova                       (gate.py check)
  tracker   listar / mudar estado das candidaturas                (tracker.py)
  extract   extrair texto de um CV .docx/.pdf                     (extract_text.py)
  audit     estado/confirmação da auditoria do CV mestre          (audit.py)
  install   instalar skill + subagentes (Claude Code/OpenCode)    (install.py)
  doctor    verificar dependências e instalação
  selftest  teste automático de ponta a ponta com dados de exemplo
"""
import importlib.util, shutil, subprocess, sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
from _common import utf8

SCRIPTS = {"init": "init_job_folder.py", "build": "build_docx.py", "check": "ats_check.py", "tracker": "tracker.py",
           "extract": "extract_text.py", "audit": "audit.py", "install": "install.py", "selftest": "selftest.py"}


def doctor():
    ok = True
    def line(good, msg, fix=""):
        nonlocal ok
        print(("[OK]   " if good else "[FALTA]") + " " + msg + ("" if good or not fix else f"  -> {fix}"))
        ok = ok and good
    line(sys.version_info >= (3, 9), f"Python {sys.version.split()[0]}", "precisa de Python 3.9+")
    line(importlib.util.find_spec("docx") is not None, "python-docx", "pip install python-docx")
    soffice = shutil.which("soffice") or shutil.which("libreoffice")
    print(("[OK]   " if soffice else "[AVISO]") + " LibreOffice (PDF e contagem exata de páginas)" +
          ("" if soffice else "  -> opcional; sem ele guarda-se como PDF a partir do Word e a contagem de páginas é estimada"))
    print(("[OK]   " if shutil.which("pdftotext") else "[AVISO]") + " pdftotext (ler CVs em PDF)" +
          ("" if shutil.which("pdftotext") else "  -> opcional; o Claude Code lê PDFs diretamente"))
    cwd, home = Path.cwd(), Path.home()
    places = {"skill (projeto, Claude)": cwd / ".claude/skills/job-hunter", "skill (projeto, OpenCode)": cwd / ".opencode/skills/job-hunter",
              "skill (utilizador, Claude)": home / ".claude/skills/job-hunter",
              "skill (utilizador, OpenCode)": home / ".config/opencode/skills/job-hunter"}
    found = [k for k, v in places.items() if v.exists()]
    print(("[OK]   " if found else "[AVISO]") + " skill instalada: " + (", ".join(found) if found else "nenhuma encontrada a partir daqui"))
    agent_dirs = [cwd / ".claude/agents", cwd / ".opencode/agents", cwd / ".opencode/agent", home / ".claude/agents",
                  home / ".config/opencode/agents", home / ".config/opencode/agent"]
    ag = [str(d) for d in agent_dirs if (d / "jh-hr.md").exists()]
    print(("[OK]   " if ag else "[AVISO]") + " subagentes jh-*: " + (", ".join(ag) if ag else
          "não instalados -> a revisão corre em modo sequencial (menos isolado). Instalar: python jh.py install --target claude-code --scope project"))
    sys.exit(0 if ok else 1)


def main():
    utf8()
    if len(sys.argv) < 2 or sys.argv[1] in ("-h", "--help"):
        print(__doc__); return
    cmd, rest = sys.argv[1], sys.argv[2:]
    if cmd == "doctor":
        doctor()
    if cmd == "hash":
        target, rest = HERE / "gate.py", ["hash"] + rest
    elif cmd == "gate":
        target, rest = HERE / "gate.py", ["check"] + rest
    elif cmd in SCRIPTS:
        target = HERE / SCRIPTS[cmd]
    else:
        sys.exit(f"Comando desconhecido: {cmd}\n{__doc__}")
    sys.exit(subprocess.call([sys.executable, str(target)] + rest))


if __name__ == "__main__":
    main()
