# Schema do CV (master_cv.json e cv.json)

Mesmo formato para o CV mestre e para os CVs adaptados. O mestre tem tudo; o adaptado é um subconjunto reordenado e reescrito.

```json
{
  "lang": "pt",
  "name": "Nome Completo",
  "headline": "Título profissional (ex.: Analista Financeiro | Contabilidade e Reporting)",
  "contacts": ["email@exemplo.com", "+258 84 000 0000", "Maputo, Moçambique", "linkedin.com/in/perfil"],
  "summary": "3-4 linhas. No CV adaptado, reescrever para a vaga.",
  "skills": {
    "Técnicas": ["Excel avançado", "SAP"],
    "Idiomas": ["Português (nativo)", "Inglês (C1)"]
  },
  "experience": [
    {
      "role": "Título OFICIAL (como no contrato/recibo/carta de referência)",
      "role_note": "Opcional: descrição funcional verificável (ex.: funções de controlo de gestão)",
      "company": "Empresa",
      "location": "Cidade, País",
      "period": "Jan 2022 - Presente",
      "bullets": ["Verbo de ação + o que fez + resultado mensurável"]
    }
  ],
  "education": [
    {"degree": "Licenciatura em ...", "school": "Instituição", "period": "2016 - 2020", "details": "Opcional: média, tese, distinções"}
  ],
  "certifications": ["Nome da certificação (Entidade, ano)"],
  "projects": [{"name": "Projeto", "description": "O que é e o resultado"}],
  "extras": ["Voluntariado, publicações, prémios..."]
}
```

`lang` (`pt`, `en`, `fr`, `es`; omissão `pt`) define o idioma dos títulos das secções; `labels` (opcional) substitui títulos individuais, ex. `"labels": {"experience": "Work history"}`. Todas as secções exceto `name` são opcionais; secções vazias não aparecem no documento. Campos extra no mestre (ex.: `"notes"`) são ignorados pelo gerador.

## Schema da carta (carta.json)

```json
{
  "lang": "pt",
  "sender": ["Nome Completo", "email", "telefone", "Cidade"],
  "date": "23 de outubro de 2026",
  "recipient": ["Nome do recrutador ou 'Equipa de Recrutamento'", "Empresa", "Cidade"],
  "subject": "Candidatura: Cargo (Ref. XYZ)",
  "salutation": "Exmo./a Sr./Sra. ...,",
  "paragraphs": ["Parágrafo 1", "Parágrafo 2", "Parágrafo 3"],
  "closing": "Com os melhores cumprimentos,",
  "signature": "Nome Completo"
}
```

## Campos de auditoria (só no `master_cv.json`; geridos com `jh audit`)

```json
{
  "audit": {"date": "2026-10-24", "confirmed_by_user": true, "notes": "resumo curto"},
  "experience": [{"role": "...", "confirmed_at": "2026-10-24", "role_note_confirmed": true}]
}
```

- `role` é sempre o título **oficial**. `role_note` aparece entre parênteses ao lado do título no CV e só pode existir se a pessoa confirmar que o diria numa referência (`role_note_confirmed`).
- `confirmed_at` marca cada cargo como confirmado pela pessoa. O `gate` recusa vagas se faltar `audit` ou `confirmed_at`, ou se a auditoria for mais antiga que `audit_max_age_days`.
- O CV adaptado (`rascunho/cv.json`) não leva estes campos de auditoria; o `role` e o `role_note` copiam-se exatamente do mestre.
