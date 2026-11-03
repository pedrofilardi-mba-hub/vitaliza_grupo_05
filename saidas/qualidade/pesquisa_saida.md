# Qualidade: `pesquisa_saida.csv`

Uma linha por resposta à pesquisa de saída do site · 643 linhas · 5 colunas · de 01/06 a 30/09/2026 · avaliado em 03/11/2026 com a skill `qualidade-dados` · medidas em [pesquisa_saida_evidencias.md](pesquisa_saida_evidencias.md)

## Resumo

Os registros estão certos:
- todas as 643 respostas caem no mesmo dia de um `cancelamento_web` nos eventos;
- todas são de quem paga pelo site (437 cartão, 206 Pix);
- 354 já tinham saído e 289 seguiam no período pago em 30/09, exatamente como diz o dicionário;
- **privacidade:** nenhum comentário traz e-mail, telefone, CPF ou nome.

Os problemas estão no **significado**:
1. **O motivo marcado muitas vezes não combina com o comentário.** E o motivo mais citado nos comentários, ter cumprido o objetivo (uma prova), nem existe na lista.
2. **Só responde quem paga pelo site**: os 70% que pagam pela loja nunca veem a pesquisa.
3. **2 pessoas responderam duas vezes.**
4. **Erros de digitação nos comentários.**

**Situação em 03/11/2026:** os 4 problemas foram decididos (D-046 a D-049 no `DECISOES.md`), para aplicar numa cópia em `dados/processados/` e na análise. Os brutos não mudam.

## Problemas para decidir

| ID | Dimensão | Coluna | O que está errado | Por que importa para o case |
|---|---|---|---|---|
| Q-ps-01 | Consistência · Validade | `motivo_principal` × `comentario` | Dos 264 que marcaram `preco`, 76 escrevem que cumpriram o objetivo ("já fiz a prova") e 22 falam de problema técnico. Dos 223 que marcaram `outro`, 109 falam de objetivo cumprido. Esse motivo (cerca de 190 respostas) não existe na lista | Contar pelo motivo marcado diria que "preço" é a principal razão de saída (41%). Pelo comentário, "objetivo cumprido" disputa o primeiro lugar, e isso muda a oferta certa (objetivo 6) |
| Q-ps-02 | Validade (uso do dado) | arquivo inteiro | Só quem cancela pelo site vê a pesquisa (100% cartão ou Pix); quem paga pela loja (cerca de 70% da base) nunca responde. Entre os cancelamentos pelo site, responderam de 49% a 57% por mês | Generalizar os motivos para todos os que saem é viés de seleção, como o próprio enunciado alerta |
| Q-ps-03 | Unicidade | `user_id` | 2 contas responderam duas vezes, em datas diferentes (643 respostas de 641 pessoas) | Contar "pessoas que saíram por preço" contaria essas duas em dobro |
| Q-ps-04 | Consistência | `comentario` | 142 comentários distintos viram 107 depois de normalizar; 52 (8,1%) diferem só por acento ou letra trocada | Contagens por comentário ficam fragmentadas |

### Q-ps-01 · O motivo marcado não combina com o comentário

**Em palavras simples:** a pessoa escolhe um motivo numa lista e pode escrever um comentário. Muitas vezes o comentário conta outra história. E a razão que mais aparece nos comentários não está na lista.

**Exemplo real do arquivo:** 14 pessoas marcaram **"preço"** e escreveram "já fiz a prova, agora não preciso mais"; 12 marcaram "preço" e escreveram "treinei pra prova e consegui, objetivo cumprido". Sem uma opção "objetivo cumprido", elas escolheram a que estava mais à mão.

- **Evidência:**
  - Classifiquei os comentários por palavras-chave (prova, maratona, era só até…; bug, GPS…; caro, aumento…; lesão, médico…).
  - Comentários de **objetivo cumprido ou evento pontual**: 194. Desses, 109 marcaram `outro`, 76 `preco`, 5 `outro_app` e 4 `nao_uso`.
  - Comentários de **problema técnico** com outro motivo marcado: 22 em `preco` e 3 em `outro_app`.
  - Marcaram `outro_app` com comentários sobre GPS e dor na lombar, que não falam de outro app.
- **Opções:**
  - **Corrigir:** sobrescrever o motivo pelo do comentário. Efeito: altera respostas que a pessoa escolheu; perde o original.
  - **Remover:** tirar as respostas incoerentes. Efeito: perde justamente as mais informativas.
  - **Marcar:** manter o motivo original e criar `motivo_revisado`, que inclui a categoria nova **`objetivo_cumprido`** e é preenchido pelo comentário quando ele existe. Agora com regras de palavras-chave; no objetivo 5, com a IA, conferida contra uma amostra rotulada à mão. Sem comentário, vale o motivo marcado. Efeito: 0 linhas; 1 coluna nova.
