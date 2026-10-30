# Evidências de qualidade: `onboarding.csv`

Gerado por `src/qualidade.py` em 29/10/2026 23:58. Só mede: nenhuma linha foi alterada. Texto · uma linha por conta · 63.929 linhas · 7 colunas.

Valores só aparecem quando se repetem pelo menos 5 vezes; colunas pessoais aparecem só em números.

## 1. Completude

Quanto falta em cada coluna. "Disfarçado" é campo preenchido que não diz nada (`nada`, `x`, `.`, emoji, `nao sei`).

| Coluna | Opcional no dicionário | Nulos | Só espaços | Disfarçados | Vazio real | % vazio real | Disfarçados mais comuns |
|---|---|---|---|---|---|---|---|
| `objetivo_texto` | sim | 5.467 | 0 | 13.768 | 19.235 | 30,1% | `nada` (1.426), `😂` (1.413), `.` (1.398), `x` (1.397), `sla` (1.396), `kkkk` (1.365), `asdf` (1.365), `nao sei` (1.361) |
| `como_conheceu` | sim | 4.586 | 0 | 11.515 | 16.101 | 25,2% | `😂` (1.194), `-` (1.190), `nao sei` (1.174), `x` (1.173), `asdf` (1.173), `sla` (1.169), `ok` (1.126), `.` (1.117) |
| `dias_por_semana` | não | 6.368 | 0 | 0 | 6.368 | 10,0% | — |
| `nivel` | não | 4.513 | 0 | 0 | 4.513 | 7,1% | — |
| `onboarding_id` | não | 0 | 0 | 0 | 0 | 0,0% | — |
| `user_id` | não | 0 | 0 | 0 | 0 | 0,0% | — |
| `respondido_em` | não | 0 | 0 | 0 | 0 | 0,0% | — |

Cobertura: 1.019 das 64.948 contas de `usuarios.csv` não têm linha neste arquivo (1,6%).

## 2. Validade

Valores que não podem ser reais ou que estão fora do que o dicionário permite.

| Coluna | Regra | Resultado | Exemplos |
|---|---|---|---|
| `dias_por_semana` | número inteiro entre 1 e 7 | 917 sem número; 0 fora da faixa | `todos` (917) |
| `respondido_em` | data válida e plausível | 0 não viram data; 0 antes do lançamento (01/09/2020); 0 depois do corte (30/09/2026) | de 01/09/2020 a 30/09/2026 |

## 3. Consistência

A mesma informação registrada de formas diferentes, dentro do arquivo ou entre arquivos.

| Coluna | Checagem | Resultado | Exemplos |
|---|---|---|---|
| `objetivo_texto` | mesma coisa escrita de jeitos diferentes (ignorando maiúsculas, acentos, espaços, pontuação e emoji) | 17.179 valores distintos viram 12.257 depois de normalizar; 9.884 linhas (15,5%) usam uma grafia diferente da mais comum | `cuidar da saúde, tô sedentário há anos` (872) = `cuidar da saúde, tô sedentario ha anos` (170) = `cuidar da saúde, tô sedentário há anos 👊` (16) e mais 193 grafias; `baixar o colesterol` (1.050) = `baixar o colesterol ✨` (22) = `baixar o colesterol 💪` (16) e mais 133 grafias; `parar de sentir dor nas costas` (1.017) = `parar de sentir dor nas costas 😅` (18) = `parar de sentir dor nas costas 🚴` (16) e mais 145 grafias |
| `como_conheceu` | mesma coisa escrita de jeitos diferentes (ignorando maiúsculas, acentos, espaços, pontuação e emoji) | 561 valores distintos viram 368 depois de normalizar; 2.397 linhas (3,7%) usam uma grafia diferente da mais comum | `já conhecia` (2.842) = `ja conhecia` (518); `procurei app de corrida na loja` (3.204) = `procureia pp de corrida na loja` (13) = `procurei app de corrida n aloja` (12) e mais 8 grafias; `vi alguém usando no parque` (2.626) = `vi alguem usando no parque` (478) = `vi alguém usando nop arque` (17) e mais 10 grafias |
| `dias_por_semana` | formas de escrever o número | 4 formas | `9` (33.527), `9 vezes` (11.563), `9x` (11.554), `todos` (917) |
| `respondido_em` | coerência com usuarios.data_cadastro | 0 antes do cadastro; 63.929 no mesmo dia; 0 depois; 0 sem cadastro | — |

## 4. Unicidade

Registros que aparecem mais de uma vez.

| Checagem | Resultado |
|---|---|
| linha inteira | 0 linhas repetidas |
| chave `onboarding_id` | 0 repetições |
| uma linha por conta (`user_id`) | 0 contas repetidas |
| texto livre `objetivo_texto` | 17.189 textos distintos em 58.462; os 20 mais comuns cobrem 38,2% |
| texto livre `como_conheceu` | 571 textos distintos em 59.343; os 20 mais comuns cobrem 67,1% |

## 5. Temporalidade

Coluna de referência: `respondido_em`, de 01/09/2020 a 30/09/2026 (dicionário: 01/09/2020 a 30/09/2026); 0 registros depois do corte. Abaixo, o volume e a falta de cada coluna por ano: uma mudança brusca de um ano para o outro indica que a forma de registrar mudou.

| Ano | Linhas | Formato de data | vazio `objetivo_texto` | vazio `como_conheceu` | vazio `nivel` | vazio `dias_por_semana` |
|---|---|---|---|---|---|---|
| 2020 | 436 | `9999-99-99` | 28,9% | 28,0% | 6,7% | 10,6% |
| 2021 | 1.358 | `9999-99-99` | 29,9% | 26,4% | 7,5% | 11,1% |
| 2022 | 1.314 | `9999-99-99` | 29,3% | 24,8% | 7,5% | 9,9% |
| 2023 | 1.423 | `9999-99-99` | 30,1% | 24,3% | 8,4% | 10,0% |
| 2024 | 11.831 | `9999-99-99` | 30,4% | 25,1% | 6,9% | 9,7% |
| 2025 | 25.770 | `9999-99-99` | 29,8% | 25,1% | 7,1% | 9,8% |
| 2026 | 21.797 | `9999-99-99` | 30,3% | 25,2% | 6,9% | 10,2% |
