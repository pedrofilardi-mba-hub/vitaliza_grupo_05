# Evidências de qualidade: `campanha_ago26.csv`

Gerado por `src/qualidade.py` em 03/11/2026 20:17. Só mede: nenhuma linha foi alterada. Tabela · uma linha por assinante sorteado · 14.120 linhas · 9 colunas.

Valores só aparecem quando se repetem pelo menos 5 vezes; colunas pessoais aparecem só em números.

## 1. Completude

Quanto falta em cada coluna. "Disfarçado" é campo preenchido que não diz nada (`nada`, `x`, `.`, emoji, `nao sei`).

| Coluna | Opcional no dicionário | Nulos | Só espaços | Disfarçados | Vazio real | % vazio real | Disfarçados mais comuns |
|---|---|---|---|---|---|---|---|
| `oferta` | não | 10.648 | 0 | 0 | 10.648 | 75,4% | — |
| `enviado_em` | não | 3.579 | 0 | 0 | 3.579 | 25,3% | — |
| `canal` | não | 3.579 | 0 | 0 | 3.579 | 25,3% | — |
| `titulo_mensagem` | não | 3.579 | 0 | 0 | 3.579 | 25,3% | — |
| `user_id` | não | 0 | 0 | 0 | 0 | 0,0% | — |
| `grupo` | não | 0 | 0 | 0 | 0 | 0,0% | — |
| `abriu_push` | não | 0 | 0 | 0 | 0 | 0,0% | — |
| `abriu_email` | não | 0 | 0 | 0 | 0 | 0,0% | — |
| `clicou` | não | 0 | 0 | 0 | 0 | 0,0% | — |

Cobertura: 50.828 das 64.948 contas de `usuarios.csv` não têm linha neste arquivo (78,3%).

## 2. Validade

Valores que não podem ser reais ou que estão fora do que o dicionário permite.

| Coluna | Regra | Resultado | Exemplos |
|---|---|---|---|
| `grupo` | domínio do dicionário | 0 fora de {controle, desafio, cupom, conteudo} | — |
| `canal` | domínio do dicionário | 0 fora de {push+email} | — |
| `oferta` | domínio do dicionário | 0 fora de {30pct_3_meses, 1_mes_gratis} | — |
| `enviado_em` | data válida e plausível | 0 não viram data; 0 antes do lançamento (01/09/2020); 0 depois do corte (30/09/2026) | de 10/08/2026 a 10/08/2026 |

## 3. Consistência

A mesma informação registrada de formas diferentes, dentro do arquivo ou entre arquivos.

Nenhuma variação encontrada.

## 4. Unicidade

Registros que aparecem mais de uma vez.

| Checagem | Resultado |
|---|---|
| linha inteira | 0 linhas repetidas |
| chave `user_id` | 0 repetições |
| uma linha por conta (`user_id`) | 0 contas repetidas |

## 5. Temporalidade

Coluna de referência: `enviado_em`, de 10/08/2026 a 10/08/2026; 0 registros depois do corte. Abaixo, o volume e a falta de cada coluna por ano: uma mudança brusca de um ano para o outro indica que a forma de registrar mudou.

| Ano | Linhas | Formato de data | vazio `oferta` |
|---|---|---|---|
| 2026 | 10.541 | `9999-99-99 99:99:99` | 67,1% |
