# Segmentação da base ativa (30/09/2026): cenários de K-means

> **Decisão (D-054, 07/11/2026):** o grupo escolheu o cenário C, que passa a se chamar **cenário escolhido**. Detalhe da segmentação escolhida: `saidas/clusters.md` (código `src/clusters.py`). Este arquivo guarda o processo de escolha.

Visão geral da base, **sem a ótica de churn**: nenhuma informação de saída entrou no cálculo nem na descrição dos grupos.
Código: `src/clusters_cenarios.py`. Métricas de todas as rodadas: `saidas/clusters_cenarios.csv`. Perfis: `saidas/clusters_perfis.json`.

## Como rodamos

- **Base:** os 14.753 assinantes ativos em 30/09/2026 (`base_assinantes_corte.parquet`), sem faltantes depois do tratamento.
- **Variáveis candidatas (6):** plano (mensal = 1), tempo de casa, treinos por semana (média de 3 meses), minutos por treino, % de treinos ao ar livre e seguidores.
- **Preparação:**
  - teto no percentil 99 para treinos por semana e minutos por treino;
  - teto de 6 para seguidores;
  - log no tempo de casa;
  - mediana nos faltantes.
- **Normalização:** `StandardScaler`, que deixa cada variável com média 0 e desvio 1. É refeita para cada combinação de variáveis.
- **Cenários:** todas as combinações de 3, 4, 5 e 6 variáveis (20 + 15 + 6 + 1 = 42), cada uma com 3 a 7 grupos. São **210 rodadas** de K-means (`n_init=10`, `random_state=0`).
- **Métricas de cada rodada:**
  - **silhueta:** quão separados estão os grupos, numa amostra fixa de 8.000;
  - **menor grupo:** percentual da base no menor grupo;
  - **estabilidade:** concordância (ARI) com outra semente e com um modelo treinado só em metade da base.
- **Regra para aceitar uma rodada:** menor grupo com pelo menos 5% da base e estabilidade de pelo menos 0,80.

## Três cuidados antes de comparar

1. **A silhueta cai naturalmente quando entram mais variáveis.** Com mais "direções", as pessoas ficam mais espalhadas. A melhor silhueta foi 0,67 com 3 variáveis, 0,44 com 4, 0,32 com 5 e 0,24 com 6. Por isso, compare a silhueta só entre cenários com o mesmo número de variáveis; entre tamanhos diferentes, valem a estabilidade e o sentido de negócio.
2. **O plano, por ser 0 ou 1, "manda" na separação.** Quando ele entra, quase todo grupo sai 100% mensal ou 100% anual, e a silhueta sobe. A mediana com plano é 0,43 contra 0,34 sem plano, com 3 variáveis. O algoritmo acaba "descobrindo" uma divisão que já conhecíamos.
3. **Idade, sexo e relógio não mudam entre os grupos em nenhum cenário.** É sempre ~46 anos, ~50% mulheres e ~38% com relógio. As personas não podem ser diferenciadas por perfil demográfico, só por comportamento, contrato e objetivo.

## A espinha dorsal que aparece em todos os cenários

Quatro "quadrantes" (plano × rua ou casa) mais um grupo pequeno de **longões** (~83 min por treino, ~6% da base) aparecem em quase todas as rodadas. São muito estáveis (ARI ≈ 1). Os cenários diferem no que acrescentam a essa espinha: frequência (intensos e pouco ativos), ciclo de vida (novatos) ou rede (veteranos enturmados).

Um achado que só a visão geral mostra: **mensais quase nunca passam 3 meses sem treinar (≤ 0,1%)**, enquanto **12% a 15% dos anuais de rua** não treinaram nenhuma vez em 3 meses. O anual pagou o ano e pode parar sem perceber o custo; o mensal que para, cancela.

## Os quatro cenários para discutir

| Cenário | Variáveis | Grupos | Silhueta | Menor grupo | Estabilidade |
|---|---|---|---|---|---|
| **A** · 3 variáveis | plano, minutos por treino, % ao ar livre | 5 | 0,665 | 5,8% | 1,00 |
| **B** · 4 variáveis | A + treinos por semana | 6 | 0,438 | 5,3% | 0,98 |
| **Cenário escolhido** (C) · 5 variáveis | tempo de casa, treinos por semana, minutos por treino, % ao ar livre, seguidores (**sem o plano**) | 5 | 0,241 | 5,7% | 0,95 |
| **D** · 6 variáveis | todas | 6 | 0,239 | 5,2% | 0,94 |

