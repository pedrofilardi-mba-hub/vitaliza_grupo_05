# Registro de decisões: Vitaliza, grupo 05

Cada decisão que muda um número, um método ou o escopo entra aqui, da mais antiga para a mais recente. Uma decisão revista não é apagada: ela ganha o status "substituída por D-XXX".

Modelo geral:

```
## D-XXX: título curto
- Data: AAAA-MM-DD · Responsável: nome · Status: proposta | aceita | substituída por D-YYY
- Contexto: o que motivou a decisão
- Decisão: o que foi decidido
- Alternativas consideradas: e por que foram descartadas
- Impacto: o que muda (arquivos, números, objetivos do case afetados)
```

Decisões de qualidade de dados ("limpar é decidir": corrigir, remover ou marcar) usam o modelo da skill `qualidade-dados`. Ele acrescenta a dimensão, o problema (Q-ID do relatório em `saidas/qualidade/`) e o **efeito na contagem**:

```
## D-XXX: <arquivo> · título curto do problema
- Data: AAAA-MM-DD · Responsável: nome · Status: aceita
- Dimensão: completude | validade | consistência | unicidade | temporalidade · Problema: Q-<arq>-NN (saidas/qualidade/<arquivo>.md)
- Contexto: o problema em uma frase, com n e %
- Decisão: corrigir | remover | marcar: como, exatamente
- Motivo: por que esta opção
- Alternativas consideradas: as outras opções e por que não
- Efeito na contagem: linhas antes → depois; valores alterados; colunas novas
- Impacto: objetivos do case ou arquivos afetados
```

---

## D-001: Dados brutos fora do repositório
- Data: 2026-10-22 · Responsável: grupo · Status: aceita
- Contexto: o data room tem cerca de 200 MB, com dois zips de heatmaps e dados pessoais (e-mail, data de nascimento).
- Decisão: `dados/brutos/` entra no `.gitignore`. Cada integrante copia os arquivos do data room para essa pasta, e eles não são alterados.
- Alternativas consideradas: versionar os dados com Git LFS. Foi descartado pelo tamanho e por causa dos dados pessoais.
- Impacto: todo arquivo de `dados/processados/` precisa poder ser recriado a partir de um script em `src/`.

## D-002: Data de corte e horizonte de previsão
- Data: 2026-10-22 · Responsável: grupo · Status: aceita
- Contexto: o enunciado fixa o corte da base em 30/09/2026 e pede a probabilidade de saída nos 60 dias seguintes.
- Decisão: corte em 30/09/2026 e alvo de churn na janela de 01/10 a 29/11/2026. Nenhuma variável usa dado posterior ao corte.
- Alternativas consideradas: nenhuma, porque é premissa do case.
- Impacto: os objetivos 4 a 7. A validação do modelo usa separação no tempo.

## D-003: onboarding.csv · objetivo vazio ou disfarçado
- Data: 2026-10-29 · Responsável: Pedro Filardi · Status: aceita
- Dimensão: completude · Problema: Q-onb-01 (saidas/qualidade/onboarding.md)
- Contexto: `objetivo_texto` tem 19.235 vazios reais (30,1%). São 5.467 nulos e 13.768 respostas que não dizem nada (`nada`, `x`, `.`, `asdf`, `kkkk`, `nao sei`, `ok`, `-`, `sla`, emoji).
- Decisão: corrigir e marcar. Na cópia processada, os disfarçados viram vazio, pela regra `vazio_disfarcado` de `src/qualidade.py`, e é criada a coluna `objetivo_informado` (sim/não). Os brutos não mudam.
- Motivo: a extração com IA (objetivo 5) deve ler só textos com conteúdo, e a marcação preserva o fato de não ter respondido.
- Alternativas consideradas: só marcar (a IA leria `asdf` como objetivo); remover as contas (−30,1% da base, perdendo as outras respostas válidas).
- Efeito na contagem: 63.929 contas → 63.929; `objetivo_texto` preenchido de 58.462 para 44.694 (13.768 valores viram vazio); 1 coluna nova.
- Impacto: objetivo 3 (segmentos pela necessidade) e objetivo 5 (extração com IA e custo por assinante).

## D-004: onboarding.csv · como_conheceu fora da base processada
- Data: 2026-10-29 · Responsável: Pedro Filardi · Status: aceita
- Dimensão: consistência · Problema: Q-onb-02 (saidas/qualidade/onboarding.md)
- Contexto: cada resposta de `como_conheceu` corresponde 100% a um único `usuarios.canal_aquisicao`. Além disso, tem 25,2% de vazio real e 2.397 linhas com grafia variante.
- Decisão: remover a coluna da cópia processada. O canal de aquisição vem de `usuarios.canal_aquisicao`. Os brutos não mudam.
- Motivo: a informação é redundante, e a fonte alternativa está completa e limpa.
- Alternativas consideradas: corrigir e manter (duplicaria uma coluna existente); marcar os vazios (manteria a redundância).
- Efeito na contagem: 63.929 contas → 63.929; 1 coluna a menos.
- Impacto: as variáveis de aquisição dos objetivos 2, 3 e 4 usam só `canal_aquisicao`.

