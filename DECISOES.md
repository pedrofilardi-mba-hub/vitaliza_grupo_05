# Registro de decisões: Vitaliza, grupo 05

Cada decisão que muda um número, um método ou o escopo entra aqui, da mais antiga para a mais recente. Uma decisão revista não é apagada: ela ganha o status "substituída por D-XXX".

Modelo geral:

```
## D-XXX: título curto
- Data: AAAA-MM-DD · Responsável: nome · Status: proposta | aceita | substituída por D-YYY
- Contexto: o que motivou a decisão
- Decisão: o que foi decidido
- Alternativas consideradas: e por que foram descartadas
- Impacto: o que muda (arquivos, números, objetivos do case afetados)
```

Decisões de qualidade de dados ("limpar é decidir": corrigir, remover ou marcar) usam o modelo da skill `qualidade-dados`. Ele acrescenta a dimensão, o problema (Q-ID do relatório em `saidas/qualidade/`) e o **efeito na contagem**:

```
## D-XXX: <arquivo> · título curto do problema
- Data: AAAA-MM-DD · Responsável: nome · Status: aceita
- Dimensão: completude | validade | consistência | unicidade | temporalidade · Problema: Q-<arq>-NN (saidas/qualidade/<arquivo>.md)
- Contexto: o problema em uma frase, com n e %
- Decisão: corrigir | remover | marcar: como, exatamente
- Motivo: por que esta opção
- Alternativas consideradas: as outras opções e por que não
- Efeito na contagem: linhas antes → depois; valores alterados; colunas novas
- Impacto: objetivos do case ou arquivos afetados
```

---

## D-001: Dados brutos fora do repositório
- Data: 2026-10-22 · Responsável: grupo · Status: aceita
- Contexto: o data room tem cerca de 200 MB, com dois zips de heatmaps e dados pessoais (e-mail, data de nascimento).
- Decisão: `dados/brutos/` entra no `.gitignore`. Cada integrante copia os arquivos do data room para essa pasta, e eles não são alterados.
- Alternativas consideradas: versionar os dados com Git LFS. Foi descartado pelo tamanho e por causa dos dados pessoais.
- Impacto: todo arquivo de `dados/processados/` precisa poder ser recriado a partir de um script em `src/`.

## D-002: Data de corte e horizonte de previsão
- Data: 2026-10-22 · Responsável: grupo · Status: aceita
- Contexto: o enunciado fixa o corte da base em 30/09/2026 e pede a probabilidade de saída nos 60 dias seguintes.
- Decisão: corte em 30/09/2026 e alvo de churn na janela de 01/10 a 29/11/2026. Nenhuma variável usa dado posterior ao corte.
- Alternativas consideradas: nenhuma, porque é premissa do case.
- Impacto: os objetivos 4 a 7. A validação do modelo usa separação no tempo.

## D-003: onboarding.csv · objetivo vazio ou disfarçado
- Data: 2026-10-29 · Responsável: Pedro Filardi · Status: aceita
- Dimensão: completude · Problema: Q-onb-01 (saidas/qualidade/onboarding.md)
- Contexto: `objetivo_texto` tem 19.235 vazios reais (30,1%). São 5.467 nulos e 13.768 respostas que não dizem nada (`nada`, `x`, `.`, `asdf`, `kkkk`, `nao sei`, `ok`, `-`, `sla`, emoji).
- Decisão: corrigir e marcar. Na cópia processada, os disfarçados viram vazio, pela regra `vazio_disfarcado` de `src/qualidade.py`, e é criada a coluna `objetivo_informado` (sim/não). Os brutos não mudam.
- Motivo: a extração com IA (objetivo 5) deve ler só textos com conteúdo, e a marcação preserva o fato de não ter respondido.
- Alternativas consideradas: só marcar (a IA leria `asdf` como objetivo); remover as contas (−30,1% da base, perdendo as outras respostas válidas).
- Efeito na contagem: 63.929 contas → 63.929; `objetivo_texto` preenchido de 58.462 para 44.694 (13.768 valores viram vazio); 1 coluna nova.
- Impacto: objetivo 3 (segmentos pela necessidade) e objetivo 5 (extração com IA e custo por assinante).

## D-004: onboarding.csv · como_conheceu fora da base processada
- Data: 2026-10-29 · Responsável: Pedro Filardi · Status: aceita
- Dimensão: consistência · Problema: Q-onb-02 (saidas/qualidade/onboarding.md)
- Contexto: cada resposta de `como_conheceu` corresponde 100% a um único `usuarios.canal_aquisicao`. Além disso, tem 25,2% de vazio real e 2.397 linhas com grafia variante.
- Decisão: remover a coluna da cópia processada. O canal de aquisição vem de `usuarios.canal_aquisicao`. Os brutos não mudam.
- Motivo: a informação é redundante, e a fonte alternativa está completa e limpa.
- Alternativas consideradas: corrigir e manter (duplicaria uma coluna existente); marcar os vazios (manteria a redundância).
- Efeito na contagem: 63.929 contas → 63.929; 1 coluna a menos.
- Impacto: as variáveis de aquisição dos objetivos 2, 3 e 4 usam só `canal_aquisicao`.

