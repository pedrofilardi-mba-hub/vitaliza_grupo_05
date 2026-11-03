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
- Data: 2026-10-29 · Responsável: Pedro Filardi · Status: substituída por D-023 (o motivo abaixo estava errado: as 42 são contas internas de cortesia)
- Dimensão: validade · consistência · Problema: Q-ass-04 (saidas/qualidade/assinaturas.md)
- Contexto: 42 assinaturas ativas começam antes de `usuarios.data_cadastro` (de 8 a 612 dias antes). O início bate com os eventos; o erro está no cadastro.
- Decisão: marcar. Na cópia processada é criada a coluna `cadastro_inconsistente` (sim/não). A correção da data de cadastro será decidida na avaliação de `usuarios.csv`. Os brutos não mudam.
- Motivo: a data de início é confirmada pelos eventos, e o problema pertence a outro arquivo.
- Alternativas consideradas: remover as 42 (perderia assinantes ativos reais); corrigir já o cadastro (é decisão do `usuarios.csv`).
- Efeito na contagem: 32.643 assinaturas → 32.643; 1 coluna nova (42 marcadas).
- Impacto: cálculos de tempo entre cadastro e assinatura; pendência para a avaliação de `usuarios.csv`.

## D-017: usuarios.csv · cidade padronizada
- Data: 2026-10-29 · Responsável: Pedro Filardi · Status: aceita
- Dimensão: consistência · Problema: Q-usu-01 (saidas/qualidade/usuarios.md)
- Contexto: `cidade` tem 36 grafias para 13 cidades (`Sampa`, `SP`, `S. Paulo`, `SAO PAULO`, `BH`, `Floripa`, `BSB`…); 13.601 contas (20,9%) fora da grafia padrão.
- Decisão: corrigir. Na cópia processada, as 36 grafias são mapeadas para os 13 nomes oficiais, com uma tabela de-para registrada no código. Os brutos não mudam.
- Motivo: as grafias são inequívocas, e a `uf` (limpa, uma por cidade) confirma cada mapeamento.
- Alternativas consideradas: manter como está (contagens por cidade partidas).
- Efeito na contagem: 64.948 contas → 64.948; 13.601 cidades reescritas (SP 8.371, RJ 2.245, BH 1.340, Brasília 896, Florianópolis 749).
- Impacto: análises e segmentos por localização (objetivos 2 e 3).

## D-018: usuarios.csv · sexo padronizado e só para controle
- Data: 2026-10-29 · Responsável: Pedro Filardi · Status: aceita
- Dimensão: consistência · completude · Problema: Q-usu-02 (saidas/qualidade/usuarios.md)
- Contexto: `sexo` tem 6 grafias (`F`, `Fem`, `feminino`, `M`, `Masc`, `masculino`) e 3.142 vazios (4,8%).
- Decisão: corrigir. Na cópia processada, os valores viram `F` e `M`, e os vazios viram `nao_informado`. Regra: sexo só para descrever e controlar análises, **nunca como critério de oferta ou contato**. Os brutos não mudam.
- Motivo: as grafias são inequívocas. Pela LGPD (art. 6º, IX, não discriminação) e pelas Aulas 2 e 3, gênero não deve guiar decisões, e não teve poder preditivo (AUC 0,50).
- Alternativas consideradas: remover a coluna (perderia a variável de controle).
- Efeito na contagem: 64.948 contas → 64.948; 24.830 valores reescritos; 3.142 vazios viram `nao_informado` (F 32.507, M 29.299).
- Impacto: objetivos 3 (segmentos) e 6 (regra de contato, que não pode usar sexo).

