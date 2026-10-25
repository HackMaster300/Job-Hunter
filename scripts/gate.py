#!/usr/bin/env python3
"""Portão de aprovação: os documentos só vão para final/ se TODOS os agentes derem GREEN sobre a mesma versão.

Uso:
  python gate.py hash  <pasta_vaga> [--write]    # hash da versão atual; --write grava rascunho/.hash (os revisores leem-no)
  python gate.py check <pasta_vaga> [--round N]  # valida a ronda; se aprovada, copia para final/

Códigos de saída: 0 = APROVADO | 1 = REPROVADO (há feedback) | 2 = limite de rondas atingido (escalar à pessoa)
                  3 = ronda INCOMPLETA (faltam veredictos; nada reprovado ainda)
                  4 = AUDITORIA do CV mestre em falta/desatualizada (fazer o levantamento com a pessoa; não é um problema de redação)
"""
import argparse, csv, hashlib, json, re, shutil, sys
from datetime import datetime
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))
from _common import load_config, utf8
from audit import audit_problems

# Etapas: A (script + fact_checker) -> B (paralelo) -> C (skeptic, lê os veredictos de B)
STAGE_A = ["fact_checker"]
STAGE_B = ["ats", "hr", "hiring_manager", "language_editor"]
STAGE_C = ["skeptic"]
AGENTS = STAGE_A + STAGE_B + STAGE_C
FILES = ["cv.json", "carta.json"]


def art_hash(folder):
    h = hashlib.sha256()
    for f in FILES:
        p = folder / "rascunho" / f
        if not p.exists():
            sys.exit(f"Falta {p}")
        h.update(f.encode() + b"\0" + p.read_bytes() + b"\0")
    return h.hexdigest()[:16]


def rounds(folder):
    return sorted(int(m.group(1)) for d in (folder / "revisoes").glob("round-*") if (m := re.fullmatch(r"round-(\d+)", d.name)))


def stale_docx(folder):
    r = folder / "rascunho"
    newest = max((r / f).stat().st_mtime for f in FILES)
    return [p.name for p in r.glob("*.docx") if p.stat().st_mtime < newest - 1]


def validate(agent, v, cur_hash, cfg):
    """Problemas que impedem este veredicto de contar como GREEN (lista vazia = GREEN válido)."""
    probs = []
    if v.get("agent") != agent:
        probs.append(f"campo 'agent' deveria ser '{agent}'")
    if v.get("artifact_hash") != cur_hash:
        probs.append(f"VERSÃO DESATUALIZADA: veredicto dado a {v.get('artifact_hash')}, rascunho atual é {cur_hash}")
    if v.get("verdict") != "GREEN":
        probs.append("veredicto RED")
    score, mn = v.get("score"), cfg["min_score"][agent]
    if not isinstance(score, (int, float)) or score < mn:
        probs.append(f"score {score} abaixo do mínimo {mn}")
    if v.get("blockers"):
        probs.append(f"{len(v['blockers'])} blocker(s) por resolver")
    if v.get("verdict") == "GREEN":
        if len(v.get("evidence", [])) < cfg["min_evidence"]:
            probs.append(f"GREEN inválido: precisa de >={cfg['min_evidence']} itens em 'evidence'")
        if len(v.get("weakest_points", [])) < cfg["min_weakest_points"]:
            probs.append(f"GREEN inválido: precisa de >={cfg['min_weakest_points']} itens em 'weakest_points'")
    return probs


def update_tracker(folder, estado):
    t = folder.parent / "tracker.csv"
    if not t.exists():
        return
    rows = list(csv.DictReader(t.open(encoding="utf-8", newline="")))
    if not rows:
        return
    for r in rows:
        if r.get("pasta") == folder.name:
            r["estado"] = estado
    with t.open("w", encoding="utf-8", newline="") as f:
        w = csv.DictWriter(f, fieldnames=list(rows[0].keys()))
        w.writeheader(); w.writerows(rows)


