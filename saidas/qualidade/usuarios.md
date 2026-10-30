# Qualidade: `usuarios.csv`

Uma linha por conta (paga ou grátis) · 64.948 linhas · 12 colunas · avaliado em 29/10/2026 com a skill `qualidade-dados` · medidas em [usuarios_evidencias.md](usuarios_evidencias.md)

**Dados pessoais:** este arquivo tem e-mail, data de nascimento, cidade e CEP. Neste relatório eles aparecem só como contagens, nunca com valores individuais.

## Resumo

O arquivo liga todos os outros pelo `user_id`, e essa ligação está íntegra: um `user_id` por linha, sem repetição, e todos os outros arquivos encontram suas contas aqui. Os problemas estão nos campos digitados pela pessoa, que o dicionário avisa que não passam por validação:
- **cidade:** 36 grafias para 13 cidades;
- **sexo:** 6 grafias para 2 valores;
- **sistema:** 5 grafias para 2 valores;
- **nascimento:** datas de "preenchimento padrão" (01/01/1900 e uma data em 2031).

Há ainda **119 contas criadas depois do corte** e **959 pessoas com duas contas**, que só se reconhecem pelo e-mail em maiúsculas e minúsculas. A avaliação também mostrou um **erro na análise anterior** sobre as 42 contas com cadastro depois do início da assinatura (Q-usu-07).

**Situação em 29/10/2026:** os 7 problemas foram decididos (D-017 a D-023 no `DECISOES.md`; a D-023 substitui a D-016), todos para aplicar numa cópia em `dados/processados/`. Os brutos não mudam. A limpeza ainda não foi feita.

## Problemas para decidir

| ID | Dimensão | Coluna | O que está errado | Por que importa para o case |
|---|---|---|---|---|
| Q-usu-01 | Consistência | `cidade` | 36 grafias para 13 cidades; 13.601 contas (20,9%) fora da grafia padrão (`Sampa`, `SP`, `S. Paulo`, `SAO PAULO`, `BH`, `Floripa`, `BSB`…) | Qualquer contagem por cidade sai partida: São Paulo apareceria dividida em 8 linhas |
| Q-usu-02 | Consistência · Completude | `sexo` | 6 grafias (`F`, `Fem`, `feminino`, `M`, `Masc`, `masculino`) e 3.142 vazios (4,8%) | Contagens erradas; e é dado sensível (LGPD), que só deve servir para controle, não para decidir ofertas (Aula 2 e Aula 3) |
| Q-usu-03 | Consistência | `sistema` | 5 grafias (`android`, `Android`, `ios`, `iOS`, `IOS`); 16.067 contas (24,7%) fora da grafia padrão | O sistema define onde a pessoa paga e cancela (loja da Apple ou do Google) |
| Q-usu-04 | Validade · Completude | `data_nascimento` | 412 em 01/01/1900, 194 numa mesma data de 2031 e 3.301 vazios; 1 conta com 13 a 17 anos | Idades de 126 anos ou negativas distorcem médias e segmentos; menor de idade pede cuidado (LGPD) |
| Q-usu-05 | Temporalidade · Validade | `data_cadastro` | 119 contas criadas depois do corte (de 10/2026 a 04/2027), sem nenhuma outra informação | Os dados foram exportados em 01/10/2026: essas datas são impossíveis, e a D-002 proíbe usar dado posterior ao corte |
| Q-usu-06 | Unicidade | `email` | 959 pares de contas com o mesmo e-mail, mudando só maiúsculas e minúsculas: 1.918 contas que são 959 pessoas | Contar contas e contar pessoas dá números diferentes; conversão e segmentos por pessoa ficam duplicados |
| Q-usu-07 | Correção de análise | `data_cadastro` × `assinaturas.inicio` | As 42 assinaturas que começam antes do cadastro (Q-ass-04, D-016) são **todas contas internas de cortesia**, sem eventos | A D-016 registrou um motivo falso. O impacto é nulo (já fora das métricas pela D-013), mas o registro precisa ser corrigido |

### Q-usu-01 · Cidade escrita de 36 jeitos

**Em palavras simples:** cada pessoa digitou o nome da cidade do seu jeito.

**Exemplo:** São Paulo aparece como `São Paulo` (19.096), `Sampa` (1.240), `são paulo` (1.232), `São Paulo - SP` (1.202), `Sao Paulo` (1.201), `S. Paulo` (1.181), `SAO PAULO` (1.160) e `SP` (1.155).

- **Evidência:**
  - 36 grafias para 13 cidades.
  - Cada grafia aponta para uma só UF, e a coluna `uf` está limpa (11 estados, sem variação). Ou seja, a UF já confirma a cidade.
  - Fora da grafia padrão: São Paulo 8.371, Rio de Janeiro 2.245, Belo Horizonte 1.340, Brasília 896 e Florianópolis 749.
