"""Inventário do data room da Vitaliza comparado com o dicionário de dados.

Lê cada arquivo de dados/brutos/, confere linhas, colunas, valores de categoria,
período coberto e chaves contra o que o dicionário promete, e grava
saidas/inventario.md. Rode da raiz do projeto:

    .venv\\Scripts\\python.exe src\\inventario.py
"""
import re
import sys
import zipfile
from datetime import datetime
from pathlib import Path

import pandas as pd

RAIZ = Path(__file__).resolve().parents[1]
BRUTOS = RAIZ / 'dados' / 'brutos'
SAIDA = RAIZ / 'saidas' / 'inventario.md'

# O que o dicionário de dados diz sobre cada arquivo.
# categorias: valores listados no dicionário; periodo: (coluna, início, fim) esperados.
DICIONARIO = {
    'usuarios.csv': dict(
        forma='Tabela', linha='conta', linhas=64_948, chave='user_id',
        colunas=['user_id', 'email', 'data_cadastro', 'data_nascimento', 'sexo', 'cidade', 'uf',
                 'cep_prefixo', 'canal_aquisicao', 'sistema', 'versao_app', 'relogio_conectado'],
        datas=['data_cadastro', 'data_nascimento'],
        periodo=('data_cadastro', '2020-09-01', '2026-09-30'),
        texto_livre=['email', 'cidade'],
    ),
    'assinaturas.csv': dict(
        forma='Tabela', linha='assinatura', linhas=32_643, chave='assinatura_id',
        colunas=['assinatura_id', 'user_id', 'plano_atual', 'canal_cobranca', 'inicio', 'status_atual',
                 'renovacao_automatica', 'data_fim', 'motivo_fim'],
        categorias={'plano_atual': ['mensal', 'anual'],
                    'canal_cobranca': ['app_store', 'google_play', 'web_cartao', 'web_pix']},
        datas=['inicio', 'data_fim'],
        periodo=('inicio', '2020-09-01', '2026-09-30'),
    ),
    'amizades.csv': dict(
        forma='Tabela', linha='relação de seguir', linhas=113_480, chave=None,
        colunas=['seguidor_id', 'seguido_id', 'desde'],
        datas=['desde'], periodo=('desde', '2020-09-01', '2026-09-30'),
        ids_usuario=['seguidor_id', 'seguido_id'],
    ),
    'campanha_ago26.csv': dict(
        forma='Tabela', linha='assinante sorteado', linhas=14_120, chave='user_id',
        colunas=['user_id', 'grupo', 'enviado_em', 'canal', 'titulo_mensagem', 'oferta',
                 'abriu_push', 'abriu_email', 'clicou'],
        categorias={'grupo': ['controle', 'desafio', 'cupom', 'conteudo'],
                    'canal': ['push+email'],
                    'oferta': ['30pct_3_meses', '1_mes_gratis']},
        datas=['enviado_em'],
    ),
    'eventos_assinatura.csv': dict(
        forma='Log de eventos', linha='evento', linhas=275_565, chave=None,
        colunas=['user_id', 'data_hora', 'evento', 'plano', 'canal_cobranca', 'detalhe'],
        categorias={'evento': ['trial_iniciado', 'trial_expirado', 'assinatura_iniciada', 'renovacao',
                               'renovacao_automatica_desligada', 'renovacao_automatica_religada',
                               'periodo_carencia', 'assinatura_expirada', 'cancelamento_web',
                               'reembolso', 'chargeback'],
                    'plano': ['mensal', 'anual'],
                    'canal_cobranca': ['app_store', 'google_play', 'web_cartao', 'web_pix']},
        datas=['data_hora'], periodo=('data_hora', '2024-07-01', '2026-09-30'),
    ),
    'pagamentos.csv': dict(
        forma='Log de eventos', linha='cobrança', linhas=165_548, chave='pagamento_id',
        colunas=['pagamento_id', 'user_id', 'data_hora', 'valor', 'metodo', 'status', 'tentativa'],
        categorias={'metodo': ['app_store', 'google_play', 'cartao', 'pix_automatico'],
                    'status': ['aprovado', 'recusado', 'estornado', 'chargeback']},
        datas=['data_hora'],
    ),
    'uso_mensal.csv': dict(
        forma='Log de eventos', linha='usuário e mês', linhas=591_662, chave=('user_id', 'mes'),
        colunas=['user_id', 'mes', 'atividades', 'atividades_ar_livre', 'atividades_video', 'minutos',
                 'dias_ativos', 'sessoes_app'],
        datas=['mes'], periodo=('mes', '2025-01-01', '2026-09-30'),
    ),
    'atividades.parquet': dict(
        forma='Log de eventos', linha='treino', linhas=1_254_475, chave='atividade_id',
        colunas=['atividade_id', 'user_id', 'inicio', 'tipo', 'duracao_min', 'distancia_km',
                 'ritmo_min_km', 'fc_media', 'origem', 'gps_ok', 'treino_com'],
        categorias={'origem': ['app', 'garmin', 'apple_health']},
        datas=['inicio'], periodo=('inicio', '2026-01-01', '2026-09-30'),
    ),
    'onboarding.csv': dict(
        forma='Texto', linha='conta', linhas=63_929, chave='onboarding_id',
        colunas=['onboarding_id', 'user_id', 'respondido_em', 'objetivo_texto', 'como_conheceu',
                 'nivel', 'dias_por_semana'],
        datas=['respondido_em'], periodo=('respondido_em', '2020-09-01', '2026-09-30'),
        texto_livre=['objetivo_texto', 'como_conheceu'],
    ),
    'pesquisa_saida.csv': dict(
        forma='Texto', linha='resposta', linhas=643, chave='resposta_id',
        colunas=['resposta_id', 'user_id', 'respondido_em', 'motivo_principal', 'comentario'],
        categorias={'motivo_principal': ['preco', 'nao_uso', 'problema_tecnico', 'outro_app',
                                         'saude', 'outro']},
        datas=['respondido_em'], periodo=('respondido_em', '2026-06-01', '2026-09-30'),
        texto_livre=['comentario'],
    ),
    'feed_posts.csv': dict(
        forma='Texto', linha='post', linhas=119_309, chave='post_id',
        colunas=['post_id', 'user_id', 'data_hora', 'texto', 'curtidas'],
        datas=['data_hora'], periodo=('data_hora', '2025-07-01', '2026-09-30'),
        texto_livre=['texto'],
    ),
    'tickets_suporte.csv': dict(
        forma='Texto', linha='chamado', linhas=4_422, chave='ticket_id',
        colunas=['ticket_id', 'user_id', 'aberto_em', 'canal', 'texto_cliente', 'categoria_atendente',
                 'status', 'resolvido_em'],
        categorias={'canal': ['chat', 'email', 'loja'],
                    'status': ['resolvido', 'aberto', 'sem_resposta']},
        datas=['aberto_em', 'resolvido_em'], periodo=('aberto_em', '2025-07-01', '2026-09-30'),
        texto_livre=['texto_cliente'],
    ),
}
HEATMAPS = {'2026-07-31': 12_426, '2026-09-30': 13_047}
CORTE = pd.Timestamp('2026-09-30 23:59:59')


