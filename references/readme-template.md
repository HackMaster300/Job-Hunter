# Template do README por vaga

Escrever em português, direto, para a pessoa agir sem voltar à conversa. Preencher tudo; se algo não se aplica, escrever "não aplicável" em vez de apagar a secção.

```markdown
# <Cargo> - <Empresa>

**Estado:** ✅ APROVADA pelo portão de revisão (ronda N), ainda NÃO enviada   <!-- ou: ❌ NÃO APROVADA: <o que bloqueia> -->
**Prazo:** <data> (faltam X dias a contar de <data de hoje>)
**Local / contrato:** <...>
**Link da vaga:** <url>
**Fit:** Alto/Médio/Baixo - <uma frase>

## Resultado da revisão (ronda N, versão <hash>)
| Agente | Nota | Ponto mais fraco que ainda vale a pena rever |
|---|---|---|
| Script ATS | PASS | - |
| ATS | 9x | ... |
| Verificador de factos | 100 | ... |
| RH | 9x | ... |
| Gestor da área | 9x | ... |
| Revisor de língua | 9x | ... |
| Diretor cético | 9x | ... |

(Preencher a partir de `revisoes/round-N/*.json`. Se a vaga NÃO foi aprovada: listar os blockers por resolver e não apresentar a pasta como pronta.)

## O que está nesta pasta
| Ficheiro | Para quê |
|---|---|
| vaga.md | Texto original do anúncio (guardado caso expire) |
| analise_fit.md | Requisitos vs. o teu perfil, lacunas e palavras-chave |
| final/CV_<Nome>_<Empresa>.docx / .pdf | CV adaptado e aprovado. **Enviar sempre os de `final/`** |
| final/Carta_<Empresa>.docx / .pdf | Carta de apresentação aprovada |
| revisoes/ | Veredictos de cada agente por ronda (para consulta) |
| rascunho/ | Versões de trabalho; não enviar |
| extras/ | <lista: email, respostas, prep entrevista> |

## Como concorrer (passo a passo)
1. <Rever os documentos: ver "Antes de enviar" abaixo>
2. <Onde submeter: portal/link ou email, com o endereço exato>  (anexar sempre os ficheiros de `final/`, nunca de `rascunho/`)
3. <Ficheiros a anexar e em que formato>
4. <Assunto do email / referência a indicar, tal como o anúncio pede>
5. <Campos ou perguntas do formulário e onde estão as respostas preparadas>
6. Guardar comprovativo/print da submissão nesta pasta e atualizar o estado: `python <skill>/scripts/jh.py tracker candidaturas set <pasta> enviada` (ou pedir ao Claude).

## Antes de enviar (checklist)
- [ ] Li o CV e todos os factos estão corretos (datas, cargos, números): o verificador não conhece a tua história melhor do que tu
- [ ] Li a carta e o nome da empresa/cargo estão certos
- [ ] Preenchi os pontos marcados com [CONFIRMAR] (se existirem)
- [ ] Ficheiros no formato pedido (PDF/Word) e abaixo do tamanho máximo
- [ ] Contactos atualizados e email com nome profissional

## Pontos de atenção
- <Lacunas do perfil e como lidar com elas na entrevista>
- <Requisitos eliminatórios ou documentos extra pedidos (certidões, cópias, referências)>
- <Cuidados com a vaga: dúvidas sobre fiabilidade, etc.>

## Depois de enviar
- Aguardar <prazo típico>; se não houver resposta, enviar um follow-up curto ao fim de ~7-10 dias úteis.
- Se houver entrevista, ver `extras/prep_entrevista.md` (ou pedir ao Claude para preparar).
```
