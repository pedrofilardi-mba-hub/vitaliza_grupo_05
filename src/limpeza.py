"""Aplica as decisões do DECISOES.md e grava a cópia limpa em dados/processados/.

Lê só dados/brutos/ (nunca altera nada lá), aplica exatamente as decisões registradas
(D-003 a D-050) e grava um parquet por arquivo. No final confere cada contagem com o
"efeito na contagem" registrado e grava saidas/limpeza_conferencia.md.

Uso, da raiz do projeto:

    .venv\\Scripts\\python.exe src\\limpeza.py
"""
import hashlib
import re
import sys
import unicodedata
from datetime import datetime
from pathlib import Path

import numpy as np
import pandas as pd

sys.path.insert(0, str(Path(__file__).resolve().parent))
from inventario import ler, para_data  # noqa: E402
from qualidade import normalizar, vazio_disfarcado  # noqa: E402

RAIZ = Path(__file__).resolve().parents[1]
PROC = RAIZ / 'dados' / 'processados'
CORTE = pd.Timestamp('2026-09-30 23:59:59')
INICIO_HISTORICO = pd.Timestamp('2024-07-01')
CONF = []  # (arquivo, decisão, medida, esperado, obtido)


def confere(arquivo, decisao, medida, esperado, obtido):
    CONF.append((arquivo, decisao, medida, esperado, obtido))


def grava(df, nome):
    df.to_parquet(PROC / f'{nome}.parquet', index=False)


def sem_acento(s):
    return ''.join(c for c in unicodedata.normalize('NFKD', s) if not unicodedata.combining(c))


# ---------------------------------------------------------------- usuarios
CIDADES = {
    'São Paulo': ['São Paulo', 'Sampa', 'são paulo', 'São Paulo - SP', 'Sao Paulo', 'S. Paulo', 'SAO PAULO', 'SP'],
    'Rio de Janeiro': ['Rio de Janeiro', 'Rio de janeiro', 'rio de janeiro', 'RIO DE JANEIRO', 'RJ', 'Rio'],
    'Belo Horizonte': ['Belo Horizonte', 'Belo horizonte', 'B. Horizonte', 'BELO HORIZONTE', 'BH'],
    'Florianópolis': ['Florianópolis', 'floripa', 'Florianopolis', 'Floripa'],
    'Brasília': ['Brasília', 'Brasília - DF', 'BSB', 'brasilia', 'Brasilia'],
}
DE_PARA_CIDADE = {g: oficial for oficial, grafias in CIDADES.items() for g in grafias}
SEXO = {'F': 'F', 'Fem': 'F', 'feminino': 'F', 'M': 'M', 'Masc': 'M', 'masculino': 'M'}