- **Opções:**
  - **Corrigir:** mapear as 36 grafias para os 13 nomes oficiais com uma tabela de-para registrada no código. Efeito: 64.948 contas → 64.948; 13.601 cidades reescritas.
  - **Remover:** não se aplica.
  - **Marcar:** manter como está. Efeito: contagens por cidade continuam partidas.
- **Recomendação:** **corrigir**. As 36 grafias são inequívocas, e a UF confirma cada uma.
- **Status:** decidido (D-017, 29/10/2026, Pedro Filardi)

### Q-usu-02 · Sexo escrito de 6 jeitos

**Em palavras simples:** a mesma resposta foi gravada de jeitos diferentes, e 4,8% não responderam.

**Exemplo:** "feminino" aparece como `F` (19.330), `Fem` (6.657) e `feminino` (6.520).

- **Evidência:**
  - Feminino: 32.507. Masculino: 29.299. Vazio: 3.142.
  - Na Aula 2, gênero não teve poder de prever cancelamento (AUC 0,50, igual ao acaso).
- **Opções:**
  - **Corrigir:** padronizar para `F` e `M`, e os vazios viram `nao_informado`. Efeito: 0 contas a menos; 24.830 valores reescritos e 3.142 vazios que viram `nao_informado`.
  - **Remover:** tirar a coluna da base processada. Efeito: perde a variável de controle.
  - **Marcar:** manter as 6 grafias. Efeito: contagens partidas.
- **Recomendação:** **corrigir**, com a regra de usar sexo **só para descrever e controlar análises, nunca para escolher quem recebe oferta**, como mostram a Aula 3 e a LGPD (art. 6º, IX, não discriminação).
- **Status:** decidido (D-018, 29/10/2026, Pedro Filardi)

### Q-usu-03 · Sistema escrito de 5 jeitos

**Exemplo:** iPhone aparece como `ios` (20.854), `iOS` (7.463) e `IOS` (1.480).

- **Evidência:** 5 grafias para 2 sistemas: Android 35.151 e iOS 29.797. Não há vazios.
- **Opções:**
  - **Corrigir:** padronizar para `android` e `ios`. Efeito: 0 contas a menos; 16.067 valores reescritos.
  - **Remover:** não se aplica.
  - **Marcar:** manter as grafias. Efeito: contagens partidas.
- **Recomendação:** **corrigir**. Não há nenhuma ambiguidade.
- **Status:** decidido (D-019, 29/10/2026, Pedro Filardi)

### Q-usu-04 · Datas de nascimento de "preenchimento padrão"

**Em palavras simples:** quando a pessoa pula o campo, alguns sistemas gravam uma data "de enchimento".

**Exemplo:** 412 pessoas "nasceram" em 01/01/1900, o que daria 126 anos, e 194 numa mesma data de 2031, ainda no futuro.

- **Evidência:**
  - Datas falsas: 412 + 194 = 606, cada grupo concentrado numa única data.
  - Mais 3.301 vazios.
  - Entre as datas restantes, as idades vão de 31 a 70 anos (do 5º ao 95º percentil), com mediana de 47.
  - 1 conta tem entre 13 e 17 anos; nenhuma tem menos de 13.
- **Opções:**
  - **Corrigir:** as 606 datas falsas viram vazio, e é criada a coluna `idade_informada` (sim/não). Efeito: 0 contas a menos; nascimento preenchido de 61.647 para 61.041.
  - **Remover:** tirar as contas sem nascimento válido. Efeito: −3.907 contas (−6,0%).
  - **Marcar:** manter as datas e marcar como suspeitas. Efeito: médias de idade ficam distorcidas.
- **Recomendação:** **corrigir**, com duas regras:
  - **idade só como variável de controle**, nunca como critério de oferta (Aula 3, LGPD);
  - a **1 conta menor de 18 anos** fica marcada e fora de qualquer campanha.
- **Status:** decidido (D-020, 29/10/2026, Pedro Filardi)

### Q-usu-05 · Contas criadas depois do corte

**Em palavras simples:** 119 contas têm data de criação depois do dia em que os dados foram exportados (01/10/2026). Isso é impossível.

**Exemplo:** uma conta "criada" em abril de 2027.

- **Evidência:**
  - Por mês: 43 em out/2026, 21 em nov, 14 em dez, 19 em jan/2027, 16 em fev, 5 em mar e 1 em abr.
  - Nenhuma delas tem evento, assinatura ou onboarding. Ou seja, não há nenhum outro dado ligado a elas.