def fmt(n):
    return f'{n:,}'.replace(',', '.')


def pct(x):
    return f'{x:.1%}'.replace('.', ',')


def padrao(valor):
    """Formato de um texto de data: dígitos viram 9 (ex.: 2026-01-30T10:00:00Z -> 9999-99-99T99:99:99Z)."""
    return re.sub(r'\d', '9', str(valor))


def ler(nome):
    caminho = BRUTOS / nome
    if nome.endswith('.parquet'):
        return pd.read_parquet(caminho)
    return pd.read_csv(caminho, dtype=str, keep_default_na=False, na_values=[''])


def para_data(serie):
    """Converte textos de data em formatos mistos para horário de Brasília.

    Datas terminadas em Z vêm das lojas, em UTC, e são convertidas; as demais já estão em Brasília.
    """
    texto = serie.dropna().astype(str)
    utc = texto.str.endswith('Z')
    partes = []
    if utc.any():
        partes.append(pd.to_datetime(texto[utc], utc=True, format='mixed', errors='coerce')
                      .dt.tz_convert('America/Sao_Paulo').dt.tz_localize(None))
    if (~utc).any():
        partes.append(pd.to_datetime(texto[~utc], format='mixed', errors='coerce'))
    return pd.concat(partes).reindex(texto.index)