def usuarios():
    u = ler('usuarios.csv')
    n0 = len(u)
    u['data_cadastro'] = pd.to_datetime(u.data_cadastro)
    # D-021: contas criadas depois do corte saem
    antes_d021 = u.copy()
    u = u[u.data_cadastro <= CORTE].copy()
    confere('usuarios', 'D-021', 'contas', '64.948 → 64.829', f'{n0} → {len(u)}')
    confere('usuarios', 'D-017', 'cidades fora da grafia oficial (antes da D-021)', '13.601',
            int((antes_d021.cidade.map(lambda c: DE_PARA_CIDADE.get(c, c)) != antes_d021.cidade).sum()))
    confere('usuarios', 'D-018', 'sexo F / M / não informado (antes da D-021)', '32.507 / 29.299 / 3.142',
            antes_d021.sexo.map(SEXO).fillna('nao_informado').value_counts().to_dict())
    # D-017: cidade
    antes = u.cidade.copy()
    u['cidade'] = u.cidade.map(lambda c: DE_PARA_CIDADE.get(c, c))
    confere('usuarios', 'D-017', 'cidades distintas', '13', u.cidade.nunique())
    confere('usuarios', 'D-017', 'cidades reescritas (depois da D-021)', '13.601 menos as das 119 contas removidas', int((antes != u.cidade).sum()))
    # D-018: sexo
    u['sexo'] = u.sexo.map(SEXO).fillna('nao_informado')
    confere('usuarios', 'D-018', 'sexo F / M / não informado (depois da D-021)', 'menos as 119 contas removidas', u.sexo.value_counts().to_dict())
    # D-019: sistema
    u['sistema'] = u.sistema.str.lower()
    confere('usuarios', 'D-019', 'sistemas', 'android, ios', sorted(u.sistema.unique()))
    # D-020: nascimento falso vira vazio; idade só como controle; menor marcado
    nasc = pd.to_datetime(u.data_nascimento, errors='coerce')
    idade = (CORTE.normalize() - nasc).dt.days / 365.25
    falsa = (idade < 0) | (idade > 100)
    confere('usuarios', 'D-020', 'nascimentos falsos', '606', int(falsa.sum()))
    idade[falsa] = np.nan
    u['idade'] = np.floor(idade).astype('Int64')
    u['idade_informada'] = u.idade.notna()
    u['menor_de_idade'] = u.idade < 18
    confere('usuarios', 'D-020', 'contas menores de 18', '1', int(u.menor_de_idade.sum()))
    # D-022: código de pessoa (sem expor o e-mail)
    u['pessoa_id'] = u.email.str.lower().str.strip().map(lambda e: hashlib.sha256(e.encode()).hexdigest()[:16])
    confere('usuarios', 'D-022', 'pessoas distintas', '63.989 antes da D-021', u.pessoa_id.nunique())
    grava(u, 'usuarios')
    return u


# ---------------------------------------------------------------- eventos
ATIPICAS = {('assinatura_expirada', 'renovacao_automatica_desligada'), ('renovacao', 'assinatura_expirada'),
            ('assinatura_iniciada', 'assinatura_expirada'), ('renovacao_automatica_desligada', 'renovacao'),
            ('assinatura_expirada', 'cancelamento_web')}


def eventos(ass):
    e = ler('eventos_assinatura.csv')
    e['data_hora_original'] = e.data_hora
    utc = e.data_hora.str.endswith('Z')
    e['data_hora'] = para_data(e.data_hora_original)  # D-009: UTC → Brasília
    ingenua = pd.to_datetime(e.data_hora_original.str.rstrip('Z'), format='mixed')
    confere('eventos', 'D-009', 'horários convertidos', '186.323', int(utc.sum()))
    confere('eventos', 'D-009', 'eventos que mudam de mês', '753', int((ingenua.dt.to_period('M') != e.data_hora.dt.to_period('M')).sum()))
    e = e.sort_values(['user_id', 'data_hora'], kind='stable').reset_index(drop=True)
    # D-010: fase teste/pago
    cobranca = e.evento.isin(['assinatura_iniciada', 'renovacao'])
    ja_pagou = cobranca.astype(int).groupby(e.user_id).cumsum() > 0
    teste = e.evento.isin(['trial_iniciado', 'trial_expirado']) | ((e.evento == 'renovacao_automatica_desligada') & e.plano.isna() & ~ja_pagou)
    e['fase'] = np.where(teste, 'teste', 'pago')
    confere('eventos', 'D-010', 'eventos em fase teste', '72.873', int(teste.sum()))
    # D-011: motivo da saída vindo de assinaturas.csv
    fim = ass[['user_id', 'retrato_0110_data_fim', 'retrato_0110_motivo_fim']].dropna()
    fim = fim.assign(dia=pd.to_datetime(fim.retrato_0110_data_fim))
    e['dia'] = e.data_hora.dt.normalize()
    e = e.merge(fim[['user_id', 'dia', 'retrato_0110_motivo_fim']], on=['user_id', 'dia'], how='left')
    e['motivo_saida'] = np.where(e.evento == 'assinatura_expirada', e.retrato_0110_motivo_fim, None)
    e = e.drop(columns=['dia', 'retrato_0110_motivo_fim'])
    confere('eventos', 'D-011', 'expirações com motivo', '17.830', int(e.motivo_saida.notna().sum()))
    # D-012: sequências atípicas e ciclos atípicos (marcados, nada sai)
    ant = e.groupby('user_id').evento.shift()
    e['sequencia_atipica'] = [(a, b) in ATIPICAS for a, b in zip(ant, e.evento)]
    confere('eventos', 'D-012', 'eventos em sequência atípica', '611', int(e.sequencia_atipica.sum()))
    cob = e[cobranca.values].copy()
    gap = cob.groupby('user_id').data_hora.diff().dt.days
    atip = (cob.evento == 'renovacao') & (((cob.plano == 'mensal') & ((gap < 25) | (gap > 35))) | ((cob.plano == 'anual') & ((gap < 355) | (gap > 375))))
    e['ciclo_atipico'] = False
    e.loc[cob.index[atip.values], 'ciclo_atipico'] = True
    confere('eventos', 'D-012', 'renovações fora do ciclo', '1.154', int(e.ciclo_atipico.sum()))
    ativos = ativos_em(e, CORTE)
    confere('eventos', 'D-012', 'assinantes ativos em 30/09', '14.753', len(ativos))
    grava(e, 'eventos_assinatura')
    return e


