#!/usr/bin/env python3
"""Tracker de candidaturas.

Uso:
  python tracker.py <raiz_candidaturas> list            # lista ordenada por prazo, com dias restantes
  python tracker.py <raiz_candidaturas> set <pasta> <estado> [--fit Alto]
Estados: encontrada | em_revisao | documentos_aprovados | enviada | entrevista | recusada | oferta | desistiu
"""
import csv, sys
from datetime import date, datetime
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))
from _common import utf8

ESTADOS = ["encontrada", "em_revisao", "documentos_aprovados", "enviada", "entrevista", "recusada", "oferta", "desistiu"]


def load(root):
    t = Path(root) / "tracker.csv"
    return t, (list(csv.DictReader(t.open(encoding="utf-8", newline=""))) if t.exists() else [])


def days_left(prazo):
    try:
        return (datetime.strptime(prazo, "%Y-%m-%d").date() - date.today()).days
    except Exception:
        return None


def main():
    utf8()
    if len(sys.argv) < 3:
        sys.exit(__doc__)
    root, cmd = sys.argv[1], sys.argv[2]
    t, rows = load(root)
    if cmd == "list":
        if not rows:
            print("Sem candidaturas registadas."); return
        def key(r):
            d = days_left(r.get("prazo", ""))
            return (d is None, d if d is not None else 0)
        print(f"{'ESTADO':<22}{'PRAZO':<14}{'DIAS':<6}{'FIT':<7}EMPRESA - CARGO")
        for r in sorted(rows, key=key):
            d = days_left(r.get("prazo", ""))
            flag = "" if d is None else (" ATRASADO" if d < 0 and r["estado"] in ESTADOS[:3] else (" URGENTE" if d <= 3 and r["estado"] in ESTADOS[:3] else ""))
            print(f"{r['estado']:<22}{r.get('prazo','') or '-':<14}{'' if d is None else d:<6}{r.get('fit','') or '-':<7}{r['empresa']} - {r['cargo']}{flag}")
    elif cmd == "set" and len(sys.argv) >= 5:
        pasta, estado = sys.argv[3], sys.argv[4]
        if estado not in ESTADOS:
            sys.exit(f"Estado inválido. Usar um de: {', '.join(ESTADOS)}")
        fit = sys.argv[sys.argv.index("--fit") + 1] if "--fit" in sys.argv else None
        hit = [r for r in rows if r["pasta"] == pasta]
        if not hit:
            sys.exit(f"Pasta não encontrada no tracker: {pasta}")
        hit[0]["estado"] = estado
        if fit:
            hit[0]["fit"] = fit
        with t.open("w", encoding="utf-8", newline="") as f:
            w = csv.DictWriter(f, fieldnames=list(rows[0].keys())); w.writeheader(); w.writerows(rows)
        print(f"{pasta} -> {estado}")
    else:
        sys.exit(__doc__)


if __name__ == "__main__":
    main()
