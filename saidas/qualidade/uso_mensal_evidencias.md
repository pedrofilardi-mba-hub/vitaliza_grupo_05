# Evidências de qualidade: `uso_mensal.csv`

Gerado por `src/qualidade.py` em 03/11/2026 19:54. Só mede: nenhuma linha foi alterada. Log de eventos · uma linha por usuário e mês · 591.662 linhas · 8 colunas.

Valores só aparecem quando se repetem pelo menos 5 vezes; colunas pessoais aparecem só em números.

## 1. Completude

Quanto falta em cada coluna. "Disfarçado" é campo preenchido que não diz nada (`nada`, `x`, `.`, emoji, `nao sei`).

| Coluna | Opcional no dicionário | Nulos | Só espaços | Disfarçados | Vazio real | % vazio real | Disfarçados mais comuns |
|---|---|---|---|---|---|---|---|
| `user_id` | não | 0 | 0 | 0 | 0 | 0,0% | — |
| `mes` | não | 0 | 0 | 0 | 0 | 0,0% | — |
| `atividades` | não | 0 | 0 | 0 | 0 | 0,0% | — |
| `atividades_ar_livre` | não | 0 | 0 | 0 | 0 | 0,0% | — |
| `atividades_video` | não | 0 | 0 | 0 | 0 | 0,0% | — |
| `minutos` | não | 0 | 0 | 0 | 0 | 0,0% | — |
| `dias_ativos` | não | 0 | 0 | 0 | 0 | 0,0% | — |
| `sessoes_app` | não | 0 | 0 | 0 | 0 | 0,0% | — |

## 2. Validade

Valores que não podem ser reais ou que estão fora do que o dicionário permite.

| Coluna | Regra | Resultado | Exemplos |
|---|---|---|---|
| `atividades` | faixa numérica | mín 0 · p1 0 · mediana 0 · p99 24 · máx 68; 0 negativos, 303.735 zeros, 23.288 acima de Q3 + 3·IQR (16) | — |
| `atividades_ar_livre` | faixa numérica | mín 0 · p1 0 · mediana 0 · p99 17 · máx 53; 0 negativos, 364.609 zeros, 36.970 acima de Q3 + 3·IQR (8) | — |
| `atividades_video` | faixa numérica | mín 0 · p1 0 · mediana 0 · p99 17 · máx 57; 0 negativos, 370.123 zeros, 27.777 acima de Q3 + 3·IQR (8) | — |
| `minutos` | faixa numérica | mín 0 · p1 0 · mediana 0 · p99 1223 · máx 8228; 0 negativos, 303.735 zeros, 34.132 acima de Q3 + 3·IQR (624) | — |
| `dias_ativos` | faixa numérica | mín 0 · p1 0 · mediana 0 · p99 17 · máx 30; 0 negativos, 303.735 zeros, 7.843 acima de Q3 + 3·IQR (16) | — |
| `sessoes_app` | faixa numérica | mín 0 · p1 0 · mediana 2 · p99 50 · máx 153; 0 negativos, 41.493 zeros, 23.038 acima de Q3 + 3·IQR (33) | — |
| `mes` | data válida e plausível | 0 não viram data; 0 antes do lançamento (01/09/2020); 0 depois do corte (30/09/2026) | de 01/01/2025 a 01/09/2026 |

## 3. Consistência

A mesma informação registrada de formas diferentes, dentro do arquivo ou entre arquivos.

Nenhuma variação encontrada.

## 4. Unicidade

Registros que aparecem mais de uma vez.

| Checagem | Resultado |
|---|---|
| linha inteira | 0 linhas repetidas |
| chave `user_id+mes` | 0 repetições |

## 5. Temporalidade

Coluna de referência: `mes`, de 01/01/2025 a 01/09/2026 (dicionário: 01/01/2025 a 30/09/2026); 0 registros depois do corte. Abaixo, o volume e a falta de cada coluna por ano: uma mudança brusca de um ano para o outro indica que a forma de registrar mudou.

| Ano | Linhas | Formato de data |
|---|---|---|
| 2025 | 152.230 | `9999-99` |
| 2026 | 439.432 | `9999-99` |
