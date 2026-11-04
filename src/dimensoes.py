"""Monta a base de assinantes num corte qualquer, com as dimensões novas, e testa cada uma.

Para cada data de corte T:
- uma linha por assinante pagante ativo em T (regra da D-012);
- só informação até T (D-002); nada das colunas de retrato de 01/10 (D-015);
- nos cortes históricos, o gabarito `saiu_60d`: assinatura expirada entre T e T + 60 dias.

Cortes:
- 31/05/2026: gabarito principal (janela jun–jul, antes da campanha de 10/08);
- 31/07/2026: conferência (a campanha cai dentro da janela);
- 30/09/2026: a base para prever (sem gabarito: a janela ainda não aconteceu).

Depois mede, para cada dimensão, quanto ela sozinha separa quem sai de quem fica
(AUC univariado, como no slide 9 da Aula 2) e grava saidas/dimensoes_novas.md.

Uso, da raiz do projeto (depois de rodar src/limpeza.py):

    .venv\\Scripts\\python.exe src\\dimensoes.py
"""
import sys
from datetime import datetime
from pathlib import Path

import numpy as np
import pandas as pd
from sklearn.metrics import roc_auc_score

RAIZ = Path(__file__).resolve().parents[1]
PROC = RAIZ / 'dados' / 'processados'
DIA = pd.Timedelta(days=1)


def ler(nome):
    return pd.read_parquet(PROC / f'{nome}.parquet')


class Dados:
    def __init__(self):
        self.ev = ler('eventos_assinatura'); self.ass = ler('assinaturas'); self.usu = ler('usuarios')
        self.pag = ler('pagamentos'); self.onb = ler('onboarding'); self.atv = ler('atividades')
        self.painel = ler('painel_uso_assinantes'); self.uso = ler('uso_mensal'); self.amz = ler('amizades')
        self.posts = ler('feed_posts'); self.tk = ler('tickets_suporte'); self.camp = ler('campanha_ago26')


def ativos_em(ev, t):
    x = ev[ev.data_hora <= t]
    return set(x[x.evento.isin(['assinatura_iniciada', 'renovacao'])].user_id) - set(x[x.evento == 'assinatura_expirada'].user_id)


