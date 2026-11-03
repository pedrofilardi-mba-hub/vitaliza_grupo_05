# Evidências de qualidade: `atividades.parquet`

Gerado por `src/qualidade.py` em 03/11/2026 20:04. Só mede: nenhuma linha foi alterada. Log de eventos · uma linha por treino · 1.254.475 linhas · 11 colunas.

Valores só aparecem quando se repetem pelo menos 5 vezes; colunas pessoais aparecem só em números.

## 1. Completude

Quanto falta em cada coluna. "Disfarçado" é campo preenchido que não diz nada (`nada`, `x`, `.`, emoji, `nao sei`).

| Coluna | Opcional no dicionário | Nulos | Só espaços | Disfarçados | Vazio real | % vazio real | Disfarçados mais comuns |
|---|---|---|---|---|---|---|---|
| `treino_com` | sim | 0 | 1.240.338 | 0 | 1.240.338 | 98,9% | — |
| `fc_media` | sim | 764.987 | 0 | 0 | 764.987 | 61,0% | — |
| `ritmo_min_km` | sim | 582.290 | 0 | 0 | 582.290 | 46,4% | — |
| `distancia_km` | sim | 574.835 | 0 | 0 | 574.835 | 45,8% | — |
| `atividade_id` | não | 0 | 0 | 0 | 0 | 0,0% | — |
| `user_id` | não | 0 | 0 | 0 | 0 | 0,0% | — |
| `inicio` | não | 0 | 0 | 0 | 0 | 0,0% | — |
| `tipo` | não | 0 | 0 | 0 | 0 | 0,0% | — |
| `duracao_min` | não | 0 | 0 | 0 | 0 | 0,0% | — |
| `origem` | não | 0 | 0 | 0 | 0 | 0,0% | — |
| `gps_ok` | não | 0 | 0 | 0 | 0 | 0,0% | — |

## 2. Validade

Valores que não podem ser reais ou que estão fora do que o dicionário permite.

| Coluna | Regra | Resultado | Exemplos |
|---|---|---|---|
| `origem` | domínio do dicionário | 0 fora de {app, garmin, apple_health} | — |
| `duracao_min` | faixa numérica | mín 0 · p1 17.9 · mediana 41.4 · p99 130.1 · máx 543.9; 0 negativos, 3.649 zeros, 14.966 acima de Q3 + 3·IQR (123.3) | — |
| `distancia_km` | faixa numérica | mín 0 · p1 1.64 · mediana 6.47 · p99 57.6361 · máx 10012.8; 0 negativos, 23 zeros, 51.650 acima de Q3 + 3·IQR (24.58) | — |
| `ritmo_min_km` | faixa numérica | mín 1.8 · p1 2.1 · mediana 6.43 · p99 12.89 · máx 13; 0 negativos, 0 zeros, 0 acima de Q3 + 3·IQR (24.34) | — |
| `fc_media` | faixa numérica | mín 61 · p1 87 · mediana 133 · p99 171 · máx 195; 0 negativos, 0 zeros, 0 acima de Q3 + 3·IQR (266) | — |
| `inicio` | data válida e plausível | 0 não viram data; 0 antes do lançamento (01/09/2020); 34 depois do corte (30/09/2026) | de 01/01/2026 a 01/10/2026 |

## 3. Consistência

A mesma informação registrada de formas diferentes, dentro do arquivo ou entre arquivos.

Nenhuma variação encontrada.

## 4. Unicidade

Registros que aparecem mais de uma vez.

| Checagem | Resultado |
|---|---|
| linha inteira | 0 linhas repetidas |
| chave `atividade_id` | 0 repetições |

## 5. Temporalidade

Coluna de referência: `inicio`, de 01/01/2026 a 01/10/2026 (dicionário: 01/01/2026 a 30/09/2026); 34 registros depois do corte. Abaixo, o volume e a falta de cada coluna por ano: uma mudança brusca de um ano para o outro indica que a forma de registrar mudou.

| Ano | Linhas | Formato de data | vazio `distancia_km` | vazio `ritmo_min_km` | vazio `fc_media` | vazio `treino_com` |
|---|---|---|---|---|---|---|
| 2026 | 1.254.475 | `9999-99-99 99:99:99` | 45,8% | 46,4% | 61,0% | 98,9% |