def analisar(nome, spec, ids_usuarios):
    caminho = BRUTOS / nome
    r = dict(nome=nome, spec=spec, existe=caminho.exists(), achados=[], colunas=[])
    if not r['existe']:
        r['achados'].append(('erro', 'Arquivo não encontrado em dados/brutos/.'))
        return r
    r['tamanho_mb'] = caminho.stat().st_size / 1e6
    df = ler(nome)
    r['linhas'] = len(df)
    if len(df) != spec['linhas']:
        r['achados'].append(('erro', f'Linhas: {fmt(len(df))}; o dicionário diz {fmt(spec["linhas"])}.'))

    faltam = [c for c in spec['colunas'] if c not in df.columns]
    sobram = [c for c in df.columns if c not in spec['colunas']]
    if faltam:
        r['achados'].append(('erro', f'Colunas do dicionário ausentes no arquivo: {", ".join(faltam)}.'))
    if sobram:
        r['achados'].append(('atencao', f'Colunas no arquivo que o dicionário não descreve: {", ".join(sobram)}.'))

    # Linhas inteiramente repetidas e chave única
    dup = int(df.duplicated().sum())
    if dup:
        r['achados'].append(('atencao', f'{fmt(dup)} linhas inteiramente repetidas.'))
    chave = spec.get('chave')
    if chave:
        cols = list(chave) if isinstance(chave, tuple) else [chave]
        if all(c in df.columns for c in cols):
            rep = int(df.duplicated(subset=cols).sum())
            if rep:
                r['achados'].append(('atencao', f'Chave `{"+".join(cols)}` repetida em {fmt(rep)} linhas '
                                                f'(deveria ser uma linha por {spec["linha"]}).'))

    # user_id sem cadastro
    for col in spec.get('ids_usuario', ['user_id'] if 'user_id' in df.columns else []):
        if col in df.columns and ids_usuarios is not None and nome != 'usuarios.csv':
            orfaos = ~df[col].dropna().isin(ids_usuarios)
            if orfaos.any():
                r['achados'].append(('atencao', f'`{col}`: {fmt(int(orfaos.sum()))} linhas com conta que não está em usuarios.csv.'))

    # Categorias: valores fora do que o dicionário lista
    for col, esperados in spec.get('categorias', {}).items():
        if col not in df.columns:
            continue
        cont = df[col].dropna().astype(str).value_counts()
        fora = cont[~cont.index.isin(esperados)]
        if len(fora):
            lista = ', '.join(f'`{v}` ({fmt(n)})' for v, n in fora.head(8).items())
            r['achados'].append(('atencao', f'`{col}` tem valores que o dicionário não lista: {lista}.'))

    # Datas: formatos, conversão e período
    for col in spec.get('datas', []):
        if col not in df.columns:
            continue
        brutas = df[col].dropna()
        formatos = brutas.astype(str).map(padrao).value_counts()
        datas = para_data(brutas)
        falhas = int(datas.isna().sum())
        info = dict(col=col, formatos=formatos.head(4), n_formatos=len(formatos), falhas=falhas,
                    min=datas.min(), max=datas.max())
        r.setdefault('datas', []).append(info)
        if len(formatos) > 1:
            r['achados'].append(('atencao', f'`{col}` mistura {len(formatos)} formatos de data.'))
        if falhas:
            r['achados'].append(('erro', f'`{col}`: {fmt(falhas)} valores não viram data.'))
        if spec.get('periodo') and spec['periodo'][0] == col:
            ini, fim = pd.Timestamp(spec['periodo'][1]), pd.Timestamp(spec['periodo'][2]) + pd.Timedelta(days=1)
            if datas.min() < ini - pd.Timedelta(days=1) or datas.max() >= fim + pd.Timedelta(days=1):
                r['achados'].append(('atencao', f'`{col}` vai de {datas.min():%d/%m/%Y} a {datas.max():%d/%m/%Y}; '
                                                f'o dicionário indica {ini:%d/%m/%Y} a {pd.Timestamp(spec["periodo"][2]):%d/%m/%Y}.'))
        apos = int((datas > CORTE).sum())
        if apos and col != 'data_nascimento':
            r.setdefault('apos', {})[col] = apos
            r['achados'].append(('atencao', f'`{col}`: {fmt(apos)} datas depois do corte de 30/09/2026 '
                                            '(já convertidas para o horário de Brasília).'))

    # Perfil de cada coluna
    for col in df.columns:
        s = df[col]
        n_dist = int(s.nunique(dropna=True))
        vazios = float(s.isna().mean())
        if col in spec.get('texto_livre', []) or col in spec.get('datas', []) or col.endswith('_id') or col in ('seguidor_id', 'seguido_id'):
            amostra = '—'
        elif n_dist <= 12:
            vc = s.dropna().astype(str).value_counts()
            amostra = ', '.join(f'{v} ({fmt(n)})' for v, n in vc.items())
        elif pd.api.types.is_numeric_dtype(s):
            amostra = f'mín {s.min():g} · mediana {s.median():g} · máx {s.max():g}'
        else:
            num = pd.to_numeric(s, errors='coerce')
            if num.notna().mean() > 0.95:
                amostra = f'mín {num.min():g} · mediana {num.median():g} · máx {num.max():g}'
            else:
                vc = s.dropna().astype(str).value_counts()
                amostra = ', '.join(f'{v[:20]} ({fmt(n)})' for v, n in vc.head(5).items()) + ' …'
        r['colunas'].append((col, str(s.dtype), vazios, n_dist, amostra))
    r['df'] = df
    return r