## D-005: onboarding.csv · nivel e dias_por_semana vazios
- Data: 2026-10-29 · Responsável: Pedro Filardi · Status: aceita
- Dimensão: completude · Problema: Q-onb-03 (saidas/qualidade/onboarding.md)
- Contexto: `nivel` tem 4.513 vazios (7,1%) e `dias_por_semana`, 6.368 (10,0%), em 10.408 contas. Os vazios são independentes entre si e não se ligam a assinar nem a sair.
- Decisão: marcar. Na cópia processada, `nivel` ganha a categoria `nao_informado`; `dias_por_semana` fica vazio e é criada a coluna `dias_informado`. Se um modelo exigir número, a mediana entra só na modelagem, junto com a marcação. Os brutos não mudam.
- Motivo: não inventar dado e não perder 16% das contas.
- Alternativas consideradas: imputar a moda e a mediana (10.881 valores inventados); remover as contas (de 63.929 para 53.521, −16,3%).
- Efeito na contagem: 63.929 contas → 63.929; 4.513 valores de `nivel` viram `nao_informado`; 1 coluna nova.
- Impacto: objetivos 3 e 4.

## D-006: onboarding.csv · dias_por_semana como número
- Data: 2026-10-29 · Responsável: Pedro Filardi · Status: aceita
- Dimensão: consistência · validade · Problema: Q-onb-04 (saidas/qualidade/onboarding.md)
- Contexto: `dias_por_semana` aparece em 4 formas: `3` (33.527), `3 vezes` (11.563), `3x` (11.554) e `todos` (917).
- Decisão: corrigir. Na cópia processada, o número é extraído e `todos` vira 7; a coluna passa a inteiro, de 1 a 7. Os brutos não mudam.
- Motivo: o valor certo é recuperável sem ambiguidade. "Todos" foi lido como todos os dias da semana.
- Alternativas consideradas: `todos` como vazio (perderia 917 respostas válidas); remover as linhas fora do padrão (−37,6%).
- Efeito na contagem: 63.929 contas → 63.929; 24.034 valores convertidos (23.117 com texto e 917 `todos`); 6.368 continuam vazios (D-005).
- Impacto: objetivos 3 e 4 (intenção de frequência declarada na entrada).

## D-007: onboarding.csv · objetivo normalizado para contagem
- Data: 2026-10-29 · Responsável: Pedro Filardi · Status: aceita
- Dimensão: consistência · Problema: Q-onb-05 (saidas/qualidade/onboarding.md)
- Contexto: 17.179 textos distintos de `objetivo_texto` viram 12.257 depois de normalizar; 9.884 linhas (15,5%) diferem da grafia mais comum só por acento, emoji ou espaço trocado.
- Decisão: marcar. Na cópia processada é criada a coluna `objetivo_norm` (minúsculas, sem acento, sem emoji, sem espaços e pontuação), só para contar e agrupar. A extração com IA usa o texto original. Os brutos não mudam.
- Motivo: agrupar sem perder o texto original, que a IA interpreta bem.
- Alternativas consideradas: sobrescrever pela grafia mais comum (perde o original e os emoji).
- Efeito na contagem: 63.929 contas → 63.929; 1 coluna nova; nenhum texto alterado.
- Impacto: objetivo 3 (contagem de necessidades) e objetivo 5.

## D-008: onboarding.csv · contas sem onboarding
- Data: 2026-10-29 · Responsável: Pedro Filardi · Status: aceita
- Dimensão: completude · Problema: Q-onb-06 (saidas/qualidade/onboarding.md)
- Contexto: 1.019 das 64.948 contas de `usuarios.csv` (1,6%) não têm linha no onboarding. Delas, 60 são `interno`, 41 têm cadastro em 2027, e só 5,9% assinaram (contra 50,3% na base).
- Decisão: marcar. Ao juntar o onboarding com outras tabelas, é criada a coluna `tem_onboarding`. As contas internas e as de 2027 ficam para a avaliação de `usuarios.csv`.
- Motivo: é um grupo diferente da base, e tirá-lo enviesaria a taxa de conversão.
- Alternativas consideradas: remover das análises (−1,6% das contas, com viés).
- Efeito na contagem: 64.948 contas → 64.948 nas tabelas integradas; 1 coluna nova.
- Impacto: integração das tabelas pelo `user_id` (objetivo 1) e análises de conversão.
