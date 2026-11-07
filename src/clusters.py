"""Segmentação escolhida (D-054): K-means com 5 variáveis de comportamento, sem o plano, 5 grupos.

Visão geral da base ativa de 30/09/2026. Os grupos são formados SEM nenhuma informação de saída
(objetivo 3 do enunciado). Só depois de formados, eles são descritos: perfil, valor, engajamento e,
para dar evidência às personas, a saída histórica de cada grupo (régua de 30/09 aplicada à base de
31/05, gabarito da D-053, sem quem já tinha anunciado a saída, D-052).

Grava:
  dados/processados/clusters_2026-09-30.parquet   user_id, grupo, nome_grupo (sem dado pessoal)
  saidas/clusters_final.json                      agregados para o painel
  saidas/clusters.md                              relatório da segmentação escolhida

Uso, da raiz do projeto (depois de src/clusters_cenarios.py):  .venv\\Scripts\\python.exe src\\clusters.py
"""
import json
import sys
from pathlib import Path

import numpy as np
import pandas as pd
from sklearn.cluster import KMeans
from sklearn.metrics import adjusted_rand_score, silhouette_samples
from sklearn.preprocessing import StandardScaler

RAIZ = Path(__file__).resolve().parents[1]
PROC = RAIZ / 'dados' / 'processados'
sys.path.insert(0, str(RAIZ / 'src'))
from clusters_cenarios import montar_base  # noqa: E402
from raio_x import cat_objetivo  # noqa: E402

VARS = ['tempo_casa', 'treinos_semana', 'min_por_treino', 'pct_ar_livre', 'seguidores']
NOMES_VARS = {'tempo_casa': 'Tempo de casa', 'treinos_semana': 'Treinos por semana', 'min_por_treino': 'Minutos por treino',
              'pct_ar_livre': '% ao ar livre', 'seguidores': 'Seguidores'}
K = 5
DIA = pd.Timedelta(days=1)
LIQ = {'app_store': .85, 'google_play': .85, 'web_cartao': .965, 'web_pix': .9901}   # enunciado, seção 03


class Regua:
    """Preparação + escala + centros aprendidos em 30/09, reaplicáveis a outra data sem treinar de novo."""

    def fit(self, raw):
        # mesma preparação de src/clusters_cenarios.py: mediana nos faltantes antes do teto no percentil 99
        self.med = {'min_por_treino': raw.min_por_treino.median(), 'pct_ar_livre': raw.pct_ar_livre.median()}
        self.teto = {'treinos_semana': raw.treinos_semana.quantile(.99),
                     'min_por_treino': raw.min_por_treino.fillna(self.med['min_por_treino']).quantile(.99)}
        x = self.preparar(raw)
        self.scaler = StandardScaler().fit(x)
        self.km = KMeans(K, n_init=10, random_state=0).fit(self.scaler.transform(x))
        return self

    def preparar(self, raw):
        return pd.DataFrame({
            'tempo_casa': np.log1p(raw.tempo_casa_meses),
            'treinos_semana': raw.treinos_semana.clip(upper=self.teto['treinos_semana']),
            'min_por_treino': raw.min_por_treino.fillna(self.med['min_por_treino']).clip(upper=self.teto['min_por_treino']),
            'pct_ar_livre': raw.pct_ar_livre.fillna(self.med['pct_ar_livre']),
            'seguidores': raw.seguidores.clip(upper=6).astype(float)}, index=raw.index)

    def z(self, raw):
        return self.scaler.transform(self.preparar(raw))

    def prever(self, raw):
        return self.km.predict(self.z(raw))


def bruto_30(b):
    return pd.DataFrame({'tempo_casa_meses': b.tempo_casa_meses, 'treinos_semana': b.treinos_semana, 'min_por_treino': b.min_por_treino,
                         'pct_ar_livre': b.pct_ar_livre_2026, 'seguidores': b.seguidores}, index=b.index)


