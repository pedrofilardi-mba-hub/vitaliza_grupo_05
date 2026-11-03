# Qualidade: `feed_posts.csv`

Uma linha por post na rede social · 119.309 linhas · 5 colunas · de 01/07/2025 a 30/09/2026 · avaliado em 03/11/2026 com a skill `qualidade-dados` · medidas em [feed_posts_evidencias.md](feed_posts_evidencias.md)

## Resumo

O que está bem:
- **Privacidade:** nenhum texto traz e-mail, telefone, CPF, perfil marcado (@), link ou nome declarado. Os posts podem ir para a IA no objetivo 5.
- **Estrutura:** nenhum post repetido (nem a mesma conta postando o mesmo texto em menos de 1 hora), todas as contas existem, e as curtidas vão de 0 a 38, faixa plausível.

Os problemas são três:
1. **122 posts com data depois do corte.**
2. **692 posts publicados algumas horas antes do cadastro da conta**, no mesmo dia.
3. **Os textos variam muito na grafia** (emoji, acento), o que fragmenta as contagens.

**Situação em 03/11/2026:** os 3 problemas foram decididos (D-043 a D-045 no `DECISOES.md`), para aplicar numa cópia em `dados/processados/`. Os brutos não mudam.

## Problemas para decidir

| ID | Dimensão | Coluna | O que está errado | Por que importa para o case |
|---|---|---|---|---|
| Q-fp-01 | Temporalidade | `data_hora` | 122 posts (0,1%) entre 01/10 e 07/10/2026, depois do corte | Usá-los seria ver o futuro (D-002): o que a pessoa postou depois do dia da previsão |
| Q-fp-02 | Validade · Consistência | `data_hora` × `usuarios.data_cadastro` | 692 posts (0,6%, de 688 contas) aparecem de minutos a 16 horas antes do horário de criação da conta, sempre no mesmo dia | É impossível postar antes de ter conta. Como acontece sempre no mesmo dia, só afeta análises hora a hora do primeiro dia |
| Q-fp-03 | Consistência | `texto` | 31.620 textos distintos viram 11.637 depois de normalizar; 51.146 posts (42,9%) diferem da grafia mais comum só por emoji, acento ou espaço | Contagens por texto ficam fragmentadas: `yoga pra fechar o dia` aparece em 332 grafias |

### Q-fp-01 · Posts depois do corte

**Em palavras simples:** é o mesmo caso das amizades (D-039): 122 posts são de 1º a 7 de outubro, mas os dados vão até 30/09.

**Exemplo:** um post de 02/10/2026. No dia da previsão (30/09), ele não existia.

- **Evidência:**
  - Por dia: 1º/10: 62; 2/10: 31; 3/10: 16; 4/10: 5; 5/10: 2; 6/10: 4; 7/10: 2.
  - O volume cai rápido; em setembro, a média era de 292 posts por dia.
- **Opções:**
  - **Corrigir:** não há data certa conhecida.
  - **Remover:** tirar os 122 da cópia processada. Efeito: 119.309 → 119.187 posts.
  - **Marcar:** criar `apos_corte` e filtrar. Efeito: 0 linhas; risco de esquecer o filtro.
- **Recomendação:** **remover**, pela mesma regra das D-002, D-021 e D-039.
- **Status:** decidido (D-043, 03/11/2026, Pedro Filardi)

### Q-fp-02 · Posts minutos ou horas antes da conta existir

**Em palavras simples:** em 692 posts, o horário do post vem antes do horário de criação da conta, sempre no mesmo dia. Não é fuso, porque não há um intervalo fixo de 3 horas: varia de minutos a 16 horas. É imprecisão no horário de um dos dois registros.

**Exemplo (ilustrativo):** conta criada às 18h de 10/03; primeiro post às 9h de 10/03.

- **Evidência:**
  - 692 posts de 688 contas: 440 criadas em 2026 e 248 em 2025.
  - Diferença: mediana de 5 horas, máximo de 16,6. Nenhum post acontece em dia anterior ao do cadastro.
  - Só 10 dessas contas são das duplicadas do `usuarios.csv` (Q-usu-06).
- **Opções:**
  - **Corrigir:** puxar o horário do post para o horário do cadastro. Efeito: inventa um horário.
  - **Remover:** tirar os 692 posts. Efeito: perde posts reais do primeiro dia, justamente o momento mais importante para o churn (Aula 3: a maior parte do churn acontece no primeiro mês).
  - **Marcar:** criar `post_antes_cadastro` e adotar a regra de **usar datas de post só no nível do dia** nas variáveis do primeiro dia. Efeito: 0 linhas; 1 coluna nova.
- **Recomendação:** **marcar**. O dia está certo, e só a hora é imprecisa.
- **Status:** decidido (D-044, 03/11/2026, Pedro Filardi)

### Q-fp-03 · Grafias diferentes do mesmo post

**Exemplo real do arquivo:** "treino de força feito" (3.389), "treino de forca feito" (638) e "treino de força feito 💪" (91), entre 426 grafias.

- **Evidência:** 31.620 textos distintos viram 11.637 depois de normalizar; 42,9% dos posts diferem da grafia mais comum.
- **Opções:**
  - **Corrigir:** sobrescrever pela grafia mais comum. Efeito: 51.146 textos alterados; perde emoji e tom.
  - **Remover:** não se aplica.
  - **Marcar:** criar `texto_norm` só para contar e agrupar; a IA lê o original, com emoji. Efeito: 0 linhas; 1 coluna nova.
- **Recomendação:** **marcar**, pela mesma regra das D-007 e D-042.
- **Status:** decidido (D-045, 03/11/2026, Pedro Filardi)

## Já decidido

- **D-002 (corte):** a Q-fp-01 aplica a regra.
- **D-007 e D-042:** a mesma regra de texto normalizado (Q-fp-03).

## O que não é problema

- **Privacidade:** 0 posts com e-mail, telefone, CPF, @perfil, link ou "meu nome é".
- **Unicidade:** 0 posts repetidos e 0 posts da mesma conta no mesmo instante.
- **Curtidas:** de 0 a 38, média de cerca de 7 por post, estável entre 2025 e 2026. Os 258 posts com 0 curtida e os 34 acima de 30 estão dentro do esperado.
- **Horário:** picos às 11h e às 19-20h, e nenhum post de madrugada (0h às 4h). Coerente com "logo depois do treino".
- **Quem posta:** 97,2% dos posts são de contas que já pagaram alguma vez.

## Observação para a análise (não é problema de qualidade)

**331 posts falam em cancelar, parar ou desistir.** É um sinal direto que só o texto traz. Vale como teste para o objetivo 5: o texto melhora a previsão?

## Números conferidos à mão

Contei com o leitor de CSV do Python e com contagem direta:
1. **Linhas:** 119.309. Bate com o dicionário.
2. **Posts depois do corte:** 122. Bate com o inventário.
3. **Posts com 0 curtida:** 258.
