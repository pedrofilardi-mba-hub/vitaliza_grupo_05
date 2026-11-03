# Qualidade: `campanha_ago26.csv`

Uma linha por assinante sorteado · 14.120 linhas · 9 colunas · envio em 10/08/2026 às 10h · avaliado em 03/11/2026 com a skill `qualidade-dados` · medidas em [campanha_ago26_evidencias.md](campanha_ago26_evidencias.md)

## Resumo

É o único experimento sorteado da base, e **o sorteio foi bem feito**. Os quatro grupos têm o mesmo perfil antes da campanha em tudo o que dá para medir, e as diferenças são do tamanho que o acaso produz (p > 0,05 em todos os testes):

| Antes de 10/08 | Conteúdo | Controle | Cupom | Desafio |
|---|---:|---:|---:|---:|
| Pessoas | 3.554 | 3.579 | 3.472 | 3.515 |
| Plano anual | 58,7% | 59,7% | 59,0% | 58,6% |
| Paga pela loja (App Store ou Google Play) | 69,1% | 70,3% | 70,5% | 70,3% |
| Tempo de casa (mediana, meses) | 8,8 | 9,1 | 9,3 | 9,0 |
| Treinou em julho | 81,5% | 81,2% | 79,7% | 81,5% |
| Minutos em julho (média) | 249 | 259 | 258 | 254 |
| Tem relógio conectado | 39,1% | 37,6% | 37,8% | 38,5% |
| Já tinha desligado a renovação | 15,2% | 14,4% | 15,1% | 15,4% |

Também confere:
- cada grupo recebeu só a sua mensagem;
- entre os de plano conhecido, a oferta combina 100% com o plano (`30pct_3_meses` só para mensal, `1_mes_gratis` só para anual); 13 cupons foram para pessoas ainda no teste grátis, sem plano definido (Q-cam-01);
- o controle não abriu nem clicou em nada;
- não há clique sem abertura.

Os problemas são poucos e pequenos, e um deles é uma **regra de como medir o resultado**, que decide se a análise do objetivo 6 vai dar a resposta certa.

**Situação em 03/11/2026:** os 3 problemas foram decididos (D-036 a D-038 no `DECISOES.md`), para aplicar numa cópia em `dados/processados/` e na análise. Os brutos não mudam.

## Problemas para decidir

| ID | Dimensão | Coluna | O que está errado | Por que importa para o case |
|---|---|---|---|---|
| Q-cam-01 | Validade | `user_id` × eventos | 48 sorteados (0,3%) estavam no teste grátis às 10h de 10/08 e fizeram a 1ª cobrança naquele mesmo dia; 1 assinante ativo não foi sorteado | O enunciado fala em "assinantes pagantes daquele dia". Tirar os 48 poderia enviesar o resultado, porque a mensagem pode ter influenciado a decisão de pagar |
| Q-cam-02 | Consistência | `abriu_push`, `abriu_email`, `clicou` | Sim/não gravado como texto (`True`/`False`) | Sem converter, somas e médias de abertura não funcionam |
| Q-cam-03 | Validade (uso do dado) | `grupo`, `abriu_*`, `clicou` | O arquivo mede atenção (abriu, clicou), não retenção. A janela observável vai só até o corte: 51 dias depois do envio. E 59% dos sorteados são anuais, que só podem sair na renovação | Medir o efeito por "quem abriu" ou só pela saída efetiva levaria a uma conclusão errada sobre qual mensagem funciona |

### Q-cam-01 · 48 sorteados ainda estavam no teste grátis

**Em palavras simples:** a lista foi feita com quem pagava "naquele dia". 48 pessoas estavam no teste grátis às 10h e passaram a pagar mais tarde, no mesmo dia.

**Exemplo:** alguém no 7º dia do teste grátis recebe a mensagem "Novo desafio" de manhã e faz a primeira cobrança à tarde.

- **Evidência:**
  - Às 10h de 10/08, os eventos mostram 14.073 pagantes; foram sorteados 14.120.
  - Os 48 a mais tinham `trial_iniciado` como último evento e fizeram a 1ª cobrança em 10/08.
  - 1 pagante ativo ficou fora do sorteio.
  - Nenhuma conta interna (cortesia) foi sorteada.
