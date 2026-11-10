#!/usr/bin/env python3
"""Banco de histórias STAR+R para entrevistas, ancorado no CV mestre.

Uso:
  stories.py <raiz> check          valida perfil/stories.json contra o master_cv.json
  stories.py <raiz> list [--tag X] lista as histórias (id, título, tags)
Formato de cada história: id, titulo, experiencia, situacao, tarefa, acao, resultado, reflexao, tags[]
`experiencia` tem de corresponder a uma empresa, cargo, projeto ou formação do CV mestre: sem prova, não entra.
"""
import json, re, sys, unicodedata
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))
from _common import utf8

CAMPOS = ["id", "titulo", "experiencia", "situacao", "tarefa", "acao", "resultado", "reflexao"]


def norm(s):
    return re.sub(r"\s+", " ", unicodedata.normalize("NFKD", str(s or "")).encode("ascii", "ignore").decode()).strip().lower()


def anchors(master):
    out = []
    for e in master.get("experience", []):
        out += [e.get("company", ""), e.get("role", "")]
    out += [p.get("name", "") for p in master.get("projects", [])]
    out += [e.get("school", "") for e in master.get("education", [])]
    return [norm(a) for a in out if a]


def check(stories, master):
    """Devolve (erros, avisos). Função pura."""
    errs, warns, ids, anc = [], [], set(), anchors(master)
    for i, s in enumerate(stories, 1):
        tag = s.get("id") or f"#{i}"
        miss = [c for c in CAMPOS if not str(s.get(c, "")).strip()]
        if miss:
            errs.append(f"{tag}: campos em falta: {', '.join(miss)}"); continue
        if s["id"] in ids:
            errs.append(f"{tag}: id repetido")
        ids.add(s["id"])
        e = norm(s["experiencia"])
        if not any(e in a or a in e for a in anc):
            errs.append(f"{tag}: a experiência '{s['experiencia']}' não existe no CV mestre (acrescentar lá primeiro, com prova)")
        if not re.search(r"\d", s["resultado"]):
            warns.append(f"{tag}: o resultado não tem números; confirmar se há um valor verificável")
    return errs, warns


def main():
    utf8()
    if len(sys.argv) < 3:
        sys.exit(__doc__)
    perfil = Path(sys.argv[1]) / "perfil"
    try:
        stories = json.loads((perfil / "stories.json").read_text(encoding="utf-8"))
    except Exception:
        sys.exit("Sem perfil/stories.json válido (lista de histórias). Ver references/entrevista.md.")
    if sys.argv[2] == "list":
        tag = sys.argv[sys.argv.index("--tag") + 1] if "--tag" in sys.argv else None
        for s in stories:
            if not tag or tag in s.get("tags", []):
                print(f"{s.get('id', '?'):<16}{s.get('titulo', ''):<50}{', '.join(s.get('tags', []))}")
        return
    try:
        master = json.loads((perfil / "master_cv.json").read_text(encoding="utf-8"))
    except Exception:
        sys.exit("Sem perfil/master_cv.json: não há CV mestre para validar as histórias.")
    errs, warns = check(stories, master)
    for w in warns:
        print("AVISO:", w)
    for e in errs:
        print("ERRO: ", e)
    print(f"{len(stories)} história(s): {len(errs)} erro(s), {len(warns)} aviso(s)")
    sys.exit(1 if errs else 0)


if __name__ == "__main__":
    main()