- **Opções:**
  - **Corrigir:** não há data certa conhecida.
  - **Remover:** tirar as 119 da cópia processada. Efeito: 64.948 → 64.829 contas.
  - **Marcar:** manter, com `cadastro_pos_corte`. Efeito: 0 contas a menos; ficam contas "do futuro" nos totais.
- **Recomendação:** **remover**. Não carregam nenhuma informação, e a D-002 já proíbe dados depois do corte.
- **Status:** decidido (D-021, 29/10/2026, Pedro Filardi)

### Q-usu-06 · A mesma pessoa com duas contas

**Em palavras simples:** 959 pessoas criaram uma segunda conta, por exemplo depois de esquecer a senha, digitando o mesmo e-mail com maiúsculas diferentes.

**Exemplo:** um par de contas com `Maria.Silva@...` e `maria.silva@...`. Exemplo ilustrativo; os e-mails reais não aparecem aqui.

- **Evidência:**
  - 959 pares (1.918 contas). Em todos, o e-mail difere só em maiúsculas e minúsculas, e a UF e a data de nascimento são as mesmas.
  - A segunda conta foi criada, na mediana, 98 dias depois da primeira.
  - Em nenhum par as duas contas pagaram: 472 pares têm uma conta com assinatura, e 487 nenhuma.
- **Opções:**
  - **Corrigir:** fundir os pares numa só conta. Efeito: é preciso reescrever o `user_id` em todos os outros arquivos, e isso cria risco de erro em cascata.
  - **Remover:** tirar a conta sem assinatura de cada par. Efeito: −959 contas; perde o histórico de uso dessa segunda conta.
  - **Marcar:** criar `pessoa_id` (o e-mail em minúsculas, transformado num código que não revela o e-mail). Contagens "por conta" usam `user_id`, e "por pessoa" usam `pessoa_id`. Efeito: 64.948 contas → 64.948; 63.989 pessoas.
- **Recomendação:** **marcar**. Nenhum dado se perde, e cada análise escolhe a unidade certa.
- **Status:** decidido (D-022, 29/10/2026, Pedro Filardi)

### Q-usu-07 · Correção da análise das 42 contas (revê a D-016)

**Em palavras simples:** na avaliação do `assinaturas.csv`, eu disse que as 42 assinaturas que começam antes do cadastro eram de assinantes reais e que o erro estava no cadastro. **Isso estava errado.** As 42 são contas internas de cortesia: canal `interno`, e-mail `@vitaliza.com.br`, nenhum evento. Não havia como confirmar a data de início pelos eventos.

- **Evidência:**
  - As 42 são `cortesia` / `interno`.
  - Das 60 contas de cortesia, 42 têm início antes do cadastro; todas as 60 têm início em 2025.
  - Nenhuma tem evento de assinatura.
- **Opções:**
  - **Corrigir o registro:** a D-016 passa a "substituída", e uma nova decisão diz que o caso é das contas internas, já fora das métricas pela D-013, e que nenhuma data será alterada. Efeito: 0 contas; a coluna `cadastro_inconsistente` deixa de ser necessária.
  - **Manter a D-016:** deixa no registro um motivo falso.
- **Recomendação:** **corrigir o registro**. A regra do `DECISOES.md` é não apagar: a D-016 fica com o status "substituída por D-XXX".
- **Status:** decidido (D-023, 29/10/2026, Pedro Filardi)

## Já decidido

- **D-008:** as 1.019 contas sem onboarding serão marcadas com `tem_onboarding`. As 119 de Q-usu-05 e as 60 internas estão entre elas.
- **D-013:** as 60 contas internas (`interno`, `@vitaliza.com.br`) são as mesmas `cortesia`: 60 = 60 = 60.

## O que não é problema

- **Chave:** 64.948 `user_id` distintos, sem repetição; os outros arquivos encontram suas contas aqui.
- **UF:** 11 estados, sem variação de grafia, e cada cidade aponta para uma só UF.
- **E-mail:** todos têm formato válido, e nenhum se repete exatamente igual. A repetição só aparece ignorando maiúsculas (Q-usu-06).
- **Cadastro × eventos:** nenhuma conta tem evento de assinatura antes da data de cadastro.
- **`canal_aquisicao`, `versao_app`, `relogio_conectado`:** sem vazios e sem variação de grafia. `nenhum` em `relogio_conectado` é um valor legítimo, não um vazio.
- **Vazios de sexo, nascimento e CEP:** estáveis de 2020 a 2026, sem mudança no jeito de registrar.

## Números conferidos à mão

Contei com o leitor de CSV do Python, sem pandas:
1. **Linhas:** 64.948. Bate com o dicionário.
2. **`sexo` = `F`:** 19.330.
3. **Nascimento em 01/01/1900:** 412.
