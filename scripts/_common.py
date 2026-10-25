"""Utilitários partilhados pelos scripts (stdlib apenas)."""
import json, sys
from pathlib import Path


def utf8():
    """Evita erros de codificação em consolas Windows."""
    for s in (sys.stdout, sys.stderr):
        try:
            s.reconfigure(encoding="utf-8")
        except Exception:
            pass


def deep_merge(base, extra):
    out = dict(base)
    for k, v in (extra or {}).items():
        out[k] = deep_merge(out[k], v) if isinstance(v, dict) and isinstance(out.get(k), dict) else v
    return out


DEFAULT_CONFIG = {
    "min_score": {"ats": 90, "fact_checker": 100, "hr": 90, "hiring_manager": 90, "language_editor": 90, "skeptic": 90},
    "min_evidence": 3,
    "min_weakest_points": 3,
    "max_rounds": 4,
    "audit_max_age_days": 90,    # o CV mestre tem de ter sido confirmado pela pessoa nos últimos N dias
    "ats_check": {
        "kw_coverage": 0.8,        # fração mínima das palavras-chave obrigatórias presentes
        "quant_ratio": 0.4,        # fração mínima de bullets com números
        "cv_words": [250, 1100],
        "letter_words": [150, 400],
        "max_pages": 2,
    },
}


def load_config(job_folder: Path) -> dict:
    """Lê candidaturas/perfil/config.json (opcional) e funde com os valores por omissão."""
    p = Path(job_folder).resolve().parent / "perfil" / "config.json"
    if p.exists():
        try:
            return deep_merge(DEFAULT_CONFIG, json.loads(p.read_text(encoding="utf-8")))
        except Exception as e:
            print(f"AVISO: config.json inválido ({e}); a usar valores por omissão", file=sys.stderr)
    return DEFAULT_CONFIG
