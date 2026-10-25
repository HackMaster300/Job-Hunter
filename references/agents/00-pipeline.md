# Pipeline de revisão (portão de qualidade)

Os documentos de uma vaga só chegam a `final/` se **todos** os agentes derem GREEN **sobre a mesma versão** dos ficheiros. Esta regra existe porque o escritor tem viés para aprovar o próprio trabalho, e porque uma correção feita para satisfazer um agente pode estragar o que outro já tinha aprovado.

## Agentes

| Etapa | Agente (id) | Subagente | Ficheiro de papel | Pergunta | Mínimo |
|---|---|---|---|---|---|
| A | script `ats_check` | - | - | Passa nas verificações mecânicas? | 0 falhas bloqueantes |
| A | `fact_checker` | `jh-fact-checker` | fact-checker.md | Tudo o que está escrito é verdade segundo o CV mestre? | 100 |
| B | `ats` | `jh-ats` | ats-scanner.md | Um ATS lê e pontua bem isto? | 90 |
| B | `hr` | `jh-hr` | hr-recruiter.md | Um recrutador passa este CV à frente? | 90 |
| B | `hiring_manager` | `jh-hiring-manager` | hiring-manager.md | O gestor da área contrataria? | 90 |
| B | `language_editor` | `jh-language-editor` | language-editor.md | Língua, tom, consistência e carta impecáveis? | 90 |
| C | `skeptic` | `jh-skeptic` | skeptic.md | Sobrevive a um diretor cético? | 90 |

Mínimos e limites são ajustáveis em `candidaturas/perfil/config.json` (ver `scripts/_common.py`, `DEFAULT_CONFIG`). Os valores por omissão são deliberadamente exigentes.

## Ciclo de uma ronda

```
escritor → rascunho/ ─► A: script + fact_checker ─► B: ats | hr | hiring_manager | language_editor (em paralelo) ─► C: skeptic ─► gate check
   ▲                         │ RED                         │ RED(s)                                                      │ RED
   └──────── feedback_para_escritor.md ◄──────────────────┴─────────────────────────────────────────────────────────────┘
```

1. **Preparar a ronda:** `mkdir revisoes/round-N`; `jh hash <pasta> --write` (grava `rascunho/.hash`, que os revisores copiam para os veredictos).
2. **Etapa A:** `jh check ...` (script) e depois o `fact_checker`. Se algum falhar, **parar aqui**: factos inventados invalidam tudo o resto. Ir a `jh gate <pasta>` para gerar o feedback.
3. **Etapa B:** lançar os 4 revisores **em paralelo** (um único pedido com 4 delegações). Em paralelo porque são independentes e assim o escritor recebe todo o feedback de uma vez, o que reduz o número de rondas.
4. **Etapa C:** só depois de B terminar, lançar o `skeptic` (lê os veredictos de B para caçar o que todos deixaram passar). O portão rejeita um skeptic gravado antes dos outros.
5. **`jh gate <pasta>`** valida tudo e dá o resultado:
   - exit **0 APROVADO** → `final/` criada; seguir para README.
   - exit **1 REPROVADO** → ler `feedback_para_escritor.md`, corrigir, reconstruir .docx, `jh hash --write`, e **começar nova ronda do princípio**.
   - exit **2 limite de rondas** (por omissão 4) → parar e explicar à pessoa o que bloqueia. Não baixar critérios.
   - exit **3 incompleta** → faltam veredictos; executar os agentes em falta.

## Como delegar a cada agente

**Com subagentes instalados** (`jh-*` visíveis; Claude Code ou OpenCode): delegar a cada um com uma mensagem curta e igual para todos, sem justificações do escritor:

> Pasta da vaga: `candidaturas/2026-10-23_empresa_cargo`. Ronda: 2. Faz a tua revisão e grava o veredicto em `revisoes/round-2/<id>.json`.

**Sem subagentes** (qualquer outro ambiente): para cada agente, por ordem A → B → C, abrir `references/agents/_common.md` + o ficheiro de papel, e fazer a revisão como passagem separada: reler os ficheiros do disco, ignorar o raciocínio do escritor, gravar o veredicto. É menos isolado (o mesmo modelo escreve e revê), por isso ser ainda mais severo: dizer à pessoa que o isolamento é reduzido e recomendar instalar os subagentes (`jh install`).

## Regras para o escritor ao rever

1. Corrigir **todos** os blockers; mexer no resto só se necessário (evita regressões).
2. **Nunca resolver um blocker inventando.** Se a correção pedir um facto que não está no `master_cv.json`: parar e **perguntar à pessoa**. Se for verdade, acrescentar ao `master_cv.json` primeiro e só depois ao CV. Se não for, registar como lacuna real em `analise_fit.md`.
3. Lacunas reais que um agente trate como blocker ("não cumpre requisito eliminatório") não se resolvem em texto. Levar à pessoa a decisão: avançar ou desistir. Se avançar, registar em `revisoes/decisao_utilizador.md` (qual a lacuna, que foi avisada, que quer concorrer); os agentes passam essa lacuna a `warning`, tudo o resto continua blocker.
4. Reconstruir os .docx (e PDF) a partir dos JSON antes de nova ronda, e voltar a gravar o hash.
5. Os veredictos são ficheiros dos revisores: o escritor **nunca os edita**.

## Formato do veredicto

Definido em `_common.md` (parte do prompt de cada subagente). Resumo: `agent`, `round`, `artifact_hash`, `verdict`, `score`, `blockers[]`, `warnings[]`, `evidence[≥3]`, `weakest_points[≥3]`.
