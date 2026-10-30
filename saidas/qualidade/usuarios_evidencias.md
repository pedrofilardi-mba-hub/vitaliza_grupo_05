# Evidências de qualidade: `usuarios.csv`

Gerado por `src/qualidade.py` em 29/10/2026 23:45. Só mede: nenhuma linha foi alterada. Tabela · uma linha por conta · 64.948 linhas · 12 colunas.

Valores só aparecem quando se repetem pelo menos 5 vezes; colunas pessoais aparecem só em números.

## 1. Completude

Quanto falta em cada coluna. "Disfarçado" é campo preenchido que não diz nada (`nada`, `x`, `.`, emoji, `nao sei`).

| Coluna | Opcional no dicionário | Nulos | Só espaços | Disfarçados | Vazio real | % vazio real | Disfarçados mais comuns |
|---|---|---|---|---|---|---|---|
| `data_nascimento` | não | 3.301 | 0 | 0 | 3.301 | 5,1% | — |
| `sexo` | não | 3.142 | 0 | 0 | 3.142 | 4,8% | — |
| `cep_prefixo` | não | 1.894 | 0 | 0 | 1.894 | 2,9% | — |
| `user_id` | não | 0 | 0 | 0 | 0 | 0,0% | — |
| `email` | não | 0 | 0 | 0 | 0 | 0,0% | — |
| `data_cadastro` | não | 0 | 0 | 0 | 0 | 0,0% | — |
| `cidade` | não | 0 | 0 | 0 | 0 | 0,0% | — |
| `uf` | não | 0 | 0 | 0 | 0 | 0,0% | — |
| `canal_aquisicao` | não | 0 | 0 | 0 | 0 | 0,0% | — |
| `sistema` | não | 0 | 0 | 0 | 0 | 0,0% | — |
| `versao_app` | não | 0 | 0 | 0 | 0 | 0,0% | — |
| `relogio_conectado` | não | 0 | 0 | 0 | 0 | 0,0% | — |

Cobertura: 0 das 64.948 contas de `usuarios.csv` não têm linha neste arquivo (0,0%).

## 2. Validade

Valores que não podem ser reais ou que estão fora do que o dicionário permite.

| Coluna | Regra | Resultado | Exemplos |
|---|---|---|---|
| `data_cadastro` | data válida e plausível | 0 não viram data; 0 antes do lançamento (01/09/2020); 119 depois do corte (30/09/2026) | de 01/09/2020 a 04/04/2027 |
| `data_nascimento` | data válida e plausível | 0 não viram data; 194 no futuro; 0 com menos de 13 anos; 412 com mais de 100 anos | de 01/01/1900 a 12/05/2031 |

## 3. Consistência

A mesma informação registrada de formas diferentes, dentro do arquivo ou entre arquivos.

| Coluna | Checagem | Resultado | Exemplos |
|---|---|---|---|
| `sistema` | mesma coisa escrita de jeitos diferentes (ignorando maiúsculas, acentos, espaços, pontuação e emoji) | 5 valores distintos viram 2 depois de normalizar; 16.067 linhas (24,7%) usam uma grafia diferente da mais comum | `android` (28.027) = `Android` (7.124); `ios` (20.854) = `iOS` (7.463) = `IOS` (1.480) |

## 4. Unicidade

Registros que aparecem mais de uma vez.

| Checagem | Resultado |
|---|---|
| linha inteira | 0 linhas repetidas |
| chave `user_id` | 0 repetições |
| uma linha por conta (`user_id`) | 0 contas repetidas |

## 5. Temporalidade

Coluna de referência: `data_cadastro`, de 01/09/2020 a 04/04/2027 (dicionário: 01/09/2020 a 30/09/2026); 119 registros depois do corte. Abaixo, o volume e a falta de cada coluna por ano: uma mudança brusca de um ano para o outro indica que a forma de registrar mudou.

| Ano | Linhas | Formato de data | vazio `data_nascimento` | vazio `sexo` | vazio `cep_prefixo` |
|---|---|---|---|---|---|
| 2020 | 439 | `9999-99-99 99:99:99` | 4,8% | 4,1% | 3,0% |
| 2021 | 1.383 | `9999-99-99 99:99:99` | 5,4% | 4,4% | 3,1% |
| 2022 | 1.336 | `9999-99-99 99:99:99` | 4,8% | 4,8% | 2,8% |
| 2023 | 1.441 | `9999-99-99 99:99:99` | 6,2% | 4,8% | 3,3% |
| 2024 | 11.939 | `9999-99-99 99:99:99` | 5,1% | 4,8% | 2,8% |
| 2025 | 26.167 | `9999-99-99 99:99:99` | 5,1% | 4,8% | 2,8% |
| 2026 | 22.202 | `9999-99-99 99:99:99` | 5,0% | 4,9% | 3,1% |
| 2027 | 41 | `9999-99-99 99:99:99` | 7,3% | 7,3% | 2,4% |
