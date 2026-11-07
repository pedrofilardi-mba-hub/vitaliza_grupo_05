"""Raio-x da base de clientes: análise exploratória com as técnicas das Aulas 2, 3 e 4.

- Granularidade (Aula 2): funil contas → teste → pagou → ativo.
- Centro e dispersão (Aula 2): cinco números, média × mediana, desvio padrão e CV, extremos pela regra de 1,5 × IQR.
- Distribuições (Aula 2): histogramas.
- Correlação (Aula 2): matriz de Pearson do comportamento e um gráfico de dispersão.
- A média esconde / regras em planilha (Aula 3): mapas de calor de churn por grupos.
- Quanto cada lente prevê (Aula 3): AUC de regressão logística com validação cruzada.
- Separar × cobrir (Aula 4): tabela de hipóteses.

Descrição: base ativa em 30/09/2026. Churn: gabarito da D-053 no corte de 31/05/2026
(desligou a renovação ou cancelou pelo site nos 60 dias seguintes), sem quem já tinha anunciado a saída (D-052).
Só números agregados. Chamado por src/painel_dados.py.
"""
import re
from pathlib import Path

import numpy as np
import pandas as pd
from sklearn.compose import ColumnTransformer
from sklearn.linear_model import LogisticRegression
from sklearn.model_selection import cross_val_score
from sklearn.pipeline import make_pipeline
from sklearn.preprocessing import OneHotEncoder, StandardScaler
from sklearn.impute import SimpleImputer

RAIZ = Path(__file__).resolve().parents[1]
PROC = RAIZ / 'dados' / 'processados'
DIA = pd.Timedelta(days=1)

OBJETIVOS = {
    'saude': r'colesterol|dor nas costas|press[aã]o|m[eé]dico|sa[uú]de(?! mental)|sedent|disposi',
    'companhia': r'galera|namorad|grupo|pessoal do trabalho|companhia|amiga|amigo|junto',
    'estetica': r'perder|peso|secar|barriga|emagrec|definir|espelho|em forma',
    'bem_estar': r'dormir|ansiedade|momento s[oó] meu|celular|sa[uú]de mental|desligar a cabe',
    'prova_com_prazo': r'prova|daqui|maratona',
    'desempenho': r'pace|tempo nos|evoluir|planilha|mais r[aá]pido|subir de n[ií]vel',
}


def cat_objetivo(t):
    if not isinstance(t, str):
        return 'nao_informado'
    t = t.lower()
    for k, rx in OBJETIVOS.items():
        if re.search(rx, t):
            return k
    return 'outro'


def ler(n):
    return pd.read_parquet(PROC / f'{n}.parquet')


def enriquecer(b):
    o = ler('onboarding').set_index('user_id')
    u = ler('usuarios').set_index('user_id')
    b = b.copy()
    b['objetivo'] = b.user_id.map(o.objetivo_texto.map(cat_objetivo)).fillna('sem_onboarding')
    b['uf'] = b.user_id.map(u.uf)
    b['treinos_semana'] = b.treinos_4s / 4
    return b


def cinco_numeros(s):
    s = pd.to_numeric(s, errors='coerce').dropna()
    q1, q2, q3 = s.quantile([.25, .5, .75])
    iqr = q3 - q1
    return {'n': int(len(s)), 'min': float(s.min()), 'q1': float(q1), 'mediana': float(q2), 'q3': float(q3), 'max': float(s.max()),
            'media': float(s.mean()), 'dp': float(s.std()), 'cv': float(s.std() / s.mean()) if s.mean() else None,
            'extremos_iqr': int(((s < q1 - 1.5 * iqr) | (s > q3 + 1.5 * iqr)).sum()), 'zeros': float((s == 0).mean())}


def hist(s, bins, labels):
    c = pd.cut(pd.to_numeric(s, errors='coerce'), bins, labels=labels, right=False).value_counts().reindex(labels).fillna(0)
    return {'labels': labels, 'valores': [int(v) for v in c.values]}


