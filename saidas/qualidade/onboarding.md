# Qualidade: `onboarding.csv`

Uma linha por conta (questionário de entrada) · 63.929 linhas · 7 colunas · avaliado em 29/10/2026 com a skill `qualidade-dados` · medidas em [onboarding_evidencias.md](onboarding_evidencias.md)

## Resumo

O arquivo é utilizável e estruturalmente limpo:
- uma linha por conta, sem duplicatas;
- todas as datas válidas, no período e no mesmo dia do cadastro da conta.

Os problemas estão no conteúdo. O vazio real de `objetivo_texto` é **30,1%**, e não os 8,6% que o arquivo mostra à primeira vista: 21,5% são respostas como `nada`, `x`, `.`, `asdf` ou emoji. `dias_por_semana` está escrito de 4 jeitos. `como_conheceu` repete o `canal_aquisicao` de `usuarios.csv`.

Nenhum problema pede remover linhas. As decisões são sobre **como representar o vazio** e **o que padronizar**, e nenhuma muda a contagem de contas.

**Situação em 29/10/2026:** os 6 problemas foram decididos (D-003 a D-008 no `DECISOES.md`), todos para aplicar numa cópia em `dados/processados/`. Os brutos não mudam. A limpeza ainda não foi feita.

## Problemas para decidir

| ID | Dimensão | Coluna | O que está errado | Por que importa para o case |
|---|---|---|---|---|
| Q-onb-01 | Completude | `objetivo_texto` | 19.235 vazios reais (30,1%): 5.467 nulos e 13.768 disfarçados | É a única fonte de **necessidade** (lente "por que contratou", Aula 3) e entra na extração com IA (objetivo 5). Tratar `asdf` como resposta gasta tokens e cria categorias falsas |
| Q-onb-02 | Completude · Consistência | `como_conheceu` | 16.101 vazios reais (25,2%); cada resposta corresponde a um único `canal_aquisicao` | É redundante: a mesma informação já existe completa e limpa em `usuarios.canal_aquisicao` |
| Q-onb-03 | Completude | `nivel`, `dias_por_semana` | `nivel` 7,1% e `dias_por_semana` 10,0% vazios (10.408 contas com pelo menos um); o dicionário não diz que são opcionais | Podem entrar no modelo de churn e na segmentação, e o tratamento do vazio muda as médias |
| Q-onb-04 | Consistência · Validade | `dias_por_semana` | 4 formas: `3` (33.527), `3 vezes` (11.563), `3x` (11.554), `todos` (917, sem número) | Sem padronizar, a coluna não vira número e não dá para calcular nada |
| Q-onb-05 | Consistência | `objetivo_texto` | 17.179 textos distintos viram 12.257 depois de normalizar; 9.884 linhas (15,5%) diferem da grafia mais comum só por acento, emoji ou espaço trocado | Contagens por texto ficam fragmentadas (`baixar o colesterol` aparece em 136 grafias) |
| Q-onb-06 | Completude (cobertura) | arquivo inteiro | 1.019 contas de `usuarios.csv` (1,6%) não têm onboarding; 60 são `interno`, 41 têm cadastro em 2027 | Ao juntar com outras tabelas, essas contas ficam sem as variáveis de entrada, e são um grupo diferente: só 5,9% assinaram, contra 50,3% na base |

### Q-onb-01 · Objetivo vazio ou disfarçado

- **Evidência:**
  - 5.467 nulos (8,6%), o número da aula.
  - Mais 13.768 respostas que não dizem nada: `nada` (1.426), `😂` (1.413), `.` (1.398), `x` (1.397), `sla` (1.396), `kkkk` (1.365), `asdf` (1.365), `nao sei` (1.361), `ok` (1.325), `-` (1.322).
  - O vazio é estável de 2020 a 2026 (28,9% a 30,4%).
  - O vazio não está ligado a assinar nem a sair: 50,8% dos que deixaram vazio assinaram, contra 51,0% dos que responderam; entre os assinantes, 54,5% saíram, contra 54,8%.