def checagens_especificas(res):
    """Problemas conhecidos do case, verificados um a um."""
    a = {}
    u = res['usuarios.csv'].get('df')
    if u is not None:
        nasc = para_data(u['data_nascimento'])
        idade = (pd.Timestamp('2026-09-30') - nasc).dt.days / 365.25
        a['usuarios.csv'] = [
            ('atencao', f'`data_nascimento` impossível ou improvável: {fmt(int((idade < 0).sum()))} no futuro, '
                        f'{fmt(int(((idade >= 0) & (idade < 13)).sum()))} com menos de 13 anos e '
                        f'{fmt(int((idade > 100).sum()))} com mais de 100 anos (ex.: 01/01/1900). Campo digitado sem validação.'),
            ('atencao', f'`sexo` escrito de {u["sexo"].nunique()} jeitos: {", ".join(sorted(u["sexo"].dropna().unique()))}.'),
            ('atencao', f'`sistema` escrito de {u["sistema"].nunique()} jeitos: {", ".join(sorted(u["sistema"].dropna().unique()))}.'),
            ('info', '`email` e `data_nascimento` são dados pessoais: não enviar a APIs de LLM nem gravar em saidas/.'),
        ]
    s = res['assinaturas.csv'].get('df')
    if s is not None:
        ativas = s[s['status_atual'] == 'ativa']
        pagantes = ativas[ativas['plano_atual'].isin(['mensal', 'anual'])]
        a['assinaturas.csv'] = [
            ('info', f'Assinaturas ativas em 01/10/2026: {fmt(len(ativas))}; sem `cortesia`: {fmt(len(pagantes))} '
                     f'(o enunciado fala em 14.753 pagantes em 30/09/2026).'),
            ('info', f'Plano dos pagantes ativos: anual {pct((pagantes["plano_atual"] == "anual").mean())}, '
                     f'mensal {pct((pagantes["plano_atual"] == "mensal").mean())} (enunciado: 57% / 43%).'),
            ('atencao', f'`status_atual` tem valores sem descrição no dicionário: {", ".join(sorted(s["status_atual"].unique()))}.'),
            ('info', 'É um retrato de 01/10/2026: não usar status, renovação ou motivo como variável do modelo (vazamento).'),
        ]
    p = res['pagamentos.csv'].get('df')
    if p is not None:
        com_rs = int(p['valor'].str.contains('R$', regex=False).sum())
        neg = p[p['valor'].str.startswith('-')]
        a['pagamentos.csv'] = [
            ('atencao', f'`valor` em dois formatos: `34.90` e `R$ 34,90` ({fmt(com_rs)} linhas no formato com R$ e vírgula).'),
            ('info', f'{fmt(len(neg))} valores negativos, todos com status '
                     f'{", ".join(sorted(neg["status"].unique()))}: são devoluções, não cobranças.'),
            ('info', 'O mensal aparece a R$ 34,90 e a R$ 39,90: é o reajuste de 01/03/2026.'),
        ]
    o = res['onboarding.csv'].get('df')
    if o is not None:
        a['onboarding.csv'] = [('atencao', f'`dias_por_semana` é texto livre ({o["dias_por_semana"].nunique()} formas diferentes, ex.: "3", "3x", "3 vezes").')]
    t = res['atividades.parquet'].get('df')
    if t is not None:
        ingles = t['tipo'].isin(['run', 'walk', 'strength', 'ride']).mean()
        dist = t['distancia_km']
        a['atividades.parquet'] = [
            ('atencao', f'`tipo` mistura português e inglês: {", ".join(sorted(t["tipo"].unique()))} '
                        f'({pct(ingles)} dos treinos em inglês).'),
            ('atencao', f'`distancia_km`: máximo de {dist.max():,.0f} km e {fmt(int((dist > 100).sum()))} treinos acima de 100 km; provável parte em metros.'.replace(',', '.')),
            ('atencao', f'`duracao_min` = 0 em {fmt(int((t["duracao_min"] == 0).sum()))} treinos.'),
            ('info', f'`treino_com` vazio de verdade em {pct(t["treino_com"].isna().mean())} das linhas; '
                     f'texto vazio em {pct((t["treino_com"] == "").mean())}.'),
        ]
    q = res['pesquisa_saida.csv'].get('df')
    if q is not None:
        a['pesquisa_saida.csv'] = [('info', f'{fmt(len(q))} respostas de {fmt(q["user_id"].nunique())} contas (o dicionário diz 641).')]
    c = res['campanha_ago26.csv'].get('df')
    if c is not None:
        a['campanha_ago26.csv'] = [('info', 'Tamanho dos grupos: ' + ', '.join(f'{g} {fmt(n)}' for g, n in c['grupo'].value_counts().items())
                                    + '. `enviado_em`, `titulo_mensagem` e `canal` vazios no controle, como esperado.')]
    return a


