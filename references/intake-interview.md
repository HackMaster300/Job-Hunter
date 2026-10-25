# Entrevista de levantamento e auditoria do CV

Objetivo: o CV mestre ser **verdadeiro, atual e completo**, antes de qualquer vaga. Um CV antigo esconde o que a pessoa faz hoje; um título "bonito" que não é o oficial cai numa verificação de referências. O CV importado é só o ponto de partida: tratá-lo como **hipótese a confirmar**, não como verdade.

Regras da entrevista:
- Conversa normal, **um bloco de cada vez** (2-4 perguntas), em português. Não despejar o questionário todo.
- Aceitar "não sei" e "não me lembro": anotar como dúvida, não preencher por palpite.
- Quando a pessoa der algo novo, **escrever no `master_cv.json` primeiro**; só depois pode ir para um CV.
- Ser direto sobre inconsistências, com respeito: "No CV está X, mas disseste Y. Qual é o correto?"
- No fim, escrever `perfil/auditoria.md` (alterações, dúvidas pendentes) e só então correr `jh audit confirm` (ver fim deste ficheiro).

## Bloco 0 - Atualidade (primeira pergunta de todas)
1. Quando foi a última vez que este CV foi atualizado? Aconteceu algo desde então (novo cargo, promoção, mudança de funções, projeto, formação, certificação, idioma)?
2. Estás a trabalhar agora? Se sim, onde e desde quando? Se não, o que fizeste desde o último cargo (freelance, biscates, estudos, voluntariado, empresa própria)? Períodos sem emprego também têm coisas válidas a mostrar.
3. Tens um perfil LinkedIn (ou equivalente)? Se sim, **colar o texto ou pedir para o ler**: recrutadores comparam o CV com ele, e diferenças parecem falta de rigor.

## Bloco 1 - Por cada cargo (do atual para trás, um de cada vez)
Perguntar e registar:
1. **Título oficial**: "Qual é o título que consta no teu contrato, recibo de vencimento, cartão ou carta de referência?" Este é o `role`.
2. **Nome legal da empresa**, cidade/país e datas exatas (mês/ano de início e fim).
3. **O que fazes (ou fazias) de facto no dia a dia**, e o que mudou desde a data do CV: responsabilidades novas, promoções, equipa, projetos, ferramentas.
4. **Resultados com números**: volumes, valores, prazos, percentagens, tamanho de equipa, orçamentos, utilizadores. "Quanto? Quantos? Em quanto tempo? Antes e depois?" Se a pessoa não tem o número exato, aceitar uma estimativa honesta marcada como aproximada ("cerca de").
5. **Prova**: "Alguém confirmaria isto numa referência?" Afirmações que a pessoa não consegue defender saem.
6. Coisas que fez e **nunca escreveu** (tarefas fora da descrição de funções, substituições, formação a colegas, melhorias de processo).

### Título oficial vs. função real (regra de ouro)
- O CV mostra **sempre o título oficial** (`role`). Nunca trocar por um título "mais bonito" ou do mercado que a pessoa não teve.
- Se a função real é maior ou diferente do título oficial, **não alterar o título**: usar `role_note` com uma descrição funcional honesta e verificável (ex.: título oficial "Assistente Administrativo", `role_note`: "funções de controlo de gestão e reporting") e só se a pessoa confirmar que o diria numa referência.
- Se a pessoa disser "o meu título é X mas na prática sou Y": registar ambos, explicar a regra e deixar a pessoa decidir se o `role_note` é defensável. Em dúvida, deixar de fora e pôr o conteúdo nos bullets.
- Títulos traduzidos para o idioma da vaga são aceitáveis se forem a tradução fiel do oficial (ex.: "Analista Financeiro Sénior" → "Senior Financial Analyst"), não uma promoção.

## Bloco 2 - Competências (verificar, não só listar)
Para cada competência/ferramenta listada: "Usaste nos últimos 2 anos? Em que nível (básico / trabalho autónomo / avançado / podes ensinar)? Em que contexto concreto?" Retirar o que ficou obsoleto ou o que a pessoa não conseguiria demonstrar numa conversa técnica. Perguntar também: "Há ferramentas que usas e não estão na lista?"

## Bloco 3 - Formação, certificações, idiomas
- Datas, instituição, grau exato e média só se for um ponto forte. Cursos em curso contam ("em curso, conclusão prevista em ...").
- Certificações: nome oficial, entidade, ano e **se ainda estão válidas**.
- Idiomas: nível real (A1-C2 ou descrição honesta). Perguntar: "Conseguirias fazer uma entrevista inteira neste idioma?"

## Bloco 4 - O que não está no CV
Projetos pessoais ou voluntariado, publicações, prémios, comunidade/associações, trabalho freelance, cursos, hackathons, mentoria, apresentações, línguas, carta de condução ou disponibilidade para viajar se relevantes para o tipo de vaga.

## Bloco 5 - Dados e coerência
- Contactos atuais (email profissional, telefone, cidade, LinkedIn). Email com nome sério.
- Datas coerentes entre cargos, sem sobreposições nem lacunas inexplicadas (explicar lacunas honestamente se existirem).
- Referências: há pelo menos duas pessoas dispostas a confirmar o trabalho? Se alguém for contactado, o que diria?

## Levantamento por vaga (além desta auditoria geral)
Em cada vaga, para cada requisito que `analise_fit.md` marca como lacuna ou fraco, perguntar: "A vaga pede X. Já fizeste algo relacionado com X, mesmo que pouco ou fora do trabalho? Num projeto, em casa, num curso, a ajudar alguém?" Se sim, registar no master (com a mesma prova e números) antes de usar. Se não, é lacuna real; não se escreve.

## Fim da auditoria
1. Escrever `perfil/auditoria.md`: o que mudou face ao CV importado (antes → depois), o que foi retirado e porquê, dúvidas por resolver.
2. Mostrar à pessoa um **resumo do CV mestre** (cargos com título oficial e datas, 3-5 resultados-chave, competências verificadas) e perguntar: "Isto está correto e atual? Algo a corrigir antes de avançarmos?"
3. **Só depois de um "sim" explícito**: `jh audit confirm candidaturas/perfil/master_cv.json --confirmado-pela-pessoa --notes "<resumo curto>"`. Nunca correr este comando por conta própria.
4. A auditoria expira (por omissão 90 dias) e o `gate` recusa vagas com a auditoria em falta. Se passar tempo ou houver novidades, repetir o Bloco 0 e rever só o que mudou.
