#!/usr/bin/env python3
"""Tracker de candidaturas.

Uso:
  tracker.py <raiz> list                              lista ordenada por prazo, com dias restantes
  tracker.py <raiz> set <pasta> <estado> [--fit Alto] [--data AAAA-MM-DD]
  tracker.py <raiz> followup                          o que precisa de follow-up hoje (cadência em config.json)
  tracker.py <raiz> followed <pasta> [--data ...]     regista que o follow-up foi enviado
  tracker.py <raiz> patterns                          funil, tempos de resposta e o que está a ser recusado
Estados: encontrada | em_revisao | documentos_aprovados | enviada | entrevista | recusada | oferta | desistiu | sem_resposta
"""
import csv, sys
from collections import Counter, defaultdict
from datetime import date, datetime
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))
from _common import utf8, load_config

ESTADOS = ["encontrada", "em_revisao", "documentos_aprovados", "enviada", "entrevista", "recusada", "oferta", "desistiu", "sem_resposta"]
FIELDS = ["pasta", "data_criada", "empresa", "cargo", "local", "prazo", "url", "fit", "estado",
          "fonte", "data_envio", "data_resposta", "followups", "ultimo_followup"]
RESPOSTA = ("entrevista", "recusada", "oferta", "sem_resposta")


def load(root):
    t = Path(root) / "tracker.csv"
    if not t.exists():
        return t, []
    rows = list(csv.DictReader(t.open(encoding="utf-8", newline="")))
    return t, [{k: (r.get(k) or "") for k in FIELDS} for r in rows]  # compatível com trackers antigos


def save(t, rows):
    with t.open("w", encoding="utf-8", newline="") as f:
        w = csv.DictWriter(f, fieldnames=FIELDS)
        w.writeheader(); w.writerows(rows)


def parse(d):
    try:
        return datetime.strptime(d, "%Y-%m-%d").date()
    except Exception:
        return None


def days_left(prazo):
    p = parse(prazo)
    return None if p is None else (p - date.today()).days


def cmd_list(rows):
    if not rows:
        print("Sem candidaturas registadas."); return
    key = lambda r: (days_left(r["prazo"]) is None, days_left(r["prazo"]) or 0)
    print(f"{'ESTADO':<22}{'PRAZO':<14}{'DIAS':<6}{'FIT':<12}EMPRESA - CARGO")
    for r in sorted(rows, key=key):
        d = days_left(r["prazo"])
        open_ = r["estado"] in ESTADOS[:3]
        flag = "" if d is None or not open_ else (" ATRASADO" if d < 0 else (" URGENTE" if d <= 3 else ""))
        print(f"{r['estado']:<22}{r['prazo'] or '-':<14}{'' if d is None else d:<6}{r['fit'] or '-':<12}{r['empresa']} - {r['cargo']}{flag}")


def cmd_set(t, rows, args):
    if len(args) < 2:
        sys.exit(__doc__)
    pasta, estado = args[0], args[1]
    if estado not in ESTADOS:
        sys.exit(f"Estado inválido. Usar um de: {', '.join(ESTADOS)}")
    opt = lambda n: args[args.index(n) + 1] if n in args else None
    hit = [r for r in rows if r["pasta"] == pasta]
    if not hit:
        sys.exit(f"Pasta não encontrada no tracker: {pasta}")
    r, when = hit[0], opt("--data") or date.today().isoformat()
    r["estado"] = estado
    if opt("--fit"):
        r["fit"] = opt("--fit")
    if estado == "enviada":
        r["data_envio"] = when
    if estado in RESPOSTA:
        r["data_resposta"] = when
    save(t, rows)
    print(f"{pasta}: {estado}")


def followups_due(rows, cfg, today=None):
    """Lista (linha, mensagem) das candidaturas enviadas que pedem ação. Função pura, testável."""
    today = today or date.today()
    dias, fim = cfg["followup"]["dias"], cfg["followup"]["encerrar_apos_dias"]
    out = []
    for r in rows:
        env = parse(r["data_envio"])
        if r["estado"] != "enviada" or env is None:
            continue
        passados, n = (today - env).days, int(r["followups"] or 0)
        if n < len(dias) and passados >= dias[n]:
            out.append((r, f"follow-up #{n + 1} (enviada há {passados} dias)"))
        elif n >= len(dias) and passados >= fim:
            out.append((r, f"sem resposta há {passados} dias: marcar 'sem_resposta' ou desistir"))
    return out


def cmd_followup(root, rows):
    due = followups_due(rows, load_config(Path(root) / "_"))
    if not due:
        print("Nada a fazer hoje."); return
    for r, msg in due:
        print(f"- {r['empresa']} - {r['cargo']}: {msg}\n    pasta: {r['pasta']}")


def cmd_followed(t, rows, args):
    hit = [r for r in rows if r["pasta"] == args[0]] if args else []
    if not hit:
        sys.exit("Pasta não encontrada no tracker.")
    when = args[args.index("--data") + 1] if "--data" in args else date.today().isoformat()
    hit[0]["followups"] = str(int(hit[0]["followups"] or 0) + 1)
    hit[0]["ultimo_followup"] = when
    save(t, rows)
    print(f"{args[0]}: follow-up #{hit[0]['followups']} registado")


def fit_label(r):
    return (r["fit"].split() or ["sem_fit"])[0]


def cmd_patterns(rows):
    sent = [r for r in rows if r["data_envio"]]
    if not sent:
        print("Ainda não há candidaturas enviadas para analisar."); return
    print("FUNIL:", ", ".join(f"{k}={v}" for k, v in Counter(r["estado"] for r in rows).items()))
    resp = [r for r in sent if r["estado"] in RESPOSTA[:3]]
    pos = [r for r in sent if r["estado"] in ("entrevista", "oferta")]
    print(f"Enviadas: {len(sent)} | com resposta: {len(resp)} | entrevistas/ofertas: {len(pos)} ({100 * len(pos) // len(sent)}%)")
    tempos = [(parse(r["data_resposta"]) - parse(r["data_envio"])).days for r in resp if parse(r["data_resposta"]) and parse(r["data_envio"])]
    if tempos:
        print(f"Tempo médio até resposta: {sum(tempos) / len(tempos):.0f} dias")
    for titulo, keyf in (("fit", fit_label), ("fonte", lambda r: r["fonte"] or "n/d"), ("local", lambda r: r["local"] or "n/d")):
        grupos = defaultdict(lambda: [0, 0, 0])
        for r in sent:
            g = grupos[keyf(r)]
            g[0] += 1; g[1] += r["estado"] in ("entrevista", "oferta"); g[2] += r["estado"] == "recusada"
        print(f"\nPor {titulo}:  (enviadas / positivas / recusadas)")
        for k, (n, p, x) in sorted(grupos.items(), key=lambda kv: -kv[1][0]):
            print(f"  {k:<20}{n:>3} / {p:>2} / {x:>2}")
    if len(sent) < 10:
        print("\nAviso: menos de 10 candidaturas; os padrões ainda são só indícios.")


def main():
    utf8()
    if len(sys.argv) < 3:
        sys.exit(__doc__)
    root, cmd, args = sys.argv[1], sys.argv[2], sys.argv[3:]
    t, rows = load(root)
    {"list": lambda: cmd_list(rows), "set": lambda: cmd_set(t, rows, args), "followup": lambda: cmd_followup(root, rows),
     "followed": lambda: cmd_followed(t, rows, args), "patterns": lambda: cmd_patterns(rows)}.get(cmd, lambda: sys.exit(__doc__))()


if __name__ == "__main__":
    main()
