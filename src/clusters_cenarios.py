"""Segmentação da base ativa de 30/09/2026 com K-means: compara cenários de 3, 4, 5 e 6 variáveis.

Visão geral da base, sem a ótica de churn: nenhuma informação de saída entra no cálculo nem na
descrição. As 6 variáveis candidatas (painel, aba "Próximo passo"):
plano, tempo de casa, treinos por semana, minutos por treino, % ao ar livre e seguidores.

Para cada combinação de variáveis (20 de 3, 15 de 4, 6 de 5 e 1 de 6) e cada número de grupos (3 a 7):
  1. prepara: teto no percentil 99, log no tempo de casa, mediana nos faltantes;
  2. normaliza: StandardScaler (média 0, desvio 1);
  3. roda o K-means (n_init=10, random_state=0);
  4. mede: silhueta (amostra fixa de 8.000), tamanho do menor grupo e estabilidade
     (ARI contra outro random_state e contra um modelo treinado só na metade da base).

Grava:
  saidas/clusters_cenarios.csv   uma linha por combinação × k, com as métricas
  saidas/clusters_perfis.json    perfil dos grupos dos cenários finalistas (só agregados)

Uso, da raiz do projeto:  .venv\\Scripts\\python.exe src\\clusters_cenarios.py
"""
import json
import sys
from itertools import combinations
from pathlib import Path

import numpy as np
import pandas as pd
from sklearn.cluster import KMeans
from sklearn.metrics import adjusted_rand_score, silhouette_score
from sklearn.preprocessing import StandardScaler

RAIZ = Path(__file__).resolve().parents[1]
PROC = RAIZ / 'dados' / 'processados'
sys.path.insert(0, str(RAIZ / 'src'))
from raio_x import cat_objetivo  # noqa: E402

VARS = ['mensal', 'tempo_casa', 'treinos_semana', 'min_por_treino', 'pct_ar_livre', 'seguidores']
NOMES = {'mensal': 'plano mensal', 'tempo_casa': 'tempo de casa', 'treinos_semana': 'treinos por semana',
         'min_por_treino': 'minutos por treino', 'pct_ar_livre': '% ao ar livre', 'seguidores': 'seguidores'}
KS = range(3, 8)
MIN_GRUPO = 0.05
# Os quatro cenários levados ao grupo (variáveis, número de grupos). O de 5 variáveis é sem o plano:
# com o plano, os grupos de 5 variáveis repetem os do cenário B (o plano 0/1 domina a distância).
ESCOLHIDOS = {
    'A': (('mensal', 'min_por_treino', 'pct_ar_livre'), 5),
    'B': (('mensal', 'treinos_semana', 'min_por_treino', 'pct_ar_livre'), 6),
    'C': (('tempo_casa', 'treinos_semana', 'min_por_treino', 'pct_ar_livre', 'seguidores'), 5),
    'D': (('mensal', 'tempo_casa', 'treinos_semana', 'min_por_treino', 'pct_ar_livre', 'seguidores'), 6),
}


def montar_base():
    b = pd.read_parquet(PROC / 'base_assinantes_corte.parquet')
    o = pd.read_parquet(PROC / 'onboarding.parquet').set_index('user_id')
    b['objetivo'] = b.user_id.map(o.objetivo_texto.map(cat_objetivo)).fillna('sem_onboarding')
    b['treinos_semana'] = b.treinos_3m / 13
    b['min_por_treino'] = b.minutos_3m / b.treinos_3m.replace(0, np.nan)
    return b


def preparar(b):
    """Tabela das 6 variáveis já tratadas (antes da padronização)."""
    p99 = lambda s: s.clip(upper=s.quantile(.99))
    med = lambda s: s.fillna(s.median())
    return pd.DataFrame({
        'mensal': (b.plano == 'mensal').astype(float),
        'tempo_casa': np.log1p(b.tempo_casa_meses),
        'treinos_semana': p99(b.treinos_semana),
        'min_por_treino': p99(med(b.min_por_treino)),
        'pct_ar_livre': med(b.pct_ar_livre_2026),
        'seguidores': b.seguidores.clip(upper=6).astype(float)}, index=b.index)


def avaliar(z, k, amostra, metade):
    km = KMeans(k, n_init=10, random_state=0).fit(z)
    lab = km.labels_
    outra = KMeans(k, n_init=10, random_state=1).fit_predict(z)
    meia = KMeans(k, n_init=10, random_state=0).fit(z[metade]).predict(z)
    return lab, {'k': k, 'silhueta': silhouette_score(z[amostra], lab[amostra]),
                 'menor_grupo': np.bincount(lab).min() / len(lab), 'maior_grupo': np.bincount(lab).max() / len(lab),
                 'ari_semente': adjusted_rand_score(lab, outra), 'ari_metade': adjusted_rand_score(lab, meia)}


