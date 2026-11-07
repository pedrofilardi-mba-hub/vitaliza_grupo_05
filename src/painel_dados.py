"""Calcula os números agregados do painel do projeto (docs/painel.html).

Lê a cópia limpa e os resultados das análises e grava saidas/painel_dados.json; em
seguida injeta esses dados no modelo docs/painel_modelo.html, gerando docs/painel.html.
Só números agregados: nenhum dado de pessoa entra no painel.

Uso, da raiz do projeto (depois de src/limpeza.py, src/dimensoes.py e src/motivos.py):

    .venv\\Scripts\\python.exe src\\painel_dados.py
"""
import json
import re
import sys
from datetime import datetime
from pathlib import Path

import pandas as pd

RAIZ = Path(__file__).resolve().parents[1]
PROC = RAIZ / 'dados' / 'processados'


def ler(n):
    return pd.read_parquet(PROC / f'{n}.parquet')


def churn_mensal(ev, ass):
    """Série do enunciado: perdas no mês / assinantes pagantes ativos no início do mês.

    Início = data da primeira cobrança em assinaturas.csv (os eventos só começam em 07/2024, e um anual
    mais antigo só aparece neles na renovação); fim = assinatura_expirada nos eventos (horário de Brasília)."""
    pag = ass[ass.pagante]
    cob = pd.Series(pd.to_datetime(pag.inicio).values, index=pag.user_id)
    fim = ev[ev.evento == 'assinatura_expirada'].groupby('user_id').data_hora.max()
    linhas = []
    for m in pd.period_range('2025-01', '2026-09', freq='M'):
        ini, fimm = m.start_time, m.end_time
        ativos = cob[cob < ini].index
        f = fim.reindex(ativos)
        ativos_ini = ativos[f.isna() | (f >= ini)]
        perdas = int(fim.reindex(ativos_ini).between(ini, fimm).sum())
        linhas.append({'mes': str(m), 'ativos_inicio': len(ativos_ini), 'perdas': perdas, 'churn': round(perdas / len(ativos_ini), 4)})
    return linhas


