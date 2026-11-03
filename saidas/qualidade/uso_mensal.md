# Qualidade: `uso_mensal.csv`

Uma linha por pessoa e mês (resumo do BI) · 591.662 linhas · 8 colunas · de jan/2025 a set/2026 · avaliado em 03/11/2026 com a skill `qualidade-dados` · medidas em [uso_mensal_evidencias.md](uso_mensal_evidencias.md)

## Resumo

Cada linha, isolada, é coerente:
- treinos ao ar livre + vídeo = total;
- nenhum minuto sem treino;
- nenhum dia ativo além dos dias do mês;
- nenhuma média acima de 6 horas por dia ativo.

O problema está no conjunto. **O arquivo mudou de regra na virada de 2025 para 2026**, e **em 2026 discorda do detalhe dos treinos** (`atividades.parquet`). Sem tratar isso, qualquer comparação entre 2025 e 2026 mede a mudança do sistema, e não a mudança do comportamento. É justamente o que o objetivo 2 pede para explicar: por que o churn subiu em 2026.

Os números do slide 35 da Aula 2 foram reproduzidos:
- dez/2025: 13.624 linhas;
- jan/2026: 41.130 linhas, 25.697 com zero minuto;
- a média cai de 265 para 118 minutos, e é de 314 contando só quem treinou.

**Situação em 03/11/2026:** os 2 problemas foram decididos (D-028 e D-029 no `DECISOES.md`), para aplicar numa cópia em `dados/processados/`. Os brutos não mudam. A limpeza ainda não foi feita.

## Problemas para decidir

| ID | Dimensão | Coluna | O que está errado | Por que importa para o case |
|---|---|---|---|---|
| Q-uso-01 | Temporalidade · Completude | arquivo inteiro | Em 2025 só aparece quem treinou no mês (0 linhas zeradas). Em 2026 aparece todo mundo, inclusive quem não treinou e quem nem é assinante (41.536 das 56.565 linhas de set/2026 são de contas não assinantes) | A média de minutos "cai" de 265 para 118 na virada do ano só por causa do registro. Comparar 2025 com 2026 assim leva a uma conclusão falsa sobre a queda de uso |
| Q-uso-02 | Consistência (entre arquivos) | `atividades`, `minutos`, `dias_ativos` | Em 2026, o resumo conta de 69% a 70% dos treinos do detalhe (set/2026: 105.373 contra 151.188). Bate em só 60% dos pares pessoa-mês, nunca conta a mais, e os minutos quase nunca coincidem. Há 2.205 pares pessoa-mês com treino no detalhe e sem linha no resumo | Duas fontes de "quanto a pessoa treinou" que discordam. Escolher sem regra muda as variáveis do modelo de churn |

### Q-uso-01 · A regra mudou na virada do ano

**Em palavras simples:** em 2025, o resumo do mês só tinha quem treinou; quem ficou parado simplesmente não aparecia. Em 2026, passou a ter uma linha para todo mundo, inclusive com zero treino, e inclusive para quem nem paga.

**Exemplo:** uma assinante que não treinou em dezembro de 2025 **não tem linha** em dezembro. A mesma pessoa, parada em janeiro de 2026, **tem linha com zero**. Quem calcular "média de minutos por pessoa" vê a média despencar de 265 para 118 em um mês, sem que ninguém tenha treinado menos.

- **Evidência:**
  - 2025: de 11.257 a 14.048 linhas por mês, 0 zeradas.
  - 2026: de 41.130 a 56.565 linhas por mês, de 25.697 a 40.880 zeradas.
  - Assinantes ativos sem linha: dez/2025, 2.401 (13.812 ativos, 11.411 com linha). Mesmo em 2026 faltam alguns: 346 em jan e 409 em set.
  - Linhas de não assinantes: cerca de 2.200 por mês em 2025, de pessoas que treinaram no plano grátis. Em 2026, de 26.825 a 41.536 por mês.
  - Contando só quem treinou, a média de 2026 (249 a 298 min) é parecida com a de 2025 (240 a 307).
- **Opções:**
  - **Corrigir:** montar uma base mensal padronizada com **uma linha por assinante ativo em cada mês** (situação pelos eventos, D-012). Quem não tem linha no mês recebe zero. As linhas de não assinantes ficam numa marcação à parte (`assinante_no_mes = não`). Efeito: os meses ficam com o tamanho da base ativa (de cerca de 8,5 mil em jan/2025 a 15,4 mil em set/2026); 2025 ganha cerca de 2.400 linhas zeradas por mês; nenhuma linha do original é perdida.
  - **Remover:** tirar as linhas zeradas de 2026, para ficar igual a 2025. Efeito: −303.735 linhas. Joga fora a informação mais valiosa para churn: o assinante que parou de treinar.
  - **Marcar:** manter como está, só marcando o ano da regra. Efeito: 0 linhas; toda comparação entre anos continua errada sem um filtro.
