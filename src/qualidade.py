"""Evidências de qualidade de um arquivo do data room nas cinco dimensões (Wang; Strong, 1996).

Completude, validade, consistência, unicidade e temporalidade. O script só mede e
descreve: não corrige nada e não altera dados/brutos/. As decisões de tratamento são
tomadas pelo grupo e registradas no DECISOES.md (skill qualidade-dados).

Uso, da raiz do projeto:

    .venv\\Scripts\\python.exe src\\qualidade.py onboarding.csv

Grava saidas/qualidade/<arquivo>_evidencias.md.
"""
import re
import sys
import unicodedata
from datetime import datetime
from pathlib import Path

import pandas as pd

sys.path.insert(0, str(Path(__file__).resolve().parent))
from inventario import BRUTOS, CORTE, DICIONARIO, fmt, ler, padrao, para_data, pct  # noqa: E402

RAIZ = Path(__file__).resolve().parents[1]
SAIDA = RAIZ / 'saidas' / 'qualidade'
LANCAMENTO = pd.Timestamp('2020-09-01')

# O que o dicionário diz além do que o inventário já usa.
EXTRAS = {
    'onboarding.csv': dict(
        uma_por_conta=True,
        opcionais=['objetivo_texto', 'como_conheceu'],
        numero_em_texto={'dias_por_semana': (1, 7)},
        data_da_conta='respondido_em',
    ),
    'usuarios.csv': dict(uma_por_conta=True),
    'campanha_ago26.csv': dict(uma_por_conta=True),
    'pesquisa_saida.csv': dict(opcionais=['comentario']),
    'tickets_suporte.csv': dict(opcionais=['resolvido_em']),
    'assinaturas.csv': dict(opcionais=['data_fim', 'motivo_fim']),
    'atividades.parquet': dict(opcionais=['distancia_km', 'ritmo_min_km', 'fc_media', 'treino_com']),
    'eventos_assinatura.csv': dict(opcionais=['detalhe']),
}

# Colunas pessoais: só números agregados, nunca valores (o repositório é público).
PESSOAIS = {'email', 'data_nascimento', 'cidade', 'cep_prefixo'}

# Respostas que ocupam o campo sem dizer nada.
TOKENS_VAZIOS = {'nada', 'nao sei', 'não sei', 'sei la', 'sei lá', 'sla', 'ok', 'x', 'xx', 'xxx', 'asdf', 'teste',
                 'n/a', 'na', 'null', 'none', 'nenhum', '-', '--', '.', '..', '...', '?', '0'}
MIN_REPETICAO = 5  # só mostra valores que aparecem pelo menos 5 vezes (não identificam ninguém)


def sem_acento(s):
    return ''.join(c for c in unicodedata.normalize('NFKD', s) if not unicodedata.combining(c))


def normalizar(v):
    """Forma canônica para achar grafias da mesma coisa: minúsculas, sem acento, sem espaço nem pontuação."""
    return re.sub(r'[\W_]+', '', sem_acento(str(v).strip().lower()))


def vazio_disfarcado(v):
    """Valor preenchido que não informa nada: token conhecido, risada, ou só símbolos/emoji."""
    t = sem_acento(str(v).strip().lower())
    if t in TOKENS_VAZIOS or re.fullmatch(r'(k|ha|rs)+', t):
        return True
    return not re.search(r'[a-z0-9]', t)


def amostra(contagem, n=8):
    linhas = [(v, c) for v, c in contagem.items() if c >= MIN_REPETICAO][:n]
    return ', '.join(f'`{str(v)[:40]}` ({fmt(int(c))})' for v, c in linhas) or '—'


def completude(df, spec, extra, ids_conta):
    linhas = []
    opc = set(extra.get('opcionais', []))
    for col in df.columns:
        s = df[col]
        nulos = int(s.isna().sum())
        texto = s.dropna().astype(str) if s.dtype == object or str(s.dtype).startswith('str') else pd.Series(dtype=str)
        brancos = int((texto.str.strip() == '').sum())
        # só em texto livre: em categorias, 'nenhum' ou 'RS' são valores legítimos
        livre = col in spec.get('texto_livre', []) and col not in PESSOAIS
        disf = texto[texto.str.strip() != ''].map(vazio_disfarcado) if livre and len(texto) else pd.Series(dtype=bool)
        n_disf = int(disf.sum())
        exemplos = amostra(texto[disf].str.strip().value_counts()) if n_disf else '—'
        total = nulos + brancos + n_disf
        linhas.append(dict(col=col, nulos=nulos, brancos=brancos, disf=n_disf, total=total, pct=total / len(df),
                           opcional='sim' if col in opc else 'não', exemplos=exemplos))
    linhas.sort(key=lambda x: -x['pct'])
    cobertura = None
    if extra.get('uma_por_conta') and ids_conta is not None and 'user_id' in df.columns:
        faltam = len(ids_conta - set(df['user_id']))
        cobertura = (faltam, len(ids_conta))
    return linhas, cobertura


