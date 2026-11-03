# Evidências de qualidade: `pesquisa_saida.csv`

Gerado por `src/qualidade.py` em 03/11/2026 20:38. Só mede: nenhuma linha foi alterada. Texto · uma linha por resposta · 643 linhas · 5 colunas.

Valores só aparecem quando se repetem pelo menos 5 vezes; colunas pessoais aparecem só em números.

## 1. Completude

Quanto falta em cada coluna. "Disfarçado" é campo preenchido que não diz nada (`nada`, `x`, `.`, emoji, `nao sei`).

| Coluna | Opcional no dicionário | Nulos | Só espaços | Disfarçados | Vazio real | % vazio real | Disfarçados mais comuns |
|---|---|---|---|---|---|---|---|
| `comentario` | sim | 183 | 0 | 0 | 183 | 28,5% | — |
| `resposta_id` | não | 0 | 0 | 0 | 0 | 0,0% | — |
| `user_id` | não | 0 | 0 | 0 | 0 | 0,0% | — |
| `respondido_em` | não | 0 | 0 | 0 | 0 | 0,0% | — |
| `motivo_principal` | não | 0 | 0 | 0 | 0 | 0,0% | — |

## 2. Validade

Valores que não podem ser reais ou que estão fora do que o dicionário permite.

| Coluna | Regra | Resultado | Exemplos |
|---|---|---|---|
| `motivo_principal` | domínio do dicionário | 0 fora de {preco, nao_uso, problema_tecnico, outro_app, saude, outro} | — |
| `respondido_em` | data válida e plausível | 0 não viram data; 0 antes do lançamento (01/09/2020); 0 depois do corte (30/09/2026) | de 01/06/2026 a 30/09/2026 |

## 3. Consistência

A mesma informação registrada de formas diferentes, dentro do arquivo ou entre arquivos.

| Coluna | Checagem | Resultado | Exemplos |
|---|---|---|---|
| `comentario` | mesma coisa escrita de jeitos diferentes (ignorando maiúsculas, acentos, espaços, pontuação e emoji) | 142 valores distintos viram 107 depois de normalizar; 52 linhas (8,1%) usam uma grafia diferente da mais comum | `já fiz a prova, agora não preciso mais` (27) e mais 1 grafias; `era só até a prova` (25) e mais 2 grafias; `app bugado depois da atualização` (23) e mais 1 grafias |

## 4. Unicidade

Registros que aparecem mais de uma vez.

| Checagem | Resultado |
|---|---|
| linha inteira | 0 linhas repetidas |
| chave `resposta_id` | 0 repetições |
| texto livre `comentario` | 141 textos distintos em 460; os 20 mais comuns cobrem 58,0% |

## 5. Temporalidade

Coluna de referência: `respondido_em`, de 01/06/2026 a 30/09/2026 (dicionário: 01/06/2026 a 30/09/2026); 0 registros depois do corte. Abaixo, o volume e a falta de cada coluna por ano: uma mudança brusca de um ano para o outro indica que a forma de registrar mudou.

| Ano | Linhas | Formato de data | vazio `comentario` |
|---|---|---|---|
| 2026 | 643 | `9999-99-99` | 28,5% |
