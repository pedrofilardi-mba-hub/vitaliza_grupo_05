# Inventário do data room × dicionário de dados

Gerado por `src/inventario.py` em 22/10/2026 22:29, a partir de `dados/brutos/`. Compara cada arquivo com o documento *Vitaliza: dicionário de dados*: linhas, colunas, valores de categoria, período e chaves. Para atualizar, rode o script de novo.

Legenda: 🔴 diverge do dicionário ou impede o uso · 🟡 problema de qualidade a tratar na limpeza · 🔵 informação útil

## Resumo

| Arquivo | Forma | Uma linha por | Linhas no dicionário | Linhas no arquivo | Confere? | Colunas | Tamanho | Achados |
|---|---|---|---:|---:|:-:|:-:|---:|---|
| `usuarios.csv` | Tabela | conta | 64.948 | 64.948 | ✅ | ✅ | 7.9 MB | 🟡 5 |
| `assinaturas.csv` | Tabela | assinatura | 32.643 | 32.643 | ✅ | ✅ | 2.5 MB | 🟡 3 |
| `amizades.csv` | Tabela | relação de seguir | 113.480 | 113.480 | ✅ | ✅ | 3.7 MB | 🟡 2 |
| `campanha_ago26.csv` | Tabela | assinante sorteado | 14.120 | 14.120 | ✅ | ✅ | 1.3 MB | — |
| `eventos_assinatura.csv` | Log de eventos | evento | 275.565 | 275.565 | ✅ | ✅ | 17.7 MB | 🟡 1 |
| `pagamentos.csv` | Log de eventos | cobrança | 165.548 | 165.548 | ✅ | ✅ | 11.6 MB | 🟡 2 |
| `uso_mensal.csv` | Log de eventos | usuário e mês | 591.662 | 591.662 | ✅ | ✅ | 19.1 MB | — |
| `atividades.parquet` | Log de eventos | treino | 1.254.475 | 1.254.475 | ✅ | ✅ | 19.1 MB | 🟡 4 |
| `onboarding.csv` | Texto | conta | 63.929 | 63.929 | ✅ | ✅ | 5.7 MB | 🟡 1 |
| `pesquisa_saida.csv` | Texto | resposta | 643 | 643 | ✅ | ✅ | 0.0 MB | — |
| `feed_posts.csv` | Texto | post | 119.309 | 119.309 | ✅ | ✅ | 8.9 MB | 🟡 2 |
| `tickets_suporte.csv` | Texto | chamado | 4.422 | 4.422 | ✅ | ✅ | 0.5 MB | 🟡 1 |
| `heatmap/2026-07-31/` | Imagem | assinante | 12.426 | 12.426 no zip | ✅ | — | — | ver seção |
| `heatmap/2026-09-30/` | Imagem | assinante | 13.047 | 13.047 no zip | ✅ | — | — | ver seção |

## Principais pontos

- **O data room está completo.** 12 de 12 arquivos têm exatamente as linhas do dicionário, 12 de 12 têm exatamente as colunas descritas, e os mapas de calor batem com as contagens do dicionário.
- 🟡 **Valores que o dicionário não descreve:** plano `cortesia`, canal `interno` (60 contas internas, não pagantes) e os valores de `status_atual` (`ativa`, `expirada`, `reembolsada`). Sem a `cortesia`, a base ativa bate com os 14.753 pagantes do enunciado.
- 🟡 **Datas depois do corte de 30/09/2026**, mesmo com o fuso convertido: `usuarios.csv` (data_cadastro: 119); `amizades.csv` (desde: 273); `atividades.parquet` (inicio: 34); `feed_posts.csv` (data_hora: 122); `tickets_suporte.csv` (resolvido_em: 41). Na construção das variáveis, filtre tudo até o corte, senão o modelo enxerga o futuro.
- 🟡 **Fusos misturados** em `eventos_assinatura.csv` e `pagamentos.csv`: as lojas gravam em UTC (`...Z`) e o site, em Brasília. Converta antes de contar por dia ou mês, porque eventos perto da meia-noite mudam de dia.
- 🟡 **Texto a padronizar:** `sexo` (6 grafias), `sistema` (5), `dias_por_semana` (texto livre), `valor` em `pagamentos.csv` (`34.90` e `R$ 34,90`) e `tipo` de treino em português e inglês.
- 🟡 **Valores suspeitos:** datas de nascimento no futuro ou em 1900, cadastros com data posterior ao corte, distâncias de até 10 mil km e treinos com 0 minuto em `atividades.parquet`.
- 🔵 **Vazamento:** `assinaturas.csv` é o retrato de 01/10/2026. Situação histórica sai de `eventos_assinatura.csv`.

