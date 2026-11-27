# Changelog

Versões semânticas; cada versão tem uma tag `vX.Y.Z` e corresponde à versão do `package.json` (pacote npm `job-hunter-skill`, preparado para publicação).

## 1.6.0
- Pacote npm `job-hunter-skill`: `npx job-hunter-skill install|doctor|selftest|jh ...`.
- `jh version`; o instalador já não copia ficheiros de npm nem imagens para a skill instalada.
- Licença Apache-2.0.
- Workflow de release por tag (`.github/workflows/release.yml`).

## 1.5.0
- Avaliação A-G com nota 0-5 ponderada, evidência obrigatória e bloqueios (`jh eval`).
- Follow-up com cadência 7/14/21 dias, análise de padrões, estado `sem_resposta` (`jh tracker ... followup|followed|patterns`).
- Banco de histórias STAR+R validado contra o CV mestre (`jh stories`).
- `jh scan links` e `jh scan add` para LinkedIn e jobs.ch (sem leitura automática); fonte Sovagas (RSS).
- Imagens novas (banner e fluxo).

## 1.4.0
- `jh scan`: scan sem LLM (Greenhouse, Lever, Ashby, RemoteOK, Remotive, WeWorkRemotely, RSS, ReliefWeb), deduplicação, prefiltro e triagem em lote. Conceito inspirado em opt-career-ops.

## 1.3.0
- Versão inicial: auditoria do CV, portão multi-agente, pasta por vaga, README por vaga.
