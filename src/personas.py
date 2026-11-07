"""Números das personas (a partir da segmentação escolhida, D-054).

4 personas: Novatos, Treino em casa, Rua no ritmo leve e "O atleta" (Intensos + Longões, D-055).
Para cada persona calcula, só com agregados:
  - perfil e valor em 30/09 (tamanho, plano, canal de cobrança, objetivo, receita mensal estimada);
  - saída histórica (régua de 30/09 aplicada em 31/05, gabarito D-053, sem saída anunciada, D-052) e sinais;
  - o gatilho de cada persona HOJE (30/09): quantas pessoas estão com o sinal e ainda não anunciaram a saída,
    para dimensionar a ação contra a capacidade do CRM (WhatsApp 1.500/mês, CS 300/mês, enunciado seção 03).

Grava saidas/personas.json. Uso, da raiz:  .venv\\Scripts\\python.exe src\\personas.py
"""
import json
import sys
from pathlib import Path

import numpy as np
import pandas as pd

RAIZ = Path(__file__).resolve().parents[1]
PROC = RAIZ / 'dados' / 'processados'
sys.path.insert(0, str(RAIZ / 'src'))
from clusters import LIQ, Regua, base_31_05, bruto_30, nomear  # noqa: E402
from clusters_cenarios import montar_base  # noqa: E402

PROVA_CONCLUIDA = r'completei|conclu[ií]d|feita ✅|terminei (minha|uma|um|a) |medalha no peito'   # mesma regra de src/motivos.py
PERSONAS = {
    'O novato que ainda está chegando': ['Novatos'],
    'Quem treina em casa': ['Treino em casa'],
    'O corredor de rua no ritmo leve': ['Rua no ritmo leve'],
    'O atleta': ['Intensos', 'Longões'],
}


def taxa(s):
    return round(float(s.mean()), 4) if len(s) else None