## D-005: onboarding.csv · nivel e dias_por_semana vazios
- Data: 2026-10-29 · Responsável: Pedro Filardi · Status: aceita
- Dimensão: completude · Problema: Q-onb-03 (saidas/qualidade/onboarding.md)
- Contexto: `nivel` tem 4.513 vazios (7,1%) e `dias_por_semana`, 6.368 (10,0%), em 10.408 contas. Os vazios são independentes entre si e não se ligam a assinar nem a sair.
- Decisão: marcar. Na cópia processada, `nivel` ganha a categoria `nao_informado`; `dias_por_semana` fica vazio e é criada a coluna `dias_informado`. Se um modelo exigir número, a mediana entra só na modelagem, junto com a marcação. Os brutos não mudam.
- Motivo: não inventar dado e não perder 16% das contas.
- Alternativas consideradas: imputar a moda e a mediana (10.881 valores inventados); remover as contas (de 63.929 para 53.521, −16,3%).
- Efeito na contagem: 63.929 contas → 63.929; 4.513 valores de `nivel` viram `nao_informado`; 1 coluna nova.
- Impacto: objetivos 3 e 4.

## D-006: onboarding.csv · dias_por_semana como número
- Data: 2026-10-29 · Responsável: Pedro Filardi · Status: aceita
- Dimensão: consistência · validade · Problema: Q-onb-04 (saidas/qualidade/onboarding.md)
- Contexto: `dias_por_semana` aparece em 4 formas: `3` (33.527), `3 vezes` (11.563), `3x` (11.554) e `todos` (917).
- Decisão: corrigir. Na cópia processada, o número é extraído e `todos` vira 7; a coluna passa a inteiro, de 1 a 7. Os brutos não mudam.
- Motivo: o valor certo é recuperável sem ambiguidade. "Todos" foi lido como todos os dias da semana.
- Alternativas consideradas: `todos` como vazio (perderia 917 respostas válidas); remover as linhas fora do padrão (−37,6%).
- Efeito na contagem: 63.929 contas → 63.929; 24.034 valores convertidos (23.117 com texto e 917 `todos`); 6.368 continuam vazios (D-005).
- Impacto: objetivos 3 e 4 (intenção de frequência declarada na entrada).

## D-007: onboarding.csv · objetivo normalizado para contagem
- Data: 2026-10-29 · Responsável: Pedro Filardi · Status: aceita
- Dimensão: consistência · Problema: Q-onb-05 (saidas/qualidade/onboarding.md)
- Contexto: 17.179 textos distintos de `objetivo_texto` viram 12.257 depois de normalizar; 9.884 linhas (15,5%) diferem da grafia mais comum só por acento, emoji ou espaço trocado.
- Decisão: marcar. Na cópia processada é criada a coluna `objetivo_norm` (minúsculas, sem acento, sem emoji, sem espaços e pontuação), só para contar e agrupar. A extração com IA usa o texto original. Os brutos não mudam.
- Motivo: agrupar sem perder o texto original, que a IA interpreta bem.
- Alternativas consideradas: sobrescrever pela grafia mais comum (perde o original e os emoji).
- Efeito na contagem: 63.929 contas → 63.929; 1 coluna nova; nenhum texto alterado.
- Impacto: objetivo 3 (contagem de necessidades) e objetivo 5.

## D-008: onboarding.csv · contas sem onboarding
- Data: 2026-10-29 · Responsável: Pedro Filardi · Status: aceita
- Dimensão: completude · Problema: Q-onb-06 (saidas/qualidade/onboarding.md)
- Contexto: 1.019 das 64.948 contas de `usuarios.csv` (1,6%) não têm linha no onboarding. Delas, 60 são `interno`, 41 têm cadastro em 2027, e só 5,9% assinaram (contra 50,3% na base).
- Decisão: marcar. Ao juntar o onboarding com outras tabelas, é criada a coluna `tem_onboarding`. As contas internas e as de 2027 ficam para a avaliação de `usuarios.csv`.
- Motivo: é um grupo diferente da base, e tirá-lo enviesaria a taxa de conversão.
- Alternativas consideradas: remover das análises (−1,6% das contas, com viés).
- Efeito na contagem: 64.948 contas → 64.948 nas tabelas integradas; 1 coluna nova.
- Impacto: integração das tabelas pelo `user_id` (objetivo 1) e análises de conversão.

