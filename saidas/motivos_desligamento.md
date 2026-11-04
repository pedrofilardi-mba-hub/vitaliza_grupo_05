# Por que desligam a renovação, e dá para prever quem vai desligar

Gerado por `src/motivos.py` em 03/11/2026 21:30. Os textos são classificados por palavras-chave, de forma provisória; a leitura com IA fica para o objetivo 5.

**Quem entrou:** 6.624 assinantes pagantes que desligaram a renovação ou cancelaram pelo site entre 01/03 e 30/09/2026, cada um comparado com um **gêmeo** que não desligou (mesmo plano, mesma faixa de tempo de casa, ativo na mesma data; 6.624 gêmeos encontrados).

## 1. O que muda nas semanas antes de desligar

| Semanas antes | Treinos por pessoa (desligou) | Treinos por pessoa (gêmeo) |
|---|---:|---:|
| 8ª | 2,42 | 2,17 |
| 7ª | 2,51 | 2,23 |
| 6ª | 2,45 | 2,27 |
| 5ª | 2,32 | 2,32 |
| 4ª | 2,19 | 2,34 |
| 3ª | 2,00 | 2,40 |
| 2ª | 1,57 | 2,48 |
| 1ª | 1,01 | 2,51 |

| Sinal antes de desligar | Desligou | Gêmeo | Quantas vezes mais comum |
|---|---:|---:|---:|
| Nenhum treino nas 4 semanas anteriores | 8,8% | 4,3% | 2,1x |
| Treinos caíram pela metade ou mais (base de 4+) | 33,3% | 9,7% | 3,4x |
| Post de prova concluída nos 30 dias anteriores | 9,1% | 1,2% | 7,9x |
| Chamado técnico nos 60 dias anteriores | 4,3% | 1,9% | 2,2x |
| 2+ treinos com GPS falho nos 60 dias anteriores | 8,9% | 5,7% | 1,6x |
| Chamado de cobrança nos 60 dias anteriores | 0,8% | 0,6% | 1,2x |
| Cartão recusado nos 60 dias anteriores | 1,5% | 1,9% | 0,8x |
| Mensal que pagava o preço antigo (R$ 34,90) | 45,4% | 44,9% | 1,0x |

| Objetivo declarado no onboarding | Desligou | Gêmeo |
|---|---:|---:|
| nao_informado | 29,9% | 30,0% |
| estetica | 15,2% | 10,5% |
| saude | 13,1% | 18,3% |
| companhia | 12,1% | 13,4% |
| desempenho | 9,9% | 6,9% |
| prova_com_prazo | 8,2% | 4,6% |
| bem_estar | 6,7% | 11,3% |
| outro | 4,9% | 4,8% |

## 2. Perfis de motivo de quem desligou

Cada pessoa recebe o **primeiro** sinal da lista que se aplica a ela: prova concluída → parou de treinar → problema técnico → cobrança → sem sinal claro.

| Perfil | Pessoas | % | Entre os mensais | Entre os anuais |
|---|---:|---:|---:|---:|
| sem_sinal_claro | 3.117 | 47,1% | 51,3% | 39,7% |
| parou_de_treinar | 2.416 | 36,5% | 32,2% | 44,0% |
| objetivo_cumprido | 606 | 9,1% | 9,1% | 9,2% |
| problema_tecnico | 425 | 6,4% | 6,1% | 6,9% |
| cobranca | 60 | 0,9% | 1,3% | 0,2% |

**Conferência com a pesquisa de saída** (quem cancelou pelo site e respondeu; `motivo_revisado`, D-046):

| Perfil deduzido \ motivo declarado | (não respondeu) | nao_uso | objetivo_cumprido | outro | outro_app | preco | problema_tecnico | saude |
|---|---:|---:|---:|---:|---:|---:|---:|---:|
| cobranca | 51 | 1 | 1 | 1 | 0 | 5 | 1 | 0 |
| objetivo_cumprido | 548 | 2 | 38 | 5 | 2 | 10 | 1 | 0 |
| parou_de_treinar | 2196 | 32 | 82 | 32 | 7 | 54 | 4 | 9 |
| problema_tecnico | 343 | 8 | 18 | 9 | 1 | 18 | 28 | 0 |
| sem_sinal_claro | 2875 | 40 | 78 | 33 | 13 | 48 | 19 | 11 |

## 3. Novo gabarito: "desligou nos próximos 60 dias" × "saiu nos 60 dias"

Assinantes ainda sem saída anunciada no corte (D-052). Para cada grupo, a taxa e as 5 dimensões que mais separam (AUC).