## `usuarios.csv`

Tabela · uma linha por conta · 64.948 linhas · 7.9 MB

- 🟡 `data_cadastro` vai de 01/09/2020 a 04/04/2027; o dicionário indica 01/09/2020 a 30/09/2026.
- 🟡 `data_cadastro`: 119 datas depois do corte de 30/09/2026 (já convertidas para o horário de Brasília).
- 🟡 `data_nascimento` impossível ou improvável: 194 no futuro, 0 com menos de 13 anos e 412 com mais de 100 anos (ex.: 01/01/1900). Campo digitado sem validação.
- 🟡 `sexo` escrito de 6 jeitos: F, Fem, M, Masc, feminino, masculino.
- 🟡 `sistema` escrito de 5 jeitos: Android, IOS, android, iOS, ios.
- 🔵 `email` e `data_nascimento` são dados pessoais: não enviar a APIs de LLM nem gravar em saidas/.

- Datas em `data_cadastro`: 01/09/2020 a 04/04/2027. Formatos: `9999-99-99 99:99:99` (64.948).
- Datas em `data_nascimento`: 01/01/1900 a 12/05/2031. Formatos: `9999-99-99` (61.647).

| Coluna | Tipo lido | Vazios | Distintos | Valores ou faixa |
|---|---|---:|---:|---|
| `user_id` | str | 0,0% | 64.948 | — |
| `email` | str | 0,0% | 64.948 | — |
| `data_cadastro` | str | 0,0% | 60.938 | — |
| `data_nascimento` | str | 5,1% | 15.201 | — |
| `sexo` | str | 4,8% | 6 | F (19.330), M (17.646), Fem (6.657), feminino (6.520), Masc (5.838), masculino (5.815) |
| `cidade` | str | 0,0% | 36 | — |
| `uf` | str | 0,0% | 11 | SP (31.994), RJ (7.513), MG (4.550), PR (3.922), DF (3.268), RS (3.267), SC (2.674), GO (1.950), PE (1.940), CE (1.939), BA (1.931) |
| `cep_prefixo` | str | 2,9% | 242 | mín 10 · mediana 201 · máx 918 |
| `canal_aquisicao` | str | 0,0% | 7 | organico (18.531), influenciador (14.067), meta_ads (11.939), indicacao (8.117), google_ads (6.801), parceria_corporativa (5.433), interno (60) |
| `sistema` | str | 0,0% | 5 | android (28.027), ios (20.854), iOS (7.463), Android (7.124), IOS (1.480) |
| `versao_app` | str | 0,0% | 6 | 5.4.1 (20.010), 5.4.0 (19.996), 5.3.2 (9.899), 5.3.0 (9.795), 5.1.0 (2.644), 4.9.8 (2.604) |
| `relogio_conectado` | str | 0,0% | 3 | nenhum (40.159), garmin (13.403), apple_watch (11.386) |

## `assinaturas.csv`

Tabela · uma linha por assinatura · 32.643 linhas · 2.5 MB