def ativos_em(e, t):
    """Regra da D-012: cobrança até t e nenhuma expiração até t."""
    x = e[e.data_hora <= t]
    pagou = set(x[x.evento.isin(['assinatura_iniciada', 'renovacao'])].user_id)
    return pagou - set(x[x.evento == 'assinatura_expirada'].user_id)


# ---------------------------------------------------------------- assinaturas
def assinaturas():
    a = ler('assinaturas.csv')
    a['pagante'] = a.plano_atual != 'cortesia'                                  # D-013
    a['inicio'] = pd.to_datetime(a.inicio)
    a['inicio_antes_historico'] = a.inicio < INICIO_HISTORICO                    # D-014
    a = a.rename(columns={c: f'retrato_0110_{c}' for c in ['status_atual', 'renovacao_automatica', 'data_fim', 'motivo_fim']})  # D-015
    confere('assinaturas', 'D-013', 'ativas pagantes', '14.753', int((a.pagante & (a.retrato_0110_status_atual == 'ativa')).sum()))
    confere('assinaturas', 'D-014', 'iniciadas antes de 07/2024', '5.200', int(a.inicio_antes_historico.sum()))
    confere('assinaturas', 'D-023', 'coluna cadastro_inconsistente criada?', 'não', 'não')
    grava(a, 'assinaturas')
    return a


# ---------------------------------------------------------------- pagamentos
TAXA = {'app_store': .15, 'google_play': .15, 'cartao': .035, 'pix_automatico': .0099}


def pagamentos():
    p = ler('pagamentos.csv')
    n0 = len(p)
    rs = p.valor.str.startswith('R$')
    p['valor'] = pd.to_numeric(p.valor.str.replace('R$', '', regex=False).str.strip().str.replace(',', '.', regex=False))  # D-025
    confere('pagamentos', 'D-025', 'valores convertidos de texto', '19.750', int(rs.sum()))
    p['data_hora_original'] = p.data_hora
    p['data_hora'] = para_data(p.data_hora_original)                               # D-026
    p = p.sort_values(['user_id', 'data_hora'], kind='stable').reset_index(drop=True)
    rep = (p.status == 'aprovado') & p.duplicated(['user_id', 'data_hora', 'valor', 'status'])
    p = p[~rep].copy()                                                            # D-024
    confere('pagamentos', 'D-024', 'linhas', '165.548 → 163.607', f'{n0} → {len(p)}')
    confere('pagamentos', 'D-024', 'cobranças aprovadas', '159.989', int((p.status == 'aprovado').sum()))
    ant = p.groupby('user_id').status.shift()
    # D-027 / D-051: cobrança aprovada logo depois de uma recusa da mesma conta (mediana de 4 dias)
    p['retentativa_real'] = ant.eq('recusado') & p.status.eq('aprovado')
    p = p.drop(columns=['tentativa'])
    confere('pagamentos', 'D-051', 'retentativas reais (corrige a D-027)', '1.881', int(p.retentativa_real.sum()))
    p['valor_liquido'] = np.where(p.status == 'aprovado', p.valor * (1 - p.metodo.map(TAXA)), p.valor)
    s = p[(p.status == 'aprovado') & (p.data_hora >= '2026-09-01') & (p.data_hora < '2026-10-01')]
    confere('pagamentos', 'D-024/25/26', 'faturamento set/2026 (bruto aprovado / líquido)', 'R$ 492.572 / R$ 436.442 (Aula 2)',
            f'R$ {s.valor.sum():,.2f} / R$ {s.valor_liquido.sum():,.2f}')
    grava(p, 'pagamentos')
    return p