- **Opções:**
  - **Corrigir:** transformar os 13.768 disfarçados em vazio. Efeito: `objetivo_texto` preenchido cai de 58.462 para 44.694; 0 linhas removidas.
  - **Remover:** tirar as contas sem objetivo. Efeito: de 63.929 para 44.694 contas (−30,1%). Joga fora contas com as outras respostas válidas.
  - **Marcar:** criar `objetivo_informado` (sim/não) e manter o texto original. Efeito: 0 linhas removidas; 1 coluna nova.
- **Recomendação:** **corrigir e marcar**. Os disfarçados viram vazio e a coluna `objetivo_informado` registra quem respondeu. Assim a extração com IA só lê os 44.694 textos com conteúdo, e o fato de não responder continua disponível para testar depois.
- **Status:** decidido (D-003, 29/10/2026, Pedro Filardi)

### Q-onb-02 · `como_conheceu` repete o canal de aquisição

- **Evidência:**
  - Cruzando as 14 respostas mais comuns com `usuarios.canal_aquisicao`, cada uma cai 100% num só canal. Exemplos: `vi um reels` → influenciador; `convênio da empresa` → parceria_corporativa; `um amigo me mandou o link` → indicacao.
  - `canal_aquisicao` está 100% preenchido.
  - `como_conheceu` tem 25,2% de vazio real e 2.397 linhas com grafia variante (`já conhecia` e `ja conhecia`).
- **Opções:**
  - **Corrigir:** padronizar as grafias e mapear para os canais. Efeito: 0 linhas; reproduz uma coluna que já existe.
  - **Remover (a coluna):** não usar `como_conheceu` como variável e usar `usuarios.canal_aquisicao`. Efeito: 0 linhas removidas; 1 coluna a menos na base processada.
  - **Marcar:** manter a coluna e marcar os vazios. Efeito: 0 linhas; mantém a redundância.
- **Recomendação:** **remover a coluna da base processada**. O canal fica com `canal_aquisicao`, que é completo e limpo. O texto original continua em `dados/brutos/`, se um dia for preciso.
- **Status:** decidido (D-004, 29/10/2026, Pedro Filardi)

### Q-onb-03 · `nivel` e `dias_por_semana` vazios

- **Evidência:**
  - `nivel` tem 4.513 vazios (7,1%) e `dias_por_semana`, 6.368 (10,0%). São 10.408 contas com pelo menos um dos dois, e 473 com os dois.
  - Os vazios dos quatro campos de texto são independentes entre si (correlação de cerca de 0).
  - Não estão ligados a assinar nem a sair: diferenças menores que 1 ponto percentual.
  - As taxas são estáveis entre os anos.
- **Opções:**
  - **Corrigir (imputar):** usar a moda em `nivel` (intermediario) e a mediana em `dias_por_semana` (3). Efeito: 0 linhas; 10.881 valores inventados. Infla a moda e esconde que a pessoa não respondeu.
  - **Remover:** tirar as contas com algum vazio. Efeito: de 63.929 para 53.521 contas (−16,3%).
  - **Marcar:** `nivel` ganha a categoria `nao_informado`; `dias_por_semana` fica vazio, com a coluna `dias_informado`. Efeito: 0 linhas; 1 categoria e 1 coluna novas.
- **Recomendação:** **marcar**. Os vazios parecem aleatórios, então remover não enviesa, mas perde 16% das contas sem necessidade. Imputar inventa dado. Se um modelo exigir número, a mediana entra só na hora de modelar, com a marcação junto.
- **Status:** decidido (D-005, 29/10/2026, Pedro Filardi)

### Q-onb-04 · `dias_por_semana` em 4 formatos

- **Evidência:**
  - Só número: 33.527.
  - `N vezes`: 11.563.
  - `Nx`: 11.554.
  - `todos`: 917. Destes, 350 são intermediários, 259 iniciantes, 246 avançados e 62 sem nível.
  - Nenhum número fora de 1 a 7.
- **Opções:**
  - **Corrigir:** extrair o número, `todos` vira 7 e a coluna passa a inteiro. Efeito: 24.034 valores reescritos (23.117 com texto e 917 `todos`); 0 linhas removidas.
  - **Remover:** tirar as linhas que não são só número. Efeito: de 63.929 para 39.895 (−37,6%).
  - **Marcar:** manter o texto e marcar o formato. Efeito: 0 linhas; a coluna continua inutilizável como número.