def base_31_05():
    """As mesmas 5 variáveis, montadas com o que se sabia em 31/05/2026, mais o gabarito da D-053."""
    T = pd.Timestamp('2026-05-31 23:59:59')
    b = pd.read_parquet(PROC / 'base_corte_2026-05-31.parquet')
    pu = pd.read_parquet(PROC / 'painel_uso_assinantes.parquet')
    g = pu[pu.mes.isin(['2026-03', '2026-04', '2026-05'])].groupby('user_id')
    tre, minu = b.user_id.map(g.atividades.sum()).fillna(0), b.user_id.map(g.minutos.sum()).fillna(0)
    at = pd.read_parquet(PROC / 'atividades.parquet', columns=['user_id', 'inicio', 'modalidade'])
    at = at[(at.inicio >= '2026-01-01') & (at.inicio <= T)]
    tot = at.groupby('user_id').size()
    ar = at[at.modalidade == 'ar_livre'].groupby('user_id').size()
    raw = pd.DataFrame({'tempo_casa_meses': b.tempo_casa_meses, 'treinos_semana': tre / 13, 'min_por_treino': minu / tre.replace(0, np.nan),
                        'pct_ar_livre': (b.user_id.map(ar).fillna(0) / b.user_id.map(tot)), 'seguidores': b.seguidores}, index=b.index)
    ev = pd.read_parquet(PROC / 'eventos_assinatura.parquet')
    des = ev[(ev.fase == 'pago') & ev.evento.isin(['renovacao_automatica_desligada', 'cancelamento_web'])].groupby('user_id').data_hora.min()
    b['desligou_60d'] = b.user_id.isin(des[(des > T) & (des <= T + 60 * DIA)].index)
    o = pd.read_parquet(PROC / 'onboarding.parquet').set_index('user_id')
    b['objetivo'] = b.user_id.map(o.objetivo_texto.map(cat_objetivo)).fillna('sem_onboarding')
    return b, raw


def nomear(prof):
    """Nome pelo perfil (não pelo número do grupo, que pode mudar)."""
    p = prof.copy()
    nomes = {}
    nomes[p.pct_ar_livre.idxmin()] = 'Treino em casa'
    resto = p.drop(index=list(nomes))
    nomes[resto.tempo_casa_meses.idxmin()] = 'Novatos'
    resto = p.drop(index=list(nomes))
    nomes[resto.min_por_treino.idxmax()] = 'Longões'
    resto = p.drop(index=list(nomes))
    nomes[resto.treinos_semana.idxmax()] = 'Intensos'
    resto = p.drop(index=list(nomes))
    nomes[resto.index[0]] = 'Rua no ritmo leve'
    return nomes


ORDEM = ['Novatos', 'Treino em casa', 'Rua no ritmo leve', 'Intensos', 'Longões']


def dist(s, cats=None, top=None):
    v = s.fillna('nao_informado').astype(str).value_counts(normalize=True)
    if cats:
        v = v.reindex(cats, fill_value=0)
    if top:
        v = v.head(top)
    return {k: round(float(x), 3) for k, x in v.items()}


def ic95(p, n):
    e = 1.96 * np.sqrt(p * (1 - p) / n) if n else 0
    return [round(max(0, p - e), 4), round(min(1, p + e), 4)]