## D-009: eventos_assinatura.csv · horários convertidos para Brasília
- Data: 2026-10-29 · Responsável: Pedro Filardi · Status: aceita
- Dimensão: temporalidade · consistência · Problema: Q-eve-01 (saidas/qualidade/eventos_assinatura.md)
- Contexto: as lojas (App Store, Google Play) gravam em UTC (`...Z`) e o site em Brasília; são 186.323 horários em UTC (67,6%). Sem converter, 753 eventos caem no mês errado.
- Decisão: corrigir. Na cópia processada, os horários em UTC são convertidos para Brasília (UTC−3), e o original fica em `data_hora_original`. Os brutos não mudam.
- Motivo: depois da conversão, 100% das 17.830 expirações caem no mesmo dia de `assinaturas.data_fim`; sem converter, só 92,1%.
- Alternativas consideradas: só marcar o fuso (os 753 continuariam no mês errado nas contagens).
- Efeito na contagem: 275.565 eventos → 275.565; 186.323 horários convertidos; 21.951 mudam de dia; 753 mudam de mês; 1 coluna nova.
- Impacto: série de churn mensal (objetivos 1 e 2) e toda contagem por dia ou mês.

## D-010: eventos_assinatura.csv · fase teste ou pago
- Data: 2026-10-29 · Responsável: Pedro Filardi · Status: aceita
- Dimensão: completude · Problema: Q-eve-02 (saidas/qualidade/eventos_assinatura.md)
- Contexto: `plano` está vazio em 72.873 eventos (26,4%). São 66.139 eventos de teste grátis e 6.734 desligamentos de renovação feitos durante o teste.
- Decisão: marcar. Na cópia processada é criada a coluna `fase`: `teste` para os eventos de teste e para os desligamentos sem plano anterior; `pago` para os demais. Os brutos não mudam.
- Motivo: desistir no teste grátis e cancelar depois de pagar são comportamentos diferentes; só o segundo é churn de assinante pagante.
- Alternativas consideradas: remover os eventos de teste (−26,4% dos eventos e todo o histórico de teste).
- Efeito na contagem: 275.565 eventos → 275.565; 1 coluna nova (72.873 eventos `teste`, 202.692 `pago`).
- Impacto: definição de churn pagante (objetivo 1) e análise de conversão do teste.

## D-011: eventos_assinatura.csv · motivo da saída vindo de assinaturas.csv
- Data: 2026-10-29 · Responsável: Pedro Filardi · Status: aceita
- Dimensão: completude · Problema: Q-eve-03 (saidas/qualidade/eventos_assinatura.md)
- Contexto: só 6.071 das 17.830 expirações (34%) têm `detalhe`. `assinaturas.motivo_fim` tem o motivo de todas e concorda 100% onde os dois existem.
- Decisão: corrigir. Na cópia processada, o motivo de cada expiração é preenchido a partir de `assinaturas.motivo_fim`, ligando por `user_id` e dia do fim (com o fuso já convertido, D-009). O motivo serve para medir e descrever o churn, **nunca como variável de previsão** para quem está ativo. Os brutos não mudam.
- Motivo: separar a saída voluntária (renovação desligada) da involuntária (falha de pagamento, chargeback) define em quem vale agir.
- Alternativas consideradas: marcar como desconhecido (66% das saídas sem motivo).
- Efeito na contagem: 275.565 eventos → 275.565; motivo preenchido de 6.071 para 17.830 expirações (16.145 renovação desligada, 1.321 falha de pagamento, 292 chargeback, 72 reembolso).
- Impacto: objetivos 2 e 6 (por que saem e em quem agir).

## D-012: eventos_assinatura.csv · eventos atípicos marcados
- Data: 2026-10-29 · Responsável: Pedro Filardi · Status: aceita
- Dimensão: consistência · validade · Problemas: Q-eve-04 e Q-eve-05 (saidas/qualidade/eventos_assinatura.md)
- Contexto: 611 eventos (0,2%) em ordem atípica, como o desligamento depois da expiração ou a expiração logo após uma renovação. Além disso, 1.154 cobranças fora do ciclo: 1.144 mensais fora de 25 a 35 dias e 10 anuais fora de 355 a 375.
- Decisão: marcar. Na cópia processada são criadas `sequencia_atipica` e `ciclo_atipico`. A regra de estado usa eventos-chave: saída = `assinatura_expirada`, em qualquer ordem; ativo = cobrança (`assinatura_iniciada` ou `renovacao`) sem expiração posterior. O ciclo atípico será investigado junto com `pagamentos.csv`. Os brutos não mudam.
- Motivo: são poucos casos, sem valor certo conhecido, e a regra de estado já reproduz os 14.753 ativos do enunciado com eles dentro.
- Alternativas consideradas: remover os atípicos (−1.765 eventos, inclusive expirações reais); reordenar ou inferir eventos (inventaria a sequência).
- Efeito na contagem: 275.565 eventos → 275.565; 2 colunas novas; ativos em 30/09/2026 = 14.753.
- Impacto: reconstrução da situação de cada assinante numa data (objetivo 1).