- 🟡 `plano_atual` tem valores que o dicionário não lista: `cortesia` (60).
- 🟡 `canal_cobranca` tem valores que o dicionário não lista: `interno` (60).
- 🟡 `status_atual` tem valores sem descrição no dicionário: ativa, expirada, reembolsada.
- 🔵 Assinaturas ativas em 01/10/2026: 14.813; sem `cortesia`: 14.753 (o enunciado fala em 14.753 pagantes em 30/09/2026).
- 🔵 Plano dos pagantes ativos: anual 57,5%, mensal 42,5% (enunciado: 57% / 43%).
- 🔵 É um retrato de 01/10/2026: não usar status, renovação ou motivo como variável do modelo (vazamento).

- Datas em `inicio`: 08/09/2020 a 30/09/2026. Formatos: `9999-99-99` (32.643).
- Datas em `data_fim`: 07/07/2024 a 30/09/2026. Formatos: `9999-99-99` (17.830).

| Coluna | Tipo lido | Vazios | Distintos | Valores ou faixa |
|---|---|---:|---:|---|
| `assinatura_id` | str | 0,0% | 32.643 | — |
| `user_id` | str | 0,0% | 32.643 | — |
| `plano_atual` | str | 0,0% | 3 | mensal (19.556), anual (13.027), cortesia (60) |
| `canal_cobranca` | str | 0,0% | 5 | app_store (11.170), google_play (10.948), web_cartao (7.087), web_pix (3.378), interno (60) |
| `inicio` | str | 0,0% | 2.170 | — |
| `status_atual` | str | 0,0% | 3 | expirada (17.758), ativa (14.813), reembolsada (72) |
| `renovacao_automatica` | str | 0,0% | 2 | nao (20.140), sim (12.503) |
| `data_fim` | str | 45,4% | 814 | — |
| `motivo_fim` | str | 45,4% | 4 | renovacao_desligada (16.145), falha_pagamento (1.321), chargeback (292), reembolso (72) |

## `amizades.csv`

Tabela · uma linha por relação de seguir · 113.480 linhas · 3.7 MB

- 🟡 `desde` vai de 05/09/2020 a 09/10/2026; o dicionário indica 01/09/2020 a 30/09/2026.
- 🟡 `desde`: 273 datas depois do corte de 30/09/2026 (já convertidas para o horário de Brasília).

- Datas em `desde`: 05/09/2020 a 09/10/2026. Formatos: `9999-99-99` (113.480).

| Coluna | Tipo lido | Vazios | Distintos | Valores ou faixa |
|---|---|---:|---:|---|
| `seguidor_id` | str | 0,0% | 50.455 | — |
| `seguido_id` | str | 0,0% | 50.547 | — |
| `desde` | str | 0,0% | 2.211 | — |

## `campanha_ago26.csv`

Tabela · uma linha por assinante sorteado · 14.120 linhas · 1.3 MB

- 🔵 Tamanho dos grupos: controle 3.579, conteudo 3.554, desafio 3.515, cupom 3.472. `enviado_em`, `titulo_mensagem` e `canal` vazios no controle, como esperado.

- Datas em `enviado_em`: 10/08/2026 a 10/08/2026. Formatos: `9999-99-99 99:99:99` (10.541).

| Coluna | Tipo lido | Vazios | Distintos | Valores ou faixa |
|---|---|---:|---:|---|
| `user_id` | str | 0,0% | 14.120 | — |
| `grupo` | str | 0,0% | 4 | controle (3.579), conteudo (3.554), desafio (3.515), cupom (3.472) |
| `enviado_em` | str | 25,3% | 1 | — |
| `canal` | str | 25,3% | 1 | push+email (10.541) |
| `titulo_mensagem` | str | 25,3% | 3 | Seu plano de treino personalizado está pronto (3.554), Novo desafio de 6 semanas montado para você (3.515), Oferta para voltar a treinar (3.472) |
| `oferta` | str | 75,4% | 2 | 1_mes_gratis (2.052), 30pct_3_meses (1.420) |
| `abriu_push` | str | 0,0% | 2 | False (10.808), True (3.312) |
| `abriu_email` | str | 0,0% | 2 | False (12.176), True (1.944) |
| `clicou` | str | 0,0% | 2 | False (12.516), True (1.604) |