def validade(df, spec, extra):
    achados = []
    for col, dominio in spec.get('categorias', {}).items():
        if col in df.columns:
            vc = df[col].dropna().astype(str).value_counts()
            fora = vc[~vc.index.isin(dominio)]
            achados.append((col, 'domínio do dicionário', f'{fmt(int(fora.sum()))} fora de {{{", ".join(dominio)}}}',
                            amostra(fora) if len(fora) else '—'))
    for col, (lo, hi) in extra.get('numero_em_texto', {}).items():
        s = df[col].dropna().astype(str).str.strip()
        num = pd.to_numeric(s.str.extract(r'^(\d+)')[0], errors='coerce')
        sem_num = s[num.isna()]
        fora = num[(num < lo) | (num > hi)]
        achados.append((col, f'número inteiro entre {lo} e {hi}',
                        f'{fmt(len(sem_num))} sem número; {fmt(len(fora))} fora da faixa',
                        amostra(sem_num.value_counts()) if len(sem_num) else '—'))
    for col in df.columns:
        if col in PESSOAIS or col in spec.get('datas', []):
            continue
        num = pd.to_numeric(df[col], errors='coerce') if not pd.api.types.is_numeric_dtype(df[col]) else df[col]
        if pd.api.types.is_bool_dtype(df[col]) or num.notna().sum() < 0.95 * df[col].notna().sum() or num.notna().sum() == 0:
            continue
        q1, q3 = num.quantile([.25, .75])
        lim = q3 + 3 * (q3 - q1)
        achados.append((col, 'faixa numérica',
                        f'mín {num.min():g} · p1 {num.quantile(.01):g} · mediana {num.median():g} · p99 {num.quantile(.99):g} · máx {num.max():g}; '
                        f'{fmt(int((num < 0).sum()))} negativos, {fmt(int((num == 0).sum()))} zeros, '
                        f'{fmt(int((num > lim).sum()))} acima de Q3 + 3·IQR ({lim:g})', '—'))
    for col in spec.get('datas', []):
        if col not in df.columns:
            continue
        d = para_data(df[col].dropna())
        if col == 'data_nascimento':
            idade = (CORTE - d).dt.days / 365.25
            regra = (f'{fmt(int(d.isna().sum()))} não viram data; {fmt(int((idade < 0).sum()))} no futuro; '
                     f'{fmt(int(((idade >= 0) & (idade < 13)).sum()))} com menos de 13 anos; {fmt(int((idade > 100).sum()))} com mais de 100 anos')
        else:
            regra = (f'{fmt(int(d.isna().sum()))} não viram data; {fmt(int((d < LANCAMENTO).sum()))} antes do lançamento (01/09/2020); '
                     f'{fmt(int((d > CORTE).sum()))} depois do corte (30/09/2026)')
        achados.append((col, 'data válida e plausível', regra,
                        f'de {d.min():%d/%m/%Y} a {d.max():%d/%m/%Y}' if d.notna().any() else '—'))
    return achados


