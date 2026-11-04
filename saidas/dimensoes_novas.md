# Dimensões novas: quanto cada uma separa quem sai

Gerado por `src/dimensoes.py` em 03/11/2026 21:14. Para cada data de corte, uma linha por assinante ativo, só com o que se sabia até aquele dia; o gabarito é se a pessoa **saiu nos 60 dias seguintes**.

| Corte | Assinantes | Saíram em 60 dias | Já tinham anunciado a saída | Saída entre os anunciados | Saída entre os demais |
|---|---:|---:|---:|---:|---:|
| 31/05/2026 (principal) | 14.102 | 12,1% | 2.137 (15,2%) | 31,9% | 8,5% |
| 31/07/2026 (conferência, campanha no meio) | 14.032 | 10,5% | 2.344 (16,7%) | 32,3% | 6,1% |

**Como ler o AUC:** 0,50 = a dimensão não separa nada (acaso); 1,00 = separa perfeitamente. É a mesma régua do slide 9 da Aula 2. Mostramos o AUC **sem os assinantes que já tinham anunciado a saída**, porque para eles a resposta já é quase certa e eles inflariam qualquer número.

Os grupos separados importam: um anual que só renova daqui a meses **não pode** sair na janela, e isso domina qualquer número da base toda. Por isso o ranking mostra também os **mensais** (podem sair a qualquer mês) e os **anuais que renovam na janela**, sempre sem os que já anunciaram a saída.

## Ranking (ordenado pelo AUC entre os mensais, corte principal)

