# Qualidade: `pagamentos.csv`

Uma linha por tentativa de cobrança · 165.548 linhas · 7 colunas · de 02/07/2024 a 30/09/2026 · avaliado em 03/11/2026 com a skill `qualidade-dados` · medidas em [pagamentos_evidencias.md](pagamentos_evidencias.md)

## Resumo

Com quatro correções, o arquivo **reproduz centavo por centavo o faturamento de setembro/2026 calculado na Aula 2** (slide 9) e **bate 100% com os eventos de cobrança**: cada uma das 159.989 cobranças aprovadas tem o seu evento `assinatura_iniciada` ou `renovacao` no mesmo dia, e vice-versa.

| Passo (setembro/2026) | Nossa conta | Aula 2 |
|---|---:|---:|
| Tudo, como está no arquivo | R$ 509.587,50 | R$ 509.588 |
| Só cobranças aprovadas | R$ 499.503,30 | R$ 499.503 |
| Com o horário convertido para Brasília | R$ 499.402,40 | R$ 499.402 |
| Sem as cobranças repetidas | R$ 492.571,70 | R$ 492.572 |
| Líquido (sem as taxas de loja, cartão e Pix) | R$ 436.442,35 | R$ 436.442 |

Os problemas para decidir são estes:
1. **1.941 cobranças repetidas.**
2. **Valores escritos em dois formatos.**
3. **O fuso horário.**
4. A coluna `tentativa`, que **não significa o que o dicionário diz**.

**Situação em 03/11/2026:** os 4 problemas foram decididos (D-024 a D-027 no `DECISOES.md`), todos para aplicar numa cópia em `dados/processados/`. Os brutos não mudam. A limpeza ainda não foi feita.

## Problemas para decidir

| ID | Dimensão | Coluna | O que está errado | Por que importa para o case |
|---|---|---|---|---|
| Q-pag-01 | Unicidade | linha inteira | 1.941 cobranças aprovadas repetidas: mesma conta, mesmo instante, mesmo valor (1.807 contas) | Inflam o faturamento: R$ 6.830 a mais só em setembro/2026. Toda conta de receita do objetivo 7 sairia errada |
| Q-pag-02 | Consistência | `valor` | 19.750 valores escritos como texto (`R$ 34,90`) em vez de número (`34.90`), todos do site (cartão e Pix) em 2024 e 2025 | Sem converter, a soma ignora ou quebra nessas linhas |
| Q-pag-03 | Temporalidade | `data_hora` | Lojas em UTC (`...Z`, 112.126 linhas) e site em Brasília (53.422) | Cobranças perto da meia-noite do último dia caem no mês errado: R$ 101 a mais em setembro |
| Q-pag-04 | Validade | `tentativa` | Das 4.866 cobranças marcadas `tentativa = 2`, só 54 vêm depois de uma recusa. As outras são a mensalidade normal do mês seguinte (3.888) ou a primeira cobrança da conta (924) | Quem usar a coluna para medir "cobrança recusada e recuperada" vai achar 4.866 casos, quando são 54 |

### Q-pag-01 · Cobranças repetidas

**Em palavras simples:** 1.941 cobranças aparecem duas vezes no arquivo, com a mesma pessoa, o mesmo valor e o mesmo segundo.

**Exemplo (ilustrativo):** uma assinante mensal aparece pagando R$ 39,90 num instante, por exemplo às 10:15:32, e de novo R$ 39,90 exatamente no mesmo segundo.

- **Evidência:**
  - 1.941 repetições em 1.807 contas, em todos os meios de pagamento (App Store 663, Google Play 639, cartão 384, Pix 255) e em todos os anos.
  - Três provas de que é **registro duplicado, e não cobrança real em dobro**:
    1. Sem as repetições, as cobranças aprovadas (159.989) batem uma a uma com os eventos de cobrança (159.989).
    2. O resultado reproduz o número da Aula 2 (R$ 492.572 em setembro).
    3. Quem aparece "cobrado em dobro" não reclamou mais no suporte: 0,5% falam em "cobrança dupla", igual aos demais pagantes. Também não saiu muito mais: 55,7% contra 53,4%.
- **Opções:**
  - **Corrigir:** não há valor a corrigir; a linha repetida é cópia exata.
  - **Remover:** manter só a primeira de cada repetição na cópia processada. Efeito: 165.548 → 163.607 linhas; aprovadas de 161.930 para 159.989; setembro/2026 de R$ 499.402 para R$ 492.572.
  - **Marcar:** criar `cobranca_repetida` e excluir as marcadas de toda soma. Efeito: 0 linhas; toda conta precisa lembrar do filtro.
- **Recomendação:** **remover**. São cópias exatas, há prova de que não são cobranças reais, e deixá-las no arquivo é convidar alguém a somar errado.
- **Status:** decidido (D-024, 03/11/2026, Pedro Filardi)

### Q-pag-02 · Valor escrito como texto

**Em palavras simples:** o site gravou parte dos valores como texto, com "R$" e vírgula.

**Exemplo:** a mesma mensalidade aparece como `34.90` (número) e como `R$ 34,90` (texto). Para o computador, `R$ 34,90` não é um número e não entra na soma.

