# Evidências de qualidade: `tickets_suporte.csv`

Gerado por `src/qualidade.py` em 03/11/2026 20:26. Só mede: nenhuma linha foi alterada. Texto · uma linha por chamado · 4.422 linhas · 8 colunas.

Valores só aparecem quando se repetem pelo menos 5 vezes; colunas pessoais aparecem só em números.

## 1. Completude

Quanto falta em cada coluna. "Disfarçado" é campo preenchido que não diz nada (`nada`, `x`, `.`, emoji, `nao sei`).

| Coluna | Opcional no dicionário | Nulos | Só espaços | Disfarçados | Vazio real | % vazio real | Disfarçados mais comuns |
|---|---|---|---|---|---|---|---|
| `resolvido_em` | sim | 1.505 | 0 | 0 | 1.505 | 34,0% | — |
| `ticket_id` | não | 0 | 0 | 0 | 0 | 0,0% | — |
| `user_id` | não | 0 | 0 | 0 | 0 | 0,0% | — |
| `aberto_em` | não | 0 | 0 | 0 | 0 | 0,0% | — |
| `canal` | não | 0 | 0 | 0 | 0 | 0,0% | — |
| `texto_cliente` | não | 0 | 0 | 0 | 0 | 0,0% | — |
| `categoria_atendente` | não | 0 | 0 | 0 | 0 | 0,0% | — |
| `status` | não | 0 | 0 | 0 | 0 | 0,0% | — |

## 2. Validade

Valores que não podem ser reais ou que estão fora do que o dicionário permite.

| Coluna | Regra | Resultado | Exemplos |
|---|---|---|---|
| `canal` | domínio do dicionário | 0 fora de {chat, email, loja} | — |
| `status` | domínio do dicionário | 0 fora de {resolvido, aberto, sem_resposta} | — |
| `aberto_em` | data válida e plausível | 0 não viram data; 0 antes do lançamento (01/09/2020); 0 depois do corte (30/09/2026) | de 01/07/2025 a 30/09/2026 |
| `resolvido_em` | data válida e plausível | 0 não viram data; 0 antes do lançamento (01/09/2020); 41 depois do corte (30/09/2026) | de 03/07/2025 a 07/10/2026 |

## 3. Consistência

A mesma informação registrada de formas diferentes, dentro do arquivo ou entre arquivos.

| Coluna | Checagem | Resultado | Exemplos |
|---|---|---|---|
| `texto_cliente` | mesma coisa escrita de jeitos diferentes (ignorando maiúsculas, acentos, espaços, pontuação e emoji) | 303 valores distintos viram 195 depois de normalizar; 529 linhas (12,0%) usam uma grafia diferente da mais comum | `quero o reembolso, não uso mais` (241) = `quero o reembolso, nao uso mais` (49) e mais 9 grafias; `como faço pra não renovar?` (223) = `como faco pra nao renovar?` (44) e mais 2 grafias; `quero cancelar minha assinatura` (245) e mais 1 grafias |

## 4. Unicidade

Registros que aparecem mais de uma vez.

| Checagem | Resultado |
|---|---|
| linha inteira | 0 linhas repetidas |
| chave `ticket_id` | 0 repetições |
| texto livre `texto_cliente` | 302 textos distintos em 4.422; os 20 mais comuns cobrem 76,3% |

## 5. Temporalidade

Coluna de referência: `aberto_em`, de 01/07/2025 a 30/09/2026 (dicionário: 01/07/2025 a 30/09/2026); 0 registros depois do corte. Abaixo, o volume e a falta de cada coluna por ano: uma mudança brusca de um ano para o outro indica que a forma de registrar mudou.

| Ano | Linhas | Formato de data | vazio `resolvido_em` |
|---|---|---|---|
| 2025 | 1.183 | `9999-99-99 99:99:99` | 20,2% |
| 2026 | 3.239 | `9999-99-99 99:99:99` | 39,1% |
