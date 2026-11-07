# Segmentação escolhida (D-054)

Cenário escolhido: K-means com **5 variáveis de comportamento. sem o plano**. e **5 grupos**. na base ativa de 30/09/2026 (14.753 assinantes). Processo de escolha: `saidas/clusters_cenarios.md`. Código: `src/clusters.py`.

Os grupos foram formados **sem nenhuma informação de saída**. A saída histórica abaixo só descreve os grupos: a régua de 30/09 foi aplicada às mesmas variáveis montadas em 31/05/2026, e medimos quem desligou a renovação ou cancelou pelo site nos 60 dias seguintes (D-053), sem quem já tinha anunciado (D-052). Taxa da base: 14,8%.

Qualidade: silhueta 0,24, estabilidade 0,95 (outra semente e metade da base).

| Grupo | % base | Meses de casa | Treinos/sem | Min/treino | % ar livre | Seguidores | % mensal | % receita mensal | Saída 60d (31/05) | % das saídas |
|---|---|---|---|---|---|---|---|---|---|---|
| Novatos | 20,3% | 1.3 | 1.08 | 43.2 | 71,0% | 0 | 57,6% | 21,8% | 19,0% | 28,3% |
| Treino em casa | 29,8% | 11.4 | 2.0 | 41.5 | 15,0% | 2 | 43,1% | 29,9% | 10,5% | 20,0% |
| Rua no ritmo leve | 28,2% | 13.2 | 1.38 | 45.5 | 81,0% | 2 | 29,4% | 26,5% | 13,6% | 23,6% |
| Intensos | 16,0% | 9.2 | 3.85 | 45.4 | 79,0% | 1 | 49,1% | 16,5% | 17,9% | 23,2% |
| Longões | 5,7% | 9.8 | 1.46 | 83.7 | 82,0% | 1 | 32,1% | 5,4% | 15,5% | 4,9% |

## O que mais pesa na saída, dentro de cada grupo (31/05)

**Novatos** · saída 19,0%
- Chamado técnico (90 dias): 35,8% com o sinal × 18,3% sem (109 pessoas com o sinal)
- Plano mensal: 22,0% com o sinal × 14,8% sem (1548 pessoas com o sinal)
- Treino caiu forte (4 semanas): 24,9% com o sinal × 18,5% sem (193 pessoas com o sinal)

**Treino em casa** · saída 10,5%
- 14+ dias sem treinar: 19,6% com o sinal × 9,8% sem (224 pessoas com o sinal)
- Plano mensal: 13,6% com o sinal × 7,5% sem (1649 pessoas com o sinal)
- Pagava o preço antigo (reajuste): 13,7% com o sinal × 7,8% sem (1531 pessoas com o sinal)

**Rua no ritmo leve** · saída 13,6%
- Treino caiu forte (4 semanas): 22,6% com o sinal × 12,4% sem (358 pessoas com o sinal)
- Chamado técnico (90 dias): 21,2% com o sinal × 13,1% sem (193 pessoas com o sinal)
- Plano mensal: 18,2% com o sinal × 10,9% sem (1142 pessoas com o sinal)

**Intensos** · saída 17,9%
- Treino caiu forte (4 semanas): 28,3% com o sinal × 17,1% sem (180 pessoas com o sinal)
- Chamado técnico (90 dias): 24,7% com o sinal × 17,1% sem (259 pessoas com o sinal)
- Plano mensal: 21,6% com o sinal × 14,4% sem (1125 pessoas com o sinal)

**Longões** · saída 15,5%
- Nenhum seguidor: 24,4% com o sinal × 12,8% sem (127 pessoas com o sinal)
- Chamado técnico (90 dias): 25,0% com o sinal × 14,7% sem (40 pessoas com o sinal)
- Anual que renova nos 60 dias: 19,1% com o sinal × 15,2% sem (42 pessoas com o sinal)

## Limites

- Cruzamentos apontam suspeitos, não provam causa.
- A saída histórica usa a régua de 30/09 em 31/05: os grupos são os mesmos, mas cada pessoa pode ter mudado de grupo entre as datas.
- Receita mensal estimada pelo preço de tabela e pela taxa do canal (enunciado, seção 03); cupons não descontados.
- Idade, sexo e relógio não mudam entre os grupos: as personas se diferenciam pelo comportamento, não pelo perfil demográfico.