def faixa_casa(m):
    return pd.cut(m, [-1, 1, 3, 6, 12, 1000], labels=['até 1 mês', '1–3 meses', '3–6 meses', '6–12 meses', '+12 meses'])


def mapa(df, linhas, colunas, alvo):
    t = df.groupby([linhas, colunas], observed=True)[alvo].agg(['mean', 'size']).reset_index()
    return {'linhas': [str(x) for x in df[linhas].cat.categories] if hasattr(df[linhas], 'cat') else sorted(df[linhas].dropna().unique().tolist()),
            'colunas': [str(x) for x in df[colunas].cat.categories] if hasattr(df[colunas], 'cat') else sorted(df[colunas].dropna().unique().tolist()),
            'celulas': [{'l': str(r[linhas]), 'c': str(r[colunas]), 'taxa': round(float(r['mean']), 4), 'n': int(r['size'])} for _, r in t.iterrows()]}


def lentes_auc(b, alvo):
    grupos = {
        'Quem é (demografia)': (['idade'], ['uf', 'sistema', 'sexo']),
        'Por que contratou (necessidade)': (['dias_por_semana_declarado'], ['objetivo', 'nivel']),
        'Contrato': (['tempo_casa_meses', 'dias_ate_renovacao'], ['plano', 'canal_cobranca', 'canal_aquisicao']),
        'O que faz (comportamento)': (['treinos_4s', 'treinos_4s_anteriores', 'semanas_ativas_8s', 'dias_desde_ultimo_treino', 'minutos_3m',
                                       'sessoes_mes', 'pct_video_90d', 'seguidores', 'posts_90d', 'treinou_acompanhado_90d'], []),
    }
    grupos['Todas juntas'] = (sum((g[0] for g in grupos.values()), []), sum((g[1] for g in grupos.values()), []))
    out = []
    y = b[alvo].astype(int)
    for nome, (num, cat) in grupos.items():
        pre = ColumnTransformer([('n', make_pipeline(SimpleImputer(strategy='median'), StandardScaler()), num)] +
                                ([('c', make_pipeline(SimpleImputer(strategy='most_frequent'), OneHotEncoder(handle_unknown='ignore')), cat)] if cat else []))
        X = b[num + cat].copy()
        for c in cat:
            X[c] = X[c].astype(str)
        modelo = make_pipeline(pre, LogisticRegression(max_iter=2000))
        auc = cross_val_score(modelo, X, y, cv=5, scoring='roc_auc').mean()
        out.append({'lente': nome, 'auc': round(float(auc), 3)})
    return out


def hipoteses(b, alvo):
    total = b[alvo].sum()
    H = [
        ('Mensal com até 1 mês de casa', (b.plano == 'mensal') & (b.tempo_casa_meses <= 1)),
        ('Plano mensal', b.plano == 'mensal'),
        ('Até 3 meses de casa', b.tempo_casa_meses <= 3),
        ('Treinos caíram pela metade (4 semanas)', b.queda_forte),
        ('Mais de 14 dias sem treinar', b.dias_desde_ultimo_treino > 14),
        ('Entrou por meta com prazo, desempenho ou estética', b.objetivo.isin(['prova_com_prazo', 'desempenho', 'estetica'])),
        ('Paga pelo Google Play', b.canal_cobranca == 'google_play'),
        ('Anual que renova em 60 dias', (b.plano == 'anual') & b.renova_em_60d),
        ('Mensal até 3 meses + meta com prazo, desempenho ou estética', (b.plano == 'mensal') & (b.tempo_casa_meses <= 3) & b.objetivo.isin(['prova_com_prazo', 'desempenho', 'estetica'])),
        ('Menos de 30 anos (só descrição; não vira gatilho)', b.idade < 30),
    ]
    out = []
    for nome, m in H:
        m = m.fillna(False)
        if m.sum() == 0:
            continue
        a, o = b[m][alvo].mean(), b[~m][alvo].mean()
        out.append({'hipotese': nome, 'n': int(m.sum()), 'pct_base': round(float(m.mean()), 3), 'taxa_dentro': round(float(a), 3),
                    'taxa_fora': round(float(o), 3), 'diferenca_pp': round(float((a - o) * 100), 1), 'cobertura': round(float(b[m][alvo].sum() / total), 3)})
    return sorted(out, key=lambda x: -x['diferenca_pp'])


