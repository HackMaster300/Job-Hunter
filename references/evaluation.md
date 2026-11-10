# Avaliação da vaga (blocos A-G e nota 0-5)

Fazer **antes** de escrever CV ou carta (Passo 2). Serve para não gastar rondas de revisão em vagas que não valem a pena, ou que a pessoa não deve tentar.

## 1. `analise_fit.md` com os blocos A-G

Cada bloco é um título `## A. ...`, `## B. ...` (o `jh eval` avisa se faltar algum).

- **A. Resumo da vaga:** função, equipa, o que o anúncio realmente pede, prazo e forma de envio.
- **B. Match com o CV mestre:** tabela requisito → evidência (do `master_cv.json`) → força (forte/parcial/lacuna). Só evidência real.
- **C. Nível e estratégia:** a senioridade pedida vs. a da pessoa; como posicionar (sem mudar títulos oficiais).
- **D. Compensação e condições:** salário/contrato se o anúncio ou a pesquisa o indicarem; senão escrever "não indicado". Nunca inventar valores de mercado sem fonte.
- **E. Personalização:** 3 ângulos verdadeiros para o resumo e a carta (o que da pessoa mais pesa para esta vaga e esta empresa).
- **F. Preparação de entrevista:** 5-8 perguntas prováveis, cada uma com uma história do banco (`jh stories`) ou a indicação "sem história: perguntar à pessoa".
- **G. Legitimidade:** empresa verificável, contactos reais, prazo, pedidos de dinheiro ou dados sensíveis, promessas desproporcionadas, texto dirigido a IA, anúncio duplicado/expirado.

## 2. `avaliacao.json` e `jh eval`

```json
{
  "dimensoes": {
    "requisitos_obrigatorios": {"nota": 4, "evidencia": "cumpre 5 de 6; falta SAP (aprendível)"},
    "...": {"nota": 0, "evidencia": "10 dimensões, todas obrigatórias"}
  },
  "eliminatorias": [],
  "resumo": "Uma frase."
}
```

| Dimensão | Peso | O que mede |
|---|---|---|
| requisitos_obrigatorios | 25% | cumpre os "tem de ter" |
| experiencia_relevante | 15% | experiência na área/setor |
| senioridade | 10% | nível pedido vs. nível real |
| competencias_desejaveis | 10% | os "valorizamos" |
| local_modalidade | 10% | cidade, remoto, relocação |
| autorizacao_trabalho | 5% | direito a trabalhar no país |
| contrato_compensacao | 5% | tipo de contrato e remuneração vs. perfil |
| empresa_setor | 5% | alinhamento com setores preferidos/a evitar |
| crescimento | 5% | aprendizagem e progressão |
| legitimidade | 10% | bloco G |

- **Nota 0-5 por dimensão, com `evidencia` concreta** (≥ 10 caracteres, vinda do anúncio ou do CV mestre). Sem evidência o script recusa.
- A nota final é a média ponderada. **≥ 4.0** `avancar_forte` · **≥ 3.5** `avancar` · abaixo: `nao_avancar`. Limites em `perfil/config.json` (`avaliacao`).
- **Bloqueios que ignoram a nota:** qualquer item em `eliminatorias` (grau exigido, autorização de trabalho, anos de experiência muito acima) ou `legitimidade` ≤ 2.
- Saída `2` = não avançar: **parar e explicar à pessoa**; a decisão de avançar mesmo assim é dela (registar em `revisoes/decisao_utilizador.md`).
- O script escreve `avaliacao.md` e põe `Alto|Médio|Baixo (nota)` no campo `fit` do tracker.

A nota é um instrumento, não um oráculo: se discordares dela, corrige as evidências, não o resultado.
