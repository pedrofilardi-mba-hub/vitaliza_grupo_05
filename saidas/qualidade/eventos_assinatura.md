# Qualidade: `eventos_assinatura.csv`

Uma linha por evento na vida de uma assinatura · 275.565 linhas · 6 colunas · de 01/07/2024 a 30/09/2026 · avaliado em 29/10/2026 com a skill `qualidade-dados` · medidas em [eventos_assinatura_evidencias.md](eventos_assinatura_evidencias.md)

## Resumo

É o arquivo mais confiável do data room para reconstruir a base. **Pelos eventos, chega-se a exatamente 14.753 assinantes ativos em 30/09/2026**, o número do enunciado, com 57,5% no plano anual e 42,5% no mensal (enunciado: 57% e 43%). Não há valores fora do domínio, datas inválidas nem eventos duplicados.

Dois problemas mudam números e precisam de decisão:
1. **O fuso.** As lojas gravam em UTC e o site em Brasília. Sem converter, **753 eventos caem no mês errado**, o que distorce o churn mensal.
2. **O motivo da saída** está só em 34% das expirações. O `assinaturas.csv` tem o motivo completo.

O resto é marcação de casos raros (menos de 1%). Nenhuma decisão muda a contagem de assinantes ativos.

**Situação em 29/10/2026:** os 5 problemas foram decididos (D-009 a D-012 no `DECISOES.md`), todos para aplicar numa cópia em `dados/processados/`. Os brutos não mudam. A limpeza ainda não foi feita.

## Problemas para decidir

| ID | Dimensão | Coluna | O que está errado | Por que importa para o case |
|---|---|---|---|---|
| Q-eve-01 | Temporalidade · Consistência | `data_hora` | 186.323 eventos (67,6%) das lojas em UTC (`...Z`) e 89.242 do site em Brasília; ao converter, 21.951 mudam de dia e 753 mudam de mês | O churn mensal é contado por mês. Sem converter, renovações e expirações perto da meia-noite do último dia vão para o mês seguinte |
| Q-eve-02 | Completude | `plano` | 72.873 vazios (26,4%): todos os eventos de teste grátis (66.139) e 6.734 `renovacao_automatica_desligada` | Os vazios são de quem desligou a renovação **durante o teste**, sinal de desistência antes de pagar. Sem marcar, se misturam com o desligamento de quem já paga |
| Q-eve-03 | Completude | `detalhe` | Motivo preenchido em só 6.071 das 17.830 expirações (34%) | Separar saída voluntária (renovação desligada) de involuntária (falha de pagamento, chargeback) é o que define em quem vale agir (objetivo 6) |
| Q-eve-04 | Consistência | sequência de eventos | 611 eventos (0,2%) em ordem atípica: 207 desligamentos depois da expiração, 220 expirações logo após uma renovação, 164 expirações logo após o início, 12 renovações logo após o desligamento, 8 cancelamentos web depois da expiração | Podem gerar estados impossíveis ao reconstruir a situação de cada um numa data |
| Q-eve-05 | Validade | intervalo entre cobranças | 1.144 renovações mensais (0,9%) fora de 25 a 35 dias desde a cobrança anterior (644 antes de 25 dias, 500 entre 36 e 45); 10 anuais fora de 355 a 375 dias (uma com 13 dias) | Afeta medidas de "tempo de casa" e de ciclo de cobrança |

### Q-eve-01 · Fusos misturados

- **Evidência:**
  - O formato depende só do canal: App Store e Google Play sempre em UTC (`2026-09-30T02:10:00Z`); cartão e Pix do site sempre em Brasília (`2026-09-29 23:10:00`).
  - **Prova de que a conversão está certa:** depois de converter, as 17.830 expirações caem 100% no mesmo dia do `data_fim` de `assinaturas.csv`. Sem converter, só 16.424 (92,1%).
  - Os 753 eventos que mudam de mês são 368 renovações, 124 inícios de teste, 86 desligamentos, 59 fins de teste, 57 expirações, 49 inícios de assinatura e outros 10.