| Corte | Grupo | Gabarito | Pessoas | Taxa | 5 dimensões que mais separam (AUC) |
|---|---|---|---:|---:|---|
| 31/05 | todos | saiu_60d | 11.965 | 8,5% | `renova_em_60d` 0,76, `plano` 0,75, `dias_ate_renovacao` 0,74, `afetado_reajuste` 0,65, `tempo_casa_meses` 0,61 |
| 31/05 | todos | desligou_60d | 11.965 | 14,8% | `tempo_casa_meses` 0,61, `plano` 0,57, `dias_ate_renovacao` 0,57, `pct_video_90d` 0,56, `sistema` 0,56 |
| 31/05 | mensais | saiu_60d | 5.688 | 16,6% | `tempo_casa_meses` 0,58, `pct_video_90d` 0,57, `gps_falhas_90d` 0,57, `sistema` 0,57, `canal_cobranca` 0,56 |
| 31/05 | mensais | desligou_60d | 5.688 | 18,5% | `tempo_casa_meses` 0,58, `pct_video_90d` 0,57, `sistema` 0,57, `gps_falhas_90d` 0,57, `canal_cobranca` 0,56 |
| 31/05 | anuais (todos) | saiu_60d | 6.277 | 1,2% | `treinos_primeiros_14d` 0,98, `renova_em_60d` 0,94, `dias_ate_renovacao` 0,90, `semanas_ativas_8s` 0,62, `tempo_casa_meses` 0,62 |
| 31/05 | anuais (todos) | desligou_60d | 6.277 | 11,5% | `tempo_casa_meses` 0,61, `pct_video_90d` 0,57, `posts_90d` 0,56, `sistema` 0,56, `canal_cobranca` 0,56 |
| 31/05 | anuais longe da renovação | saiu_60d | 5.647 | 0,1% | `treinos_primeiros_14d` 0,98, `dias_ate_renovacao` 0,98, `treinos_4s_anteriores` 0,92, `canal_aquisicao` 0,91, `irregularidade_8s` 0,90 |
| 31/05 | anuais longe da renovação | desligou_60d | 5.647 | 11,5% | `tempo_casa_meses` 0,61, `posts_90d` 0,56, `pct_video_90d` 0,56, `sistema` 0,56, `canal_cobranca` 0,56 |
| 31/07 | todos | saiu_60d | 11.688 | 6,1% | `renova_em_60d` 0,74, `dias_ate_renovacao` 0,72, `plano` 0,71, `tempo_casa_meses` 0,62, `dias_desde_ultimo_treino` 0,57 |
| 31/07 | todos | desligou_60d | 11.688 | 10,8% | `dias_desde_ultimo_treino` 0,60, `tempo_casa_meses` 0,58, `semanas_ativas_8s` 0,58, `treinos_4s` 0,57, `sessoes_mes` 0,56 |
| 31/07 | mensais | saiu_60d | 5.511 | 11,1% | `tempo_casa_meses` 0,61, `dias_desde_ultimo_treino` 0,59, `afetado_reajuste` 0,58, `irregularidade_8s` 0,56, `semanas_ativas_8s` 0,55 |
| 31/07 | mensais | desligou_60d | 5.511 | 11,4% | `tempo_casa_meses` 0,61, `afetado_reajuste` 0,58, `dias_desde_ultimo_treino` 0,58, `canal_aquisicao` 0,55, `irregularidade_8s` 0,54 |
| 31/07 | anuais (todos) | saiu_60d | 6.177 | 1,6% | `renova_em_60d` 0,92, `dias_ate_renovacao` 0,88, `treinos_primeiros_14d` 0,74, `treinos_4s` 0,72, `dias_desde_ultimo_treino` 0,72 |
| 31/07 | anuais (todos) | desligou_60d | 6.177 | 10,3% | `dias_desde_ultimo_treino` 0,63, `semanas_ativas_8s` 0,62, `treinos_4s` 0,62, `sessoes_mes` 0,61, `minutos_3m` 0,60 |
| 31/07 | anuais longe da renovação | saiu_60d | 5.364 | 0,1% | `dias_ate_renovacao` 0,97, `treinos_4s_anteriores` 0,92, `irregularidade_8s` 0,91, `minutos_3m` 0,88, `semanas_ativas_8s` 0,87 |
| 31/07 | anuais longe da renovação | desligou_60d | 5.364 | 10,3% | `dias_desde_ultimo_treino` 0,63, `semanas_ativas_8s` 0,61, `treinos_4s` 0,61, `sessoes_mes` 0,60, `minutos_3m` 0,59 |