## `eventos_assinatura.csv`

Log de eventos · uma linha por evento · 275.565 linhas · 17.7 MB

- 🟡 `data_hora` mistura 2 formatos de data.

- Datas em `data_hora`: 01/07/2024 a 30/09/2026. Formatos: `9999-99-99T99:99:99Z` (186.323), `9999-99-99 99:99:99` (89.242).

| Coluna | Tipo lido | Vazios | Distintos | Valores ou faixa |
|---|---|---:|---:|---|
| `user_id` | str | 0,0% | 52.196 | — |
| `data_hora` | str | 0,0% | 275.116 | — |
| `evento` | str | 0,0% | 11 | renovacao (132.606), trial_iniciado (46.996), assinatura_iniciada (27.383), renovacao_automatica_desligada (26.923), trial_expirado (19.143), assinatura_expirada (17.830), renovacao_automatica_religada (1.798), periodo_carencia (1.346), cancelamento_web (1.172), chargeback (296), reembolso (72) |
| `plano` | str | 26,4% | 2 | mensal (170.993), anual (31.699) |
| `canal_cobranca` | str | 0,0% | 4 | google_play (93.582), app_store (92.741), web_cartao (58.775), web_pix (30.467) |
| `detalhe` | str | 97,8% | 4 | renovacao_desligada (5.139), falha_pagamento (800), chargeback (109), reembolso (23) |

## `pagamentos.csv`

Log de eventos · uma linha por cobrança · 165.548 linhas · 11.6 MB

- 🟡 `data_hora` mistura 2 formatos de data.
- 🟡 `valor` em dois formatos: `34.90` e `R$ 34,90` (19.750 linhas no formato com R$ e vírgula).
- 🔵 368 valores negativos, todos com status chargeback, estornado: são devoluções, não cobranças.
- 🔵 O mensal aparece a R$ 34,90 e a R$ 39,90: é o reajuste de 01/03/2026.

- Datas em `data_hora`: 02/07/2024 a 30/09/2026. Formatos: `9999-99-99T99:99:99Z` (112.126), `9999-99-99 99:99:99` (53.422).

| Coluna | Tipo lido | Vazios | Distintos | Valores ou faixa |
|---|---|---:|---:|---|
| `pagamento_id` | str | 0,0% | 165.548 | — |
| `user_id` | str | 0,0% | 31.782 | — |
| `data_hora` | str | 0,0% | 163.473 | — |
| `valor` | str | 0,0% | 9 | 34.90 (85.508), 39.90 (44.632), R$ 34,90 (17.746), 299.90 (13.732), R$ 299,90 (1.852), 239.90 (1.558), -39.90 (206), -299.90 (162), R$ 239,90 (152) |
| `metodo` | str | 0,0% | 4 | app_store (57.020), google_play (55.106), cartao (34.676), pix_automatico (18.746) |
| `status` | str | 0,0% | 4 | aprovado (161.930), recusado (3.250), chargeback (296), estornado (72) |
| `tentativa` | str | 0,0% | 2 | 1 (160.682), 2 (4.866) |

## `uso_mensal.csv`

Log de eventos · uma linha por usuário e mês · 591.662 linhas · 19.1 MB

- ✅ Confere com o dicionário.

- Datas em `mes`: 01/01/2025 a 01/09/2026. Formatos: `9999-99` (591.662).

