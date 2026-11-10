#!/usr/bin/env python3
"""Avaliação de uma vaga: nota 0-5 ponderada, com evidência obrigatória por dimensão.

Uso: evaluate.py <pasta_da_vaga> [avaliacao.json]
Lê <pasta>/avaliacao.json, valida, calcula a nota e escreve <pasta>/avaliacao.md.
Atualiza o campo `fit` no tracker. Códigos de saída: 0 avançar · 2 não avançar · 1 erro de validação.
Verifica também que analise_fit.md tem os blocos A-G (aviso, não bloqueia).
"""
import csv, json, re, sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))
from _common import utf8, load_config
from tracker import FIELDS

PESOS = {
    "requisitos_obrigatorios": 0.25, "experiencia_relevante": 0.15, "senioridade": 0.10, "competencias_desejaveis": 0.10,
    "local_modalidade": 0.10, "autorizacao_trabalho": 0.05, "contrato_compensacao": 0.05, "empresa_setor": 0.05,
    "crescimento": 0.05, "legitimidade": 0.10,
}
BLOCOS = "ABCDEFG"


def validate(data):
    """Devolve a lista de erros (vazia se válido)."""
    dims, errs = data.get("dimensoes", {}), []
    for k in PESOS:
        d = dims.get(k)
        if not isinstance(d, dict):
            errs.append(f"falta a dimensão '{k}'"); continue
        n = d.get("nota")
        if not isinstance(n, (int, float)) or not 0 <= n <= 5:
            errs.append(f"'{k}': nota tem de estar entre 0 e 5")
        if len(str(d.get("evidencia", "")).strip()) < 10:
            errs.append(f"'{k}': falta evidência concreta (do anúncio ou do CV mestre)")
    extra = set(dims) - set(PESOS)
    return errs + ([f"dimensões desconhecidas: {sorted(extra)}"] if extra else [])


def score(data):
    return round(sum(PESOS[k] * data["dimensoes"][k]["nota"] for k in PESOS), 2)


def decide(data, cfg):
    """(veredicto, razões). Eliminatórias e vaga suspeita bloqueiam sempre, qualquer que seja a nota."""
    s, th, why = score(data), cfg["avaliacao"], []
    elim = [e for e in data.get("eliminatorias", []) if str(e).strip()]
    if elim:
        why.append("lacuna(s) eliminatória(s): " + "; ".join(elim))
    if data["dimensoes"]["legitimidade"]["nota"] <= 2:
        why.append("legitimidade duvidosa (nota ≤ 2)")
    if why:
        return "nao_avancar", why
    if s >= th["min_forte"]:
        return "avancar_forte", []
    if s >= th["min_avancar"]:
        return "avancar", []
    return "nao_avancar", [f"nota {s} abaixo do mínimo {th['min_avancar']}"]


def label(s, cfg):
    return "Alto" if s >= cfg["avaliacao"]["min_forte"] else ("Médio" if s >= cfg["avaliacao"]["min_avancar"] else "Baixo")


def render(data, s, verdict, why):
    lines = [f"# Avaliação: nota {s}/5 ({verdict.replace('_', ' ')})", ""]
    lines += [f"- ⚠ {w}" for w in why] + ([""] if why else [])
    lines += ["| Dimensão | Peso | Nota | Evidência |", "|---|---|---|---|"]
    for k, w in PESOS.items():
        d = data["dimensoes"][k]
        lines.append(f"| {k.replace('_', ' ')} | {int(w * 100)}% | {d['nota']} | {str(d['evidencia']).replace('|', '/')} |")
    if data.get("resumo"):
        lines += ["", "## Resumo", "", data["resumo"]]
    return "\n".join(lines) + "\n"


def update_tracker(job, fit):
    t = job.parent / "tracker.csv"
    if not t.exists():
        return
    rows = list(csv.DictReader(t.open(encoding="utf-8", newline="")))
    for r in rows:
        if r.get("pasta") == job.name:
            r["fit"] = fit
    with t.open("w", encoding="utf-8", newline="") as f:
        w = csv.DictWriter(f, fieldnames=FIELDS, restval="")
        w.writeheader(); w.writerows(rows)


def missing_blocks(job):
    p = job / "analise_fit.md"
    if not p.exists():
        return list(BLOCOS)
    found = set(re.findall(r"^#{1,3}\s*([A-G])[\s\.\):\-]", p.read_text(encoding="utf-8"), re.M))
    return [b for b in BLOCOS if b not in found]


def main():
    utf8()
    if len(sys.argv) < 2:
        sys.exit(__doc__)
    job = Path(sys.argv[1]).resolve()
    src = Path(sys.argv[2]) if len(sys.argv) > 2 else job / "avaliacao.json"
    try:
        data = json.loads(src.read_text(encoding="utf-8"))
    except Exception as e:
        sys.exit(f"Não consegui ler {src}: {e}")
    errs = validate(data)
    if errs:
        print("avaliacao.json inválido:\n- " + "\n- ".join(errs)); sys.exit(1)
    cfg = load_config(job)
    s = score(data)
    verdict, why = decide(data, cfg)
    (job / "avaliacao.md").write_text(render(data, s, verdict, why), encoding="utf-8")
    update_tracker(job, f"{label(s, cfg)} ({s})")
    miss = missing_blocks(job)
    print(f"Nota {s}/5 -> {verdict}" + "".join(f"\n  - {w}" for w in why))
    if miss:
        print(f"AVISO: analise_fit.md sem os blocos {', '.join(miss)} (ver references/evaluation.md)")
    sys.exit(2 if verdict == "nao_avancar" else 0)


if __name__ == "__main__":
    main()