- **Opções:**
  - **Corrigir:** converter os horários em UTC para Brasília (UTC−3, sem horário de verão desde 2019). Efeito: 275.565 → 275.565 eventos; 186.323 horários convertidos; 21.951 mudam de dia; 753 mudam de mês.
  - **Remover:** não se aplica.
  - **Marcar:** manter o horário original e anotar o fuso. Efeito: 0 linhas, mas toda contagem por dia ou mês continua errada para os 753.
- **Recomendação:** **corrigir**. Há prova externa de que a conversão é a certa (100% de coincidência com `assinaturas.csv`). Manter o horário original numa coluna à parte (`data_hora_original`) para auditoria.
- **Status:** decidido (D-009, 29/10/2026, Pedro Filardi)

### Q-eve-02 · Plano vazio

- **Evidência:**
  - `trial_iniciado` (46.996) e `trial_expirado` (19.143) nunca têm plano. É esperado: no teste ainda não se escolheu plano.
  - Os outros 6.734 vazios são todos de `renovacao_automatica_desligada` que não têm nenhum evento com plano antes. 6.200 desligamentos vêm logo depois de `trial_iniciado`, e 6.178 são seguidos de `trial_expirado`: **é quem desistiu durante o teste**.
  - A soma bate: 46.996 + 19.143 + 6.734 = 72.873.
- **Opções:**
  - **Corrigir:** não há plano a recuperar.
  - **Remover:** tirar os eventos sem plano. Efeito: 275.565 → 202.692 eventos (−26,4%); apaga todo o histórico de teste grátis.
  - **Marcar:** criar a coluna `fase` (`teste` ou `pago`). Os eventos de teste e os desligamentos sem plano anterior ficam `teste`; os demais, `pago`. Efeito: 0 linhas; 1 coluna nova.
- **Recomendação:** **marcar**. Desligar a renovação no teste e desligar depois de pagar são comportamentos diferentes, e só o segundo é churn de assinante pagante.
- **Status:** decidido (D-010, 29/10/2026, Pedro Filardi)

### Q-eve-03 · Motivo da saída incompleto

- **Evidência:**
  - Das 17.830 expirações, só 6.071 têm `detalhe`: 5.139 renovação desligada, 800 falha de pagamento, 109 chargeback e 23 reembolso.
  - `assinaturas.motivo_fim` tem motivo para as 17.830, e onde os dois existem **concordam 100%** (6.071 de 6.071).
  - Pelo `assinaturas.csv`: 16.145 renovação desligada (90,5%), 1.321 falha de pagamento, 292 chargeback e 72 reembolso.
  - As 1.321 falhas batem com os 1.321 `periodo_carencia` seguidos de expiração.
- **Opções:**
  - **Corrigir:** preencher o motivo de cada expiração a partir de `assinaturas.motivo_fim`, ligando por `user_id` e dia do fim. Efeito: 0 linhas; motivo preenchido de 6.071 para 17.830.
  - **Remover:** não se aplica.
  - **Marcar:** deixar vazio e marcar `motivo_desconhecido`. Efeito: 0 linhas; 66% das saídas sem motivo.
- **Recomendação:** **corrigir**. Atenção: o motivo descreve uma saída que já aconteceu. Pode ser usado para medir e descrever o churn, mas **não pode virar variável** de previsão para quem ainda está ativo (vazamento).
- **Status:** decidido (D-011, 29/10/2026, Pedro Filardi)

### Q-eve-04 · Eventos em ordem atípica

- **Evidência:**
  - `assinatura_expirada` → `renovacao_automatica_desligada`: 207 (o aviso de desligamento chegou depois do fim).
  - `renovacao` → `assinatura_expirada` sem desligamento: 220. Têm motivo: 58 renovação desligada e 14 reembolso; os outros 148 estão sem motivo.
  - `assinatura_iniciada` → `assinatura_expirada`: 164, dos quais 55 chargeback.
  - `renovacao_automatica_desligada` → `renovacao`: 12.
  - `assinatura_expirada` → `cancelamento_web`: 8.

  Não são atípicos (são esperados): chargeback (136) e reembolso (40) depois da expiração, porque a contestação vem depois.
