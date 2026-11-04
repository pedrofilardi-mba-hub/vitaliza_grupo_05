"""Por que as pessoas desligam a renovação, e dá para prever quem vai desligar?

1. Trajetória: para cada assinante pagante que desligou a renovação (ou cancelou pelo site)
   entre 01/03 e 30/09/2026, compara as 8 semanas anteriores com as de um "gêmeo" que não
   desligou (mesmo plano, mesma faixa de tempo de casa, ativo na mesma data).
2. Perfis de motivo: sinais antes do desligamento (parou de treinar, prova concluída,
   problema técnico, cobrança) viram perfis; conferidos contra a pesquisa de saída do site.
3. Novo gabarito: "desligou nos próximos 60 dias", comparado com "saiu nos 60 dias".

Os textos são classificados por palavras-chave (provisório; a leitura com IA é o objetivo 5).
Uso, da raiz do projeto (depois de src/limpeza.py e src/dimensoes.py):

    .venv\\Scripts\\python.exe src\\motivos.py
"""
import re
import sys
from datetime import datetime
from pathlib import Path

import numpy as np
import pandas as pd

sys.path.insert(0, str(Path(__file__).resolve().parent))
from dimensoes import auc  # noqa: E402

RAIZ = Path(__file__).resolve().parents[1]
PROC = RAIZ / 'dados' / 'processados'
DIA = pd.Timedelta(days=1)
RNG = np.random.default_rng(42)

PROVA_CONCLUIDA = r'completei|conclu[ií]d|feita ✅|terminei (minha|uma|um|a) |medalha no peito'
OBJETIVOS = {
    'saude': r'colesterol|dor nas costas|press[aã]o|m[eé]dico|sa[uú]de(?! mental)|sedent|disposi',
    'companhia': r'galera|namorad|grupo|pessoal do trabalho|companhia|amiga|amigo|junto',
    'estetica': r'perder|peso|secar|barriga|emagrec|definir|espelho|em forma',
    'bem_estar': r'dormir|ansiedade|momento s[oó] meu|celular|sa[uú]de mental|desligar a cabe',
    'prova_com_prazo': r'prova|daqui|maratona',
    'desempenho': r'pace|tempo nos|evoluir|planilha|mais r[aá]pido|subir de n[ií]vel',
}


def ler(n):
    return pd.read_parquet(PROC / f'{n}.parquet')


def cat_objetivo(t):
    if not isinstance(t, str):
        return 'nao_informado'
    t = t.lower()
    for k, rx in OBJETIVOS.items():
        if re.search(rx, t):
            return k
    return 'outro'