def check(folder, rnd):
    cfg = load_config(folder)
    cur = art_hash(folder)
    rd = folder / "revisoes" / f"round-{rnd}"
    if not rd.exists():
        sys.exit(f"Não existe {rd}")
    report, feedback = [], []
    red, missing = False, False

    # 0. o CV mestre tem de estar auditado e confirmado pela pessoa (senão pode estar desatualizado ou ter títulos que não são os dela)
    ablock, awarn = audit_problems(folder.parent / "perfil" / "master_cv.json", cfg["audit_max_age_days"])
    for w in awarn:
        print("AVISO auditoria:", w)
    if ablock:
        print("=> AUDITORIA DO CV MESTRE EM FALTA/DESATUALIZADA. Fazer o levantamento com a pessoa (references/intake-interview.md) antes de aprovar qualquer vaga:")
        for b in ablock:
            print("   - " + b)
        if (folder / "final").exists():
            shutil.rmtree(folder / "final")
        (folder / "revisoes" / "APROVADO.json").unlink(missing_ok=True)
        return 4

    # script determinístico
    ac = rd / "ats_check.json"
    if not ac.exists():
        report.append(("ats_check.py", "NÃO EXECUTADO")); missing = True
    else:
        j = json.loads(ac.read_text(encoding="utf-8"))
        if j.get("status") != "PASS":
            red = True; report.append(("ats_check.py", "FAIL"))
            fb = ["## Script ats_check (verificações mecânicas)"]
            fb += [f"- **{c['name']}**: {c['detail']}" for c in j["checks"] if not c["pass"] and c["blocking"]]
            feedback.append("\n".join(fb) + "\n")
        else:
            report.append(("ats_check.py", "PASS"))

    stale = stale_docx(folder)
    if stale:
        red = True; report.append(("docx", "DESATUALIZADO"))
        feedback.append("## .docx desatualizados\n- Reconstruir a partir dos JSON: " + ", ".join(stale) + "\n")

    verdicts = {}
    for ag in AGENTS:
        f = rd / f"{ag}.json"
        if not f.exists():
            report.append((ag, "aguarda execução")); missing = True; continue
        try:
            v = json.loads(f.read_text(encoding="utf-8"))
        except Exception as e:
            red = True; report.append((ag, f"JSON INVÁLIDO ({e})"))
            feedback.append(f"## Agente `{ag}`\n- ⚠ O ficheiro do veredicto não é JSON válido: {e}\n"); continue
        verdicts[ag] = (f, v)
        probs = validate(ag, v, cur, cfg)
        if ag == "skeptic":  # tem de ter lido os outros: gravado depois deles
            others = [verdicts[a][0].stat().st_mtime for a in STAGE_A + STAGE_B if a in verdicts]
            if others and f.stat().st_mtime < max(others) - 1:
                probs.append("o skeptic foi gravado ANTES de outros veredictos; tem de correr depois e ler os veredictos da ronda")
        if probs:
            red = True
            report.append((ag, f"RED ({v.get('score')})"))
            fb = [f"## Agente `{ag}` - score {v.get('score')} (mínimo {cfg['min_score'][ag]})"]
            fb += [f"- ⚠ {p}" for p in probs]
            for b in v.get("blockers", []):
                fb.append(f"- **BLOCKER** em `{b.get('where')}`: {b.get('problem')}  \n  -> Correção: {b.get('fix_hint')}")
            fb += [f"- aviso: {w}" for w in v.get("warnings", [])[:5]]
            feedback.append("\n".join(fb) + "\n")
        else:
            report.append((ag, f"GREEN ({v['score']})"))

    print(f"Ronda {rnd} | versão {cur}")
    for name, st in report:
        print(f"  {name:<16} {st}")

    if not red and not missing:
        final = folder / "final"
        if final.exists():
            shutil.rmtree(final)
        final.mkdir()
        for p in list((folder / "rascunho").glob("*.docx")) + list((folder / "rascunho").glob("*.pdf")):
            shutil.copy2(p, final / p.name)
        (folder / "revisoes" / "APROVADO.json").write_text(json.dumps(
            {"round": rnd, "artifact_hash": cur, "approved_at": datetime.now().isoformat(timespec="seconds"),
             "scores": {a: verdicts[a][1]["score"] for a in AGENTS}}, indent=2, ensure_ascii=False), encoding="utf-8")
        update_tracker(folder, "documentos_aprovados")
        print("=> APROVADO. Documentos copiados para final/")
        return 0

    # nunca deixar em final/ uma versão que já não está aprovada
    if (folder / "final").exists():
        shutil.rmtree(folder / "final")
        print("   (final/ removida: continha uma versão que já não está aprovada)")
    (folder / "revisoes" / "APROVADO.json").unlink(missing_ok=True)

    if red:
        (rd / "feedback_para_escritor.md").write_text(
            f"# Feedback da ronda {rnd} para o escritor\n\nVersão avaliada: `{cur}`\n\n"
            "Corrigir todos os blockers sem inventar factos (ver references/agents/00-pipeline.md). "
            "Reconstruir os .docx, gravar o novo hash e iniciar a ronda seguinte do princípio.\n\n" + "\n".join(feedback),
            encoding="utf-8")
        update_tracker(folder, "em_revisao")
        if rnd >= cfg["max_rounds"]:
            print(f"=> REPROVADO e LIMITE DE {cfg['max_rounds']} RONDAS ATINGIDO. Parar e explicar à pessoa o que bloqueia.")
            return 2
        print(f"=> REPROVADO. Feedback em {rd / 'feedback_para_escritor.md'}")
        return 1
    print("=> RONDA INCOMPLETA: faltam veredictos (nada reprovado até agora).")
    return 3


def main():
    utf8()
    ap = argparse.ArgumentParser()
    ap.add_argument("cmd", choices=["hash", "check"])
    ap.add_argument("folder")
    ap.add_argument("--round", type=int)
    ap.add_argument("--write", action="store_true")
    a = ap.parse_args()
    folder = Path(a.folder)
    if a.cmd == "hash":
        h = art_hash(folder)
        if a.write:
            (folder / "rascunho" / ".hash").write_text(h + "\n", encoding="utf-8")
        print(h); return 0
    rs = rounds(folder)
    rnd = a.round or (rs[-1] if rs else None)
    if not rnd:
        sys.exit("Sem rondas em revisoes/. Criar revisoes/round-1/ primeiro.")
    return check(folder, rnd)


if __name__ == "__main__":
    sys.exit(main())