- **Evidência:**
  - 19.750 linhas com `R$`: cartão 13.044 e Pix 6.706. Por ano: 8.415 em 2024 e 11.335 em 2025.
  - Nenhuma em 2026: o site mudou o formato na virada do ano.
  - As lojas sempre gravaram como número.
- **Opções:**
  - **Corrigir:** tirar o `R$`, trocar a vírgula por ponto e guardar como número. Efeito: 0 linhas; 19.750 valores convertidos.
  - **Remover:** tirar essas linhas. Efeito: −19.750 cobranças (−11,9%) e toda a receita do site em 2024 e 2025.
  - **Marcar:** não resolve; o valor continua sem somar.
- **Recomendação:** **corrigir**. O valor certo é óbvio, e não há ambiguidade.
- **Status:** decidido (D-025, 03/11/2026, Pedro Filardi)

### Q-pag-03 · Fuso horário

**Em palavras simples:** é o mesmo caso dos eventos (D-009). As lojas anotam no horário de Londres (UTC), 3 horas à frente; o site anota no horário de Brasília.

**Exemplo:** uma renovação pela Google Play às 22h de 30/09 (Brasília) fica gravada como 01h de 01/10 e vai para o faturamento de outubro.

- **Evidência:**
  - App Store e Google Play: 100% em UTC. Cartão e Pix: 100% em Brasília.
  - Convertendo, setembro/2026 passa de R$ 499.503 para R$ 499.402, igual à Aula 2.
  - Com a conversão, as cobranças batem com os eventos no mesmo dia em 100% dos casos.
- **Opções:**
  - **Corrigir:** converter UTC para Brasília e guardar o original em `data_hora_original`. Efeito: 0 linhas; 112.126 horários convertidos.
  - **Remover:** não se aplica.
  - **Marcar:** não resolve as contagens por mês.
- **Recomendação:** **corrigir**, com a mesma regra da D-009.
- **Status:** decidido (D-026, 03/11/2026, Pedro Filardi)

### Q-pag-04 · A coluna "tentativa" engana

**Em palavras simples:** o dicionário diz que `tentativa = 2` é uma nova tentativa depois de o cartão ser recusado. Na prática, quase nunca é.

**Exemplo:** uma assinante mensal paga normalmente em agosto (`tentativa = 1`) e, 30 dias depois, paga setembro normalmente, mas a linha vem marcada `tentativa = 2`. Não houve nenhuma recusa no meio.

- **Evidência:**
  - Das 4.866 linhas com `tentativa = 2`, todas aprovadas:
    - 3.888 vêm 30 dias depois de uma cobrança aprovada (mediana de 720 horas);
    - 924 são a primeira cobrança da conta;
    - só 54 vêm depois de uma recusa, cerca de 4 dias depois.
  - Das 3.250 recusas, 54 foram recuperadas em nova tentativa. Outras 1.346 abriram período de carência no mesmo dia (`periodo_carencia` nos eventos), e as 1.321 que não se recuperaram viraram saída por falha de pagamento.
- **Opções:**
  - **Corrigir:** recalcular. É criada a coluna `retentativa_real` (sim quando a cobrança vem depois de uma recusa da mesma conta), e `tentativa` não é usada. Efeito: 0 linhas; 54 marcadas como retentativa real.
  - **Remover:** tirar a coluna `tentativa`. Efeito: perde-se a informação, mesmo ruim, sem pôr nada no lugar.
  - **Marcar:** manter e avisar no nome (`tentativa_nao_confiavel`). Efeito: 0 linhas; alguém ainda pode usar.
- **Recomendação:** **corrigir**. Criar `retentativa_real` e deixar a `tentativa` original fora da base processada.
- **Status:** decidido (D-027, 03/11/2026, Pedro Filardi)

## Já decidido

- **D-002 (corte):** 0 cobranças depois de 30/09/2026.
- **D-009:** a mesma regra de fuso dos eventos (Q-pag-03 a aplica a este arquivo).
- **D-013:** as 60 contas internas não têm nenhuma cobrança neste arquivo.

## O que não é problema

- **Domínios:** 0 valores fora das listas do dicionário em `metodo` e `status`.
- **Chave:** 165.548 `pagamento_id` distintos.
- **Valores negativos:** os 368 aparecem só em `estornado` (72, sempre −299,90) e `chargeback` (296). É a convenção de devolução. Batem com os 72 reembolsos e 296 chargebacks dos eventos.
- **Preços:** a mensalidade é R$ 34,90 até 28/02/2026 e R$ 39,90 depois. Há 16 cobranças de R$ 34,90 depois do reajuste, um caso raro que não muda nenhuma conta. O anual é R$ 299,90, e R$ 239,90 com cupom de influenciador.
- **Recusas sem carência:** 1.904 recusas não abriram carência no mesmo dia. O que aconteceu depois com elas não foi medido nesta avaliação. Fica como pergunta para a análise de churn involuntário, não como problema de registro.

## Números conferidos à mão

Contei com o leitor de CSV do Python, sem pandas:
1. **Linhas:** 165.548. Bate com o dicionário.
2. **Valores com `R$`:** 19.750.
3. **Recusadas:** 3.250.

E os cinco números de setembro/2026 da Aula 2, todos reproduzidos (tabela no resumo).