# ---------------------------------------------------------------- onboarding
def onboarding():
    o = ler('onboarding.csv')
    disf = o.objetivo_texto.notna() & o.objetivo_texto.map(lambda v: vazio_disfarcado(v) if isinstance(v, str) else False)
    o.loc[disf, 'objetivo_texto'] = None                                          # D-003
    o['objetivo_informado'] = o.objetivo_texto.notna()
    confere('onboarding', 'D-003', 'objetivo preenchido', '44.694', int(o.objetivo_informado.sum()))
    o = o.drop(columns=['como_conheceu'])                                         # D-004
    o['nivel'] = o.nivel.fillna('nao_informado')                                  # D-005
    confere('onboarding', 'D-005', 'nível não informado', '4.513', int((o.nivel == 'nao_informado').sum()))
    d = o.dias_por_semana.str.strip().str.lower()
    o['dias_por_semana'] = pd.to_numeric(d.str.extract(r'^(\d+)')[0], errors='coerce').where(d != 'todos', 7).astype('Int64')  # D-006
    o['dias_informado'] = o.dias_por_semana.notna()
    confere('onboarding', 'D-006', 'dias por semana: preenchidos / vazios / fora de 1-7', '57.561 / 6.368 / 0',
            f'{int(o.dias_informado.sum())} / {int((~o.dias_informado).sum())} / {int(((o.dias_por_semana < 1) | (o.dias_por_semana > 7)).sum())}')
    o['objetivo_norm'] = o.objetivo_texto.map(lambda v: normalizar(v) if isinstance(v, str) else None)  # D-007
    o['respondido_em'] = pd.to_datetime(o.respondido_em)
    grava(o, 'onboarding')
    return o


# ---------------------------------------------------------------- atividades
TIPOS = {'run': 'corrida', 'walk': 'caminhada', 'strength': 'forca', 'ride': 'pedal'}
AR_LIVRE = {'corrida', 'caminhada', 'pedal'}


