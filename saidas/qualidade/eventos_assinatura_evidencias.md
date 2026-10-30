# Evidências de qualidade: `eventos_assinatura.csv`

Gerado por `src/qualidade.py` em 29/10/2026 22:56. Só mede: nenhuma linha foi alterada. Log de eventos · uma linha por evento · 275.565 linhas · 6 colunas.

Valores só aparecem quando se repetem pelo menos 5 vezes; colunas pessoais aparecem só em números.

## 1. Completude

Quanto falta em cada coluna. "Disfarçado" é campo preenchido que não diz nada (`nada`, `x`, `.`, emoji, `nao sei`).

| Coluna | Opcional no dicionário | Nulos | Só espaços | Disfarçados | Vazio real | % vazio real | Disfarçados mais comuns |
|---|---|---|---|---|---|---|---|
| `detalhe` | sim | 269.494 | 0 | 0 | 269.494 | 97,8% | — |
| `plano` | não | 72.873 | 0 | 0 | 72.873 | 26,4% | — |
| `user_id` | não | 0 | 0 | 0 | 0 | 0,0% | — |
| `data_hora` | não | 0 | 0 | 0 | 0 | 0,0% | — |
| `evento` | não | 0 | 0 | 0 | 0 | 0,0% | — |
| `canal_cobranca` | não | 0 | 0 | 0 | 0 | 0,0% | — |

## 2. Validade

Valores que não podem ser reais ou que estão fora do que o dicionário permite.

| Coluna | Regra | Resultado | Exemplos |
|---|---|---|---|
| `evento` | domínio do dicionário | 0 fora de {trial_iniciado, trial_expirado, assinatura_iniciada, renovacao, renovacao_automatica_desligada, renovacao_automatica_religada, periodo_carencia, assinatura_expirada, cancelamento_web, reembolso, chargeback} | — |
| `plano` | domínio do dicionário | 0 fora de {mensal, anual} | — |
| `canal_cobranca` | domínio do dicionário | 0 fora de {app_store, google_play, web_cartao, web_pix} | — |
| `data_hora` | data válida e plausível | 0 não viram data; 0 antes do lançamento (01/09/2020); 0 depois do corte (30/09/2026) | de 01/07/2024 a 30/09/2026 |

## 3. Consistência

A mesma informação registrada de formas diferentes, dentro do arquivo ou entre arquivos.

| Coluna | Checagem | Resultado | Exemplos |
|---|---|---|---|
| `data_hora` | formatos de data | 2 formatos | `9999-99-99T99:99:99Z` (186.323), `9999-99-99 99:99:99` (89.242) |

## 4. Unicidade

Registros que aparecem mais de uma vez.

| Checagem | Resultado |
|---|---|
| linha inteira | 0 linhas repetidas |

## 5. Temporalidade

Coluna de referência: `data_hora`, de 01/07/2024 a 30/09/2026 (dicionário: 01/07/2024 a 30/09/2026); 0 registros depois do corte. Abaixo, o volume e a falta de cada coluna por ano: uma mudança brusca de um ano para o outro indica que a forma de registrar mudou.

| Ano | Linhas | Formato de data | vazio `plano` | vazio `detalhe` |
|---|---|---|---|---|
| 2024 | 43.506 | `9999-99-99T99:99:99Z` | 31,6% | 98,6% |
| 2025 | 122.424 | `9999-99-99T99:99:99Z` | 26,1% | 97,8% |
| 2026 | 109.635 | `9999-99-99T99:99:99Z` | 24,8% | 97,4% |
