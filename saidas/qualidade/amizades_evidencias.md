# Evidências de qualidade: `amizades.csv`

Gerado por `src/qualidade.py` em 03/11/2026 20:23. Só mede: nenhuma linha foi alterada. Tabela · uma linha por relação de seguir · 113.480 linhas · 3 colunas.

Valores só aparecem quando se repetem pelo menos 5 vezes; colunas pessoais aparecem só em números.

## 1. Completude

Quanto falta em cada coluna. "Disfarçado" é campo preenchido que não diz nada (`nada`, `x`, `.`, emoji, `nao sei`).

| Coluna | Opcional no dicionário | Nulos | Só espaços | Disfarçados | Vazio real | % vazio real | Disfarçados mais comuns |
|---|---|---|---|---|---|---|---|
| `seguidor_id` | não | 0 | 0 | 0 | 0 | 0,0% | — |
| `seguido_id` | não | 0 | 0 | 0 | 0 | 0,0% | — |
| `desde` | não | 0 | 0 | 0 | 0 | 0,0% | — |

## 2. Validade

Valores que não podem ser reais ou que estão fora do que o dicionário permite.

| Coluna | Regra | Resultado | Exemplos |
|---|---|---|---|
| `desde` | data válida e plausível | 0 não viram data; 0 antes do lançamento (01/09/2020); 273 depois do corte (30/09/2026) | de 05/09/2020 a 09/10/2026 |

## 3. Consistência

A mesma informação registrada de formas diferentes, dentro do arquivo ou entre arquivos.

Nenhuma variação encontrada.

## 4. Unicidade

Registros que aparecem mais de uma vez.

| Checagem | Resultado |
|---|---|
| linha inteira | 0 linhas repetidas |

## 5. Temporalidade

Coluna de referência: `desde`, de 05/09/2020 a 09/10/2026 (dicionário: 01/09/2020 a 30/09/2026); 273 registros depois do corte. Abaixo, o volume e a falta de cada coluna por ano: uma mudança brusca de um ano para o outro indica que a forma de registrar mudou.

| Ano | Linhas | Formato de data |
|---|---|---|
| 2020 | 337 | `9999-99-99` |
| 2021 | 2.596 | `9999-99-99` |
| 2022 | 2.430 | `9999-99-99` |
| 2023 | 2.745 | `9999-99-99` |
| 2024 | 16.446 | `9999-99-99` |
| 2025 | 48.415 | `9999-99-99` |
| 2026 | 40.511 | `9999-99-99` |
