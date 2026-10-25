#!/usr/bin/env python3
"""Auditoria do CV mestre: garante que foi confirmado pela pessoa e que não está desatualizado.

Uso:
  python audit.py status  <candidaturas/perfil/master_cv.json>
  python audit.py confirm <candidaturas/perfil/master_cv.json> --confirmado-pela-pessoa [--notes "texto"]

`confirm` carimba a auditoria e `confirmed_at` em TODAS as experiências. Só correr depois de a pessoa
ter dito explicitamente que o conteúdo está correto e atual. O gate.py recusa qualquer vaga se a auditoria
faltar ou for mais antiga que `audit_max_age_days` (por omissão 90).
"""
import json, re, sys
from datetime import date, datetime
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))
from _common import DEFAULT_CONFIG, utf8
from ats_check import parse_period


def _days(s):
    try:
        return (date.today() - datetime.strptime(s, "%Y-%m-%d").date()).days
    except Exception:
        return None


def audit_problems(master_path, max_age=None):
    """(bloqueantes, avisos) sobre o estado da auditoria do CV mestre."""
    max_age = max_age if max_age is not None else DEFAULT_CONFIG["audit_max_age_days"]
    p = Path(master_path)
    if not p.exists():
        return [f"não existe {p}: fazer primeiro a auditoria/levantamento do CV (Passo 0)"], []
    m = json.loads(p.read_text(encoding="utf-8"))
    block, warn = [], []
    a = m.get("audit") or {}
    age = _days(a.get("date", ""))
    if not a.get("confirmed_by_user") or age is None:
        block.append("o CV mestre nunca foi auditado e confirmado pela pessoa (falta 'audit')")
    elif age > max_age:
        block.append(f"a última auditoria foi há {age} dias (máximo {max_age}): repetir o levantamento")
    for i, e in enumerate(m.get("experience", [])):
        if not e.get("confirmed_at"):
            block.append(f"experience[{i}] ({e.get('role', '?')} @ {e.get('company', '?')}) sem confirmação da pessoa ('confirmed_at')")
        if e.get("role_note") and not e.get("role_note_confirmed"):
            block.append(f"experience[{i}].role_note ('{e['role_note']}') não está confirmado como verificável ('role_note_confirmed')")
    periods = [parse_period(e.get("period", "")) for e in m.get("experience", [])]
    periods = [x for x in periods if x]
    if periods:
        today = date.today()
        last_end = max(x[1] for x in periods)
        months = (today.year - last_end[0]) * 12 + (today.month - last_end[1])
        if months > 3:
            warn.append(f"o último cargo terminou há ~{months} meses e nada o substitui: perguntar o que fez desde então (emprego, freelance, formação, projetos)")
    if age is not None and age > 30:
        warn.append(f"auditoria com {age} dias: confirmar se houve novidades (promoção, projeto, ferramenta, certificação)")
    return block, warn


def main():
    utf8()
    if len(sys.argv) < 3 or sys.argv[1] not in ("status", "confirm"):
        sys.exit(__doc__)
    cmd, path = sys.argv[1], Path(sys.argv[2])
    if cmd == "status":
        block, warn = audit_problems(path)
        for b in block:
            print("BLOQUEIA  " + b)
        for w in warn:
            print("AVISO     " + w)
        print("=> AUDITORIA " + ("EM FALTA/DESATUALIZADA" if block else "OK"))
        sys.exit(1 if block else 0)
    if "--confirmado-pela-pessoa" not in sys.argv:
        sys.exit("Recusado: só confirmar depois de a pessoa dizer explicitamente que o CV mestre está correto e atual. "
                 "Repetir com --confirmado-pela-pessoa.")
    m = json.loads(path.read_text(encoding="utf-8"))
    today = date.today().isoformat()
    notes = sys.argv[sys.argv.index("--notes") + 1] if "--notes" in sys.argv else ""
    m["audit"] = {"date": today, "confirmed_by_user": True, "notes": notes}
    for e in m.get("experience", []):
        e["confirmed_at"] = today
        if e.get("role_note"):
            e["role_note_confirmed"] = True
    path.write_text(json.dumps(m, ensure_ascii=False, indent=2), encoding="utf-8")
    print(f"Auditoria confirmada em {today} ({len(m.get('experience', []))} experiências).")


if __name__ == "__main__":
    main()