- **Recomendação:** **corrigir**, com a base padronizada por assinante ativo. "Assinante que não treinou no mês" é um dos sinais mais importantes para prever saída, e só a base completa o mostra igual nos dois anos.
- **Status:** decidido (D-028, 03/11/2026, Pedro Filardi)

### Q-uso-02 · O resumo e o detalhe discordam em 2026

**Em palavras simples:** para 2026, temos duas fontes de "quanto a pessoa treinou": o resumo mensal, feito pelo BI da empresa, e a lista detalhada de cada treino. Elas não batem, e o resumo sempre conta menos.

**Exemplo:** em setembro de 2026, o resumo soma 105.373 treinos; a lista detalhada tem 151.188. Para uma mesma pessoa no mesmo mês, o resumo pode dizer 2 treinos e a lista mostrar 8.

- **Evidência:**
  - O resumo conta de 69% a 70% do detalhe, todo mês, de forma estável.
  - Em 60% dos pares pessoa-mês as contagens batem; nos outros 40%, o resumo tem menos. Em 1 de cada 4 pares, ele conta no máximo 27% dos treinos do detalhe.
  - Os minutos coincidem em menos de 1% dos casos.
  - Testei 4 explicações, e nenhuma reproduz o resumo: só treinos do app; sem treinos de duração zero; sem as 9.383 duplicatas app × relógio da Aula 2; separando ar livre e vídeo.
  - Há 2.205 pares pessoa-mês com treino no detalhe e sem linha no resumo.
  - O dicionário diz que o resumo "esconde o que aconteceu dentro do mês" e indica o detalhe como a fonte para 2026.
- **Opções:**
  - **Corrigir:** recalcular o resumo de 2026 a partir do detalhe, depois da avaliação de qualidade de `atividades.parquet` (duplicatas, fuso, distâncias). Efeito: 0 linhas perdidas; os valores de 2026 passam a vir do detalhe.
  - **Remover:** descartar o resumo de 2026. Efeito: perde `sessoes_app`, que só existe no resumo.
  - **Marcar:** manter as duas fontes com uma regra de uso:
    - **treinos, minutos e dias de 2026 vêm do detalhe**, depois de avaliado;
    - **o resumo vale para 2025 e para `sessoes_app`**;
    - nunca comparar números de fontes diferentes como se fossem a mesma medida.

    Efeito: 0 linhas; 1 coluna `fonte` (`resumo` ou `detalhe`).
- **Recomendação:** **marcar, com a regra de uso**. A recontagem do resumo pelo detalhe só faz sentido depois da avaliação do `atividades.parquet`, que é o próximo arquivo. Fica também uma **pergunta para o professor**: a diferença é proposital no case, uma métrica do BI com definição desconhecida? A resposta muda qual fonte é a "verdade" para 2025.
- **Status:** decidido (D-029, 03/11/2026, Pedro Filardi)

## Já decidido

- **D-002 (corte):** 0 meses depois de set/2026 neste arquivo.
- **D-012:** a situação de assinante em cada mês sai dos eventos. É a base da correção proposta em Q-uso-01.
- **D-013:** as 60 contas internas não têm linha neste arquivo.

## O que não é problema

- **Chave:** 0 repetições de pessoa e mês.
- **Somas internas:** ar livre + vídeo = total em 100% das linhas; 0 linhas com minutos sem treino ou treino sem minutos; 0 com dias ativos acima do total de treinos ou dos dias do mês; 0 com treino e nenhuma abertura do app.
- **Valores extremos:** o maior total é de 8.228 minutos em 30 dias ativos (cerca de 4,6 horas por dia). Nenhuma linha passa de 6 horas por dia ativo, e nenhum treino passa de 222 minutos em média. Alto, mas possível.
- **Fora do arquivo (vai para a avaliação de `atividades.parquet`):** os 34 treinos do detalhe em "01/10/2026" são todos do Garmin, entre 00h e 01h. É o fuso UTC: em Brasília, são de 30/09.

## Números conferidos à mão

Contei com o leitor de CSV do Python, sem pandas:
1. **Linhas:** 591.662. Bate com o dicionário.
2. **Jan/2026 com minutos = 0:** 25.697. Bate com a Aula 2, slide 35.
3. **Pares app × relógio no detalhe, com a regra da aula:** 9.383. Bate com a Aula 2, slide 34.