## D-019: usuarios.csv · sistema padronizado
- Data: 2026-10-29 · Responsável: Pedro Filardi · Status: aceita
- Dimensão: consistência · Problema: Q-usu-03 (saidas/qualidade/usuarios.md)
- Contexto: `sistema` tem 5 grafias para 2 sistemas; 16.067 contas (24,7%) fora da grafia padrão.
- Decisão: corrigir. Na cópia processada, os valores viram `android` e `ios`. Os brutos não mudam.
- Motivo: as grafias são inequívocas.
- Alternativas consideradas: manter as grafias (contagens partidas).
- Efeito na contagem: 64.948 contas → 64.948; 16.067 valores reescritos (android 35.151, ios 29.797).
- Impacto: análises por canal de pagamento e por loja (objetivos 2 e 6).

## D-020: usuarios.csv · datas de nascimento falsas viram vazio
- Data: 2026-10-29 · Responsável: Pedro Filardi · Status: aceita
- Dimensão: validade · completude · Problema: Q-usu-04 (saidas/qualidade/usuarios.md)
- Contexto: 412 nascimentos em 01/01/1900, 194 numa mesma data de 2031 (datas de preenchimento padrão) e 3.301 vazios; 1 conta com 13 a 17 anos.
- Decisão: corrigir. Na cópia processada, as 606 datas falsas viram vazio, e é criada a coluna `idade_informada` (sim/não). Regras: idade só como variável de controle, **nunca como critério de oferta ou contato**; a conta menor de 18 anos é marcada e fica fora de qualquer campanha. Os brutos não mudam.
- Motivo: as datas falsas distorcem médias e segmentos. Pela LGPD e pela Aula 3, idade não deve decidir ofertas, e menores pedem cuidado extra.
- Alternativas consideradas: remover as contas sem nascimento válido (−3.907, −6,0%); manter e marcar como suspeita (médias distorcidas).
- Efeito na contagem: 64.948 contas → 64.948; nascimento preenchido de 61.647 para 61.041; 1 coluna nova; 1 conta marcada como menor.
- Impacto: objetivos 3 e 4 (idade como controle) e 6 (exclusão do menor das campanhas).

## D-021: usuarios.csv · contas criadas depois do corte removidas
- Data: 2026-10-29 · Responsável: Pedro Filardi · Status: aceita
- Dimensão: temporalidade · validade · Problema: Q-usu-05 (saidas/qualidade/usuarios.md)
- Contexto: 119 contas com `data_cadastro` entre 10/2026 e 04/2027, depois da exportação (01/10/2026). Nenhuma tem evento, assinatura ou onboarding.
- Decisão: remover. As 119 ficam fora da cópia processada. Os brutos não mudam.
- Motivo: as datas são impossíveis, as contas não carregam nenhuma outra informação, e a D-002 proíbe dado posterior ao corte.
- Alternativas consideradas: marcar com `cadastro_pos_corte` (deixaria contas "do futuro" nos totais).
- Efeito na contagem: 64.948 contas → 64.829.
- Impacto: total de contas e taxa de conversão de cadastro em assinatura (objetivo 1).

## D-022: usuarios.csv · código de pessoa para contas duplicadas
- Data: 2026-10-29 · Responsável: Pedro Filardi · Status: aceita
- Dimensão: unicidade · Problema: Q-usu-06 (saidas/qualidade/usuarios.md)
- Contexto: 959 pares de contas (1.918) com o mesmo e-mail, variando só maiúsculas e minúsculas, com a mesma UF e a mesma data de nascimento; em nenhum par as duas contas pagaram.
- Decisão: marcar. Na cópia processada é criada `pessoa_id`, um código derivado do e-mail em minúsculas que não revela o e-mail. Contagens "por conta" usam `user_id`; "por pessoa" usam `pessoa_id`. Os brutos não mudam.
- Motivo: nenhum dado se perde, e a ligação com os outros arquivos pelo `user_id` continua intacta.
- Alternativas consideradas: fundir as contas (reescreveria o `user_id` em todos os arquivos, com risco de erro em cascata); remover a conta sem assinatura de cada par (−959 contas e o histórico de uso delas).
- Efeito na contagem: 64.948 contas → 64.948 (64.829 depois da D-021); pessoas distintas = 63.989 antes da D-021; 1 coluna nova.
- Impacto: conversão e segmentos por pessoa (objetivos 1 e 3).