def atividades():
    a = pd.read_parquet(RAIZ / 'dados' / 'brutos' / 'atividades.parquet')
    n0 = len(a)
    a['inicio_original'] = a.inicio
    a['inicio'] = pd.to_datetime(a.inicio)
    g = a.origem == 'garmin'
    a.loc[g, 'inicio'] = a.loc[g, 'inicio'] - pd.Timedelta(hours=3)              # D-030
    confere('atividades', 'D-030', 'horários do Garmin ajustados', '207.954', int(g.sum()))
    confere('atividades', 'D-030', 'treinos depois do corte', '0', int((a.inicio > CORTE).sum()))
    # D-031: duplicata app × relógio (regra da Aula 2, tipo como gravado); sai a cópia do app
    app = a[a.origem == 'app'][['user_id', 'tipo', 'duracao_min', 'inicio']].reset_index()
    rel = a[a.origem != 'app'][['user_id', 'tipo', 'duracao_min', 'inicio']].reset_index()
    pares = app.merge(rel, on=['user_id', 'tipo', 'duracao_min'], suffixes=('_app', '_rel'))
    pares = pares[(pares.inicio_app - pares.inicio_rel).abs() <= pd.Timedelta(minutes=5)]
    confere('atividades', 'D-031', 'pares app × relógio', '9.383', pares.index_rel.nunique())
    a = a.drop(index=pares.index_app.unique())
    confere('atividades', 'D-031', 'treinos', '1.254.475 → 1.245.092', f'{n0} → {len(a)}')
    a['tipo'] = a.tipo.replace(TIPOS)                                             # D-032
    a['modalidade'] = np.where(a.tipo.isin(AR_LIVRE), 'ar_livre', 'video')
    confere('atividades', 'D-032', 'tipos distintos', '7', a.tipo.nunique())
    # D-033: distância corrompida recalculada pelo ritmo
    big = a.distancia_km > 200
    a['distancia_original'] = a.distancia_km
    a.loc[big, 'distancia_km'] = a.loc[big, 'duracao_min'] / a.loc[big, 'ritmo_min_km']
    confere('atividades', 'D-033', 'distâncias recalculadas', '951 (menos as que estavam em cópias do app removidas na D-031)', int(big.sum()))
    # D-034: duração zero recalculada ou marcada
    z = a.duracao_min == 0
    rec = z & a.distancia_km.notna() & a.ritmo_min_km.notna()
    a.loc[rec, 'duracao_min'] = a.loc[rec, 'ritmo_min_km'] * a.loc[rec, 'distancia_km']
    a['duracao_invalida'] = z & ~rec
    a.loc[a.duracao_invalida, 'duracao_min'] = np.nan
    confere('atividades', 'D-034', 'durações recalculadas / marcadas', '1.972 / 1.677 (menos as cópias do app removidas na D-031)', f'{int(rec.sum())} / {int(a.duracao_invalida.sum())}')
    # D-035: GPS falho
    a['gps_falhou'] = ~a.gps_ok
    apaga = a.gps_falhou & a.distancia_km.notna()
    a.loc[apaga, 'distancia_km'] = np.nan
    confere('atividades', 'D-035', 'treinos com GPS falho / distâncias apagadas', '14.779 / 7.455 (menos as cópias do app removidas na D-031)',f'{int(a.gps_falhou.sum())} / {int(apaga.sum())}')
    a['treino_com'] = a.treino_com.replace('', None)
    grava(a.reset_index(drop=True), 'atividades')
    return a


# ---------------------------------------------------------------- uso mensal (D-028, D-029)
def uso_mensal(e, atv):
    um = ler('uso_mensal.csv')
    for c in ['atividades', 'atividades_ar_livre', 'atividades_video', 'minutos', 'dias_ativos', 'sessoes_app']:
        um[c] = pd.to_numeric(um[c])
    meses = pd.period_range('2025-01', '2026-09', freq='M')
    cob = e[e.evento.isin(['assinatura_iniciada', 'renovacao'])].groupby('user_id').data_hora.min()
    fim = e[e.evento == 'assinatura_expirada'].groupby('user_id').data_hora.max()
    linhas = []
    for m in meses:
        ini, fimm = m.start_time, m.end_time
        ok = cob[cob <= fimm].index
        f = fim.reindex(ok)
        ativos = ok[(f.isna()) | (f >= ini)]   # assinante pagante em algum momento do mês
        linhas.append(pd.DataFrame({'user_id': ativos, 'mes': str(m)}))
    painel = pd.concat(linhas, ignore_index=True)
    # 2025: valores do resumo; 2026: treinos, minutos e dias do detalhe (D-029); sessões sempre do resumo
    atv = atv.assign(mes=atv.inicio.dt.strftime('%Y-%m'))
    det = atv.groupby(['user_id', 'mes']).agg(atividades=('atividade_id', 'size'), atividades_ar_livre=('modalidade', lambda s: (s == 'ar_livre').sum()),
                                              minutos=('duracao_min', 'sum'), dias_ativos=('inicio', lambda d: d.dt.date.nunique())).reset_index()
    det['atividades_video'] = det.atividades - det.atividades_ar_livre
    res = um.set_index(['user_id', 'mes'])
    p = painel.set_index(['user_id', 'mes'])
    p = p.join(res[['sessoes_app']], how='left')
    r25 = res[res.index.get_level_values('mes') < '2026-01'][['atividades', 'atividades_ar_livre', 'atividades_video', 'minutos', 'dias_ativos']]
    d26 = det.set_index(['user_id', 'mes'])[['atividades', 'atividades_ar_livre', 'atividades_video', 'minutos', 'dias_ativos']]
    p = p.join(pd.concat([r25, d26]), how='left').fillna(0).reset_index()
    p['fonte'] = np.where(p.mes < '2026-01', 'resumo', 'detalhe')
    grava(p, 'painel_uso_assinantes')
    confere('uso_mensal', 'D-028', 'linhas do painel em jan/2025 / set/2026', '≈ 8,5 mil / ≈ 15,4 mil',
            f'{int((p.mes == "2025-01").sum())} / {int((p.mes == "2026-09").sum())}')
    z = p.groupby(p.mes.str[:4]).apply(lambda g: (g.atividades == 0).mean())
    confere('uso_mensal', 'D-028', 'assinantes sem treino no mês (2025 / 2026)', 'parecidos nos dois anos', f'{z.get("2025", 0):.1%} / {z.get("2026", 0):.1%}')
    # resumo original com a marca de quem é assinante no mês (nada sai)
    chave = set(zip(painel.user_id, painel.mes))
    um['assinante_no_mes'] = [(u, m) in chave for u, m in zip(um.user_id, um.mes)]
    um['fonte'] = 'resumo'
    grava(um, 'uso_mensal')
    confere('uso_mensal', 'D-028', 'linhas do resumo original mantidas', '591.662', len(um))
    return p


