# Evidências de qualidade: `feed_posts.csv`

Gerado por `src/qualidade.py` em 03/11/2026 20:32. Só mede: nenhuma linha foi alterada. Texto · uma linha por post · 119.309 linhas · 5 colunas.

Valores só aparecem quando se repetem pelo menos 5 vezes; colunas pessoais aparecem só em números.

## 1. Completude

Quanto falta em cada coluna. "Disfarçado" é campo preenchido que não diz nada (`nada`, `x`, `.`, emoji, `nao sei`).

| Coluna | Opcional no dicionário | Nulos | Só espaços | Disfarçados | Vazio real | % vazio real | Disfarçados mais comuns |
|---|---|---|---|---|---|---|---|
| `post_id` | não | 0 | 0 | 0 | 0 | 0,0% | — |
| `user_id` | não | 0 | 0 | 0 | 0 | 0,0% | — |
| `data_hora` | não | 0 | 0 | 0 | 0 | 0,0% | — |
| `texto` | não | 0 | 0 | 0 | 0 | 0,0% | — |
| `curtidas` | não | 0 | 0 | 0 | 0 | 0,0% | — |

## 2. Validade

Valores que não podem ser reais ou que estão fora do que o dicionário permite.

| Coluna | Regra | Resultado | Exemplos |
|---|---|---|---|
| `curtidas` | faixa numérica | mín 0 · p1 1 · mediana 6 · p99 24 · máx 38; 0 negativos, 258 zeros, 3.236 acima de Q3 + 3·IQR (20) | — |
| `data_hora` | data válida e plausível | 0 não viram data; 0 antes do lançamento (01/09/2020); 122 depois do corte (30/09/2026) | de 01/07/2025 a 07/10/2026 |

## 3. Consistência

A mesma informação registrada de formas diferentes, dentro do arquivo ou entre arquivos.

| Coluna | Checagem | Resultado | Exemplos |
|---|---|---|---|
| `texto` | mesma coisa escrita de jeitos diferentes (ignorando maiúsculas, acentos, espaços, pontuação e emoji) | 31.620 valores distintos viram 11.637 depois de normalizar; 51.146 linhas (42,9%) usam uma grafia diferente da mais comum | `yoga pra fechar o dia` (3.982) = `yoga pra fechar o dia 😂` (111) = `yoga pra fechar o dia ✨` (105) e mais 329 grafias; `funcional em casa` (4.083) = `funcional em casa 🧘` (112) = `funcional em casa 🏃` (109) e mais 296 grafias; `treino de força feito` (3.389) = `treino de forca feito` (638) = `treino de força feito 💪` (91) e mais 423 grafias |

## 4. Unicidade

Registros que aparecem mais de uma vez.

| Checagem | Resultado |
|---|---|
| linha inteira | 0 linhas repetidas |
| chave `post_id` | 0 repetições |
| texto livre `texto` | 31.597 textos distintos em 119.309; os 20 mais comuns cobrem 32,7% |

## 5. Temporalidade

Coluna de referência: `data_hora`, de 01/07/2025 a 07/10/2026 (dicionário: 01/07/2025 a 30/09/2026); 122 registros depois do corte. Abaixo, o volume e a falta de cada coluna por ano: uma mudança brusca de um ano para o outro indica que a forma de registrar mudou.

| Ano | Linhas | Formato de data |
|---|---|---|
| 2025 | 45.045 | `9999-99-99 99:99:99` |
| 2026 | 74.264 | `9999-99-99 99:99:99` |