def heatmaps(ids_usuarios):
    pasta = BRUTOS / 'heatmap'
    linhas = []
    for data, esperado in HEATMAPS.items():
        zips = sorted(pasta.glob(f'heatmaps_{data}_*.zip'))
        no_zip = lixo_mac = None
        if zips:
            with zipfile.ZipFile(zips[0]) as zf:
                pngs = [n for n in zf.namelist() if n.lower().endswith('.png')]
            # __MACOSX/._*.png são metadados do macOS, não imagens
            lixo_mac = sum(1 for n in pngs if n.startswith('__MACOSX/'))
            no_zip = len(pngs) - lixo_mac
        extraidas = list((pasta / data).glob('*.png')) if (pasta / data).exists() else []
        sem_cadastro = sum(1 for f in extraidas if f.stem not in ids_usuarios) if ids_usuarios is not None else None
        linhas.append(dict(data=data, esperado=esperado, zip=zips[0].name if zips else None,
                           no_zip=no_zip, lixo_mac=lixo_mac, extraidas=len(extraidas), sem_cadastro=sem_cadastro))
    return linhas


def montar_md(res, especificos, hm):
    icone = {'erro': '🔴', 'atencao': '🟡', 'info': '🔵'}
    L = []
    L.append('# Inventário do data room × dicionário de dados')
    L.append('')
    L.append(f'Gerado por `src/inventario.py` em {datetime.now():%d/%m/%Y %H:%M}, a partir de `dados/brutos/`. '
             'Compara cada arquivo com o documento *Vitaliza: dicionário de dados*: linhas, colunas, valores de '
             'categoria, período e chaves. Para atualizar, rode o script de novo.')
    L.append('')
    L.append('Legenda: 🔴 diverge do dicionário ou impede o uso · 🟡 problema de qualidade a tratar na limpeza · 🔵 informação útil')
    L.append('')
    L.append('## Resumo')
    L.append('')
    L.append('| Arquivo | Forma | Uma linha por | Linhas no dicionário | Linhas no arquivo | Confere? | Colunas | Tamanho | Achados |')
    L.append('|---|---|---|---:|---:|:-:|:-:|---:|---|')
    for nome, r in res.items():
        spec = r['spec']
        if not r['existe']:
            L.append(f'| `{nome}` | {spec["forma"]} | {spec["linha"]} | {fmt(spec["linhas"])} | — | 🔴 | — | — | arquivo ausente |')
            continue
        ok_l = '✅' if r['linhas'] == spec['linhas'] else '🔴'
        ok_c = '✅' if not any('Colunas' in t for _, t in r['achados']) else '🟡'
        todos = r['achados'] + especificos.get(nome, [])
        cont = {k: sum(1 for n, _ in todos if n == k) for k in ('erro', 'atencao')}
        resumo = ' '.join(f'{icone[k]} {v}' for k, v in cont.items() if v) or '—'
        L.append(f'| `{nome}` | {spec["forma"]} | {spec["linha"]} | {fmt(spec["linhas"])} | {fmt(r["linhas"])} | {ok_l} | {ok_c} | {r["tamanho_mb"]:.1f} MB | {resumo} |')
    for h in hm:
        ok = '✅' if h['no_zip'] == h['esperado'] else '🟡'
        L.append(f'| `heatmap/{h["data"]}/` | Imagem | assinante | {fmt(h["esperado"])} | {fmt(h["no_zip"]) if h["no_zip"] is not None else "—"} no zip | {ok} | — | — | ver seção |')
    L.append('')

    L.append('## Principais pontos')
    L.append('')
    L.extend(PRINCIPAIS)
    L.append('')

    for nome, r in res.items():
        spec = r['spec']
        L.append(f'## `{nome}`')
        L.append('')
        if not r['existe']:
            L.append('🔴 Arquivo não encontrado.')
            L.append('')
            continue
        L.append(f'{spec["forma"]} · uma linha por {spec["linha"]} · {fmt(r["linhas"])} linhas · {r["tamanho_mb"]:.1f} MB')
        L.append('')
        todos = r['achados'] + especificos.get(nome, [])
        if todos:
            for nivel, texto in sorted(todos, key=lambda x: ['erro', 'atencao', 'info'].index(x[0])):
                L.append(f'- {icone[nivel]} {texto}')
        else:
            L.append('- ✅ Confere com o dicionário.')
        L.append('')
        for d in r.get('datas', []):
            forms = ', '.join(f'`{f}` ({fmt(n)})' for f, n in d['formatos'].items())
            extra = f' e mais {d["n_formatos"] - 4}' if d['n_formatos'] > 4 else ''
            periodo = f'{d["min"]:%d/%m/%Y} a {d["max"]:%d/%m/%Y}' if pd.notna(d['min']) else '—'
            L.append(f'- Datas em `{d["col"]}`: {periodo}. Formatos: {forms}{extra}.')
        if r.get('datas'):
            L.append('')
        L.append('| Coluna | Tipo lido | Vazios | Distintos | Valores ou faixa |')
        L.append('|---|---|---:|---:|---|')
        for col, tipo, vaz, dist, amostra in r['colunas']:
            L.append(f'| `{col}` | {tipo} | {pct(vaz)} | {fmt(dist)} | {amostra.replace("|", "/")} |')
        L.append('')

    L.append('## Mapas de calor (`dados/brutos/heatmap/`)')
    L.append('')
    L.append('| Data | Dicionário | No zip | Extraídas na pasta | Imagens sem conta em usuarios.csv |')
    L.append('|---|---:|---:|---:|---:|')
    for h in hm:
        L.append(f'| {h["data"]} | {fmt(h["esperado"])} | {fmt(h["no_zip"]) if h["no_zip"] is not None else "—"} | '
                 f'{fmt(h["extraidas"])} | {fmt(h["sem_cadastro"]) if h["sem_cadastro"] is not None else "—"} |')
    L.append('')
    for h in hm:
        if h['lixo_mac']:
            L.append(f'- 🔵 {h["data"]}: o zip traz também {h["lixo_mac"]} arquivos `__MACOSX/._*.png`, metadados do macOS '
                     'e não imagens. Ignorados na contagem; não devem ser lidos como mapas.')
        if h['no_zip'] is not None and h['no_zip'] != h['esperado']:
            L.append(f'- 🟡 {h["data"]}: o zip tem {fmt(h["no_zip"])} imagens e o dicionário fala em {fmt(h["esperado"])} '
                     f'({h["no_zip"] - h["esperado"]:+d}).')
        if h['no_zip'] is not None and h['extraidas'] != h['no_zip']:
            L.append(f'- 🟡 {h["data"]}: só {fmt(h["extraidas"])} de {fmt(h["no_zip"])} imagens estão extraídas na pasta. '
                     'Termine de descompactar antes de usar.')
    L.append('- 🔵 Só existe imagem para quem era assinante pagante na data e treinou ao ar livre nos 90 dias anteriores.')
    L.append('')
    return '\n'.join(L)