## D-023: correção da D-016 · as 42 assinaturas são contas internas
- Data: 2026-10-29 · Responsável: Pedro Filardi · Status: aceita · Substitui: D-016
- Dimensão: validade · Problema: Q-usu-07 (saidas/qualidade/usuarios.md) e Q-ass-04 (saidas/qualidade/assinaturas.md)
- Contexto: a D-016 afirmou que as 42 assinaturas com início antes do cadastro eram de assinantes ativos e que o erro estava no cadastro, porque o início "batia com os eventos". A avaliação de `usuarios.csv` mostrou que as 42 são todas `cortesia` / `interno`, sem nenhum evento; o motivo da D-016 era falso.
- Decisão: nenhuma data é alterada e a coluna `cadastro_inconsistente` não é criada. O caso pertence às contas internas, que já estão fora de todas as métricas pela D-013.
- Motivo: corrigir o registro sem apagar a decisão anterior.
- Alternativas consideradas: manter a D-016 (deixaria um motivo falso no registro).
- Efeito na contagem: 0 contas; 0 colunas (a coluna prevista na D-016 deixa de existir).
- Impacto: nenhum número de negócio muda.
## D-024: pagamentos.csv · cobranças repetidas removidas
- Data: 2026-11-03 · Responsável: Pedro Filardi · Status: aceita
- Dimensão: unicidade · Problema: Q-pag-01 (saidas/qualidade/pagamentos.md)
- Contexto: 1.941 cobranças aprovadas repetidas (mesma conta, mesmo instante, mesmo valor), em 1.807 contas e em todos os meios de pagamento.
- Decisão: remover. Na cópia processada fica só a primeira de cada repetição. Os brutos não mudam.
- Motivo: são cópias de registro, não cobranças reais. Sem elas, as aprovadas batem 1 a 1 com os eventos de cobrança (159.989), o faturamento de setembro/2026 reproduz a Aula 2 (R$ 492.572), e quem aparece "cobrado em dobro" não reclamou mais no suporte (0,5% nos dois grupos).
- Alternativas consideradas: marcar com `cobranca_repetida` (toda soma precisaria lembrar do filtro).
- Efeito na contagem: 165.548 linhas → 163.607; aprovadas de 161.930 para 159.989; setembro/2026 de R$ 499.402 para R$ 492.572.
- Impacto: toda conta de receita e retorno (objetivo 7).

## D-025: pagamentos.csv · valores em texto convertidos para número
- Data: 2026-11-03 · Responsável: Pedro Filardi · Status: aceita
- Dimensão: consistência · Problema: Q-pag-02 (saidas/qualidade/pagamentos.md)
- Contexto: 19.750 valores gravados como texto (`R$ 34,90`), todos do site (cartão 13.044, Pix 6.706), em 2024 e 2025.
- Decisão: corrigir. Na cópia processada, o `R$` é retirado, a vírgula vira ponto e o valor é guardado como número. Os brutos não mudam.
- Motivo: o valor certo é inequívoco, e sem converter essas linhas ficam fora das somas.
- Alternativas consideradas: remover as linhas (−11,9% das cobranças e toda a receita do site em 2024 e 2025).
- Efeito na contagem: 163.607 linhas → 163.607; 19.750 valores convertidos.
- Impacto: receita (objetivos 1 e 7).