| Coluna | Tipo lido | Vazios | Distintos | Valores ou faixa |
|---|---|---:|---:|---|
| `user_id` | str | 0,0% | 63.830 | — |
| `mes` | str | 0,0% | 21 | — |
| `atividades` | str | 0,0% | 67 | mín 0 · mediana 0 · máx 68 |
| `atividades_ar_livre` | str | 0,0% | 53 | mín 0 · mediana 0 · máx 53 |
| `atividades_video` | str | 0,0% | 52 | mín 0 · mediana 0 · máx 57 |
| `minutos` | str | 0,0% | 2.534 | mín 0 · mediana 0 · máx 8228 |
| `dias_ativos` | str | 0,0% | 31 | mín 0 · mediana 0 · máx 30 |
| `sessoes_app` | str | 0,0% | 135 | mín 0 · mediana 2 · máx 153 |

## `atividades.parquet`

Log de eventos · uma linha por treino · 1.254.475 linhas · 19.1 MB

- 🟡 `inicio`: 34 datas depois do corte de 30/09/2026 (já convertidas para o horário de Brasília).
- 🟡 `tipo` mistura português e inglês: caminhada, corrida, forca, funcional, hiit, pedal, ride, run, strength, walk, yoga (30,0% dos treinos em inglês).
- 🟡 `distancia_km`: máximo de 10.013 km e 1.935 treinos acima de 100 km; provável parte em metros.
- 🟡 `duracao_min` = 0 em 3.649 treinos.
- 🔵 `treino_com` vazio de verdade em 0,0% das linhas; texto vazio em 98,9%.

- Datas em `inicio`: 01/01/2026 a 01/10/2026. Formatos: `9999-99-99 99:99:99` (1.254.475).

| Coluna | Tipo lido | Vazios | Distintos | Valores ou faixa |
|---|---|---:|---:|---|
| `atividade_id` | str | 0,0% | 1.254.475 | — |
| `user_id` | str | 0,0% | 36.551 | — |
| `inicio` | str | 0,0% | 223.408 | — |
| `tipo` | str | 0,0% | 11 | corrida (223.818), run (162.108), funcional (145.476), caminhada (118.024), yoga (113.849), forca (112.704), hiit (109.934), walk (88.509), strength (85.548), pedal (53.740), ride (40.765) |
| `duracao_min` | float64 | 0,0% | 3.289 | mín 0 · mediana 41.4 · máx 543.9 |
| `distancia_km` | float64 | 45,8% | 9.584 | mín 0 · mediana 6.47 · máx 10012.8 |
| `ritmo_min_km` | float64 | 46,4% | 1.007 | mín 1.8 · mediana 6.43 · máx 13 |
| `fc_media` | float64 | 61,0% | 133 | mín 61 · mediana 133 · máx 195 |
| `origem` | str | 0,0% | 3 | app (881.706), garmin (207.954), apple_health (164.815) |
| `gps_ok` | bool | 0,0% | 2 | True (1.239.696), False (14.779) |
| `treino_com` | str | 0,0% | 2.766 |  (1.240.338), u_26ec2fcc (59), u_f3b52442 (49), u_0e8e6152 (47), u_a8e579de (43) … |

## `onboarding.csv`

Texto · uma linha por conta · 63.929 linhas · 5.7 MB

- 🟡 `dias_por_semana` é texto livre (22 formas diferentes, ex.: "3", "3x", "3 vezes").

- Datas em `respondido_em`: 01/09/2020 a 30/09/2026. Formatos: `9999-99-99` (63.929).

| Coluna | Tipo lido | Vazios | Distintos | Valores ou faixa |
|---|---|---:|---:|---|
| `onboarding_id` | str | 0,0% | 63.929 | — |
| `user_id` | str | 0,0% | 63.929 | — |
| `respondido_em` | str | 0,0% | 2.177 | — |
| `objetivo_texto` | str | 8,6% | 17.189 | — |
| `como_conheceu` | str | 7,2% | 571 | — |
| `nivel` | str | 7,1% | 3 | intermediario (25.631), iniciante (23.682), avancado (10.103) |
| `dias_por_semana` | str | 10,0% | 22 | 3 (10.268), 2 (7.576), 4 (7.437), 5 (3.649), 3 vezes (3.450) … |