def montar(d, T):
    T = pd.Timestamp(T) + DIA - pd.Timedelta(seconds=1)          # fim do dia do corte
    ev = d.ev[d.ev.data_hora <= T]
    b = pd.DataFrame({'user_id': sorted(ativos_em(d.ev, T))})
    m = lambda s: b.user_id.map(s)                                # noqa: E731

    # ---- assinatura e contrato
    cob = ev[ev.evento.isin(['assinatura_iniciada', 'renovacao'])]
    b['plano'] = m(ev.dropna(subset=['plano']).groupby('user_id').plano.last())
    a = d.ass.set_index('user_id')
    b['canal_cobranca'] = m(a.canal_cobranca)
    b['inicio'] = m(a.inicio)
    b['tempo_casa_meses'] = ((T - b.inicio).dt.days / 30.44).round(1)
    b['inicio_antes_historico'] = m(a.inicio_antes_historico)
    ren = ev[ev.evento.isin(['renovacao_automatica_desligada', 'renovacao_automatica_religada', 'cancelamento_web',
                             'assinatura_iniciada', 'renovacao'])].groupby('user_id').evento.last()
    b['saida_anunciada'] = m(ren).isin(['renovacao_automatica_desligada', 'cancelamento_web'])
    b['em_carencia'] = m(ev.groupby('user_id').evento.last()).eq('periodo_carencia')
    ult_cob = m(cob.groupby('user_id').data_hora.max())
    ciclo = np.where(b.plano == 'anual', 365, 30)
    b['dias_ate_renovacao'] = ((ult_cob + pd.to_timedelta(ciclo, unit='D')) - T).dt.days.clip(lower=0)
    b['renova_em_60d'] = b.dias_ate_renovacao <= 60                                   # NOVA (contrato)
    p = d.pag[d.pag.data_hora <= T]; ok = p[p.status == 'aprovado']
    b['afetado_reajuste'] = (b.plano == 'mensal') & m(ok[(ok.valor == 34.9)].groupby('user_id').size()).fillna(0).gt(0) & (T >= pd.Timestamp('2026-03-01'))  # NOVA
    b['entrou_com_cupom'] = m(ok[ok.valor == 239.9].groupby('user_id').size()).fillna(0).gt(0)                                   # NOVA
    b['cupom_renova_em_60d'] = b.entrou_com_cupom & b.renova_em_60d & (b.plano == 'anual')                                       # NOVA

    # ---- cadastro (sexo e idade só para controle: D-018, D-020)
    u = d.usu.set_index('user_id')
    for c in ['canal_aquisicao', 'sistema', 'relogio_conectado', 'versao_app', 'sexo', 'idade']:
        b[c] = m(u[c])

    # ---- pagamento
    b['recusas_90d'] = m(p[(p.status == 'recusado') & (p.data_hora > T - 90 * DIA)].groupby('user_id').size()).fillna(0)
    b['recusa_30d'] = m(p[(p.status == 'recusado') & (p.data_hora > T - 30 * DIA)].groupby('user_id').size()).fillna(0).gt(0)   # NOVA
    b['retentativas'] = m(p[p.retentativa_real].groupby('user_id').size()).fillna(0)

    # ---- onboarding
    o = d.onb.set_index('user_id')
    b['tem_onboarding'] = b.user_id.isin(o.index)
    b['objetivo_informado'] = m(o.objetivo_informado)
    b['nivel'] = m(o.nivel)
    b['dias_por_semana_declarado'] = m(o.dias_por_semana).astype(float)

    # ---- comportamento: treinos detalhados (2026)
    at = d.atv[d.atv.inicio <= T]
    j = lambda ini, fim: at[(at.inicio > T - ini * DIA) & (at.inicio <= T - fim * DIA)]  # noqa: E731
    b['treinos_4s'] = m(j(28, 0).groupby('user_id').size()).fillna(0)
    b['treinos_4s_anteriores'] = m(j(56, 28).groupby('user_id').size()).fillna(0)
    b['variacao_treinos_4s'] = b.treinos_4s - b.treinos_4s_anteriores                                                          # NOVA
    b['queda_forte'] = (b.treinos_4s_anteriores >= 4) & (b.treinos_4s <= b.treinos_4s_anteriores / 2)                          # NOVA
    a8 = j(56, 0).assign(semana=lambda x: ((T - x.inicio).dt.days // 7))
    b['semanas_ativas_8s'] = m(a8.groupby('user_id')['semana'].nunique()).fillna(0)                                            # NOVA
    sem = a8.groupby(['user_id', 'semana']).size().unstack(fill_value=0).reindex(columns=range(8), fill_value=0)
    b['irregularidade_8s'] = m((sem.std(axis=1) / sem.mean(axis=1).replace(0, np.nan)).round(2))                               # NOVA
    b['dias_desde_ultimo_treino'] = (T - m(at.groupby('user_id').inicio.max())).dt.days
    novo = (b.inicio >= pd.Timestamp('2026-01-01')) & (b.inicio + 14 * DIA <= T)
    pri = at.merge(b[['user_id', 'inicio']], on='user_id')
    pri = pri[(pri.inicio_x >= pri.inicio_y) & (pri.inicio_x < pri.inicio_y + 14 * DIA)]
    b['treinos_primeiros_14d'] = np.where(novo, m(pri.groupby('user_id').size()).fillna(0), np.nan)                            # NOVA
    b['gps_falhas_90d'] = m(j(90, 0)[j(90, 0).gps_falhou].groupby('user_id').size()).fillna(0)                                   # NOVA
    tot90 = m(j(90, 0).groupby('user_id').size()).fillna(0)
    b['pct_video_90d'] = (m(j(90, 0)[j(90, 0).modalidade == 'video'].groupby('user_id').size()).fillna(0) / tot90.replace(0, np.nan)).round(2)
    mes_T = T.strftime('%Y-%m')
    us = d.uso[d.uso.mes == mes_T].set_index('user_id')
    b['sessoes_mes'] = m(us.sessoes_app).fillna(0)
    b['sessoes_sem_treino_mes'] = (b.sessoes_mes - m(d.painel[d.painel.mes == mes_T].set_index('user_id').dias_ativos).fillna(0)).clip(lower=0)  # NOVA
    tri = d.painel[(d.painel.mes <= mes_T) & (d.painel.mes > (T - 92 * DIA).strftime('%Y-%m'))]
    b['minutos_3m'] = m(tri.groupby('user_id').minutos.sum()).fillna(0)

    # ---- rede social
    amz = d.amz[d.amz.desde <= T]
    sai = d.ev[(d.ev.evento == 'assinatura_expirada') & (d.ev.data_hora > T - 60 * DIA) & (d.ev.data_hora <= T)].user_id.unique()
    seg = amz.assign(saiu=amz.seguido_id.isin(sai))
    b['seguindo'] = m(seg.groupby('seguidor_id').size()).fillna(0)
    b['seguidores'] = m(amz.groupby('seguido_id').size()).fillna(0)
    b['amigos_que_sairam_60d'] = m(seg.groupby('seguidor_id').saiu.sum()).fillna(0)                                            # NOVA
    b['algum_amigo_saiu_60d'] = b.amigos_que_sairam_60d > 0                                                                     # NOVA
    pares = set(zip(amz.seguidor_id, amz.seguido_id))
    b['seguimentos_reciprocos'] = m(amz[[(s, f) in pares for f, s in zip(amz.seguidor_id, amz.seguido_id)]].groupby('seguidor_id').size()).fillna(0)  # NOVA
    ativosT = set(b.user_id)
    comp = j(90, 0).dropna(subset=['treino_com'])
    b['treinou_acompanhado_90d'] = m(comp.groupby('user_id').size()).fillna(0)
    b['parceiro_de_treino_saiu'] = m(comp.assign(fora=~comp.treino_com.isin(ativosT)).groupby('user_id').fora.any()).fillna(False)  # NOVA
    ps = d.posts[(d.posts.data_hora <= T) & (d.posts.data_hora > T - 90 * DIA)]
    b['posts_90d'] = m(ps.groupby('user_id').size()).fillna(0)

    # ---- suporte (situação em T)
    tk = d.tk[d.tk.aberto_em <= T]
    aberto_T = tk.resolvido_em.isna() | (tk.resolvido_em > T)
    b['chamado_sem_solucao_em_T'] = b.user_id.isin(tk[aberto_T].user_id)                                                        # NOVA (no corte T)
    t90 = tk[tk.aberto_em > T - 90 * DIA]
    b['chamados_90d'] = m(t90.groupby('user_id').size()).fillna(0)
    b['chamado_cobranca_90d'] = b.user_id.isin(t90[t90.categoria_texto == 'cobranca'].user_id)
    b['chamado_tecnico_90d'] = b.user_id.isin(t90[t90.categoria_texto == 'tecnico'].user_id)
    b['reclamou_do_app_90d'] = b.user_id.isin(t90[t90.texto_norm.str.contains('atualiza|bug|trav|gps', regex=True)].user_id)  # NOVA

    # ---- gabarito: saiu nos 60 dias seguintes (só nos cortes históricos)
    fim = T + 60 * DIA
    exp = d.ev[(d.ev.evento == 'assinatura_expirada') & (d.ev.data_hora > T) & (d.ev.data_hora <= fim)].user_id
    b['saiu_60d'] = b.user_id.isin(set(exp)) if fim <= pd.Timestamp('2026-09-30 23:59:59') else np.nan
    return b


NOVAS = ['renova_em_60d', 'dias_ate_renovacao', 'afetado_reajuste', 'entrou_com_cupom', 'cupom_renova_em_60d', 'recusa_30d',
         'variacao_treinos_4s', 'queda_forte', 'semanas_ativas_8s', 'irregularidade_8s', 'treinos_primeiros_14d', 'gps_falhas_90d',
         'sessoes_sem_treino_mes', 'amigos_que_sairam_60d', 'algum_amigo_saiu_60d', 'seguimentos_reciprocos', 'parceiro_de_treino_saiu',
         'chamado_sem_solucao_em_T', 'reclamou_do_app_90d']
FAMILIA = {**{c: 'contrato' for c in ['renova_em_60d', 'dias_ate_renovacao', 'afetado_reajuste', 'entrou_com_cupom', 'cupom_renova_em_60d',
                                      'plano', 'canal_cobranca', 'tempo_casa_meses', 'saida_anunciada', 'em_carencia', 'inicio_antes_historico']},
           **{c: 'comportamento' for c in ['variacao_treinos_4s', 'queda_forte', 'semanas_ativas_8s', 'irregularidade_8s', 'treinos_primeiros_14d',
                                           'gps_falhas_90d', 'sessoes_sem_treino_mes', 'treinos_4s', 'treinos_4s_anteriores', 'dias_desde_ultimo_treino',
                                           'pct_video_90d', 'sessoes_mes', 'minutos_3m', 'dias_por_semana_declarado', 'nivel', 'objetivo_informado', 'tem_onboarding']},
           **{c: 'rede social' for c in ['amigos_que_sairam_60d', 'algum_amigo_saiu_60d', 'seguimentos_reciprocos', 'parceiro_de_treino_saiu',
                                         'seguindo', 'seguidores', 'treinou_acompanhado_90d', 'posts_90d']},
           **{c: 'pagamento e suporte' for c in ['recusa_30d', 'recusas_90d', 'retentativas', 'chamado_sem_solucao_em_T', 'chamados_90d',
                                                 'chamado_cobranca_90d', 'chamado_tecnico_90d', 'reclamou_do_app_90d']},
           **{c: 'cadastro' for c in ['canal_aquisicao', 'sistema', 'relogio_conectado', 'versao_app', 'sexo', 'idade']}}


def auc(x, y):
    """AUC univariado: numérico pelo próprio valor; categórico pela taxa de saída de cada categoria. Sempre >= 0,5 (direção indicada)."""
    ok = x.notna()
    x, y = x[ok], y[ok].astype(int)
    if y.nunique() < 2 or len(x) < 50:
        return np.nan, '', ok.mean()
    if x.dtype == object or isinstance(x.dtype, pd.CategoricalDtype) or x.dtype.name in ('str', 'string'):
        score = x.map(y.groupby(x).mean())
    else:
        score = x.astype(float)
    a = roc_auc_score(y, score)
    return max(a, 1 - a), ('↑ mais saída' if a >= 0.5 else '↓ menos saída'), ok.mean()


def main():
    sys.stdout.reconfigure(encoding='utf-8')
    d = Dados()
    bases = {}
    for T in ['2026-05-31', '2026-07-31', '2026-09-30']:
        b = montar(d, T)
        b.to_parquet(PROC / f'base_corte_{T}.parquet', index=False)
        bases[T] = b
        print(T, len(b), 'saiu_60d:', b.saiu_60d.mean() if b.saiu_60d.notna().any() else '-')
    cols = [c for c in bases['2026-05-31'].columns if c not in ('user_id', 'inicio', 'saiu_60d')]
    linhas = []
    for c in cols:
        r = {'dimensao': c, 'nova': c in NOVAS, 'familia': FAMILIA.get(c, '')}
        for T in ['2026-05-31', '2026-07-31']:
            b = bases[T]
            a1, dirc, cob = auc(b[c], b.saiu_60d)
            sem = b[~b.saida_anunciada]
            a2, _, _ = auc(sem[c], sem.saiu_60d) if c != 'saida_anunciada' else (np.nan, '', 0)
            r[f'auc_{T}'] = a1; r[f'auc_sem_anunciados_{T}'] = a2; r['direcao'] = r.get('direcao') or dirc; r['cobertura'] = cob
        linhas.append(r)
    res = pd.DataFrame(linhas)
    # quem pode sair na janela: mensais, e anuais que renovam nos 60 dias (sem os que já anunciaram)
    for nome, filtro in [('mensal', lambda b: (b.plano == 'mensal') & ~b.saida_anunciada),
                         ('anual_renova', lambda b: (b.plano == 'anual') & b.renova_em_60d & ~b.saida_anunciada)]:
        for T in ['2026-05-31', '2026-07-31']:
            b = bases[T][filtro(bases[T])]
            res[f'auc_{nome}_{T}'] = [auc(b[c], b.saiu_60d)[0] if b[c].nunique() > 1 else np.nan for c in res.dimensao]
    res = res.sort_values('auc_mensal_2026-05-31', ascending=False)
    res.to_csv(RAIZ / 'saidas' / 'dimensoes_auc.csv', index=False)
    relatorio(bases, res)


def taxa(b, mask):
    return f'{b[mask].saiu_60d.mean():.1%} (n={int(mask.sum()):,})'.replace(',', '.').replace('.', ',', 1) if mask.sum() else '—'


def relatorio(bases, res):
    def f(x): return '—' if pd.isna(x) else f'{x:.2f}'.replace('.', ',')
    b5, b7 = bases['2026-05-31'], bases['2026-07-31']
    s5 = b5[~b5.saida_anunciada]
    L = ['# Dimensões novas: quanto cada uma separa quem sai', '',
         f'Gerado por `src/dimensoes.py` em {datetime.now():%d/%m/%Y %H:%M}. Para cada data de corte, uma linha por assinante ativo, '
         'só com o que se sabia até aquele dia; o gabarito é se a pessoa **saiu nos 60 dias seguintes**.', '',
         '| Corte | Assinantes | Saíram em 60 dias | Já tinham anunciado a saída | Saída entre os anunciados | Saída entre os demais |',
         '|---|---:|---:|---:|---:|---:|']
    for T, b in [('31/05/2026 (principal)', b5), ('31/07/2026 (conferência, campanha no meio)', b7)]:
        an = b.saida_anunciada
        pc = lambda x: f'{x:.1%}'.replace('.', ',')            # noqa: E731
        nm = lambda x: f'{x:,}'.replace(',', '.')               # noqa: E731
        L.append(f'| {T} | {nm(len(b))} | {pc(b.saiu_60d.mean())} | {nm(int(an.sum()))} ({pc(an.mean())}) | '
                 f'{pc(b[an].saiu_60d.mean())} | {pc(b[~an].saiu_60d.mean())} |')
    L += ['', '**Como ler o AUC:** 0,50 = a dimensão não separa nada (acaso); 1,00 = separa perfeitamente. É a mesma régua do slide 9 da Aula 2. '
          'Mostramos o AUC **sem os assinantes que já tinham anunciado a saída**, porque para eles a resposta já é quase certa e eles inflariam qualquer número.', '',
          'Os grupos separados importam: um anual que só renova daqui a meses **não pode** sair na janela, e isso domina qualquer número da base toda. '
          'Por isso o ranking mostra também os **mensais** (podem sair a qualquer mês) e os **anuais que renovam na janela**, sempre sem os que já anunciaram a saída.', '',
          '## Ranking (ordenado pelo AUC entre os mensais, corte principal)', '',
          '| # | Dimensão | Nova? | Família | Todos 31/05 | Todos 31/07 | Mensais 31/05 | Mensais 31/07 | Anuais que renovam 31/05 | Anuais que renovam 31/07 | Direção |',
          '|---:|---|:-:|---|---:|---:|---:|---:|---:|---:|---|']
    for i, r in enumerate(res.to_dict('records'), 1):
        L.append(f'| {i} | `{r["dimensao"]}` | {"✅" if r["nova"] else ""} | {r["familia"]} | {f(r["auc_sem_anunciados_2026-05-31"])} | '
                 f'{f(r["auc_sem_anunciados_2026-07-31"])} | {f(r["auc_mensal_2026-05-31"])} | {f(r["auc_mensal_2026-07-31"])} | '
                 f'{f(r["auc_anual_renova_2026-05-31"])} | {f(r["auc_anual_renova_2026-07-31"])} | {r["direcao"]} |')
    (RAIZ / 'saidas' / 'dimensoes_novas.md').write_text('\n'.join(L) + '\n', encoding='utf-8')
    for nome, filtro in [('mensal', lambda b: (b.plano == 'mensal') & ~b.saida_anunciada),
                         ('anual_renova', lambda b: (b.plano == 'anual') & b.renova_em_60d & ~b.saida_anunciada)]:
        for T in ['2026-05-31', '2026-07-31']:
            b = bases[T][filtro(bases[T])]
            print(nome, T, 'n', len(b), 'saida', round(b.saiu_60d.mean(), 3))
    pd.set_option('display.width', 250)
    print(res[['dimensao', 'nova', 'auc_mensal_2026-05-31', 'auc_mensal_2026-07-31', 'auc_anual_renova_2026-05-31', 'auc_anual_renova_2026-07-31', 'direcao']].head(30).round(3).to_string())


if __name__ == '__main__':
    main()