Para 5 variáveis levamos a versão **sem o plano**. As versões com plano repetem os grupos do cenário B (o plano domina). Sem ele, os grupos nascem só do comportamento, e o plano vira uma descrição. Em cada cenário, o número de grupos é o de melhor silhueta entre as rodadas aceitas, exceto em C. Ali, 5 e 6 grupos empatam (0,241 contra 0,243), e 5 é mais estável e mais fácil de explicar.

### Cenário A · 3 variáveis, 5 grupos

| Grupo | % base | Retrato |
|---|---|---|
| Anuais de rua | 32,5% | 80% ao ar livre, 1,4 treino por semana, 10,5 meses de casa; 12% sem treinar em 3 meses; 23% entraram por prova ou desempenho |
| Mensais de rua | 22,4% | 80% ao ar livre, 2 treinos por semana, 6 meses de casa; 23% vieram por influenciador |
| Anuais em casa | 20,9% | Só 15% ao ar livre; mais objetivo de bem-estar (13%) |
| Mensais em casa | 18,4% | Só 15% ao ar livre; bem-estar é o objetivo nº 1 (26% de quem informou) |
| Longões | 5,8% | 83 minutos por treino; 29% avançados; 28% entraram por prova ou desempenho |

- ✔ **Prós:** o mais simples de explicar e o mais estável (estabilidade 1,00, maior silhueta).
- ✖ **Contras:**
  - quatro dos cinco grupos são só "plano × lugar", o que já sabíamos sem K-means;
  - não enxerga quanto a pessoa treina nem há quanto tempo ela está na casa;
  - o maior grupo (32%) esconde os anuais que pararam.
- **Personas que se formam:** "o mensal que treina em casa por bem-estar"; "os longões".
- **Considerar ou descartar:** **descartar** como segmentação principal: é simples demais para virar 3 a 4 personas diferentes. Serve como slide de abertura ("rua × casa" é o primeiro corte da base).

### Cenário B · 4 variáveis, 6 grupos

| Grupo | % base | Retrato |
|---|---|---|
| Anuais de rua pouco ativos | 25,8% | 0,9 treino por semana; **15% sem treinar em 3 meses** |
| Mensais de rua | 20,8% | 1,9 treino por semana, 6 meses de casa; 23% por influenciador |
| Anuais em casa | 19,3% | 15% ao ar livre; bem-estar 13% |
| Mensais em casa | 18,0% | 15% ao ar livre; bem-estar 18% |
| Intensos | 10,8% | **4,4 treinos por semana**; 22% avançados; 26% por prova ou desempenho; 79% anuais |
| Longões | 5,3% | 85 minutos por treino; 32% avançados |

- ✔ **Prós:**
  - acrescenta a frequência e revela dois grupos novos: os **intensos** e os **anuais pouco ativos** (1 em cada 4 assinantes);
  - muito estável (0,98).
- ✖ **Contras:**
  - quatro grupos continuam presos ao "plano × lugar";
  - não enxerga os novatos.
- **Personas que se formam:**
  - "o anual que pagou e esfriou";
  - "o atleta intenso";
  - "o mensal de casa, que treina por bem-estar";
  - "o longão".
- **Considerar ou descartar:** **considerar**, como segunda opção, se o grupo quiser o plano explícito nos grupos.

### Cenário escolhido (C) · 5 variáveis sem o plano, 5 grupos