## D-026: pagamentos.csv · horários convertidos para Brasília
- Data: 2026-11-03 · Responsável: Pedro Filardi · Status: aceita
- Dimensão: temporalidade · Problema: Q-pag-03 (saidas/qualidade/pagamentos.md)
- Contexto: App Store e Google Play gravam em UTC (112.126 linhas); cartão e Pix em Brasília (53.422).
- Decisão: corrigir, com a mesma regra da D-009. Na cópia processada, os horários em UTC são convertidos para Brasília (UTC−3), e o original fica em `data_hora_original`. Os brutos não mudam.
- Motivo: com a conversão, as cobranças batem com os eventos no mesmo dia em 100% dos casos, e setembro/2026 reproduz a Aula 2 (R$ 499.402 antes de tirar as repetidas).
- Alternativas consideradas: só marcar o fuso (cobranças continuariam no mês errado).
- Efeito na contagem: 163.607 linhas → 163.607; 112.126 horários convertidos (menos os das repetidas removidas); 1 coluna nova.
- Impacto: receita mensal (objetivos 1 e 7).

## D-027: pagamentos.csv · retentativa real no lugar de "tentativa"
- Data: 2026-11-03 · Responsável: Pedro Filardi · Status: aceita
- Dimensão: validade · Problema: Q-pag-04 (saidas/qualidade/pagamentos.md)
- Contexto: das 4.866 cobranças com `tentativa = 2`, só 54 vêm depois de uma recusa. As outras são a mensalidade normal do mês seguinte (3.888) ou a primeira cobrança da conta (924).
- Decisão: corrigir. Na cópia processada é criada `retentativa_real` (sim quando a cobrança vem depois de uma recusa da mesma conta), e a coluna `tentativa` original fica de fora. Os brutos não mudam.
- Motivo: a coluna original não significa o que o dicionário diz, e usá-la superestimaria a recuperação de cartões recusados (4.866 contra 54).
- Alternativas consideradas: remover a coluna sem substituta; manter com aviso no nome (ainda poderia ser usada por engano).
- Efeito na contagem: 163.607 linhas → 163.607; 54 marcadas como retentativa real; 1 coluna nova e 1 coluna a menos.
- Impacto: análise de churn involuntário (objetivos 2 e 6).
## D-028: uso_mensal.csv · base mensal padronizada por assinante ativo
- Data: 2026-11-03 · Responsável: Pedro Filardi · Status: aceita
- Dimensão: temporalidade · completude · Problema: Q-uso-01 (saidas/qualidade/uso_mensal.md)
- Contexto: em 2025 o resumo só traz quem treinou no mês (0 linhas zeradas). Em 2026 traz todo mundo, com zero para quem não treinou e inclusive contas não assinantes (41.536 das 56.565 linhas de set/2026). A média de minutos "cai" de 265 para 118 na virada só por causa do registro.
- Decisão: corrigir. Na cópia processada é montada uma base com uma linha por assinante ativo em cada mês (situação pelos eventos, D-012). Quem não tem linha no mês recebe zero. As linhas de não assinantes ficam marcadas com `assinante_no_mes = não`. Os brutos não mudam.
- Motivo: só a base completa mostra "assinante que não treinou" do mesmo jeito nos dois anos, um sinal central para prever saída e para explicar a subida do churn em 2026.
- Alternativas consideradas: remover os zeros de 2026 (−303.735 linhas e perda do sinal de inatividade); só marcar o ano da regra (comparações entre anos continuariam erradas).
- Efeito na contagem: nenhuma linha do original é perdida; a base de assinantes passa a ter, por mês, o tamanho da base ativa (de cerca de 8,5 mil em jan/2025 a cerca de 15,4 mil em set/2026); 2025 ganha cerca de 2.400 linhas zeradas por mês; 1 coluna nova.
- Impacto: objetivos 2 (por que o churn subiu) e 4 (variáveis de uso no modelo).