def main():
    sys.stdout.reconfigure(encoding='utf-8')
    b = montar_base()
    regua = Regua().fit(bruto_30(b))
    lab = regua.km.labels_
    g = b.assign(g=lab)
    prof = g.groupby('g')[['tempo_casa_meses', 'treinos_semana', 'min_por_treino']].median()
    prof['pct_ar_livre'] = g.groupby('g').pct_ar_livre_2026.median()
    nomes = nomear(prof)
    b['nome_grupo'] = pd.Series(lab, index=b.index).map(nomes)
    conf = pd.read_parquet(PROC / 'clusters_2026-09-30.parquet').set_index('user_id').nome_grupo
    assert (b.set_index('user_id').nome_grupo == conf.reindex(b.user_id).values).all(), 'grupos diferentes do arquivo gravado'

    # sinais de hoje (30/09) que vêm da base do corte
    d30 = pd.read_parquet(PROC / 'base_corte_2026-09-30.parquet').set_index('user_id')
    for c in ['queda_forte', 'chamado_tecnico_90d', 'renova_em_60d']:
        b[c] = b.user_id.map(d30[c]).fillna(False).astype(bool)
    fp = pd.read_parquet(PROC / 'feed_posts.parquet')
    fp = fp[(fp.data_hora > '2026-08-31') & (fp.data_hora <= '2026-09-30 23:59:59')]
    b['prova_concluida_30d'] = b.user_id.isin(fp[fp.texto.str.lower().str.contains(PROVA_CONCLUIDA.replace('(', '(?:'), regex=True, na=False)].user_id)
    b['parado_14d'] = b.dias_desde_ultimo_treino.fillna(999) >= 14
    b['mrr_liq'] = np.where(b.plano == 'mensal', 39.90, 299.90 / 12) * b.canal_cobranca.map(LIQ).fillna(.85)

    # saída histórica (31/05)
    b5, raw5 = base_31_05()
    b5['nome_grupo'] = pd.Series(regua.prever(raw5), index=b5.index).map(nomes)
    m5 = b5[~b5.saida_anunciada]
    base_taxa, total_des = float(m5.desligou_60d.mean()), int(m5.desligou_60d.sum())

    # gatilho de cada persona: o sinal que mais aumentou a saída dentro dela em 31/05 (seção 7 da aba Segmentação escolhida)
    gatilhos = {
        'O novato que ainda está chegando': ('treino caiu forte nas últimas 4 semanas (ou chamado técnico)', lambda s: s.queda_forte | s.chamado_tecnico_90d),
        'Quem treina em casa': ('14+ dias sem treinar (ainda treinou em 2026)', lambda s: s.parado_14d & (s.treinos_3m > 0)),
        'O corredor de rua no ritmo leve': ('treino caiu forte nas últimas 4 semanas (ou chamado técnico)', lambda s: s.queda_forte | s.chamado_tecnico_90d),
        'O atleta': ('treino caiu forte, chamado técnico ou post de prova concluída nos últimos 30 dias', lambda s: s.queda_forte | s.chamado_tecnico_90d | s.prova_concluida_30d),
    }
    extras = {  # contagens de apoio, hoje, entre quem ainda não anunciou a saída
        'no_1o_ou_2o_mes': lambda s: s.tempo_casa_meses <= 2,
        'parado_14d': lambda s: s.parado_14d,
        'sem_treino_3m': lambda s: s.treinos_3m == 0,
        'queda_forte': lambda s: s.queda_forte,
        'prova_concluida_30d': lambda s: s.prova_concluida_30d,
        'chamado_tecnico_90d': lambda s: s.chamado_tecnico_90d,
    }
    sinais5 = {
        'Plano mensal': lambda h: h.plano == 'mensal',
        'Treino caiu forte (4 semanas)': lambda h: h.queda_forte,
        '14+ dias sem treinar': lambda h: h.dias_desde_ultimo_treino.fillna(999) >= 14,
        'Chamado técnico (90 dias)': lambda h: h.chamado_tecnico_90d,
        'Nenhum seguidor': lambda h: h.seguidores.fillna(0) == 0,
        'Anual que renova nos 60 dias': lambda h: (h.plano == 'anual') & h.renova_em_60d,
    }
    out = {'base_taxa': round(base_taxa, 4), 'n_base': len(b), 'mrr_total': round(float(b.mrr_liq.sum()), 0), 'personas': []}
    for nome, grupos in PERSONAS.items():
        s = b[b.nome_grupo.isin(grupos)]
        h = m5[m5.nome_grupo.isin(grupos)]
        livre = s[~s.saida_anunciada]
        txt, regra = gatilhos[nome]
        gat = livre[regra(livre)]
        drv = []
        for sn, f in sinais5.items():
            mk = f(h)
            if mk.sum() >= 40 and (~mk).sum() >= 40:
                drv.append({'sinal': sn, 'pct': round(float(mk.mean()), 3), 'com': taxa(h[mk].desligou_60d), 'sem': taxa(h[~mk].desligou_60d), 'n_com': int(mk.sum())})
        drv.sort(key=lambda d: -(d['com'] - d['sem']))
        obj = s.objetivo[~s.objetivo.isin(['nao_informado', 'sem_onboarding'])].value_counts(normalize=True)
        p = {
            'persona': nome, 'grupos': grupos, 'n': int(len(s)), 'pct': round(len(s) / len(b), 4),
            'sub': {gr: {'n': int((s.nome_grupo == gr).sum()), 'saida': taxa(h[h.nome_grupo == gr].desligou_60d)} for gr in grupos},
            'mediana': {'tempo_casa_meses': round(float(s.tempo_casa_meses.median()), 1), 'treinos_semana': round(float(s.treinos_semana.median()), 2),
                        'min_por_treino': round(float(s.min_por_treino.median()), 1), 'pct_ar_livre': round(float(s.pct_ar_livre_2026.median()), 2),
                        'seguidores': float(s.seguidores.median()), 'idade': float(s.idade.median())},
            'mensal': round(float((s.plano == 'mensal').mean()), 3),
            'loja': round(float(s.canal_cobranca.isin(['app_store', 'google_play']).mean()), 3),
            'influenciador': round(float((s.canal_aquisicao == 'influenciador').mean()), 3),
            'avancado': round(float((s.nivel == 'avancado').mean()), 3),
            'objetivo_top': {k: round(float(v), 2) for k, v in obj.head(3).items()},
            'objetivo_informado': round(float((~s.objetivo.isin(['nao_informado', 'sem_onboarding'])).mean()), 3),
            'mrr_pct': round(float(s.mrr_liq.sum() / b.mrr_liq.sum()), 4), 'mrr_mes': round(float(s.mrr_liq.sum()), 0),
            'receita_total_mediana': round(float(s.receita_liquida_total.median()), 0),
            'sem_treino_3m': round(float((s.treinos_3m == 0).mean()), 3), 'parado_14d': round(float(s.parado_14d.mean()), 3),
            'prova_concluida_30d': round(float(s.prova_concluida_30d.mean()), 3), 'chamado_tecnico_90d': round(float(s.chamado_tecnico_90d.mean()), 3),
            'saida_anunciada': int(s.saida_anunciada.sum()), 'saida_anunciada_pct': round(float(s.saida_anunciada.mean()), 3),
            'saida': taxa(h.desligou_60d), 'saida_mensal': taxa(h[h.plano == 'mensal'].desligou_60d), 'saida_anual': taxa(h[h.plano == 'anual'].desligou_60d),
            'pct_das_saidas': round(float(h.desligou_60d.sum() / total_des), 4), 'n_hist': int(len(h)),
            'drivers': drv[:4],
            'gatilho': {'regra': txt, 'n': int(len(gat)), 'pct_persona': round(len(gat) / len(livre), 3),
                        'mensal': int((gat.plano == 'mensal').sum()), 'anual': int((gat.plano == 'anual').sum()),
                        'loja': round(float(gat.canal_cobranca.isin(['app_store', 'google_play']).mean()), 3) if len(gat) else None,
                        'mrr_mes': round(float(gat.mrr_liq.sum()), 0)},
            'hoje': {k: int(f(livre).sum()) for k, f in extras.items()},
        }
        out['personas'].append(p)
        print(f"{nome:34s} {p['pct']:6.1%} saída {p['saida']:6.1%} gatilho hoje {p['gatilho']['n']:5d} ({p['gatilho']['pct_persona']:.0%}) anunciados {p['saida_anunciada']}")
        print('     hoje', p['hoje'], 'gatilho', p['gatilho'])
        print('    ', p['sub'], 'mensal', p['mensal'], 'loja', p['loja'], 'obj', p['objetivo_top'], 'prova30', p['prova_concluida_30d'], 'chamado', p['chamado_tecnico_90d'])
        for d in p['drivers']:
            print('      ', d)
    out['gatilho_total'] = sum(p['gatilho']['n'] for p in out['personas'])
    out['anunciados_total'] = int(b.saida_anunciada.sum())
    (RAIZ / 'saidas' / 'personas.json').write_text(json.dumps(out, ensure_ascii=False, indent=1), encoding='utf-8')
    print('gatilho total', out['gatilho_total'], 'anunciados', out['anunciados_total'])


if __name__ == '__main__':
    main()
