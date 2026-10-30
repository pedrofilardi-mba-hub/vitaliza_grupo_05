# Evidências de qualidade: `assinaturas.csv`

Gerado por `src/qualidade.py` em 29/10/2026 23:29. Só mede: nenhuma linha foi alterada. Tabela · uma linha por assinatura · 32.643 linhas · 9 colunas.

Valores só aparecem quando se repetem pelo menos 5 vezes; colunas pessoais aparecem só em números.

## 1. Completude

Quanto falta em cada coluna. "Disfarçado" é campo preenchido que não diz nada (`nada`, `x`, `.`, emoji, `nao sei`).

| Coluna | Opcional no dicionário | Nulos | Só espaços | Disfarçados | Vazio real | % vazio real | Disfarçados mais comuns |
|---|---|---|---|---|---|---|---|
| `data_fim` | sim | 14.813 | 0 | 0 | 14.813 | 45,4% | — |
| `motivo_fim` | sim | 14.813 | 0 | 0 | 14.813 | 45,4% | — |
| `assinatura_id` | não | 0 | 0 | 0 | 0 | 0,0% | — |
| `user_id` | não | 0 | 0 | 0 | 0 | 0,0% | — |
| `plano_atual` | não | 0 | 0 | 0 | 0 | 0,0% | — |
| `canal_cobranca` | não | 0 | 0 | 0 | 0 | 0,0% | — |
| `inicio` | não | 0 | 0 | 0 | 0 | 0,0% | — |
| `status_atual` | não | 0 | 0 | 0 | 0 | 0,0% | — |
| `renovacao_automatica` | não | 0 | 0 | 0 | 0 | 0,0% | — |

## 2. Validade

Valores que não podem ser reais ou que estão fora do que o dicionário permite.

| Coluna | Regra | Resultado | Exemplos |
|---|---|---|---|
| `plano_atual` | domínio do dicionário | 60 fora de {mensal, anual} | `cortesia` (60) |
| `canal_cobranca` | domínio do dicionário | 60 fora de {app_store, google_play, web_cartao, web_pix} | `interno` (60) |
| `inicio` | data válida e plausível | 0 não viram data; 0 antes do lançamento (01/09/2020); 0 depois do corte (30/09/2026) | de 08/09/2020 a 30/09/2026 |
| `data_fim` | data válida e plausível | 0 não viram data; 0 antes do lançamento (01/09/2020); 0 depois do corte (30/09/2026) | de 07/07/2024 a 30/09/2026 |

## 3. Consistência

A mesma informação registrada de formas diferentes, dentro do arquivo ou entre arquivos.

Nenhuma variação encontrada.

## 4. Unicidade

Registros que aparecem mais de uma vez.

| Checagem | Resultado |
|---|---|
| linha inteira | 0 linhas repetidas |
| chave `assinatura_id` | 0 repetições |

## 5. Temporalidade

Coluna de referência: `inicio`, de 08/09/2020 a 30/09/2026 (dicionário: 01/09/2020 a 30/09/2026); 0 registros depois do corte. Abaixo, o volume e a falta de cada coluna por ano: uma mudança brusca de um ano para o outro indica que a forma de registrar mudou.

| Ano | Linhas | Formato de data | vazio `data_fim` | vazio `motivo_fim` |
|---|---|---|---|---|
| 2020 | 407 | `9999-99-99` | 46,4% | 46,4% |
| 2021 | 1.366 | `9999-99-99` | 34,3% | 34,3% |
| 2022 | 1.308 | `9999-99-99` | 24,4% | 24,4% |
| 2023 | 1.429 | `9999-99-99` | 23,2% | 23,2% |
| 2024 | 5.828 | `9999-99-99` | 23,4% | 23,4% |
| 2025 | 12.293 | `9999-99-99` | 37,3% | 37,3% |
| 2026 | 10.012 | `9999-99-99` | 75,5% | 75,5% |
