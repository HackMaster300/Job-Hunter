# Depois do envio: follow-up, contacto, padrões e entrevista

## Registar
`jh tracker candidaturas set <pasta> enviada [--data AAAA-MM-DD]` guarda a data de envio. Depois: `entrevista`, `recusada`, `oferta`, `desistiu` ou `sem_resposta` (guardam a data de resposta).

## Follow-up com cadência
- `jh tracker candidaturas followup` lista o que pede ação hoje. Cadência por omissão: 1.º aos 7 dias, 2.º aos 14, e aos 21 sugere fechar como `sem_resposta` (`perfil/config.json`, bloco `followup`).
- Ao enviar uma mensagem: `jh tracker candidaturas followed <pasta>`.
- **Redigir** a mensagem em `extras/followup_N.md`: 3-5 linhas, no idioma da vaga, a referir o cargo e a data de envio, a reafirmar **um** ponto de valor verdadeiro (do CV aprovado) e a perguntar pelo estado. Sem pressão, sem culpa, sem inventar novidades. Quem envia é a pessoa.

## Contacto direto (LinkedIn ou email)
Mensagem curta a um recrutador ou gestor, em `extras/contacto.md`:
- Quem és (1 linha, factual) + porque esta vaga + 1 prova do CV aprovado + pedido pequeno (ex.: confirmar que a candidatura chegou, ou 10 minutos).
- LinkedIn: máx. ~300 caracteres no pedido de ligação. Email: assunto claro com o cargo.
- Só nomes e cargos que a pessoa confirmou ou que estão no anúncio. Se não houver contacto verificável, dizê-lo em vez de adivinhar.

## Padrões
`jh tracker candidaturas patterns`: funil, taxa de resposta, tempo médio, resultados por `fit`, `fonte` e `local`. Com menos de 10 envios são só indícios.
Ler os números com a pessoa e propor **uma** mudança de cada vez (ex.: "as vagas de fit Médio quase não respondem: concentrar em Alto"; "uma fonte não rende: trocar por outra"). Se há recusas repetidas pelo mesmo motivo, voltar ao CV mestre (auditoria) em vez de maquilhar.

## Banco de histórias STAR+R (`perfil/stories.json`)
Cada história: `id, titulo, experiencia, situacao, tarefa, acao, resultado, reflexao, tags[]`.
- **S**ituação, **T**arefa, **A**ção, **R**esultado (com números verificáveis) + **R**eflexão (o que aprendeste/farias diferente).
- `experiencia` **tem de existir no CV mestre** (empresa, cargo, projeto ou formação): `jh stories candidaturas check` recusa as que não existem. Uma história nova começa por entrar no mestre, com prova.
- Alimenta o bloco F da avaliação: reutilizar as histórias entre vagas, escolhendo por `tags`. `jh stories candidaturas list --tag excel`.
- Perguntar à pessoa, não deduzir: as histórias são dela.