def main():
    sys.stdout.reconfigure(encoding='utf-8')
    ev, atv, tk, posts = ler('eventos_assinatura'), ler('atividades'), ler('tickets_suporte'), ler('feed_posts')
    onb, pag, q, ass = ler('onboarding'), ler('pagamentos'), ler('pesquisa_saida'), ler('assinaturas')
    onb['objetivo_cat'] = onb.objetivo_texto.map(cat_objetivo)
    obj = onb.set_index('user_id').objetivo_cat
    inicio = ass.set_index('user_id').inicio
    plano_ev = ev.dropna(subset=['plano'])

    # ---------------- desligamentos pagos em 2026 (com 8 semanas de treinos detalhados antes)
    des = ev[(ev.fase == 'pago') & ev.evento.isin(['renovacao_automatica_desligada', 'cancelamento_web'])]
    des = des.sort_values('data_hora').groupby('user_id').first().reset_index()
    des = des[(des.data_hora >= '2026-03-01') & (des.data_hora <= '2026-09-30 23:59:59')][['user_id', 'data_hora']].rename(columns={'data_hora': 'D'})
    ja_desligou = ev[(ev.fase == 'pago') & ev.evento.isin(['renovacao_automatica_desligada', 'cancelamento_web'])].groupby('user_id').data_hora.min()

    # ---------------- gêmeos: mesmo plano, mesma faixa de tempo de casa, ativos e sem desligar em D ± 60 dias
    cob = ev[ev.evento.isin(['assinatura_iniciada', 'renovacao'])].groupby('user_id').data_hora.min()
    fim = ev[ev.evento == 'assinatura_expirada'].groupby('user_id').data_hora.max()
    faixa = lambda meses: pd.cut(meses, [-1, 1, 3, 6, 12, 1000], labels=False)  # noqa: E731
    candidatos = pd.DataFrame({'user_id': cob.index, 'cob': cob.values})
    candidatos['fim'] = candidatos.user_id.map(fim); candidatos['jd'] = candidatos.user_id.map(ja_desligou)
    candidatos['inicio'] = candidatos.user_id.map(inicio)
    gemeos = []
    for D, grupo in des.groupby(des.D.dt.to_period('W')):
        dia = grupo.D.median()
        ok = candidatos[(candidatos.cob <= dia) & (candidatos.fim.isna() | (candidatos.fim > dia + 60 * DIA))
                        & (candidatos.jd.isna() | (candidatos.jd > dia + 60 * DIA))].copy()
        ok['plano'] = ok.user_id.map(plano_ev[plano_ev.data_hora <= dia].groupby('user_id').plano.last())
        ok['faixa'] = faixa((dia - ok.inicio).dt.days / 30.44)
        for _, r in grupo.iterrows():
            pl = plano_ev[(plano_ev.user_id == r.user_id) & (plano_ev.data_hora <= r.D)].plano.iloc[-1:]
            fx = faixa(pd.Series([(r.D - inicio.get(r.user_id)).days / 30.44])).iloc[0]
            pool = ok[(ok.plano == (pl.iloc[0] if len(pl) else None)) & (ok.faixa == fx)]
            if len(pool):
                gemeos.append((pool.user_id.iloc[RNG.integers(len(pool))], r.D))
    gem = pd.DataFrame(gemeos, columns=['user_id', 'D'])
    des['grupo'] = 'desligou'; gem['grupo'] = 'gemeo'
    todos = pd.concat([des, gem], ignore_index=True)
    todos['plano'] = [plano_ev[(plano_ev.user_id == u) & (plano_ev.data_hora <= d)].plano.iloc[-1] if ((plano_ev.user_id == u) & (plano_ev.data_hora <= d)).any() else None
                      for u, d in zip(todos.user_id, todos.D)]

    # ---------------- sinais antes de D
    a = atv[['user_id', 'inicio', 'gps_falhou']].merge(todos[['user_id', 'D', 'grupo']], on='user_id')
    a['semana'] = ((a.D - a.inicio).dt.days // 7)
    a60 = a[(a.inicio < a.D) & (a.semana < 9)]
    a = a[(a.inicio < a.D) & (a['semana'] < 8)]
    semanal = a.groupby(['grupo', 'user_id', 'D', 'semana']).size().unstack(fill_value=0).reindex(columns=range(8), fill_value=0)
    semanal = semanal.reindex(pd.MultiIndex.from_frame(todos[['grupo', 'user_id', 'D']]), fill_value=0)
    todos['treinos_sem_1a4'] = semanal[[0, 1, 2, 3]].sum(axis=1).values
    todos['treinos_sem_5a8'] = semanal[[4, 5, 6, 7]].sum(axis=1).values
    g60 = a60[a60.gps_falhou].groupby(['user_id', 'D']).size()
    todos['gps_falhas_60d'] = [g60.get((u, d), 0) for u, d in zip(todos.user_id, todos.D)]
    p = posts[['user_id', 'data_hora', 'texto']].merge(todos[['user_id', 'D']], on='user_id')
    p = p[(p.data_hora < p.D) & (p.data_hora >= p.D - 30 * DIA)]
    prova = set(map(tuple, p[p.texto.str.lower().str.contains(PROVA_CONCLUIDA, regex=True)][['user_id', 'D']].values))
    todos['prova_concluida_30d'] = [(u, d) in prova for u, d in zip(todos.user_id, todos.D)]
    t = tk[['user_id', 'aberto_em', 'categoria_texto', 'texto_norm']].merge(todos[['user_id', 'D']], on='user_id')
    t = t[(t.aberto_em < t.D) & (t.aberto_em >= t.D - 60 * DIA)]
    chave = lambda df: set(map(tuple, df[['user_id', 'D']].values))  # noqa: E731
    tec, cobr = chave(t[t.categoria_texto == 'tecnico']), chave(t[t.categoria_texto == 'cobranca'])
    todos['chamado_tecnico_60d'] = [(u, d) in tec for u, d in zip(todos.user_id, todos.D)]
    todos['chamado_cobranca_60d'] = [(u, d) in cobr for u, d in zip(todos.user_id, todos.D)]
    pg = pag[pag.status == 'recusado'][['user_id', 'data_hora']].merge(todos[['user_id', 'D']], on='user_id')
    rec = chave(pg[(pg.data_hora < pg.D) & (pg.data_hora >= pg.D - 60 * DIA)])
    todos['recusa_60d'] = [(u, d) in rec for u, d in zip(todos.user_id, todos.D)]
    velho = set(pag[(pag.status == 'aprovado') & (pag.valor == 34.9)].user_id)
    todos['mensal_afetado_reajuste'] = (todos.plano == 'mensal') & todos.user_id.isin(velho)
    todos['objetivo_cat'] = todos.user_id.map(obj).fillna('sem_onboarding')

    # ---------------- perfis (para quem desligou), em ordem de prioridade
    def perfil(r):
        if r.prova_concluida_30d:
            return 'objetivo_cumprido'
        if r.treinos_sem_1a4 == 0 or (r.treinos_sem_5a8 >= 4 and r.treinos_sem_1a4 <= r.treinos_sem_5a8 / 2):
            return 'parou_de_treinar'
        if r.chamado_tecnico_60d or r.gps_falhas_60d >= 2:
            return 'problema_tecnico'
        if r.chamado_cobranca_60d or r.recusa_60d:
            return 'cobranca'
        return 'sem_sinal_claro'
    todos['perfil'] = todos.apply(perfil, axis=1)
    todos.to_parquet(PROC / 'desligamentos_e_gemeos.parquet', index=False)

    # ---------------- conferência com a pesquisa de saída (só quem cancelou pelo site e respondeu)
    qq = q[q.ultima_resposta].set_index('user_id').motivo_revisado
    d1 = todos[todos.grupo == 'desligou'].copy()
    d1['motivo_declarado'] = d1.user_id.map(qq)
    conf = pd.crosstab(d1.perfil, d1.motivo_declarado.fillna('(não respondeu)'))

    # ---------------- novo gabarito: "desligou nos próximos 60 dias"
    res = []
    for T in ['2026-05-31', '2026-07-31']:
        b = pd.read_parquet(PROC / f'base_corte_{T}.parquet')
        Tf = pd.Timestamp(T) + DIA - pd.Timedelta(seconds=1)
        prox = ja_desligou[(ja_desligou > Tf) & (ja_desligou <= Tf + 60 * DIA)].index
        b['desligou_60d'] = b.user_id.isin(prox)
        b = b[~b.saida_anunciada]
        for nome, filtro in [('todos', b.plano.notna()), ('mensais', b.plano == 'mensal'), ('anuais (todos)', b.plano == 'anual'),
                             ('anuais longe da renovação', (b.plano == 'anual') & ~b.renova_em_60d)]:
            x = b[filtro]
            for alvo in ['saiu_60d', 'desligou_60d']:
                cols = [c for c in b.columns if c not in ('user_id', 'inicio', 'saiu_60d', 'desligou_60d', 'saida_anunciada')]
                aucs = sorted(((auc(x[c], x[alvo])[0], c) for c in cols if x[c].nunique() > 1), key=lambda z: -(z[0] if pd.notna(z[0]) else 0))
                top = [(c, a) for a, c in aucs if pd.notna(a)][:5]
                res.append({'corte': T, 'grupo': nome, 'alvo': alvo, 'n': len(x), 'taxa': x[alvo].mean(), 'top': top})

    relatorio(todos, semanal, conf, res)


def relatorio(todos, semanal, conf, res):
    pc = lambda v: f'{v:.1%}'.replace('.', ',')   # noqa: E731
    nm = lambda v: f'{v:,}'.replace(',', '.')      # noqa: E731
    d1, g = todos[todos.grupo == 'desligou'], todos[todos.grupo == 'gemeo']
    L = ['# Por que desligam a renovação, e dá para prever quem vai desligar', '',
         f'Gerado por `src/motivos.py` em {datetime.now():%d/%m/%Y %H:%M}. Os textos são classificados por palavras-chave, de forma provisória; a leitura com IA fica para o objetivo 5.', '',
         f'**Quem entrou:** {nm(len(d1))} assinantes pagantes que desligaram a renovação ou cancelaram pelo site entre 01/03 e 30/09/2026, '
         f'cada um comparado com um **gêmeo** que não desligou (mesmo plano, mesma faixa de tempo de casa, ativo na mesma data; {nm(len(g))} gêmeos encontrados).', '',
         '## 1. O que muda nas semanas antes de desligar', '',
         '| Semanas antes | Treinos por pessoa (desligou) | Treinos por pessoa (gêmeo) |', '|---|---:|---:|']
    med = semanal.groupby(level='grupo').mean()
    for s in range(7, -1, -1):
        L.append(f'| {s + 1}ª | {med.loc["desligou", s]:.2f} | {med.loc["gemeo", s]:.2f} |'.replace('.', ','))
    L += ['', '| Sinal antes de desligar | Desligou | Gêmeo | Quantas vezes mais comum |', '|---|---:|---:|---:|']
    sinais = {'Nenhum treino nas 4 semanas anteriores': lambda x: x.treinos_sem_1a4 == 0,
              'Treinos caíram pela metade ou mais (base de 4+)': lambda x: (x.treinos_sem_5a8 >= 4) & (x.treinos_sem_1a4 <= x.treinos_sem_5a8 / 2),
              'Post de prova concluída nos 30 dias anteriores': lambda x: x.prova_concluida_30d,
              'Chamado técnico nos 60 dias anteriores': lambda x: x.chamado_tecnico_60d,
              '2+ treinos com GPS falho nos 60 dias anteriores': lambda x: x.gps_falhas_60d >= 2,
              'Chamado de cobrança nos 60 dias anteriores': lambda x: x.chamado_cobranca_60d,
              'Cartão recusado nos 60 dias anteriores': lambda x: x.recusa_60d,
              'Mensal que pagava o preço antigo (R$ 34,90)': lambda x: x.mensal_afetado_reajuste}
    for nome, f in sinais.items():
        a, b = f(d1).mean(), f(g).mean()
        L.append(f'| {nome} | {pc(a)} | {pc(b)} | {"—" if b == 0 else f"{a / b:.1f}x".replace(".", ",")} |')
    L += ['', '| Objetivo declarado no onboarding | Desligou | Gêmeo |', '|---|---:|---:|']
    for k in d1.objetivo_cat.value_counts().index:
        L.append(f'| {k} | {pc((d1.objetivo_cat == k).mean())} | {pc((g.objetivo_cat == k).mean())} |')
    L += ['', '## 2. Perfis de motivo de quem desligou', '',
          'Cada pessoa recebe o **primeiro** sinal da lista que se aplica a ela: prova concluída → parou de treinar → problema técnico → cobrança → sem sinal claro.', '',
          '| Perfil | Pessoas | % | Entre os mensais | Entre os anuais |', '|---|---:|---:|---:|---:|']
    for k, n in d1.perfil.value_counts().items():
        L.append(f'| {k} | {nm(n)} | {pc(n / len(d1))} | {pc((d1[d1.plano == "mensal"].perfil == k).mean())} | {pc((d1[d1.plano == "anual"].perfil == k).mean())} |')
    L += ['', '**Conferência com a pesquisa de saída** (quem cancelou pelo site e respondeu; `motivo_revisado`, D-046):', '',
          '| Perfil deduzido \\ motivo declarado | ' + ' | '.join(conf.columns) + ' |', '|---|' + '---:|' * len(conf.columns)]
    for k, r in conf.iterrows():
        L.append(f'| {k} | ' + ' | '.join(str(v) for v in r.values) + ' |')
    L += ['', '## 3. Novo gabarito: "desligou nos próximos 60 dias" × "saiu nos 60 dias"', '',
          'Assinantes ainda sem saída anunciada no corte (D-052). Para cada grupo, a taxa e as 5 dimensões que mais separam (AUC).', '',
          '| Corte | Grupo | Gabarito | Pessoas | Taxa | 5 dimensões que mais separam (AUC) |', '|---|---|---|---:|---:|---|']
    for r in res:
        top = ', '.join(f'`{c}` {a:.2f}'.replace('.', ',') for c, a in r['top'])
        L.append(f'| {r["corte"][8:10]}/{r["corte"][5:7]} | {r["grupo"]} | {r["alvo"]} | {nm(r["n"])} | {pc(r["taxa"])} | {top} |')
    (RAIZ / 'saidas' / 'motivos_desligamento.md').write_text('\n'.join(L) + '\n', encoding='utf-8')
    print('\n'.join(L))


if __name__ == '__main__':
    main()