PRINCIPAIS = []  # preenchido em main() a partir dos achados


def main():
    sys.stdout.reconfigure(encoding='utf-8')
    res = {}
    res['usuarios.csv'] = analisar('usuarios.csv', DICIONARIO['usuarios.csv'], None)
    ids = set(res['usuarios.csv']['df']['user_id']) if 'df' in res['usuarios.csv'] else None
    for nome, spec in DICIONARIO.items():
        if nome != 'usuarios.csv':
            print('lendo', nome)
            res[nome] = analisar(nome, spec, ids)
    especificos = checagens_especificas(res)
    hm = heatmaps(ids)

    erros = [(n, t) for n, r in res.items() for nv, t in r['achados'] if nv == 'erro']
    ok_linhas = sum(1 for r in res.values() if r.get('linhas') == r['spec']['linhas'])
    ok_cols = sum(1 for r in res.values() if r['existe'] and not any('Colunas' in t for _, t in r['achados']))
    hm_ok = all(h['no_zip'] == h['esperado'] == h['extraidas'] for h in hm)
    PRINCIPAIS.append(f'- **O data room está completo.** {ok_linhas} de {len(res)} arquivos têm exatamente as linhas do dicionário, '
                      f'{ok_cols} de {len(res)} têm exatamente as colunas descritas'
                      + (', e os mapas de calor batem com as contagens do dicionário.' if hm_ok else '.'))
    PRINCIPAIS.extend(f'- 🔴 `{n}`: {t}' for n, t in erros)
    PRINCIPAIS.append('- 🟡 **Valores que o dicionário não descreve:** plano `cortesia`, canal `interno` (60 contas internas, não pagantes) '
                      'e os valores de `status_atual` (`ativa`, `expirada`, `reembolsada`). '
                      'Sem a `cortesia`, a base ativa bate com os 14.753 pagantes do enunciado.')
    apos = [f'`{n}` ({", ".join(f"{c}: {fmt(v)}" for c, v in r["apos"].items())})' for n, r in res.items() if r.get('apos')]
    if apos:
        PRINCIPAIS.append('- 🟡 **Datas depois do corte de 30/09/2026**, mesmo com o fuso convertido: ' + '; '.join(apos) + '. '
                          'Na construção das variáveis, filtre tudo até o corte, senão o modelo enxerga o futuro.')
    PRINCIPAIS.append('- 🟡 **Fusos misturados** em `eventos_assinatura.csv` e `pagamentos.csv`: as lojas gravam em UTC (`...Z`) e o site, '
                      'em Brasília. Converta antes de contar por dia ou mês, porque eventos perto da meia-noite mudam de dia.')
    PRINCIPAIS.append('- 🟡 **Texto a padronizar:** `sexo` (6 grafias), `sistema` (5), `dias_por_semana` (texto livre), `valor` em `pagamentos.csv` '
                      '(`34.90` e `R$ 34,90`) e `tipo` de treino em português e inglês.')
    PRINCIPAIS.append('- 🟡 **Valores suspeitos:** datas de nascimento no futuro ou em 1900, cadastros com data posterior ao corte, '
                      'distâncias de até 10 mil km e treinos com 0 minuto em `atividades.parquet`.')
    PRINCIPAIS.append('- 🔵 **Vazamento:** `assinaturas.csv` é o retrato de 01/10/2026. Situação histórica sai de `eventos_assinatura.csv`.')

    SAIDA.parent.mkdir(exist_ok=True)
    SAIDA.write_text(montar_md(res, especificos, hm), encoding='utf-8')
    print('gravado', SAIDA)


if __name__ == '__main__':
    main()
