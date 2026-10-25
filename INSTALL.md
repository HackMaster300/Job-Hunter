# Instalação do job-hunter (Claude Code e OpenCode)

## 1. Requisitos
- Python 3.9+ e `pip install python-docx`
- Opcional: LibreOffice (gerar PDF e contar páginas com exatidão), `pdftotext` (poppler) para ler PDFs

## 2. Instalar (recomendado: uma pasta de trabalho só para candidaturas)

```bash
mkdir ~/candidaturas-ws && cd ~/candidaturas-ws
python path/para/job-hunter/scripts/jh.py install --target claude-code --scope project --workspace .
# OpenCode:   --target opencode      Ambos: --target both
# Para todos os projetos (em vez desta pasta):   --scope user
```

Isto copia a skill, **gera os 6 subagentes revisores** (`jh-ats`, `jh-fact-checker`, `jh-hr`, `jh-hiring-manager`, `jh-language-editor`, `jh-skeptic`), cria `candidaturas/`, um `CLAUDE.md`/`AGENTS.md` com regras de privacidade e põe `candidaturas/` no `.gitignore`. Para atualizar uma instalação existente, acrescentar `--force`.

Verificar: `python .claude/skills/job-hunter/scripts/jh.py doctor` e `... selftest` (14 testes com dados fictícios).

## 3. Usar (a primeira conversa é uma entrevista)
Na primeira vez, antes de procurar vagas, a skill **audita o teu CV**: pergunta o que mudou desde que foi escrito, confirma o título oficial de cada cargo (o do contrato ou da carta de referência, não um "mais bonito"), pede números e verifica as competências. O CV só é usado depois de confirmares que está correto e atual; a confirmação expira ao fim de 90 dias e o portão recusa vagas sem ela. Responde com calma: é isto que evita enviar um CV antigo ou com títulos que não são os teus.

Abrir `claude` (ou `opencode`) nessa pasta e escrever, por exemplo:
> Quero procurar vagas de analista financeiro em Maputo. O meu CV está em cv.docx.

A skill dispara sozinha; no Claude Code também com `/job-hunter`.

## Notas por ferramenta

**Claude Code**
- Os subagentes só têm `Read, Glob, Grep, Write` (sem Bash nem web): leem a pasta da vaga e gravam o veredicto; nada sai do computador e não alteram o CV.
- Vão pedir autorização para gravar ficheiros. Para evitar interrupções, permitir escrita em `candidaturas/**` nas permissões do projeto (`/permissions`), e execução de `python .../jh.py *`.
- Se quiseres um modelo mais forte nos revisores, trocar `model: inherit` por `opus` nos ficheiros em `.claude/agents/jh-*.md`.

**OpenCode**
- Lê skills de `.opencode/skills/`, `~/.config/opencode/skills/` e também de `.claude/skills/` (por isso `--target both` instala a skill uma só vez).
- O formato dos agentes mudou entre versões (v1: `.opencode/agent/` + `tools:`/`permission:`; v2: `.opencode/agents/` + `permissions:` em lista). O instalador gera frontmatter **mínimo** (`description` + `mode: subagent`) que funciona nas duas, mas **sem restrição de ferramentas**. Para restringir (só ler/gravar, sem web nem shell) acrescenta as permissões da tua versão, conforme https://opencode.ai/docs/agents/. Se a tua versão usa a pasta antiga, instalar com `--opencode-agent-dir agent`.
- Se o `task`/subagente não estiver disponível, a skill cai no modo sequencial (revisão menos isolada).

## Ajustar a exigência
Criar `candidaturas/perfil/config.json` (só os campos que queres mudar):
```json
{"min_score": {"hr": 85, "skeptic": 85}, "max_rounds": 5, "ats_check": {"max_pages": 1, "quant_ratio": 0.3}}
```
O `fact_checker` deve ficar sempre em 100.