## `pesquisa_saida.csv`

Texto · uma linha por resposta · 643 linhas · 0.0 MB

- 🔵 643 respostas de 641 contas (o dicionário diz 641).

- Datas em `respondido_em`: 01/06/2026 a 30/09/2026. Formatos: `9999-99-99` (643).

| Coluna | Tipo lido | Vazios | Distintos | Valores ou faixa |
|---|---|---:|---:|---|
| `resposta_id` | str | 0,0% | 643 | — |
| `user_id` | str | 0,0% | 641 | — |
| `respondido_em` | str | 0,0% | 121 | — |
| `motivo_principal` | str | 0,0% | 6 | preco (264), outro (223), nao_uso (81), outro_app (34), problema_tecnico (27), saude (14) |
| `comentario` | str | 28,5% | 142 | — |

## `feed_posts.csv`

Texto · uma linha por post · 119.309 linhas · 8.9 MB

- 🟡 `data_hora` vai de 01/07/2025 a 07/10/2026; o dicionário indica 01/07/2025 a 30/09/2026.
- 🟡 `data_hora`: 122 datas depois do corte de 30/09/2026 (já convertidas para o horário de Brasília).

- Datas em `data_hora`: 01/07/2025 a 07/10/2026. Formatos: `9999-99-99 99:99:99` (119.309).

| Coluna | Tipo lido | Vazios | Distintos | Valores ou faixa |
|---|---|---:|---:|---|
| `post_id` | str | 0,0% | 119.309 | — |
| `user_id` | str | 0,0% | 26.899 | — |
| `data_hora` | str | 0,0% | 119.066 | — |
| `texto` | str | 0,0% | 31.620 | — |
| `curtidas` | str | 0,0% | 37 | mín 0 · mediana 6 · máx 38 |

## `tickets_suporte.csv`

Texto · uma linha por chamado · 4.422 linhas · 0.5 MB

- 🟡 `resolvido_em`: 41 datas depois do corte de 30/09/2026 (já convertidas para o horário de Brasília).

- Datas em `aberto_em`: 01/07/2025 a 30/09/2026. Formatos: `9999-99-99 99:99:99` (4.422).
- Datas em `resolvido_em`: 03/07/2025 a 07/10/2026. Formatos: `9999-99-99` (2.917).

| Coluna | Tipo lido | Vazios | Distintos | Valores ou faixa |
|---|---|---:|---:|---|
| `ticket_id` | str | 0,0% | 4.422 | — |
| `user_id` | str | 0,0% | 3.989 | — |
| `aberto_em` | str | 0,0% | 4.389 | — |
| `canal` | str | 0,0% | 3 | chat (2.195), email (1.120), loja (1.107) |
| `texto_cliente` | str | 0,0% | 303 | — |
| `categoria_atendente` | str | 0,0% | 6 | tecnico (961), cancelamento (913), conta (757), cobranca (651), conteudo (588), duvida_geral (552) |
| `status` | str | 0,0% | 3 | resolvido (2.917), aberto (981), sem_resposta (524) |
| `resolvido_em` | str | 34,0% | 460 | — |

## Mapas de calor (`dados/brutos/heatmap/`)

| Data | Dicionário | No zip | Extraídas na pasta | Imagens sem conta em usuarios.csv |
|---|---:|---:|---:|---:|
| 2026-07-31 | 12.426 | 12.426 | 12.426 | 0 |
| 2026-09-30 | 13.047 | 13.047 | 13.047 | 0 |

- 🔵 2026-07-31: o zip traz também 5 arquivos `__MACOSX/._*.png`, metadados do macOS e não imagens. Ignorados na contagem; não devem ser lidos como mapas.
- 🔵 Só existe imagem para quem era assinante pagante na data e treinou ao ar livre nos 90 dias anteriores.