## D-029: uso_mensal.csv × atividades.parquet · regra de fonte para o uso
- Data: 2026-11-03 · Responsável: Pedro Filardi · Status: aceita
- Dimensão: consistência · Problema: Q-uso-02 (saidas/qualidade/uso_mensal.md)
- Contexto: em 2026, o resumo mensal conta de 69% a 70% dos treinos do detalhe (`atividades.parquet`); bate em só 60% dos pares pessoa-mês, e os minutos quase nunca coincidem. Nenhuma de 4 explicações testadas reproduz a diferença.
- Decisão: marcar, com regra de uso. Para 2026, treinos, minutos e dias ativos vêm do `atividades.parquet`, depois da avaliação de qualidade dele. O `uso_mensal.csv` vale para 2025 e para `sessoes_app`, que só existe nele. Nunca comparar números de fontes diferentes como se fossem a mesma medida. Na cópia processada é criada a coluna `fonte` (`resumo` ou `detalhe`). Os brutos não mudam.
- Motivo: o dicionário indica o detalhe como fonte de 2026, e ele é verificável treino a treino; o resumo é a única fonte de 2025 e das sessões no app.
- Alternativas consideradas: recalcular já o resumo de 2026 pelo detalhe (depende da avaliação de `atividades.parquet`); descartar o resumo de 2026 (perderia `sessoes_app`).
- Efeito na contagem: 591.662 linhas → 591.662; 1 coluna nova.
- Impacto: objetivos 2, 3 e 4. Pendência: perguntar ao professor se a diferença entre as fontes é proposital no case.
## D-030: atividades.parquet · horário do Garmin convertido para Brasília
- Data: 2026-11-03 · Responsável: Pedro Filardi · Status: aceita
- Dimensão: temporalidade · Problema: Q-atv-01 (saidas/qualidade/atividades.md)
- Contexto: os 207.954 treinos do Garmin estão em UTC. Eles têm o pico às 9h, contra 6h no app e no Apple Health, e 34 deles caem em "01/10/2026".
- Decisão: corrigir. Na cópia processada, 3 horas são subtraídas do início dos treinos do Garmin, e o original fica em `inicio_original`. Os brutos não mudam.
- Motivo: é a mesma regra das D-009 e D-026, confirmada pelo padrão de horário, e é pré-condição para encontrar as duplicatas (D-031).
- Alternativas consideradas: remover os 34 de outubro (os outros 207.920 continuariam com o horário errado); só marcar o fuso.
- Efeito na contagem: 1.254.475 treinos → 1.254.475; 207.954 horários ajustados; os 34 de "outubro" passam para 30/09.
- Impacto: dias e meses de treino (objetivos 2 a 4) e detecção de duplicatas.

## D-031: atividades.parquet · treinos em dobro (app e relógio)
- Data: 2026-11-03 · Responsável: Pedro Filardi · Status: aceita
- Dimensão: unicidade · Problema: Q-atv-02 (saidas/qualidade/atividades.md)
- Contexto: 9.383 treinos chegaram duas vezes, pelo app e pelo relógio (4.184 Apple Health e 5.199 Garmin). Regra da Aula 2: mesma conta, mesmo tipo, mesma duração, início a até 5 minutos (fuso já corrigido, D-030), uma origem `app` e outra `garmin` ou `apple_health`.
- Decisão: remover. Na cópia processada sai a cópia de origem `app`, e fica a do relógio. Os brutos não mudam.
- Motivo: o relógio tem os mesmos dados e mais a frequência cardíaca; manter as duas inflaria treinos e minutos de quem tem relógio.
- Alternativas consideradas: marcar `treino_duplicado` (toda contagem precisaria lembrar do filtro).
- Efeito na contagem: 1.254.475 treinos → 1.245.092.
- Impacto: variáveis de frequência e volume de treino (objetivos 3 e 4).