| # | Dimensão | Nova? | Família | Todos 31/05 | Todos 31/07 | Mensais 31/05 | Mensais 31/07 | Anuais que renovam 31/05 | Anuais que renovam 31/07 | Direção |
|---:|---|:-:|---|---:|---:|---:|---:|---:|---:|---|
| 1 | `tempo_casa_meses` |  | contrato | 0,61 | 0,62 | 0,58 | 0,61 | 0,64 | 0,57 | ↓ menos saída |
| 2 | `pct_video_90d` |  | comportamento | 0,55 | 0,53 | 0,57 | 0,53 | 0,61 | 0,60 | ↓ menos saída |
| 3 | `gps_falhas_90d` | ✅ | comportamento | 0,56 | 0,51 | 0,57 | 0,51 | 0,51 | 0,52 | ↑ mais saída |
| 4 | `sistema` |  | cadastro | 0,56 | 0,51 | 0,57 | 0,51 | 0,50 | 0,54 | ↑ mais saída |
| 5 | `canal_cobranca` |  | contrato | 0,56 | 0,53 | 0,56 | 0,54 | 0,58 | 0,56 | ↑ mais saída |
| 6 | `canal_aquisicao` |  | cadastro | 0,55 | 0,55 | 0,55 | 0,54 | 0,57 | 0,55 | ↑ mais saída |
| 7 | `irregularidade_8s` | ✅ | comportamento | 0,54 | 0,55 | 0,54 | 0,56 | 0,55 | 0,60 | ↑ mais saída |
| 8 | `posts_90d` |  | rede social | 0,54 | 0,52 | 0,54 | 0,53 | 0,50 | 0,58 | ↑ mais saída |
| 9 | `dias_ate_renovacao` | ✅ | contrato | 0,74 | 0,72 | 0,54 | 0,53 | 0,68 | 0,62 | ↓ menos saída |
| 10 | `dias_desde_ultimo_treino` |  | comportamento | 0,52 | 0,57 | 0,54 | 0,59 | 0,59 | 0,74 | ↑ mais saída |
| 11 | `seguimentos_reciprocos` | ✅ | rede social | 0,54 | 0,53 | 0,54 | 0,53 | 0,53 | 0,53 | ↓ menos saída |
| 12 | `seguidores` |  | rede social | 0,54 | 0,54 | 0,54 | 0,53 | 0,51 | 0,55 | ↓ menos saída |
| 13 | `seguindo` |  | rede social | 0,54 | 0,54 | 0,53 | 0,53 | 0,51 | 0,56 | ↓ menos saída |
| 14 | `relogio_conectado` |  | cadastro | 0,52 | 0,51 | 0,53 | 0,51 | 0,54 | 0,52 | ↑ mais saída |
| 15 | `semanas_ativas_8s` | ✅ | comportamento | 0,51 | 0,54 | 0,53 | 0,55 | 0,61 | 0,69 | ↓ menos saída |
| 16 | `afetado_reajuste` | ✅ | contrato | 0,65 | 0,56 | 0,53 | 0,58 | — | — | ↑ mais saída |
| 17 | `versao_app` |  | cadastro | 0,53 | 0,51 | 0,53 | 0,52 | 0,56 | 0,56 | ↑ mais saída |
| 18 | `inicio_antes_historico` |  | contrato | 0,54 | 0,54 | 0,53 | 0,53 | 0,58 | 0,50 | ↓ menos saída |
| 19 | `queda_forte` | ✅ | comportamento | 0,52 | 0,54 | 0,52 | 0,54 | 0,52 | 0,53 | ↑ mais saída |
| 20 | `chamados_90d` |  | pagamento e suporte | 0,52 | 0,50 | 0,52 | 0,50 | 0,51 | 0,50 | ↑ mais saída |
| 21 | `treinou_acompanhado_90d` |  | rede social | 0,51 | 0,50 | 0,51 | 0,51 | 0,51 | 0,52 | ↓ menos saída |
| 22 | `chamado_tecnico_90d` |  | pagamento e suporte | 0,51 | 0,51 | 0,51 | 0,51 | 0,51 | 0,51 | ↑ mais saída |
| 23 | `treinos_4s` |  | comportamento | 0,51 | 0,54 | 0,51 | 0,54 | 0,58 | 0,73 | ↓ menos saída |
| 24 | `idade` |  | cadastro | 0,52 | 0,51 | 0,51 | 0,51 | 0,51 | 0,53 | ↓ menos saída |
| 25 | `sessoes_mes` |  | comportamento | 0,51 | 0,52 | 0,51 | 0,53 | 0,60 | 0,68 | ↓ menos saída |
| 26 | `chamado_sem_solucao_em_T` | ✅ | pagamento e suporte | 0,51 | 0,50 | 0,51 | 0,50 | 0,52 | 0,52 | ↑ mais saída |
| 27 | `dias_por_semana_declarado` |  | comportamento | 0,51 | 0,51 | 0,51 | 0,51 | 0,51 | 0,54 | ↑ mais saída |
| 28 | `retentativas` |  | pagamento e suporte | 0,51 | 0,51 | 0,51 | 0,51 | 0,50 | 0,51 | ↑ mais saída |
| 29 | `treinos_primeiros_14d` | ✅ | comportamento | 0,51 | 0,51 | 0,51 | 0,51 | — | — | ↑ mais saída |
| 30 | `em_carencia` |  | contrato | 0,51 | 0,52 | 0,51 | 0,51 | 0,51 | 0,52 | ↑ mais saída |
| 31 | `reclamou_do_app_90d` | ✅ | pagamento e suporte | 0,51 | 0,51 | 0,51 | 0,51 | 0,50 | 0,51 | ↑ mais saída |
| 32 | `recusa_30d` | ✅ | pagamento e suporte | 0,51 | 0,52 | 0,51 | 0,52 | 0,51 | 0,52 | ↑ mais saída |
| 33 | `nivel` |  | comportamento | 0,50 | 0,51 | 0,51 | 0,53 | 0,58 | 0,56 | ↑ mais saída |
| 34 | `sexo` |  | cadastro | 0,51 | 0,51 | 0,51 | 0,51 | 0,51 | 0,54 | ↑ mais saída |
| 35 | `treinos_4s_anteriores` |  | comportamento | 0,52 | 0,51 | 0,51 | 0,50 | 0,57 | 0,66 | ↓ menos saída |
| 36 | `minutos_3m` |  | comportamento | 0,51 | 0,53 | 0,51 | 0,53 | 0,55 | 0,69 | ↓ menos saída |
| 37 | `recusas_90d` |  | pagamento e suporte | 0,51 | 0,53 | 0,51 | 0,52 | 0,51 | 0,52 | ↑ mais saída |
| 38 | `objetivo_informado` |  | comportamento | 0,50 | 0,50 | 0,51 | 0,50 | 0,53 | 0,51 | ↓ menos saída |
| 39 | `variacao_treinos_4s` | ✅ | comportamento | 0,50 | 0,53 | 0,50 | 0,54 | 0,53 | 0,55 | ↓ menos saída |
| 40 | `sessoes_sem_treino_mes` | ✅ | comportamento | 0,50 | 0,50 | 0,50 | 0,50 | 0,55 | 0,53 | ↓ menos saída |
| 41 | `algum_amigo_saiu_60d` | ✅ | rede social | 0,50 | 0,51 | 0,50 | 0,50 | 0,52 | 0,52 | ↑ mais saída |
| 42 | `amigos_que_sairam_60d` | ✅ | rede social | 0,50 | 0,51 | 0,50 | 0,50 | 0,52 | 0,52 | ↑ mais saída |
| 43 | `chamado_cobranca_90d` |  | pagamento e suporte | 0,51 | 0,51 | 0,50 | 0,51 | 0,51 | — | ↑ mais saída |
| 44 | `parceiro_de_treino_saiu` | ✅ | rede social | 0,50 | 0,50 | 0,50 | 0,50 | 0,50 | 0,50 | ↑ mais saída |
| 45 | `plano` |  | contrato | 0,75 | 0,71 | — | — | — | — | ↑ mais saída |
| 46 | `saida_anunciada` |  | contrato | — | — | — | — | — | — | ↑ mais saída |
| 47 | `renova_em_60d` | ✅ | contrato | 0,76 | 0,74 | — | — | — | — | ↑ mais saída |
| 48 | `entrou_com_cupom` | ✅ | contrato | 0,52 | 0,52 | — | — | 0,51 | 0,52 | ↓ menos saída |
| 49 | `cupom_renova_em_60d` | ✅ | contrato | 0,50 | 0,50 | — | — | 0,51 | 0,52 | ↑ mais saída |
| 50 | `tem_onboarding` |  | comportamento | 0,50 | 0,50 | — | — | — | — | ↑ mais saída |
