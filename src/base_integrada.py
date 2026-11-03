"""Base integrada no corte: uma linha por assinante pagante ativo em 30/09/2026.

Junta a cópia limpa (dados/processados/, gerada por src/limpeza.py) usando só o que
se sabia até o corte (D-002). Não usa as colunas de retrato de 01/10 (D-015) nem
nenhum dado posterior. O alvo (saída nos 60 dias) não está aqui: ele cai depois do
corte e será montado no objetivo 4 com cortes históricos.

Uso, da raiz do projeto (depois de rodar src/limpeza.py):

    .venv\\Scripts\\python.exe src\\base_integrada.py
"""
import sys
from datetime import datetime
from pathlib import Path

import numpy as np
import pandas as pd

RAIZ = Path(__file__).resolve().parents[1]
PROC = RAIZ / 'dados' / 'processados'
CORTE = pd.Timestamp('2026-09-30 23:59:59')
JAN90 = CORTE - pd.Timedelta(days=90)


def ler(nome):
    return pd.read_parquet(PROC / f'{nome}.parquet')


def main():
    sys.stdout.reconfigure(encoding='utf-8')
    ev, ass, usu = ler('eventos_assinatura'), ler('assinaturas'), ler('usuarios')
    ev = ev[ev.data_hora <= CORTE]
    # quem é assinante pagante ativo no corte (regra da D-012)
    pagou = set(ev[ev.evento.isin(['assinatura_iniciada', 'renovacao'])].user_id)
    saiu = set(ev[ev.evento == 'assinatura_expirada'].user_id)
    ids = sorted(pagou - saiu)
    b = pd.DataFrame({'user_id': ids})

    # assinatura (sem as colunas de retrato, D-015)
    a = ass.set_index('user_id')
    b['plano'] = b.user_id.map(ev.dropna(subset=['plano']).groupby('user_id').plano.last())
    b['canal_cobranca'] = b.user_id.map(a.canal_cobranca)
    b['inicio'] = b.user_id.map(a.inicio)
    b['tempo_casa_meses'] = ((CORTE - b.inicio).dt.days / 30.44).round(1)
    b['inicio_antes_historico'] = b.user_id.map(a.inicio_antes_historico)

    # situação da renovação no corte (eventos até 30/09)
    ren = ev[ev.evento.isin(['renovacao_automatica_desligada', 'renovacao_automatica_religada', 'cancelamento_web',
                             'assinatura_iniciada', 'renovacao'])].groupby('user_id').evento.last()
    b['saida_anunciada'] = b.user_id.map(ren).isin(['renovacao_automatica_desligada', 'cancelamento_web'])
    b['em_carencia'] = b.user_id.map(ev.groupby('user_id').evento.last()).eq('periodo_carencia')
    b['n_renovacoes'] = b.user_id.map(ev[ev.evento == 'renovacao'].groupby('user_id').size()).fillna(0).astype(int)
    b['ciclo_atipico'] = b.user_id.map(ev.groupby('user_id').ciclo_atipico.any()).fillna(False)

    # cadastro (sexo e idade só para descrever e controlar, D-018 e D-020)
    u = usu.set_index('user_id')
    for c in ['pessoa_id', 'canal_aquisicao', 'sistema', 'uf', 'cidade', 'relogio_conectado', 'versao_app', 'sexo', 'idade', 'idade_informada', 'menor_de_idade']:
        b[c] = b.user_id.map(u[c])

    # pagamentos até o corte
    p = ler('pagamentos'); p = p[p.data_hora <= CORTE]
    ok = p[p.status == 'aprovado']
    b['receita_liquida_total'] = b.user_id.map(ok.groupby('user_id').valor_liquido.sum()).fillna(0).round(2)
    b['recusas_90d'] = b.user_id.map(p[(p.status == 'recusado') & (p.data_hora > JAN90)].groupby('user_id').size()).fillna(0).astype(int)
    b['retentativas'] = b.user_id.map(p[p.retentativa_real].groupby('user_id').size()).fillna(0).astype(int)
    b['pagou_preco_antigo'] = b.user_id.map(ok[(ok.valor == 34.9) & (ok.data_hora < '2026-03-01')].groupby('user_id').size()).fillna(0).gt(0)

    # onboarding (tem_onboarding, D-008)
    o = ler('onboarding').set_index('user_id')
    b['tem_onboarding'] = b.user_id.isin(o.index)
    for c in ['objetivo_informado', 'nivel', 'dias_por_semana']:
        b[c] = b.user_id.map(o[c])

    # uso: painel padronizado (D-028/D-029), últimos 3 meses
    pu = ler('painel_uso_assinantes')
    tri = pu[pu.mes.isin(['2026-07', '2026-08', '2026-09'])]
    g = tri.groupby('user_id')
    b['treinos_3m'] = b.user_id.map(g.atividades.sum()).fillna(0)
    b['minutos_3m'] = b.user_id.map(g.minutos.sum()).fillna(0).round(0)
    b['dias_ativos_3m'] = b.user_id.map(g.dias_ativos.sum()).fillna(0)
    b['sessoes_app_3m'] = b.user_id.map(g.sessoes_app.sum()).fillna(0)
    b['meses_sem_treino_3m'] = b.user_id.map(g.atividades.apply(lambda s: int((s == 0).sum()))).fillna(3).astype(int)
    set_, jul = pu[pu.mes == '2026-09'].set_index('user_id').minutos, pu[pu.mes == '2026-07'].set_index('user_id').minutos
    b['variacao_minutos_jul_set'] = (b.user_id.map(set_).fillna(0) - b.user_id.map(jul).fillna(0)).round(0)

    # treinos detalhados: recência e modalidade
    at = ler('atividades'); at = at[at.inicio <= CORTE]
    ult = at.groupby('user_id').inicio.max()
    b['dias_desde_ultimo_treino'] = (CORTE - b.user_id.map(ult)).dt.days
    tot = at.groupby('user_id').size()
    b['pct_ar_livre_2026'] = (b.user_id.map(at[at.modalidade == 'ar_livre'].groupby('user_id').size()).fillna(0) / b.user_id.map(tot)).round(2)
    b['pct_treinos_acompanhado_2026'] = (b.user_id.map(at[at.treino_com.notna()].groupby('user_id').size()).fillna(0) / b.user_id.map(tot)).round(3)

    # rede social e posts
    am = ler('amizades')
    b['seguidores'] = b.user_id.map(am.groupby('seguido_id').size()).fillna(0).astype(int)
    b['seguindo'] = b.user_id.map(am.groupby('seguidor_id').size()).fillna(0).astype(int)
    fp = ler('feed_posts')
    f90 = fp[fp.data_hora > JAN90]
    b['posts_90d'] = b.user_id.map(f90.groupby('user_id').size()).fillna(0).astype(int)
    b['curtidas_media_90d'] = b.user_id.map(f90.groupby('user_id').curtidas.mean()).round(1)

    # suporte, com a situação no corte (D-041) e categoria pelo texto (D-040)
    tk = ler('tickets_suporte')
    t90 = tk[tk.aberto_em > JAN90]
    b['chamados_90d'] = b.user_id.map(t90.groupby('user_id').size()).fillna(0).astype(int)
    b['chamado_sem_solucao_no_corte'] = b.user_id.isin(tk[tk.status_no_corte.isin(['aberto', 'sem_resposta'])].user_id)
    for cat in ['cobranca', 'tecnico', 'cancelamento']:
        b[f'chamados_{cat}_90d'] = b.user_id.map(t90[t90.categoria_texto == cat].groupby('user_id').size()).fillna(0).astype(int)

    # campanha de agosto (para o uplift do objetivo 6; regra da D-038)
    c = ler('campanha_ago26').set_index('user_id')
    b['grupo_campanha'] = b.user_id.map(c.grupo).fillna('nao_sorteado')

    # pesquisa de saída (só quem cancelou pelo site, D-047)
    q = ler('pesquisa_saida'); q = q[q.ultima_resposta]
    b['motivo_saida_declarado'] = b.user_id.map(q.set_index('user_id').motivo_revisado)

    b.to_parquet(PROC / 'base_assinantes_corte.parquet', index=False)

    # resumo agregado (sem dados por pessoa) em saidas/base_integrada.md
    def pct(x): return f'{x:.1%}'.replace('.', ',')
    def n(x): return f'{x:,.0f}'.replace(',', '.')
    L = ['# Base integrada no corte (30/09/2026)', '',
         f'Gerada por `src/base_integrada.py` em {datetime.now():%d/%m/%Y %H:%M}, a partir da cópia limpa (`src/limpeza.py`). '
         'Uma linha por assinante pagante ativo em 30/09/2026, só com o que se sabia até o corte (D-002). '
         'Não usa as colunas de retrato de 01/10 (D-015). O alvo (saída até 29/11) fica para o objetivo 4.', '',
         f'**Assinantes:** {n(len(b))} (enunciado: 14.753) · **colunas:** {b.shape[1]} · arquivo: `dados/processados/base_assinantes_corte.parquet`', '',
         '## Retrato da base', '',
         '| Medida | Valor | Referência |', '|---|---:|---|',
         f'| Plano anual / mensal | {pct((b.plano == "anual").mean())} / {pct((b.plano == "mensal").mean())} | enunciado: 57% / 43% |',
         f'| Paga pela loja (App Store + Google Play) | {pct(b.canal_cobranca.isin(["app_store", "google_play"]).mean())} | enunciado: 70,2% |',
         f'| App Store / Google Play / cartão / Pix | {" / ".join(pct((b.canal_cobranca == k).mean()) for k in ["app_store", "google_play", "web_cartao", "web_pix"])} | enunciado: 36,6% / 33,6% / 20,3% / 9,5% |',
         f'| Já anunciaram a saída (renovação desligada ou cancelamento web) | {n(b.saida_anunciada.sum())} ({pct(b.saida_anunciada.mean())}) | avaliação dos eventos: 2.250 |',
         f'| Em período de carência no corte | {n(b.em_carencia.sum())} | avaliação dos eventos: 25 |',
         f'| Tempo de casa (mediana, meses) | {b.tempo_casa_meses.median():.1f} | |'.replace('.', ','),
         f'| Sem nenhum treino em jul–set/2026 | {pct((b.treinos_3m == 0).mean())} | |',
         f'| Dias desde o último treino (mediana) | {b.dias_desde_ultimo_treino.median():.0f} | |',
         f'| Com chamado sem solução no corte | {pct(b.chamado_sem_solucao_no_corte.mean())} | |',
         f'| Sorteados na campanha de agosto | {pct((b.grupo_campanha != "nao_sorteado").mean())} | os demais começaram a pagar depois de 10/08 |',
         f'| Têm onboarding | {pct(b.tem_onboarding.mean())} | |', '',
         '## Colunas', '',
         '| Grupo | Colunas |', '|---|---|',
         '| Identificação | `user_id`, `pessoa_id` |',
         '| Assinatura | `plano`, `canal_cobranca`, `inicio`, `tempo_casa_meses`, `inicio_antes_historico` (D-014), `saida_anunciada`, `em_carencia`, `n_renovacoes`, `ciclo_atipico` |',
         '| Cadastro | `canal_aquisicao`, `sistema`, `uf`, `cidade`, `relogio_conectado`, `versao_app`; `sexo`, `idade`, `idade_informada`, `menor_de_idade` (só para controle, D-018/D-020) |',
         '| Pagamentos | `receita_liquida_total`, `recusas_90d`, `retentativas` (D-051), `pagou_preco_antigo` |',
         '| Onboarding | `tem_onboarding` (D-008), `objetivo_informado`, `nivel`, `dias_por_semana` |',
         '| Uso (jul–set/2026) | `treinos_3m`, `minutos_3m`, `dias_ativos_3m`, `sessoes_app_3m`, `meses_sem_treino_3m`, `variacao_minutos_jul_set`, `dias_desde_ultimo_treino`, `pct_ar_livre_2026`, `pct_treinos_acompanhado_2026` |',
         '| Rede e posts | `seguidores`, `seguindo`, `posts_90d`, `curtidas_media_90d` |',
         '| Suporte | `chamados_90d`, `chamado_sem_solucao_no_corte`, `chamados_cobranca_90d`, `chamados_tecnico_90d`, `chamados_cancelamento_90d` (categoria pelo texto, D-040) |',
         '| Campanha e pesquisa | `grupo_campanha` (D-038), `motivo_saida_declarado` (D-046/D-047) |', '',
         '## Cuidados para o modelo (objetivo 4)', '',
         '- **`saida_anunciada`** quase garante a saída nos 60 dias. O grupo decide se esses assinantes vão para uma regra à parte ou entram no modelo (observação da avaliação dos eventos).',
         '- **`motivo_saida_declarado`** só existe para quem já cancelou pelo site: é consequência da decisão de sair, não causa. Não usar como variável de previsão.',
         '- **`sexo` e `idade`** só para controle, nunca para decidir quem recebe oferta (D-018, D-020).',
         '- **`tempo_casa_meses`** dos clientes anteriores a 07/2024 vem de sobreviventes (D-014).',
         '- Para treinar o modelo, é preciso repetir esta montagem num corte anterior (ex.: 31/07/2026) e observar a saída nos 60 dias seguintes, que caem antes de 30/09.']
    (RAIZ / 'saidas' / 'base_integrada.md').write_text('\n'.join(L) + '\n', encoding='utf-8')
    print('\n'.join(L[:20]))


if __name__ == '__main__':
    main()