## D-013: assinaturas.csv · contas de cortesia fora das métricas
- Data: 2026-10-29 · Responsável: Pedro Filardi · Status: aceita
- Dimensão: validade · Problema: Q-ass-01 (saidas/qualidade/assinaturas.md)
- Contexto: 60 assinaturas `cortesia`, canal `interno`, todas ativas, sem eventos e sem cobrança. São contas internas, e o dicionário só prevê os planos `mensal` e `anual`.
- Decisão: marcar. Na cópia processada é criada a coluna `pagante` (sim/não), e as 60 `cortesia` ficam como `não`, fora de toda conta de assinantes, churn e receita. Os brutos não mudam.
- Motivo: o dado está certo, só não é de pagante; marcar mantém o registro e evita inflar as métricas.
- Alternativas consideradas: remover as 60 da cópia processada (perderia o registro de quem são).
- Efeito na contagem: 32.643 assinaturas → 32.643; ativos pagantes = 14.753 (e não 14.813); 1 coluna nova.
- Impacto: toda métrica de base, churn e receita (objetivos 1, 2 e 7).

## D-014: assinaturas.csv · histórico só a partir de julho de 2024
- Data: 2026-10-29 · Responsável: Pedro Filardi · Status: aceita
- Dimensão: completude · temporalidade · Problema: Q-ass-02 (saidas/qualidade/assinaturas.md)
- Contexto: nenhuma assinatura termina antes de 07/07/2024. As 5.200 iniciadas antes de 07/2024 são só as que sobreviveram até lá; as que saíram antes não estão em nenhum arquivo.
- Decisão: marcar. Na cópia processada é criada a coluna `inicio_antes_historico` (sim/não). Regra: **taxas de churn só a partir de 07/2024**, e análises por ano de entrada ou tempo de casa sempre com a ressalva de que os clientes antigos são sobreviventes. Os brutos não mudam.
- Motivo: não há como recuperar o que falta, e remover tiraria 1.462 assinantes ativos reais. A série de churn pedida (2025 e 2026) está inteira no período coberto.
- Alternativas consideradas: remover as 5.200 (de 32.643 para 27.443, perdendo 1.462 ativos).
- Efeito na contagem: 32.643 assinaturas → 32.643; 1 coluna nova (5.200 marcadas).
- Impacto: série de churn (objetivos 1 e 2), tempo de casa no modelo e nos segmentos (objetivos 3 e 4).

## D-015: assinaturas.csv · colunas de retrato nunca usadas para prever
- Data: 2026-10-29 · Responsável: Pedro Filardi · Status: aceita
- Dimensão: temporalidade · Problema: Q-ass-03 (saidas/qualidade/assinaturas.md)
- Contexto: `status_atual`, `renovacao_automatica`, `data_fim` e `motivo_fim` descrevem o dia 01/10/2026; o sistema sobrescreve o valor a cada mudança.
- Decisão: marcar. Na cópia processada, as quatro colunas ganham o prefixo `retrato_0110_`. Regra: **nunca usar como variável de previsão**; a situação em datas passadas vem de `eventos_assinatura.csv` (D-012). Os brutos não mudam.
- Motivo: evitar vazamento. Usar essas colunas daria ao modelo a resposta, e na prática a empresa não teria a informação a tempo de agir.
- Alternativas consideradas: remover as colunas (perderia o motivo da saída, usado no D-011).
- Efeito na contagem: 32.643 assinaturas → 32.643; 4 colunas renomeadas.
- Impacto: objetivo 4 (modelo de churn) e qualquer análise do passado.

## D-016: assinaturas.csv · assinatura antes do cadastro
- Data: 2026-10-29 · Responsável: Pedro Filardi · Status: aceita
- Dimensão: validade · consistência · Problema: Q-ass-04 (saidas/qualidade/assinaturas.md)
- Contexto: 42 assinaturas ativas começam antes de `usuarios.data_cadastro` (de 8 a 612 dias antes). O início bate com os eventos; o erro está no cadastro.
- Decisão: marcar. Na cópia processada é criada a coluna `cadastro_inconsistente` (sim/não). A correção da data de cadastro será decidida na avaliação de `usuarios.csv`. Os brutos não mudam.
- Motivo: a data de início é confirmada pelos eventos, e o problema pertence a outro arquivo.
- Alternativas consideradas: remover as 42 (perderia assinantes ativos reais); corrigir já o cadastro (é decisão do `usuarios.csv`).
- Efeito na contagem: 32.643 assinaturas → 32.643; 1 coluna nova (42 marcadas).
- Impacto: cálculos de tempo entre cadastro e assinatura; pendência para a avaliação de `usuarios.csv`.