def consistencia(df, spec, extra, nome):
    grupos = []
    livres = set(spec.get('texto_livre', []))
    for col in df.columns:
        if col in PESSOAIS or col in spec.get('datas', []) or col.endswith('_id') or col in ('seguidor_id', 'seguido_id', 'treino_com'):
            continue
        s = df[col].dropna().astype(str)
        if s.nunique() > 200 and col not in livres:
            continue
        s = s[~s.map(vazio_disfarcado)]  # vazios disfarçados já entram na completude
        vc = s.value_counts()
        por_chave = pd.Series(vc.values, index=vc.index).groupby(vc.index.map(normalizar))
        variantes = sorted([g.sort_values(ascending=False) for _, g in por_chave if len(g) > 1], key=lambda g: -g.sum())
        if variantes:
            afetadas = sum(int(g.iloc[1:].sum()) for g in variantes)
            ex = []
            for g in variantes[:3]:
                freq = [(v, c) for v, c in g.items() if c >= MIN_REPETICAO]
                txt = ' = '.join(f'`{v}` ({fmt(int(c))})' for v, c in freq[:3])
                resto = len(g) - min(len(freq), 3)
                ex.append(txt + (f' e mais {resto} grafias' if resto else ''))
            grupos.append((col, 'mesma coisa escrita de jeitos diferentes (ignorando maiúsculas, acentos, espaços, pontuação e emoji)',
                           f'{fmt(vc.size)} valores distintos viram {fmt(por_chave.ngroups)} depois de normalizar; '
                           f'{fmt(afetadas)} linhas ({pct(afetadas / len(df))}) usam uma grafia diferente da mais comum',
                           '; '.join(ex)))
        if col in extra.get('numero_em_texto', {}):
            formas = s.str.strip().str.lower().map(lambda v: re.sub(r'\d+', '9', v)).value_counts()
            grupos.append((col, 'formas de escrever o número', f'{len(formas)} formas', amostra(formas)))
    for col in spec.get('datas', []):
        if col in df.columns:
            formas = df[col].dropna().astype(str).map(padrao).value_counts()
            if len(formas) > 1:
                grupos.append((col, 'formatos de data', f'{len(formas)} formatos', amostra(formas)))
    data_conta = extra.get('data_da_conta')
    if data_conta and 'user_id' in df.columns:
        u = ler('usuarios.csv')[['user_id', 'data_cadastro']]
        m = df[['user_id', data_conta]].merge(u, on='user_id', how='left')
        dif = (para_data(m[data_conta]).dt.normalize() - para_data(m['data_cadastro']).dt.normalize()).dt.days
        grupos.append((data_conta, 'coerência com usuarios.data_cadastro',
                       f'{fmt(int((dif < 0).sum()))} antes do cadastro; {fmt(int((dif == 0).sum()))} no mesmo dia; '
                       f'{fmt(int((dif > 0).sum()))} depois; {fmt(int(m["data_cadastro"].isna().sum()))} sem cadastro', '—'))
    return grupos


def unicidade(df, spec, extra):
    achados = [('linha inteira', f'{fmt(int(df.duplicated().sum()))} linhas repetidas')]
    chave = spec.get('chave')
    if chave:
        cols = list(chave) if isinstance(chave, tuple) else [chave]
        achados.append((f'chave `{"+".join(cols)}`', f'{fmt(int(df.duplicated(subset=cols).sum()))} repetições'))
    if extra.get('uma_por_conta') and 'user_id' in df.columns:
        achados.append(('uma linha por conta (`user_id`)', f'{fmt(int(df["user_id"].duplicated().sum()))} contas repetidas'))
    for col in spec.get('texto_livre', []):
        if col in df.columns and col not in PESSOAIS:
            s = df[col].dropna().astype(str).str.strip().str.lower()
            top = s.value_counts()
            achados.append((f'texto livre `{col}`',
                            f'{fmt(s.nunique())} textos distintos em {fmt(len(s))}; os 20 mais comuns cobrem {pct(top.head(20).sum() / max(len(s), 1))}'))
    return achados


def temporalidade(df, spec, extra):
    col = (spec.get('periodo') or [None])[0] or (spec.get('datas') or [None])[0]
    if not col or col not in df.columns:
        return None
    d = para_data(df[col])
    ano = d.dt.year
    vol = ano.value_counts().sort_index()
    vazio = df.drop(columns=[col]).apply(
        lambda s: s.isna() | s.astype(str).str.strip().eq('')
        | (s.astype(str).map(vazio_disfarcado) & s.notna() if s.name in spec.get('texto_livre', []) else False))
    faltas = vazio.groupby(ano).mean()
    faltas = faltas.loc[:, faltas.max() > 0]
    formatos = df[col].astype(str).map(padrao).groupby(ano).agg(lambda s: s.value_counts().index[0])
    ini, fim = (pd.Timestamp(spec['periodo'][1]), pd.Timestamp(spec['periodo'][2])) if spec.get('periodo') else (None, None)
    return dict(col=col, vol=vol, faltas=faltas, formatos=formatos, ini=ini, fim=fim, min=d.min(), max=d.max(),
                apos=int((d > CORTE).sum()))


def tabela(cab, linhas):
    out = ['| ' + ' | '.join(cab) + ' |', '|' + '|'.join('---' for _ in cab) + '|']
    out += ['| ' + ' | '.join(str(c).replace('|', '/') for c in l) + ' |' for l in linhas]
    return out