def perfil(b, x, lab):
    d = b.assign(g=lab)
    linhas = []
    for g, s in d.groupby('g'):
        obj = s.objetivo[~s.objetivo.isin(['nao_informado', 'sem_onboarding'])].value_counts(normalize=True)
        linhas.append({
            'grupo': int(g), 'n': int(len(s)), 'pct': round(len(s) / len(d), 3),
            'mensal': round((s.plano == 'mensal').mean(), 3),
            'tempo_casa_meses': round(s.tempo_casa_meses.median(), 1),
            'treinos_semana': round(s.treinos_semana.median(), 2),
            'min_por_treino': round(s.min_por_treino.median(), 1),
            'pct_ar_livre': round(s.pct_ar_livre_2026.median(), 2),
            'seguidores': round(s.seguidores.median(), 1),
            'sem_treino_3m': round((s.treinos_3m == 0).mean(), 3),
            'idade': round(float(s.idade.median()), 1),
            'mulheres': round((s.sexo == 'F').mean(), 3),
            'avancado': round((s.nivel == 'avancado').mean(), 3),
            'relogio': round((s.relogio_conectado != 'nenhum').mean(), 3),
            'influenciador': round((s.canal_aquisicao == 'influenciador').mean(), 3),
            'indicacao': round((s.canal_aquisicao == 'indicacao').mean(), 3),
            'objetivo_top': {k: round(v, 2) for k, v in obj.head(3).items()},
            'bem_estar': round((s.objetivo == 'bem_estar').mean(), 3),
            'prova_desempenho': round(s.objetivo.isin(['prova_com_prazo', 'desempenho']).mean(), 3),
            'receita_total_mediana': round(s.receita_liquida_total.median(), 0),
            'receita_total_soma_pct': round(s.receita_liquida_total.sum() / d.receita_liquida_total.sum(), 3)})
    return linhas


def main():
    sys.stdout.reconfigure(encoding='utf-8')
    b = montar_base()
    x = preparar(b)
    print(f'{len(x)} assinantes ativos em 30/09; faltantes depois do tratamento: {int(x.isna().sum().sum())}')
    rng = np.random.RandomState(42)
    amostra = rng.choice(len(x), 8000, replace=False)
    metade = rng.choice(len(x), len(x) // 2, replace=False)

    linhas, rotulos = [], {}
    for n in (3, 4, 5, 6):
        for combo in combinations(VARS, n):
            z = StandardScaler().fit_transform(x[list(combo)])
            for k in KS:
                lab, m = avaliar(z, k, amostra, metade)
                m.update({'n_vars': n, 'variaveis': '+'.join(combo)})
                linhas.append(m)
                rotulos[(combo, k)] = lab
        print(f'{n} variáveis: ok')
    r = pd.DataFrame(linhas)
    r['estavel'] = r[['ari_semente', 'ari_metade']].min(axis=1)
    r['aceito'] = (r.menor_grupo >= MIN_GRUPO) & (r.estavel >= .8)
    r = r[['n_vars', 'variaveis', 'k', 'silhueta', 'menor_grupo', 'maior_grupo', 'ari_semente', 'ari_metade', 'estavel', 'aceito']].round(3)
    (RAIZ / 'saidas').mkdir(exist_ok=True)
    r.to_csv(RAIZ / 'saidas' / 'clusters_cenarios.csv', index=False)

    # finalistas automáticos: para cada número de variáveis, as 3 melhores combinações aceitas (melhor k de cada)
    fin = (r[r.aceito].sort_values('silhueta', ascending=False)
           .drop_duplicates('variaveis').groupby('n_vars').head(3))
    pd.set_option('display.width', 250)
    print(fin.to_string(index=False))

    # cenários levados ao grupo (um por número de variáveis; escolha explicada em saidas/clusters_cenarios.md)
    saida = []
    for nome, (combo, k) in ESCOLHIDOS.items():
        m = r[(r.variaveis == '+'.join(combo)) & (r.k == k)].iloc[0]
        grupos = perfil(b, x, rotulos[(combo, k)])
        saida.append({'cenario': nome, 'n_vars': len(combo), 'variaveis': list(combo), 'nomes': [NOMES[v] for v in combo], 'k': k,
                      'silhueta': float(m.silhueta), 'menor_grupo': float(m.menor_grupo), 'estavel': float(m.estavel),
                      'silhueta_por_k': r[r.variaveis == '+'.join(combo)][['k', 'silhueta', 'menor_grupo', 'estavel', 'aceito']].to_dict('records'),
                      'grupos': sorted(grupos, key=lambda g: -g['n'])})
    melhor = r.sort_values('silhueta', ascending=False).drop_duplicates('n_vars')[['n_vars', 'silhueta']]
    resumo = {'assinantes': len(x), 'combinacoes': int(r.variaveis.nunique()), 'rodadas': len(r),
              'aceitas': int(r.aceito.sum()), 'melhor_silhueta_por_n': melhor.sort_values('n_vars').to_dict('records'),
              'cenarios': saida}
    (RAIZ / 'saidas' / 'clusters_perfis.json').write_text(json.dumps(resumo, ensure_ascii=False, indent=1), encoding='utf-8')
    for c in saida:
        print(f"\n{c['cenario']}: {', '.join(c['nomes'])} · k={c['k']} · silhueta {c['silhueta']:.3f} · estável {c['estavel']:.3f}")
        print(pd.DataFrame(c['grupos'])[['pct', 'mensal', 'tempo_casa_meses', 'treinos_semana', 'min_por_treino', 'pct_ar_livre', 'seguidores', 'sem_treino_3m', 'receita_total_mediana']].to_string(index=False))


if __name__ == '__main__':
    main()