- **Recomendação:** **corrigir**. O valor certo é recuperável sem ambiguidade. O único ponto de julgamento é `todos` = 7, e vale registrar isso na decisão.
- **Status:** decidido (D-006, 29/10/2026, Pedro Filardi)

### Q-onb-05 · Mesmo objetivo em várias grafias

- **Evidência:**
  - 9.884 linhas (15,5%) usam uma grafia diferente da mais comum: emoji no fim, acento faltando ou espaço trocado.
  - Exemplos: `cuidar da saúde, tô sedentário há anos` (872) e `cuidar da saúde, tô sedentario ha anos` (170); `baixar o colesterol` (1.050) em 136 grafias.
- **Opções:**
  - **Corrigir no lugar:** sobrescrever o texto pela grafia mais comum. Efeito: 9.884 valores alterados. Perde o texto original, inclusive emoji que pode carregar tom.
  - **Remover:** não se aplica, porque o conteúdo é válido.
  - **Marcar:** criar `objetivo_norm` (minúsculas, sem acento, sem emoji, espaços corrigidos) ao lado do original. Efeito: 0 linhas; 1 coluna nova.
- **Recomendação:** **marcar**. Criar `objetivo_norm` só para contar e agrupar, e mandar o texto original para a extração com IA, que lida bem com erro de digitação. Mapear 12 mil textos à mão não compensa.
- **Status:** decidido (D-007, 29/10/2026, Pedro Filardi)

### Q-onb-06 · Contas sem onboarding

- **Evidência:**
  - Das 64.948 contas de `usuarios.csv`, 1.019 não têm linha aqui. Delas:
    - 60 são `interno`;
    - 41 têm cadastro em 2027, um problema de `usuarios.csv` já apontado no inventário;
    - 802 são de 2025 e 2026.
  - Só 5,9% delas assinaram, contra 50,3% na base.
- **Opções:**
  - **Corrigir:** não há como recuperar respostas que não existem.
  - **Remover:** tirar essas contas da análise. Efeito: −1.019 contas (−1,6%). Elas são um grupo diferente, e tirá-las enviesa a taxa de conversão.
  - **Marcar:** criar `tem_onboarding` ao juntar com outras tabelas. Efeito: 0 linhas.
- **Recomendação:** **marcar**. As contas `interno` e as com cadastro em 2027 serão tratadas na avaliação de `usuarios.csv`, sem decidir aqui.
- **Status:** decidido (D-008, 29/10/2026, Pedro Filardi)

## Já decidido

- **D-002 (data de corte):** todas as datas de `respondido_em` estão até 30/09/2026. Nenhuma linha é afetada.

## O que não é problema

- **Unicidade:** 0 linhas repetidas, 0 `onboarding_id` repetidos, 0 contas com duas respostas.
- **Datas:** 100% no formato `AAAA-MM-DD`, de 01/09/2020 (lançamento) a 30/09/2026. Todas no mesmo dia do cadastro da conta. Para o problema do início (*cold start*, Aula 3), isso é bom: a informação existe desde o primeiro dia.
- **`nivel`:** só 3 valores, todos coerentes. Os avançados declaram mais dias de treino: mediana de 4, contra 3 nos outros níveis.
- **Temporalidade:** vazios e formatos estáveis de 2020 a 2026. Não houve mudança na forma de registrar.

## Números conferidos à mão

Contei os três com pandas, separadamente do script `src/qualidade.py`:
1. **Nulos de `objetivo_texto`:** 5.467. Bate com o número da aula, slide 31.
2. **Vazios disfarçados de `objetivo_texto`:** 13.768. A soma das 10 respostas mais comuns (1.426 + 1.413 + 1.398 + 1.397 + 1.396 + 1.365 + 1.365 + 1.361 + 1.325 + 1.322) dá exatamente 13.768.
3. **`dias_por_semana` = `todos`:** 917. Bate com a contagem direta de valores.