- **Recomendação:** **marcar**. O que a pessoa escreveu é mais rico que o que ela clicou, mas o clique original fica para comparação.
- **Status:** decidido (D-046, 03/11/2026, Pedro Filardi)

### Q-ps-02 · Só quem cancela pelo site responde

**Em palavras simples:** quem paga pela App Store ou pelo Google Play cancela no celular, fora do app, e nunca vê a pesquisa. E, entre os que cancelam pelo site, só cerca de metade responde.

**Exemplo:** se 40% dos que responderam citam preço, não dá para dizer que 40% de todos os que saem saem por preço. Quem paga pela loja pode sair por motivos diferentes, e quem não quis responder também.

- **Evidência:**
  - 643 respostas, 100% de quem paga pelo site.
  - Respostas sobre cancelamentos web: jun 210/378, jul 182/323, ago 154/271, set 97/200.
  - O enunciado: de 3.389 assinaturas que terminaram entre junho e setembro, só 353 responderam (cerca de 10%). O arquivo dá 354 respostas de quem já tinha saído.
- **Opções:**
  - **Corrigir:** não há como corrigir quem não respondeu.
  - **Remover:** não se aplica.
  - **Marcar (regra de uso):**
    - os motivos descrevem **só quem cancela pelo site e responde**, e nunca são extrapolados como "motivo de saída da base";
    - sempre que aparecerem num número, vêm com o tamanho do grupo e a ressalva;
    - para quem paga pela loja, o motivo precisa ser inferido de sinais de uso, chamados e posts.

    Efeito: 0 linhas; regra registrada.
- **Recomendação:** **marcar, com a regra**.
- **Status:** decidido (D-047, 03/11/2026, Pedro Filardi)

### Q-ps-03 · Duas pessoas responderam duas vezes

**Exemplo:** uma conta respondeu "outro" em 24/06 e "preço" em 23/07, provavelmente porque cancelou, voltou atrás e cancelou de novo.

- **Evidência:** 2 contas com 2 respostas cada, em datas diferentes. Uma mudou o motivo (`outro` → `preco`); a outra manteve `outro`.
- **Opções:**
  - **Corrigir:** não se aplica; as duas respostas são reais.
  - **Remover:** manter só a mais recente de cada conta. Efeito: 643 → 641 respostas; perde a primeira resposta.
  - **Marcar:** criar `ultima_resposta` (sim ou não). Contagens "por pessoa" usam só a última; contagens "por resposta" usam todas. Efeito: 0 linhas; 1 coluna nova.
- **Recomendação:** **marcar**, porque nenhuma resposta se perde.
- **Status:** decidido (D-048, 03/11/2026, Pedro Filardi)

### Q-ps-04 · Erros de digitação nos comentários

**Exemplo real do arquivo:** "o gps não funciona no meu celular" e "o gps não funciona no mue celular".

- **Opções:**
  - **Corrigir:** sobrescrever pela grafia mais comum. Efeito: 52 comentários alterados.
  - **Remover:** não se aplica.
  - **Marcar:** criar `texto_norm` só para contar; a IA lê o original. Efeito: 0 linhas; 1 coluna nova.
- **Recomendação:** **marcar**, pela mesma regra das D-007, D-042 e D-045.
- **Status:** decidido (D-049, 03/11/2026, Pedro Filardi)

## Já decidido

- **D-002 (corte):** todas as respostas estão até 30/09/2026.
- **D-011:** o motivo "técnico" da saída (renovação desligada, falha de pagamento etc.) vem de `assinaturas.csv`. Esta pesquisa traz o motivo **declarado pela pessoa**, que é outra coisa.

## O que não é problema

- **Ligação com os eventos:** 643 de 643 respostas no mesmo dia de um `cancelamento_web`.
- **Situação no corte:** 354 já saíram e 289 ainda estavam no período pago em 30/09. Bate com o dicionário.
- **Comentário vazio:** 183 (28,5%). O comentário é opcional.
- **Privacidade:** 0 comentários com e-mail, telefone, CPF ou nome.
- **Domínio:** 0 motivos fora da lista do dicionário.

## Números conferidos à mão

Contei com o leitor de CSV do Python e com contagem direta:
1. **Linhas:** 643. Bate com o dicionário.
2. **Contas distintas:** 641. Bate com o dicionário.
3. **Motivo `outro`:** 223.