def montar():
    r = {}
    # ---------------- funil (granularidade)
    usu, ass, ev = ler('usuarios'), ler('assinaturas'), ler('eventos_assinatura')
    b30 = enriquecer(pd.read_parquet(PROC / 'base_corte_2026-09-30.parquet'))
    trial = ev[ev.evento == 'trial_iniciado'].user_id.nunique()
    r['funil'] = [{'etapa': 'Contas criadas (até 30/09)', 'n': int(len(usu))},
                  {'etapa': 'Começaram o teste grátis (desde 07/2024)', 'n': int(trial)},
                  {'etapa': 'Pagaram alguma vez', 'n': int(ass.pagante.sum())},
                  {'etapa': 'Pagantes ativos em 30/09', 'n': int(len(b30))},
                  {'etapa': '… sem saída anunciada (modelo, D-052)', 'n': int((~b30.saida_anunciada).sum())}]

    # ---------------- centro, dispersão e extremos (base ativa 30/09)
    nomes = {'idade': 'Idade (anos)', 'tempo_casa_meses': 'Tempo de casa (meses)', 'treinos_4s': 'Treinos nas últimas 4 semanas',
             'minutos_3m': 'Minutos de treino em 3 meses', 'dias_desde_ultimo_treino': 'Dias desde o último treino', 'sessoes_mes': 'Aberturas do app no mês',
             'seguidores': 'Seguidores na rede', 'posts_90d': 'Posts em 90 dias', 'dias_por_semana_declarado': 'Dias por semana declarados no onboarding'}
    r['estatisticas'] = [{'variavel': v, **cinco_numeros(b30[k])} for k, v in nomes.items()]

    # ---------------- histogramas
    r['hist'] = {
        'idade': hist(b30.idade, [18, 25, 30, 35, 40, 45, 50, 55, 60, 65, 70, 101], ['18–24', '25–29', '30–34', '35–39', '40–44', '45–49', '50–54', '55–59', '60–64', '65–69', '70+']),
        'tempo_casa': hist(b30.tempo_casa_meses, [0, 1, 2, 3, 6, 9, 12, 18, 24, 36, 1000], ['<1', '1', '2', '3–5', '6–8', '9–11', '12–17', '18–23', '24–35', '36+']),
        'treinos_4s': hist(b30.treinos_4s, [0, 1, 3, 5, 9, 13, 17, 25, 1000], ['0', '1–2', '3–4', '5–8', '9–12', '13–16', '17–24', '25+']),
        'dias_sem_treinar': hist(b30.dias_desde_ultimo_treino, [0, 2, 4, 8, 15, 31, 61, 91, 1000], ['0–1', '2–3', '4–7', '8–14', '15–30', '31–60', '61–90', '90+']),
    }
    r['hist']['treinos_4s']['nota'] = f"{(b30.dias_desde_ultimo_treino.isna()).sum()} sem nenhum treino registrado em 2026"

    # ---------------- composição (frequências)
    def freq(s, top=None):
        v = s.fillna('não informado').astype(str).value_counts(normalize=True)
        v = v.head(top) if top else v
        return [{'valor': k, 'pct': round(float(p), 3)} for k, p in v.items()]
    r['composicao'] = {'objetivo': freq(b30.objetivo), 'canal_aquisicao': freq(b30.canal_aquisicao), 'relogio': freq(b30.relogio_conectado),
                       'nivel': freq(b30.nivel), 'uf': freq(b30.uf, 6), 'sistema': freq(b30.sistema)}

    # ---------------- declarado × real
    dr = b30.dropna(subset=['dias_por_semana_declarado']).groupby('dias_por_semana_declarado').agg(n=('user_id', 'size'), real=('treinos_semana', 'mean'), mediana_real=('treinos_semana', 'median'))
    r['declarado_real'] = [{'declarado': int(k), 'n': int(x.n), 'real_media': round(float(x.real), 2), 'real_mediana': round(float(x.mediana_real), 2)} for k, x in dr.iterrows()]

    # ---------------- correlação (Pearson) e dispersão
    cols = {'tempo_casa_meses': 'Tempo de casa', 'treinos_4s': 'Treinos 4 sem.', 'minutos_3m': 'Minutos 3 meses', 'semanas_ativas_8s': 'Semanas ativas',
            'dias_desde_ultimo_treino': 'Dias sem treinar', 'sessoes_mes': 'Sessões no app', 'seguidores': 'Seguidores', 'posts_90d': 'Posts 90 dias',
            'pct_video_90d': '% vídeo', 'idade': 'Idade', 'dias_por_semana_declarado': 'Dias declarados'}
    corr = b30[list(cols)].corr(method='pearson').round(2)
    r['correlacao'] = {'nomes': list(cols.values()), 'matriz': corr.values.tolist()}
    amostra = b30[['sessoes_mes', 'treinos_4s']].dropna().sample(500, random_state=1)
    r['dispersao'] = {'x': 'Aberturas do app no mês', 'y': 'Treinos nas últimas 4 semanas', 'r': round(float(b30.sessoes_mes.corr(b30.treinos_4s)), 2),
                      'pontos': amostra.round(0).astype(int).values.tolist()}

    # ---------------- churn: gabarito da D-053 em 31/05
    b5 = enriquecer(pd.read_parquet(PROC / 'base_corte_2026-05-31.parquet'))
    des = ev[(ev.fase == 'pago') & ev.evento.isin(['renovacao_automatica_desligada', 'cancelamento_web'])].groupby('user_id').data_hora.min()
    T = pd.Timestamp('2026-05-31 23:59:59')
    b5['desligou_60d'] = b5.user_id.isin(des[(des > T) & (des <= T + 60 * DIA)].index)
    m = b5[~b5.saida_anunciada].copy()
    r['churn_base'] = {'n': int(len(m)), 'taxa': round(float(m.desligou_60d.mean()), 4), 'corte': '31/05/2026'}
    m['casa'] = faixa_casa(m.tempo_casa_meses)
    m['freq'] = pd.cut(m.treinos_semana, [-0.01, 0.99, 2, 3, 100], labels=['menos de 1x', '1 a 2x', '2 a 3x', 'mais de 3x'])
    m['plano_c'] = pd.Categorical(m.plano, categories=['mensal', 'anual'])
    r['mapa_plano_casa'] = mapa(m, 'plano_c', 'casa', 'desligou_60d')
    r['mapa_casa_freq'] = mapa(m, 'casa', 'freq', 'desligou_60d')
    obj_ord = ['prova_com_prazo', 'desempenho', 'estetica', 'companhia', 'saude', 'bem_estar', 'outro', 'nao_informado', 'sem_onboarding']
    m['objetivo_c'] = pd.Categorical(m.objetivo, categories=obj_ord)
    r['mapa_objetivo_plano'] = mapa(m, 'objetivo_c', 'plano_c', 'desligou_60d')
    r['lentes'] = lentes_auc(m, 'desligou_60d')
    r['hipoteses'] = hipoteses(m, 'desligou_60d')
    return r


if __name__ == '__main__':
    import json, sys
    sys.stdout.reconfigure(encoding='utf-8')
    x = montar()
    print(json.dumps({k: x[k] for k in ['funil', 'churn_base', 'lentes', 'hipoteses', 'declarado_real']}, ensure_ascii=False, indent=1))