- **Opções:**
  - **Corrigir:** reordenar ou inferir eventos faltantes. Efeito: inventa uma sequência sem base.
  - **Remover:** tirar os 611 eventos. Efeito: 275.565 → 274.954; pode apagar expirações reais (as 220 e as 164).
  - **Marcar:** criar `sequencia_atipica` nos eventos afetados e definir a regra de estado por eventos-chave. Saída = `assinatura_expirada`, em qualquer ordem; ativo = cobrança (`assinatura_iniciada` ou `renovacao`) sem expiração posterior. Efeito: 0 linhas; 1 coluna nova.
- **Recomendação:** **marcar**. A regra de estado já reproduz os 14.753 ativos do enunciado com esses casos dentro, então eles não distorcem a contagem.
- **Status:** decidido (D-012, 29/10/2026, Pedro Filardi)

### Q-eve-05 · Intervalos de cobrança fora do ciclo

- **Evidência:**
  - Mensais: mediana de 30 dias entre cobranças. 1.144 fora de 25 a 35 dias: 2 com 8 e 9 dias, 642 entre 14 e 24 dias, e 500 entre 36 e 45 dias.
  - Anuais: mediana de 365 dias. 10 fora de 355 a 375: 1 com 13 dias e 9 entre 354 e 380.
  - Pode ser mudança de data de cobrança, nova tentativa ou erro. Vale cruzar com `pagamentos.csv`, onde há 4.866 segundas tentativas aprovadas contra 3.250 recusas, uma conta que também não fecha.
- **Opções:**
  - **Corrigir:** não há valor certo conhecido.
  - **Remover:** tirar essas renovações. Efeito: −1.154 eventos; o assinante fica com um "buraco" no histórico.
  - **Marcar:** criar `ciclo_atipico`. Efeito: 0 linhas; 1 coluna nova.
- **Recomendação:** **marcar** agora e investigar junto com a avaliação de `pagamentos.csv`.
- **Status:** decidido (D-012, 29/10/2026, Pedro Filardi)

## Já decidido

- **D-002 (corte em 30/09/2026):** os eventos vão até 30/09/2026, 0 depois do corte, já com o fuso convertido.

## O que não é problema

- **Domínios:** 0 valores fora das listas do dicionário em `evento`, `plano` e `canal_cobranca`.
- **Unicidade:** 0 linhas repetidas; 0 eventos iguais para a mesma conta no mesmo instante ou em menos de 1 hora.
- **Canal:** cada conta usa um só canal de cobrança em todo o histórico.
- **Uma assinatura por pessoa:** nenhuma conta tem mais de um `assinatura_iniciada`. O dicionário diz que a pessoa pode sair e voltar, mas na base isso não acontece.
- **Contas só de teste:** 52.196 contas têm eventos; 19.613 nunca pagaram, ficaram só no teste.
- **Assinaturas sem eventos:** 60, todas `cortesia` e ativas. Esperado.
- **Fechamentos com `pagamentos.csv`:** 296 chargebacks = 296; 72 reembolsos = 72 estornos.
- **`cancelamento_web`:** só existe a partir de 01/06/2026, quando entrou a pesquisa de saída. Antes disso, quem cancelava pelo site aparece como `renovacao_automatica_desligada` (8.564 casos). É uma mudança de registro esperada; ao comparar períodos, trate os dois como "desligou".

## Observação para o modelo (não é problema de qualidade)

Dos 14.753 ativos em 30/09, **2.250 já tinham anunciado a saída**: 2.018 com a renovação desligada e 232 com cancelamento web. Outros 25 estavam em carência. Eles continuam pagantes até o fim do período pago, mas a saída deles nos 60 dias seguintes é praticamente certa. Para o objetivo 4, decidam se esse grupo entra no modelo ou vai para uma regra à parte: incluir o desligamento como variável faz o modelo "acertar" o óbvio e esconde quem ainda pode ser convencido. Para o objetivo 6, eles estão na janela entre os dois avisos da loja (enunciado, lacuna 2).

## Números conferidos à mão

Contei com o leitor de CSV do Python, sem pandas, separadamente do script:
1. **Linhas:** 275.565. Bate com o dicionário.
2. **Horários em UTC (terminados em `Z`):** 186.323.
3. **Expirações:** 17.830. Bate com `assinaturas.csv`: 17.758 expiradas + 72 reembolsadas.

E a reconstrução: **14.753 ativos em 30/09/2026**, igual ao enunciado.
