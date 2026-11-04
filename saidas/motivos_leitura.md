# Por que desligam a renovação: o que aprendemos

03/11/2026 · Leitura dos resultados de `src/motivos.py`. As tabelas completas estão em [motivos_desligamento.md](motivos_desligamento.md).

## O que fizemos

Pegamos as **6.624 pessoas** que, pagando, desligaram a renovação ou cancelaram pelo site entre março e setembro de 2026. Para cada uma, escolhemos um **"gêmeo"**: alguém com o mesmo plano e o mesmo tempo de casa, ativo no mesmo dia, que **não** desligou. Comparar os dois mostra o que é diferente em quem desliga, e não o que é comum a todo assinante.

## 1. As pessoas param de treinar antes de desligar

Treinos por semana, nas 8 semanas antes do desligamento:

| Semana antes | 8ª | 7ª | 6ª | 5ª | 4ª | 3ª | 2ª | 1ª |
|---|---:|---:|---:|---:|---:|---:|---:|---:|
| Quem desligou | 2,4 | 2,5 | 2,5 | 2,3 | 2,2 | 2,0 | 1,6 | **1,0** |
| Gêmeo | 2,2 | 2,2 | 2,3 | 2,3 | 2,3 | 2,4 | 2,5 | 2,5 |

Quem vai desligar treinava **igual ou até mais** que o gêmeo dois meses antes. A queda começa umas **4 semanas antes** e se acentua nas duas últimas. Quem teve os treinos **cortados pela metade** aparece **3,4 vezes mais** entre os que desligaram.

👉 **Para a ação:** existe uma janela de umas 3 a 4 semanas em que dá para perceber a queda e agir **antes** da decisão.

## 2. "Objetivo cumprido" existe, e dá para ver nos posts

- **Post de prova concluída** ("completei minha meia maratona!! chorei na chegada", "medalha no peito") no mês anterior é **7,9 vezes mais comum** entre quem desliga (9,1% contra 1,2%).
- O **objetivo declarado na entrada** também conta:

| Objetivo no onboarding | Entre quem desligou | Entre os gêmeos |
|---|---:|---:|
| Treinar para uma prova com prazo | 8,2% | 4,6% |
| Desempenho (melhorar o pace, os 10k) | 9,9% | 6,9% |
| Estética (perder peso, secar a barriga) | 15,2% | 10,5% |
| Saúde (colesterol, dor nas costas, pressão) | 13,1% | 18,3% |
| Bem-estar (dormir, ansiedade, momento só meu) | 6,7% | 11,3% |

Quem entrou por **meta com prazo ou aparência** sai mais. Quem entrou por **saúde ou bem-estar** fica mais. É a "lente da necessidade" da Aula 3 aparecendo nos dados.

## 3. Preço, cobrança e suporte quase não aparecem

Comparando pessoas com o **mesmo tempo de casa**:
- **Pagar o preço antigo (R$ 34,90) e sofrer o reajuste:** 45,4% entre quem desligou e 44,9% entre os gêmeos, **nenhuma diferença**. A hipótese de que **o reajuste de março explica a saída perde força** (objetivo 2).
- **Cartão recusado e chamado de cobrança:** quase iguais nos dois grupos.
- **Problema técnico** (chamado técnico ou GPS falhando): um pouco mais comum (2,2 vezes), mas em poucas pessoas.

## 4. Perfis de motivo

| Perfil | % de quem desligou |
|---|---:|
| Parou de treinar (zerou ou caiu pela metade) | 36,5% |
| Objetivo cumprido (post de prova concluída) | 9,1% |
| Problema técnico | 6,4% |
| Cobrança | 0,9% |
| **Sem sinal claro nos dados** | **47,1%** |

**Conferindo com a pesquisa de saída** (só quem cancelou pelo site e respondeu):
- O perfil **"objetivo cumprido"** bate bem: 38 dos 59 que responderam disseram exatamente isso.
- O perfil **"problema técnico"** bate em parte: 28 de 83.
- **"Parou de treinar" é o como, e não o porquê.** Entre os que responderam, a maioria disse "objetivo cumprido" (82) ou "preço" (54), e não "não uso" (32). A pessoa para de treinar **porque** atingiu a meta ou perdeu o interesse. A queda de treino é o **aviso**, e o motivo está por trás.
- Para quase metade, os dados não mostram um sinal claro. É aí que **ler os textos com IA** (objetivo 5) pode ajudar.

## 5. O novo gabarito: "vai desligar a renovação" funciona melhor

| Corte | Grupo | "Saiu nos 60 dias" | "Desligou nos 60 dias" |
|---|---|---:|---:|
| 31/05 | anuais | 1,2% | **11,5%** |
| 31/07 | anuais | 1,6% | **10,3%** |
| 31/05 | mensais | 16,6% | 18,5% |

- **Para os anuais, muda tudo.** Com o gabarito antigo, quase nenhum anual "sai" em 60 dias, e o modelo os ignoraria. Mas **1 em cada 10 anuais desliga a renovação** nesse período, meses antes de sair. Com o gabarito novo, eles entram no radar **enquanto ainda dá para agir**.
- **Para os mensais, quase não muda**, porque desligar e sair acontecem no mesmo mês.
- Com o gabarito novo, o que mais separa é o **uso recente**: dias desde o último treino, semanas ativas, treinos nas últimas 4 semanas (AUC de 0,60 a 0,63 em 31/07). Sozinhas, essas dimensões são fracas; o modelo precisará combiná-las.

## O que propomos

1. **Decidido (D-053):** o gabarito do modelo passa a ser *"desligou a renovação (ou cancelou pelo site) nos próximos 60 dias"*. Ele avisa **antes** da decisão e inclui os anuais.
2. **Usar os perfis para escolher a mensagem** (objetivo 6):
   - **parou de treinar** → convite para desafio ou plano personalizado, na janela de queda;
   - **objetivo cumprido** → **nova meta** (a próxima prova), e não desconto;
   - **problema técnico** → contato do suporte.
3. **Objetivo 2:** o reajuste de preço **não aparece** como causa quando se compara gente com o mesmo tempo de casa. A explicação da subida de 2026 deve estar em outro lugar, como o perfil de quem entrou ou as metas com prazo.
4. **Objetivo 5:** ler textos (onboarding, posts, chamados) com IA, para reduzir os 47% "sem sinal claro".

*Os perfis usam palavras-chave e são provisórios. A leitura com IA e a conferência com uma amostra feita à mão vêm no objetivo 5.*