| Grupo | % base | Retrato | Plano (descrição) | Receita líquida |
|---|---|---|---|---|
| Treino em casa | 29,8% | Só 15% ao ar livre, 2 treinos por semana, 11 meses de casa; bem-estar 17% (contra 6% a 8% nos outros) | 43% mensal | 34% do total; mediana R$ 386 |
| Rua no ritmo leve | 28,2% | 81% ao ar livre, 1,4 treino por semana, 13 meses de casa; **13% sem treinar em 3 meses** | 29% mensal | 34% do total; mediana R$ 472 |
| Novatos | 20,3% | **1,3 mês de casa**, 1,1 treino por semana, **nenhum seguidor**; 27% por influenciador (o dobro dos outros) | 58% mensal | 8,5% do total; mediana R$ 116 |
| Intensos | 16,0% | **3,9 treinos por semana**, 9 meses de casa; 21% avançados; 22% por prova ou desempenho | 49% mensal | 17% do total |
| Longões | 5,7% | 84 minutos por treino; 30% avançados; 27% por prova ou desempenho | 32% mensal | 6% do total |

- ✔ **Prós:**
  - os grupos nascem só do **comportamento** (como treina, há quanto tempo, com quem), e cada um cabe numa frase;
  - aparecem os **novatos**, que nenhum cenário com plano isola bem;
  - o plano e o objetivo, que ficaram de fora do cálculo, mudam de forma coerente entre os grupos: novatos mais mensais e vindos de influenciador, casa com mais bem-estar, intensos e longões com mais prova. É sinal de grupos reais;
  - estável (0,95).
- ✖ **Contras:**
  - silhueta baixa (0,24): os grupos se tocam nas bordas, o que é comum em dados de clientes;
  - o plano não é variável, então um grupo mistura mensais e anuais e a ação comercial precisa olhar o plano dentro do grupo;
  - os longões ficam no limite de 5%.
- **Personas que se formam (3 a 4):**
  1. **"O novato que ainda está chegando"** (20%): acabou de entrar, sem rede, veio por influenciador. Pede onboarding e conexão com outras pessoas.
  2. **"Quem treina em casa"** (30%): vídeo, bem-estar, rotina regular. Pede conteúdo em vídeo novo.
  3. **"O corredor de rua no ritmo leve"** (28%): veterano e de maior receita, mas 1 em cada 8 está parado há 3 meses. Pede um desafio para reativar.
  4. **"O atleta"** (intensos + longões, 22%): treina muito ou longe, avançado, focado em prova. Pede planilha e metas.
- **Decisão:** **escolhido pelo grupo (D-054)**. É o que melhor responde "quem são os nossos clientes" e rende personas diferentes entre si.

### Cenário D · 6 variáveis, 6 grupos

| Grupo | % base | Retrato |
|---|---|---|
| Anuais de rua | 27,5% | 1,4 treino por semana; 14% sem treinar em 3 meses |
| Anuais em casa | 19,1% | 15% ao ar livre |
| Mensais de rua ativos | 17,6% | 91% mensal, 10 meses de casa, 2,7 treinos por semana |
| Novatos | 15,7% | 1 mês de casa, nenhum seguidor, 65% mensal; 28% por influenciador |
| Mensais em casa | 14,9% | 8,5 meses de casa; bem-estar 20% |
| Longões | 5,2% | 85 minutos por treino |

- ✔ **Prós:**
  - usa toda a informação;
  - mostra os novatos e mantém o plano explícito.
- ✖ **Contras:**
  - o plano volta a dominar: quatro grupos são de novo "plano × lugar";
  - os intensos se diluem;
  - é a menor silhueta (0,24), com estabilidade parecida com a de C;
  - a 6ª variável não acrescentou um grupo novo em relação a C.
- **Personas que se formam:**
  - "o novato";
  - "o mensal de rua engajado";
  - "o mensal de casa por bem-estar";
  - "o longão".
- **Considerar ou descartar:** **descartar**. Tem a complexidade de 6 variáveis sem ganhar um grupo que C ou B não mostrem.

## Recomendação levada à discussão e decisão

1. **Principal: cenário C** (5 variáveis sem o plano, 5 grupos, 4 personas). **Escolhido pelo grupo em 07/11/2026 (D-054)** e renomeado para "cenário escolhido".
2. **Alternativa: cenário B**, se o grupo preferir grupos separados por plano.
3. **Descartar A e D:** A é simples demais; D é complexo sem ganho.

Depois da escolha:
- gravamos o grupo de cada assinante (`dados/processados/clusters_2026-09-30.parquet`);
- registramos a decisão no DECISOES.md;
- escrevemos os cartões de persona no formato da Aula 4.