## D-032: atividades.parquet · tipos de treino em português
- Data: 2026-11-03 · Responsável: Pedro Filardi · Status: aceita
- Dimensão: consistência · Problema: Q-atv-03 (saidas/qualidade/atividades.md)
- Contexto: 11 nomes para 7 tipos; 376.930 treinos (30%), todos registrados pelo app, com nome em inglês (`run`, `walk`, `strength`, `ride`).
- Decisão: corrigir. Na cópia processada, `run` vira corrida, `walk` vira caminhada, `strength` vira força e `ride` vira pedal. É criada a coluna `modalidade` (ar livre: corrida, caminhada e pedal; vídeo: força, funcional, hiit e yoga). Os brutos não mudam.
- Motivo: o mapeamento é inequívoco, e a proporção em inglês é igual em todas as versões do app.
- Alternativas consideradas: manter os 11 nomes (contagens por tipo partidas).
- Efeito na contagem: 1.245.092 treinos → 1.245.092; 376.930 tipos reescritos (menos os das duplicatas removidas); 1 coluna nova.
- Impacto: segmentos por tipo de treino (objetivo 3).

## D-033: atividades.parquet · distância recalculada pelo ritmo
- Data: 2026-11-03 · Responsável: Pedro Filardi · Status: aceita
- Dimensão: validade · Problema: Q-atv-04 (saidas/qualidade/atividades.md)
- Contexto: 951 treinos acima de 200 km (máximo de 10.013 km), cerca de 100 vezes a distância real; ritmo e duração estão coerentes.
- Decisão: corrigir. Na cópia processada, a distância desses treinos passa a ser duração ÷ ritmo, e a original fica em `distancia_original`. Os brutos não mudam.
- Motivo: nas linhas normais, ritmo = duração ÷ distância em 99,6% dos casos, e a distância recalculada fica no padrão de cada tipo (corrida 6,67 km, típico 6,51).
- Alternativas consideradas: remover os treinos (−951 reais); deixar a distância vazia (perderia um valor recuperável).
- Efeito na contagem: 1.245.092 treinos → 1.245.092; 951 distâncias reescritas.
- Impacto: variáveis de distância e mapas de rota (objetivos 3 a 5).

## D-034: atividades.parquet · duração zero recalculada ou marcada
- Data: 2026-11-03 · Responsável: Pedro Filardi · Status: aceita
- Dimensão: validade · Problema: Q-atv-05 (saidas/qualidade/atividades.md)
- Contexto: 3.649 treinos com 0 minuto. Desses, 1.972 têm distância e ritmo; 1.677 não têm.
- Decisão: corrigir e marcar. Na cópia processada, a duração dos 1.972 passa a ser ritmo × distância. Os 1.677 restantes ficam com duração vazia e a marca `duracao_invalida`: contam como treino, mas não entram na soma de minutos. Os brutos não mudam.
- Motivo: recuperar o que é recuperável sem inventar o resto.
- Alternativas consideradas: remover os 3.649 (perderia treinos reais); só marcar (perderia 1.972 durações recuperáveis).
- Efeito na contagem: 1.245.092 treinos → 1.245.092; 1.972 durações recalculadas; 1.677 marcadas.
- Impacto: minutos de treino (objetivos 3 e 4).

## D-035: atividades.parquet · distância de GPS falho descartada
- Data: 2026-11-03 · Responsável: Pedro Filardi · Status: aceita
- Dimensão: validade · Problema: Q-atv-06 (saidas/qualidade/atividades.md)
- Contexto: 14.779 treinos com `gps_ok = falso`, todos ao ar livre; 7.455 deles têm uma distância gravada, cortada (mediana de 0,6 km) e sem ritmo.
- Decisão: marcar. Na cópia processada é criada `gps_falhou` nos 14.779; a distância dos 7.455 vira vazia, e o treino e a duração continuam valendo. Os brutos não mudam.
- Motivo: o treino aconteceu, só a distância não é confiável e não dá para recalcular, porque não há ritmo.
- Alternativas consideradas: remover os treinos (−14.779 reais).
- Efeito na contagem: 1.245.092 treinos → 1.245.092; 7.455 distâncias apagadas na cópia; 1 coluna nova.
- Impacto: médias de distância (objetivos 3 e 5).