def main():
    sys.stdout.reconfigure(encoding='utf-8')
    b = montar_base()
    raw = bruto_30(b)
    regua = Regua().fit(raw)
    z = regua.z(raw)
    lab = regua.km.labels_
    prof0 = b.assign(g=lab).groupby('g')[['tempo_casa_meses', 'treinos_semana', 'min_por_treino']].median()
    prof0['pct_ar_livre'] = b.assign(g=lab).groupby('g').pct_ar_livre_2026.median()
    nomes = nomear(prof0)
    b['grupo'] = lab
    b['nome_grupo'] = b.grupo.map(nomes)
    b[['user_id', 'grupo', 'nome_grupo']].to_parquet(PROC / 'clusters_2026-09-30.parquet', index=False)

    # ------------------------------------------------ qualidade da segmentação
    rng = np.random.RandomState(42)
    amostra = rng.choice(len(b), 8000, replace=False)
    sil = pd.Series(silhouette_samples(z[amostra], lab[amostra]), index=b.index[amostra])
    ari_sem = adjusted_rand_score(lab, KMeans(K, n_init=10, random_state=1).fit_predict(z))
    metade = rng.choice(len(b), len(b) // 2, replace=False)
    ari_met = adjusted_rand_score(lab, KMeans(K, n_init=10, random_state=0).fit(z[metade]).predict(z))
    centros = pd.DataFrame(regua.km.cluster_centers_, columns=VARS)

    # ------------------------------------------------ régua aplicada a 31/05 (saída histórica, D-053)
    b5, raw5 = base_31_05()
    b5['nome_grupo'] = pd.Series(regua.prever(raw5), index=b5.index).map(nomes)
    m5 = b5[~b5.saida_anunciada]
    taxa_base = float(m5.desligou_60d.mean())
    total_des = int(m5.desligou_60d.sum())

    # sinais (drivers) dentro de cada grupo, em 31/05: taxa com o sinal × sem o sinal
    sinais = {
        'Plano mensal': m5.plano == 'mensal',
        'Anual que renova nos 60 dias': (m5.plano == 'anual') & m5.renova_em_60d,
        'Pagava o preço antigo (reajuste)': m5.afetado_reajuste,
        'Treino caiu forte (4 semanas)': m5.queda_forte,
        '14+ dias sem treinar': m5.dias_desde_ultimo_treino.fillna(999) >= 14,
        'Cartão recusado (30 dias)': m5.recusa_30d,
        'Chamado técnico (90 dias)': m5.chamado_tecnico_90d,
        'Entrou com cupom': m5.entrou_com_cupom,
        'Nenhum seguidor': m5.seguidores.fillna(0) == 0,
    }

    # ------------------------------------------------ receita líquida mensal estimada (preço de tabela, enunciado seção 03)
    liq = b.canal_cobranca.map(LIQ).fillna(.85)
    b['mrr_liq'] = np.where(b.plano == 'mensal', 39.90, 299.90 / 12) * liq
    mrr_total = float(b.mrr_liq.sum())

    grupos = []
    for nome in ORDEM:
        s = b[b.nome_grupo == nome]
        gi = s.grupo.iloc[0]
        h = m5[m5.nome_grupo == nome]
        taxa = float(h.desligou_60d.mean())
        drv = []
        for sn, mask in sinais.items():
            mk = mask.loc[h.index]
            com, sem = h[mk], h[~mk]
            if len(com) >= 40 and len(sem) >= 40:
                drv.append({'sinal': sn, 'n_com': int(len(com)), 'pct_grupo': round(float(mk.mean()), 3),
                            'taxa_com': round(float(com.desligou_60d.mean()), 4), 'taxa_sem': round(float(sem.desligou_60d.mean()), 4)})
        drv = sorted(drv, key=lambda d: -(d['taxa_com'] - d['taxa_sem']))
        q = lambda c: [round(float(v), 2) for v in s[c].quantile([.1, .25, .5, .75, .9])]
        grupos.append({
            'nome': nome, 'grupo': int(gi), 'n': int(len(s)), 'pct': round(len(s) / len(b), 4),
            'centro_z': {v: round(float(centros.loc[gi, v]), 2) for v in VARS},
            'quantis': {'tempo_casa_meses': q('tempo_casa_meses'), 'treinos_semana': q('treinos_semana'),
                        'min_por_treino': [round(float(v), 1) for v in s.min_por_treino.dropna().quantile([.1, .25, .5, .75, .9])],
                        'pct_ar_livre_2026': [round(float(v), 2) for v in s.pct_ar_livre_2026.dropna().quantile([.1, .25, .5, .75, .9])],
                        'seguidores': q('seguidores')},
            'mediana': {'tempo_casa_meses': round(float(s.tempo_casa_meses.median()), 1), 'treinos_semana': round(float(s.treinos_semana.median()), 2),
                        'min_por_treino': round(float(s.min_por_treino.median()), 1), 'pct_ar_livre': round(float(s.pct_ar_livre_2026.median()), 2),
                        'seguidores': float(s.seguidores.median()), 'idade': float(s.idade.median())},
            'plano': dist(s.plano, ['mensal', 'anual']),
            'canal_cobranca': dist(s.canal_cobranca, ['app_store', 'google_play', 'web_cartao', 'web_pix']),
            'canal_aquisicao': dist(s.canal_aquisicao, ['organico', 'influenciador', 'meta_ads', 'indicacao', 'google_ads', 'parceria_corporativa']),
            'objetivo': dist(s.objetivo, ['prova_com_prazo', 'desempenho', 'estetica', 'saude', 'bem_estar', 'companhia', 'outro', 'nao_informado', 'sem_onboarding']),
            'nivel': dist(s.nivel, ['iniciante', 'intermediario', 'avancado', 'nao_informado']),
            'sexo_f': round(float((s.sexo == 'F').mean()), 3), 'relogio': round(float((s.relogio_conectado != 'nenhum').mean()), 3),
            'engajamento': {'sem_treino_3m': round(float((s.treinos_3m == 0).mean()), 3),
                            'dias_sem_treinar_mediana': float(s.dias_desde_ultimo_treino.median()),
                            'parado_30d': round(float((s.dias_desde_ultimo_treino.fillna(999) > 30).mean()), 3),
                            'posts_90d': round(float(s.posts_90d.mean()), 2), 'sessoes_mes': round(float(s.sessoes_app_3m.mean() / 3), 1),
                            'com_post': round(float((s.posts_90d > 0).mean()), 3)},
            'valor': {'receita_total_mediana': round(float(s.receita_liquida_total.median()), 0),
                      'receita_total_pct': round(float(s.receita_liquida_total.sum() / b.receita_liquida_total.sum()), 4),
                      'mrr_liq': round(float(s.mrr_liq.sum()), 0), 'mrr_pct': round(float(s.mrr_liq.sum() / mrr_total), 4),
                      'mrr_por_pessoa': round(float(s.mrr_liq.mean()), 2)},
            'saida_anunciada_30_09': round(float(s.saida_anunciada.mean()), 3),
            'historico': {'n': int(len(h)), 'pct_base_31_05': round(len(b5[b5.nome_grupo == nome]) / len(b5), 4), 'taxa': round(taxa, 4),
                          'ic95': ic95(taxa, len(h)), 'desligamentos': int(h.desligou_60d.sum()),
                          'pct_dos_desligamentos': round(float(h.desligou_60d.sum() / total_des), 4),
                          'mensal_taxa': round(float(h[h.plano == 'mensal'].desligou_60d.mean()), 4),
                          'anual_taxa': round(float(h[h.plano == 'anual'].desligou_60d.mean()), 4)},
            'drivers': drv[:4],
            'silhueta': round(float(sil[b.loc[sil.index, 'nome_grupo'] == nome].mean()), 3),
        })
        print(f"{nome:18s} {len(s)/len(b):6.1%}  saída 31/05 {taxa:6.1%} (n={len(h)})  MRR {s.mrr_liq.sum()/mrr_total:6.1%}")

    out = {'cenario': 'escolhido', 'variaveis': VARS, 'nomes_vars': NOMES_VARS, 'k': K, 'n': int(len(b)),
           'qualidade': {'silhueta': round(float(sil.mean()), 3), 'ari_semente': round(ari_sem, 3), 'ari_metade': round(ari_met, 3)},
           'historico': {'corte': '31/05/2026', 'n': int(len(m5)), 'taxa_base': round(taxa_base, 4), 'desligamentos': total_des,
                         'regua': 'escala e centros de 30/09 aplicados às mesmas 5 variáveis montadas em 31/05'},
           'mrr_total': round(mrr_total, 0), 'grupos': grupos}
    (RAIZ / 'saidas' / 'clusters_final.json').write_text(json.dumps(out, ensure_ascii=False, indent=1), encoding='utf-8')
    escrever_md(out)
    print(json.dumps(out['qualidade']), out['historico'])


def escrever_md(o):
    pc = lambda v: f'{v * 100:.1f}%'.replace('.', ',')
    L = ['# Segmentação escolhida (D-054)', '',
         'Cenário escolhido: K-means com **5 variáveis de comportamento, sem o plano**, e **5 grupos**, na base ativa de 30/09/2026 '
         f'({o["n"]:,} assinantes). Processo de escolha: `saidas/clusters_cenarios.md`. Código: `src/clusters.py`.'.replace(',', '.'), '',
         'Os grupos foram formados **sem nenhuma informação de saída**. A saída histórica abaixo só descreve os grupos: a régua de 30/09 '
         f'foi aplicada às mesmas variáveis montadas em 31/05/2026, e medimos quem desligou a renovação ou cancelou pelo site nos 60 dias seguintes (D-053), sem quem já tinha anunciado (D-052). Taxa da base: {pc(o["historico"]["taxa_base"])}.', '',
         f'Qualidade: silhueta {o["qualidade"]["silhueta"]:.2f}, estabilidade {min(o["qualidade"]["ari_semente"], o["qualidade"]["ari_metade"]):.2f} (outra semente e metade da base).'.replace('.', ',', 2), '',
         '| Grupo | % base | Meses de casa | Treinos/sem | Min/treino | % ar livre | Seguidores | % mensal | % receita mensal | Saída 60d (31/05) | % das saídas |',
         '|---|---|---|---|---|---|---|---|---|---|---|']
    for g in o['grupos']:
        m = g['mediana']
        L.append(f"| {g['nome']} | {pc(g['pct'])} | {m['tempo_casa_meses']} | {m['treinos_semana']} | {m['min_por_treino']} | {pc(m['pct_ar_livre'])} | {m['seguidores']:.0f} | "
                 f"{pc(g['plano']['mensal'])} | {pc(g['valor']['mrr_pct'])} | {pc(g['historico']['taxa'])} | {pc(g['historico']['pct_dos_desligamentos'])} |")
    L += ['', '## O que mais pesa na saída, dentro de cada grupo (31/05)', '']
    for g in o['grupos']:
        L.append(f"**{g['nome']}** · saída {pc(g['historico']['taxa'])}")
        for d in g['drivers'][:3]:
            L.append(f"- {d['sinal']}: {pc(d['taxa_com'])} com o sinal × {pc(d['taxa_sem'])} sem ({d['n_com']} pessoas com o sinal)")
        L.append('')
    L += ['## Limites', '',
          '- Cruzamentos apontam suspeitos, não provam causa.',
          '- A saída histórica usa a régua de 30/09 em 31/05: os grupos são os mesmos, mas cada pessoa pode ter mudado de grupo entre as datas.',
          '- Receita mensal estimada pelo preço de tabela e pela taxa do canal (enunciado, seção 03); cupons não descontados.',
          '- Idade, sexo e relógio não mudam entre os grupos: as personas se diferenciam pelo comportamento, não pelo perfil demográfico.']
    (RAIZ / 'saidas' / 'clusters.md').write_text('\n'.join(L) + '\n', encoding='utf-8')


if __name__ == '__main__':
    main()