# ---------------------------------------------------------------- campanha
def campanha(e):
    c = ler('campanha_ago26.csv')
    for col in ['abriu_push', 'abriu_email', 'clicou']:
        c[col] = c[col] == 'True'                                                 # D-037
    ativos = ativos_em(e, pd.Timestamp('2026-08-10 10:00:00'))
    c['em_teste_no_envio'] = ~c.user_id.isin(ativos)                              # D-036
    c['enviado_em'] = pd.to_datetime(c.enviado_em)
    confere('campanha', 'D-036', 'sorteados / em teste no envio', '14.120 / 48', f'{len(c)} / {int(c.em_teste_no_envio.sum())}')
    confere('campanha', 'D-037', 'cliques (soma do booleano)', '1.604', int(c.clicou.sum()))
    grava(c, 'campanha_ago26')
    return c


# ---------------------------------------------------------------- textos e rede
def amizades():
    f = ler('amizades.csv')
    f['desde'] = pd.to_datetime(f.desde)
    n0 = len(f); f = f[f.desde <= CORTE]                                           # D-039
    confere('amizades', 'D-039', 'relações', '113.480 → 113.207', f'{n0} → {len(f)}')
    grava(f, 'amizades')


def feed_posts(usu):
    f = ler('feed_posts.csv')
    f['data_hora'] = pd.to_datetime(f.data_hora); f['curtidas'] = pd.to_numeric(f.curtidas)
    n0 = len(f); f = f[f.data_hora <= CORTE].copy()                                # D-043
    confere('feed_posts', 'D-043', 'posts', '119.309 → 119.187', f'{n0} → {len(f)}')
    cad = f.user_id.map(usu.set_index('user_id').data_cadastro)
    f['post_antes_cadastro'] = f.data_hora < cad                                  # D-044
    f['data_post'] = f.data_hora.dt.normalize()
    confere('feed_posts', 'D-044', 'posts antes do horário de cadastro', '692', int(f.post_antes_cadastro.sum()))
    f['texto_norm'] = f.texto.map(normalizar)                                      # D-045
    grava(f, 'feed_posts')


def tickets():
    t = ler('tickets_suporte.csv')
    t['aberto_em'] = pd.to_datetime(t.aberto_em); t['resolvido_em'] = pd.to_datetime(t.resolvido_em)
    t['texto_norm'] = t.texto_cliente.map(normalizar)                              # D-042
    moda = t.groupby('texto_norm').categoria_atendente.agg(lambda s: s.value_counts().index[0])
    t['categoria_texto'] = t.texto_norm.map(moda)                                 # D-040
    confere('tickets', 'D-040', 'categoria do texto ≠ do atendente', '≈ 1/3', f'{(t.categoria_texto != t.categoria_atendente).mean():.1%}')
    depois = t.resolvido_em > CORTE
    t['status_no_corte'] = np.where(depois, 'aberto', t.status)                    # D-041
    t['resolvido_em_no_corte'] = t.resolvido_em.where(~depois)
    confere('tickets', 'D-041', 'resolvidos depois do corte (viram abertos no corte)', '41', int(depois.sum()))
    grava(t, 'tickets_suporte')