def main():
    sys.stdout.reconfigure(encoding='utf-8')
    ev = ler('eventos_assinatura')
    d = {'gerado_em': datetime.now().strftime('%d/%m/%Y %H:%M')}
    d['churn_mensal'] = churn_mensal(ev, ler('assinaturas'))

    b = ler('base_assinantes_corte')
    d['base'] = {'assinantes': len(b),
                 'plano': b.plano.value_counts(normalize=True).round(3).to_dict(),
                 'canal': b.canal_cobranca.value_counts(normalize=True).round(3).to_dict(),
                 'saida_anunciada': int(b.saida_anunciada.sum())}

    # gabarito histórico (31/05): churn por tempo de casa e por canal entre os mensais sem saída anunciada
    b5 = pd.read_parquet(PROC / 'base_corte_2026-05-31.parquet')
    m = b5[(b5.plano == 'mensal') & ~b5.saida_anunciada].copy()
    m['faixa'] = pd.cut(m.tempo_casa_meses, [-1, 1, 3, 6, 12, 1000], labels=['até 1 mês', '1–3 meses', '3–6 meses', '6–12 meses', '+12 meses'])
    d['mensal_tempo_casa'] = [{'faixa': str(k), 'n': int(len(g)), 'saida': round(g.saiu_60d.mean(), 3)} for k, g in m.groupby('faixa', observed=True)]
    d['mensal_canal'] = [{'canal': k, 'n': int(len(g)), 'saida': round(g.saiu_60d.mean(), 3)} for k, g in m.groupby('canal_cobranca')]
    an = b5[b5.saida_anunciada]
    d['anunciados'] = {'n': int(len(an)), 'mensal': round(an[an.plano == 'mensal'].saiu_60d.mean(), 3), 'anual': round(an[an.plano == 'anual'].saiu_60d.mean(), 3)}

    # dimensões (AUC)
    auc = pd.read_csv(RAIZ / 'saidas' / 'dimensoes_auc.csv')
    auc['melhor'] = auc[['auc_sem_anunciados_2026-05-31', 'auc_mensal_2026-05-31', 'auc_anual_renova_2026-07-31']].max(axis=1)
    top = auc.sort_values('melhor', ascending=False).head(14)
    d['dimensoes'] = [{'dimensao': r.dimensao, 'nova': bool(r.nova), 'familia': r.familia,
                       'todos': None if pd.isna(r['auc_sem_anunciados_2026-05-31']) else round(r['auc_sem_anunciados_2026-05-31'], 3),
                       'mensais': None if pd.isna(r['auc_mensal_2026-05-31']) else round(r['auc_mensal_2026-05-31'], 3),
                       'anuais_renovam': None if pd.isna(r['auc_anual_renova_2026-07-31']) else round(r['auc_anual_renova_2026-07-31'], 3)}
                      for _, r in top.iterrows()]

    # motivos: trajetória, sinais, perfis, objetivo
    t = ler('desligamentos_e_gemeos')
    dl, gm = t[t.grupo == 'desligou'], t[t.grupo == 'gemeo']
    mot = (RAIZ / 'saidas' / 'motivos_desligamento.md').read_text(encoding='utf-8')
    traj = re.findall(r'\| (\d)ª \| ([\d,]+) \| ([\d,]+) \|', mot)
    d['trajetoria'] = [{'semana': int(s), 'desligou': float(a.replace(',', '.')), 'gemeo': float(g.replace(',', '.'))} for s, a, g in traj]
    sinais = {'Treinos caíram pela metade': (lambda x: (x.treinos_sem_5a8 >= 4) & (x.treinos_sem_1a4 <= x.treinos_sem_5a8 / 2)),
              'Post de prova concluída (30 dias)': (lambda x: x.prova_concluida_30d),
              'Nenhum treino em 4 semanas': (lambda x: x.treinos_sem_1a4 == 0),
              'Chamado técnico (60 dias)': (lambda x: x.chamado_tecnico_60d),
              'Cartão recusado (60 dias)': (lambda x: x.recusa_60d),
              'Pagava o preço antigo (reajuste)': (lambda x: x.mensal_afetado_reajuste)}
    d['sinais'] = [{'sinal': k, 'desligou': round(f(dl).mean(), 3), 'gemeo': round(f(gm).mean(), 3)} for k, f in sinais.items()]
    d['perfis'] = [{'perfil': k, 'n': int(v)} for k, v in dl.perfil.value_counts().items()]
    d['objetivos'] = [{'objetivo': k, 'desligou': round((dl.objetivo_cat == k).mean(), 3), 'gemeo': round((gm.objetivo_cat == k).mean(), 3)}
                      for k in ['prova_com_prazo', 'desempenho', 'estetica', 'companhia', 'saude', 'bem_estar']]
    d['desligamentos'] = len(dl)

    # decisões: contagem por arquivo / tipo
    dec = (RAIZ / 'DECISOES.md').read_text(encoding='utf-8')
    tit = re.findall(r'^## (D-\d+): (.+)$', dec, flags=re.M)
    st = re.findall(r'^## (D-\d+).*?\n- Data: .*?Status: ([^\n]+)', dec, flags=re.M | re.S)
    d['decisoes'] = {'total': len(tit), 'substituidas': sum('substituída' in s for _, s in st)}
    acoes = re.findall(r'^- Decisão: (corrigir|remover|marcar|regra)', dec, flags=re.M | re.I)
    d['decisoes']['acoes'] = pd.Series([a.lower() for a in acoes]).value_counts().to_dict()
    dims = re.findall(r'^- Dimensão: ([^·\n]+)', dec, flags=re.M)
    cont = {}
    for s in dims:
        for k in ['completude', 'validade', 'consistência', 'unicidade', 'temporalidade']:
            if k in s:
                cont[k] = cont.get(k, 0) + 1
    d['decisoes']['dimensoes'] = cont

    # raio-x da base (EDA das Aulas 2 e 3)
    sys.path.insert(0, str(RAIZ / 'src'))
    import raio_x
    d['raiox'] = raio_x.montar()

    (RAIZ / 'saidas' / 'painel_dados.json').write_text(json.dumps(d, ensure_ascii=False, indent=1), encoding='utf-8')
    modelo = (RAIZ / 'docs' / 'painel_modelo.html')
    if modelo.exists():
        html = modelo.read_text(encoding='utf-8').replace('/*__DADOS__*/{}', json.dumps(d, ensure_ascii=False))
        (RAIZ / 'docs' / 'painel.html').write_text(html, encoding='utf-8')
        print('gravado docs/painel.html')
    print(json.dumps({k: d[k] for k in ['churn_mensal', 'base', 'anunciados', 'decisoes']}, ensure_ascii=False)[:3000])


if __name__ == '__main__':
    main()
