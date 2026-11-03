# Evidências de qualidade: `pagamentos.csv`

Gerado por `src/qualidade.py` em 03/11/2026 19:43. Só mede: nenhuma linha foi alterada. Log de eventos · uma linha por cobrança · 165.548 linhas · 7 colunas.

Valores só aparecem quando se repetem pelo menos 5 vezes; colunas pessoais aparecem só em números.

## 1. Completude

Quanto falta em cada coluna. "Disfarçado" é campo preenchido que não diz nada (`nada`, `x`, `.`, emoji, `nao sei`).

| Coluna | Opcional no dicionário | Nulos | Só espaços | Disfarçados | Vazio real | % vazio real | Disfarçados mais comuns |
|---|---|---|---|---|---|---|---|
| `pagamento_id` | não | 0 | 0 | 0 | 0 | 0,0% | — |
| `user_id` | não | 0 | 0 | 0 | 0 | 0,0% | — |
| `data_hora` | não | 0 | 0 | 0 | 0 | 0,0% | — |
| `valor` | não | 0 | 0 | 0 | 0 | 0,0% | — |
| `metodo` | não | 0 | 0 | 0 | 0 | 0,0% | — |
| `status` | não | 0 | 0 | 0 | 0 | 0,0% | — |
| `tentativa` | não | 0 | 0 | 0 | 0 | 0,0% | — |

## 2. Validade

Valores que não podem ser reais ou que estão fora do que o dicionário permite.

| Coluna | Regra | Resultado | Exemplos |
|---|---|---|---|
| `metodo` | domínio do dicionário | 0 fora de {app_store, google_play, cartao, pix_automatico} | — |
| `status` | domínio do dicionário | 0 fora de {aprovado, recusado, estornado, chargeback} | — |
| `tentativa` | faixa numérica | mín 1 · p1 1 · mediana 1 · p99 2 · máx 2; 0 negativos, 0 zeros, 4.866 acima de Q3 + 3·IQR (1) | — |
| `data_hora` | data válida e plausível | 0 não viram data; 0 antes do lançamento (01/09/2020); 0 depois do corte (30/09/2026) | de 02/07/2024 a 30/09/2026 |

## 3. Consistência

A mesma informação registrada de formas diferentes, dentro do arquivo ou entre arquivos.

| Coluna | Checagem | Resultado | Exemplos |
|---|---|---|---|
| `valor` | mesma coisa escrita de jeitos diferentes (ignorando maiúsculas, acentos, espaços, pontuação e emoji) | 9 valores distintos viram 7 depois de normalizar; 368 linhas (0,2%) usam uma grafia diferente da mais comum | `39.90` (44.632) = `-39.90` (206); `299.90` (13.732) = `-299.90` (162) |
| `data_hora` | formatos de data | 2 formatos | `9999-99-99T99:99:99Z` (112.126), `9999-99-99 99:99:99` (53.422) |

## 4. Unicidade

Registros que aparecem mais de uma vez.

| Checagem | Resultado |
|---|---|
| linha inteira | 0 linhas repetidas |
| chave `pagamento_id` | 0 repetições |

## 5. Temporalidade

Coluna de referência: `data_hora`, de 02/07/2024 a 30/09/2026; 0 registros depois do corte. Abaixo, o volume e a falta de cada coluna por ano: uma mudança brusca de um ano para o outro indica que a forma de registrar mudou.

| Ano | Linhas | Formato de data |
|---|---|---|
| 2024 | 25.732 | `9999-99-99T99:99:99Z` |
| 2025 | 75.213 | `9999-99-99T99:99:99Z` |
| 2026 | 64.603 | `9999-99-99T99:99:99Z` |