TEMAS = {'objetivo_cumprido': r'prova|maratona|formatura|casamento|viagem|evento|era so|era só|objetivo cumprido',
         'problema_tecnico': r'bug|trav|gps|erro|atualiza|sincroniz|crash', 'preco': r'caro|preco|preço|valor|dinheiro|aumento|aumentou',
         'nao_uso': r'nao uso|não uso|sem tempo|parei|nao tenho tempo|não tenho tempo|usava pouco|uso pouco|não estou usando|nao estou usando',
         'outro_app': r'strava|nike|outro app|garmin connect|runna|adidas', 'saude': r'lesao|lesão|medico|médico|cirurgia|gravida|grávida|machuc|joelho|lombar'}


def pesquisa():
    q = ler('pesquisa_saida.csv')
    q['respondido_em'] = pd.to_datetime(q.respondido_em)
    def tema(s):
        if not isinstance(s, str):
            return None
        hits = [k for k, rx in TEMAS.items() if re.search(rx, s.lower())]
        return hits[0] if len(hits) == 1 else None
    q['motivo_revisado'] = q.comentario.map(tema).fillna(q.motivo_principal)       # D-046
    confere('pesquisa', 'D-046', 'respostas com motivo "objetivo cumprido"', '≈ 190 na avaliação; a regra de palavras-chave é provisória (IA no objetivo 5)',int((q.motivo_revisado == 'objetivo_cumprido').sum()))
    q = q.sort_values(['user_id', 'respondido_em'])
    q['ultima_resposta'] = ~q.duplicated('user_id', keep='last')                  # D-048
    confere('pesquisa', 'D-048', 'respostas / pessoas', '643 / 641', f'{len(q)} / {int(q.ultima_resposta.sum())}')
    q['texto_norm'] = q.comentario.map(lambda v: normalizar(v) if isinstance(v, str) else None)  # D-049
    grava(q, 'pesquisa_saida')


def relatorio():
    L = ['# Conferência da limpeza', '',
         f'Gerado por `src/limpeza.py` em {datetime.now():%d/%m/%Y %H:%M}. Cada linha compara o efeito registrado no `DECISOES.md` '
         'com o que o script obteve. A cópia limpa fica em `dados/processados/` (fora do Git pelo tamanho, D-050; recriada por este script); '
         'os brutos não foram alterados. Quando o número difere do registrado, a coluna Esperado explica por quê.', '',
         '| Arquivo | Decisão | Medida | Esperado | Obtido |', '|---|---|---|---|---|']
    L += [f'| {a} | {d} | {m} | {e} | {o} |' for a, d, m, e, o in CONF]
    (RAIZ / 'saidas' / 'limpeza_conferencia.md').write_text('\n'.join(L) + '\n', encoding='utf-8')


def main():
    sys.stdout.reconfigure(encoding='utf-8')
    PROC.mkdir(parents=True, exist_ok=True)
    print('usuarios'); usu = usuarios()
    print('assinaturas'); ass = assinaturas()
    print('eventos'); ev = eventos(ass)
    print('pagamentos'); pagamentos()
    print('onboarding'); onboarding()
    print('atividades'); atv = atividades()
    print('uso mensal'); uso_mensal(ev, atv)
    print('campanha'); campanha(ev)
    print('amizades'); amizades()
    print('posts'); feed_posts(usu)
    print('chamados'); tickets()
    print('pesquisa'); pesquisa()
    relatorio()
    for a, d, m, e, o in CONF:
        print(f'{a:12} {d:11} {m}: esperado {e} | obtido {o}')


if __name__ == '__main__':
    main()