def main():
    sys.stdout.reconfigure(encoding='utf-8')
    if len(sys.argv) != 2 or sys.argv[1] not in DICIONARIO:
        print('Uso: python src/qualidade.py <arquivo>. Arquivos:', ', '.join(DICIONARIO))
        sys.exit(1)
    nome = sys.argv[1]
    spec, extra = DICIONARIO[nome], EXTRAS.get(nome, {})
    df = ler(nome)
    ids = set(ler('usuarios.csv')['user_id']) if nome != 'usuarios.csv' else set(df['user_id'])

    comp, cob = completude(df, spec, extra, ids)
    val = validade(df, spec, extra)
    cons = consistencia(df, spec, extra, nome)
    uni = unicidade(df, spec, extra)
    tmp = temporalidade(df, spec, extra)

    L = [f'# Evidências de qualidade: `{nome}`', '',
         f'Gerado por `src/qualidade.py` em {datetime.now():%d/%m/%Y %H:%M}. Só mede: nenhuma linha foi alterada. '
         f'{spec["forma"]} · uma linha por {spec["linha"]} · {fmt(len(df))} linhas · {len(df.columns)} colunas.', '',
         'Valores só aparecem quando se repetem pelo menos 5 vezes; colunas pessoais aparecem só em números.', '']

    L += ['## 1. Completude', '', 'Quanto falta em cada coluna. "Disfarçado" é campo preenchido que não diz nada '
          '(`nada`, `x`, `.`, emoji, `nao sei`).', '']
    L += tabela(['Coluna', 'Opcional no dicionário', 'Nulos', 'Só espaços', 'Disfarçados', 'Vazio real', '% vazio real', 'Disfarçados mais comuns'],
                [(f'`{c["col"]}`', c['opcional'], fmt(c['nulos']), fmt(c['brancos']), fmt(c['disf']), fmt(c['total']),
                  pct(c['pct']), c['exemplos']) for c in comp])
    if cob:
        L += ['', f'Cobertura: {fmt(cob[0])} das {fmt(cob[1])} contas de `usuarios.csv` não têm linha neste arquivo ({pct(cob[0] / cob[1])}).']
    L += ['', '## 2. Validade', '', 'Valores que não podem ser reais ou que estão fora do que o dicionário permite.', '']
    L += tabela(['Coluna', 'Regra', 'Resultado', 'Exemplos'], [(f'`{a}`', b, c, d) for a, b, c, d in val]) if val else ['Nenhuma regra aplicável.']
    L += ['', '## 3. Consistência', '', 'A mesma informação registrada de formas diferentes, dentro do arquivo ou entre arquivos.', '']
    L += tabela(['Coluna', 'Checagem', 'Resultado', 'Exemplos'], [(f'`{a}`', b, c, d) for a, b, c, d in cons]) if cons else ['Nenhuma variação encontrada.']
    L += ['', '## 4. Unicidade', '', 'Registros que aparecem mais de uma vez.', '']
    L += tabela(['Checagem', 'Resultado'], uni)
    L += ['', '## 5. Temporalidade', '']
    if tmp:
        L.append(f'Coluna de referência: `{tmp["col"]}`, de {tmp["min"]:%d/%m/%Y} a {tmp["max"]:%d/%m/%Y}'
                 + (f' (dicionário: {tmp["ini"]:%d/%m/%Y} a {tmp["fim"]:%d/%m/%Y})' if tmp['ini'] is not None else '')
                 + f'; {fmt(tmp["apos"])} registros depois do corte. Abaixo, o volume e a falta de cada coluna por ano: '
                 'uma mudança brusca de um ano para o outro indica que a forma de registrar mudou.')
        L.append('')
        cols = list(tmp['faltas'].columns)
        L += tabela(['Ano', 'Linhas', 'Formato de data'] + [f'vazio `{c}`' for c in cols],
                    [(int(a), fmt(int(tmp['vol'].get(a, 0))), f'`{tmp["formatos"].get(a, "")}`')
                     + tuple(pct(tmp['faltas'].loc[a, c]) for c in cols) for a in tmp['vol'].index])
    else:
        L.append('O arquivo não tem coluna de data.')
    L.append('')

    SAIDA.mkdir(parents=True, exist_ok=True)
    destino = SAIDA / f'{Path(nome).stem}_evidencias.md'
    destino.write_text('\n'.join(L), encoding='utf-8')
    print('gravado', destino)


if __name__ == '__main__':
    main()
