# Base integrada no corte (30/09/2026)

Gerada por `src/base_integrada.py` em 03/11/2026 20:53, a partir da cópia limpa (`src/limpeza.py`). Uma linha por assinante pagante ativo em 30/09/2026, só com o que se sabia até o corte (D-002). Não usa as colunas de retrato de 01/10 (D-015). O alvo (saída até 29/11) fica para o objetivo 4.

**Assinantes:** 14.753 (enunciado: 14.753) · **colunas:** 49 · arquivo: `dados/processados/base_assinantes_corte.parquet`

## Retrato da base

| Medida | Valor | Referência |
|---|---:|---|
| Plano anual / mensal | 57,5% / 42,5% | enunciado: 57% / 43% |
| Paga pela loja (App Store + Google Play) | 70,2% | enunciado: 70,2% |
| App Store / Google Play / cartão / Pix | 36,6% / 33,6% / 20,3% / 9,5% | enunciado: 36,6% / 33,6% / 20,3% / 9,5% |
| Já anunciaram a saída (renovação desligada ou cancelamento web) | 2.250 (15,3%) | avaliação dos eventos: 2.250 |
| Em período de carência no corte | 25 | avaliação dos eventos: 25 |
| Tempo de casa (mediana, meses) | 8,6 | |
| Sem nenhum treino em jul–set/2026 | 5,0% | |
| Dias desde o último treino (mediana) | 2 | |
| Com chamado sem solução no corte | 6,3% | |
| Sorteados na campanha de agosto | 87,2% | os demais começaram a pagar depois de 10/08 |
| Têm onboarding | 100,0% | |

## Colunas

| Grupo | Colunas |
|---|---|
| Identificação | `user_id`, `pessoa_id` |
| Assinatura | `plano`, `canal_cobranca`, `inicio`, `tempo_casa_meses`, `inicio_antes_historico` (D-014), `saida_anunciada`, `em_carencia`, `n_renovacoes`, `ciclo_atipico` |
| Cadastro | `canal_aquisicao`, `sistema`, `uf`, `cidade`, `relogio_conectado`, `versao_app`; `sexo`, `idade`, `idade_informada`, `menor_de_idade` (só para controle, D-018/D-020) |
| Pagamentos | `receita_liquida_total`, `recusas_90d`, `retentativas` (D-051), `pagou_preco_antigo` |
| Onboarding | `tem_onboarding` (D-008), `objetivo_informado`, `nivel`, `dias_por_semana` |
| Uso (jul–set/2026) | `treinos_3m`, `minutos_3m`, `dias_ativos_3m`, `sessoes_app_3m`, `meses_sem_treino_3m`, `variacao_minutos_jul_set`, `dias_desde_ultimo_treino`, `pct_ar_livre_2026`, `pct_treinos_acompanhado_2026` |
| Rede e posts | `seguidores`, `seguindo`, `posts_90d`, `curtidas_media_90d` |
| Suporte | `chamados_90d`, `chamado_sem_solucao_no_corte`, `chamados_cobranca_90d`, `chamados_tecnico_90d`, `chamados_cancelamento_90d` (categoria pelo texto, D-040) |
| Campanha e pesquisa | `grupo_campanha` (D-038), `motivo_saida_declarado` (D-046/D-047) |

## Cuidados para o modelo (objetivo 4)

- **`saida_anunciada`** quase garante a saída nos 60 dias. O grupo decide se esses assinantes vão para uma regra à parte ou entram no modelo (observação da avaliação dos eventos).
- **`motivo_saida_declarado`** só existe para quem já cancelou pelo site: é consequência da decisão de sair, não causa. Não usar como variável de previsão.
- **`sexo` e `idade`** só para controle, nunca para decidir quem recebe oferta (D-018, D-020).
- **`tempo_casa_meses`** dos clientes anteriores a 07/2024 vem de sobreviventes (D-014).
- Para treinar o modelo, é preciso repetir esta montagem num corte anterior (ex.: 31/07/2026) e observar a saída nos 60 dias seguintes, que caem antes de 30/09.