- **Opções:**
  - **Corrigir:** não há o que corrigir; o sorteio é o que é.
  - **Remover:** tirar os 48 da análise. Efeito: 14.120 → 14.072. Risco de viés, porque a mensagem pode ter influenciado a decisão de pagar, e isso aconteceu depois do sorteio.
  - **Marcar:** criar `em_teste_no_envio` e manter todos na análise principal, como sorteados. Efeito: 0 linhas; 1 coluna nova; a análise pode ser repetida sem eles para conferir.
- **Recomendação:** **marcar**. Num experimento, a regra é analisar todos como foram sorteados. Os 48 são 0,3%, e a conferência sem eles mostra se mudam algo.
- **Status:** decidido (D-036, 03/11/2026, Pedro Filardi)

### Q-cam-02 · Sim/não gravado como texto

**Exemplo:** `abriu_push` aparece como a palavra `True`, e não como o valor verdadeiro. Somar a coluna para contar aberturas não funciona.

- **Evidência:** as três colunas só têm `True` e `False`, sem vazios.
- **Opções:**
  - **Corrigir:** converter para sim/não de verdade (booleano). Efeito: 0 linhas; 3 colunas convertidas.
  - **Remover:** não se aplica.
  - **Marcar:** não resolve.
- **Recomendação:** **corrigir**.
- **Status:** decidido (D-037, 03/11/2026, Pedro Filardi)

### Q-cam-03 · Como medir se a campanha funcionou

**Em palavras simples:** o arquivo diz quem **abriu e clicou**, mas o que importa é quem **ficou**. Há três cuidados:
1. **Comparar os grupos inteiros, como foram sorteados, e não só quem abriu.** Quem abre já é mais engajado; comparar só os que abriram mistura o efeito da mensagem com o perfil da pessoa.
2. **A janela tem 51 dias.** Do envio (10/08) até o corte (30/09). Não dá para medir 60 dias.
3. **Os anuais (59%) só podem sair na renovação.** Para eles, em 51 dias, o sinal de saída é **desligar a renovação**, e não a saída efetiva.

**Exemplo:** o grupo cupom tem a maior taxa de clique (16,4%, contra 14,3% do desafio). Isso não diz se ele segurou mais gente. Só a comparação de saída entre cupom e controle diz.

- **Evidência:**
  - Abertura de push de 30,6% a 32,0% nos grupos com mensagem; clique de 14,3% a 16,4%.
  - Plano anual em 58,6% a 59,7% dos grupos.
  - A situação de cada pessoa em qualquer data sai dos eventos (D-012).
- **Opções:**
  - **Corrigir:** não se aplica.
  - **Remover:** não se aplica.
  - **Marcar (regra de análise):**
    - o efeito de cada mensagem é a diferença entre o grupo e o controle, **com todos os sorteados**;
    - o resultado se mede **pelos eventos**, de 10/08 até 30/09, em duas medidas:
      - (a) **saiu**: assinatura expirada no período;
      - (b) **anunciou saída**: desligou a renovação no período, sem religar até 30/09;
    - os resultados saem **separados para mensal e anual**;
    - abertura e clique só descrevem atenção à mensagem.

    Efeito: 0 linhas; a regra fica registrada para os objetivos 6 e 7.
- **Recomendação:** **marcar, com essa regra**. Sem ela, é fácil medir o efeito do jeito errado.
- **Status:** decidido (D-038, 03/11/2026, Pedro Filardi)

## Já decidido

- **D-012:** a saída depois da campanha se mede pelos eventos.
- **D-013:** nenhuma conta interna foi sorteada.
- **D-015:** o retrato de 01/10 (`assinaturas.csv`) não serve para medir o resultado: ele não diz quando a pessoa saiu.

## O que não é problema

- **Vazios:** `enviado_em`, `canal` e `titulo_mensagem` estão vazios só no controle (3.579), como esperado. `oferta` está vazia em todos fora do grupo cupom.
- **Unicidade:** cada pessoa aparece uma vez, num único grupo.
- **Tamanho dos grupos:** de 3.472 a 3.579, diferença compatível com o acaso (p = 0,60).
- **Horário de envio:** o mesmo para todos, 10/08/2026 às 10h, no horário de Brasília (o formato é o do site).

## Números conferidos à mão

Contei com o leitor de CSV do Python, sem pandas:
1. **Linhas:** 14.120. Bate com o dicionário.
2. **Controle:** 3.579.
3. **Cupons de "1 mês grátis":** 2.052: 2.047 para anuais e 5 para pessoas ainda no teste grátis.
