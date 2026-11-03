# Qualidade: `tickets_suporte.csv`

Uma linha por chamado ao suporte · 4.422 linhas · 8 colunas · de 01/07/2025 a 30/09/2026 · avaliado em 03/11/2026 com a skill `qualidade-dados` · medidas em [tickets_suporte_evidencias.md](tickets_suporte_evidencias.md)

## Resumo

O que está bem:
- **Privacidade:** nenhum texto traz e-mail, telefone, CPF, número de cartão ou nome declarado. O texto pode ir para a IA no objetivo 5 sem expor ninguém.
- **Ligações:** todas as contas existem, todas são de pagantes, e nenhum chamado foi aberto antes do cadastro.
- **Situação e data:** coerentes. Todo `resolvido` tem data; nenhum `aberto` ou `sem_resposta` tem; nenhuma resolução é anterior à abertura.

Os problemas são três:
1. **A categoria do atendente é pouco confiável:** o mesmo texto recebe categorias diferentes em 1 de cada 3 chamados.
2. **41 resoluções acontecem depois do corte.**
3. **Os textos têm erros de digitação** que fragmentam as contagens.

**Situação em 03/11/2026:** os 3 problemas foram decididos (D-040 a D-042 no `DECISOES.md`), para aplicar numa cópia em `dados/processados/`. Os brutos não mudam.

## Problemas para decidir

| ID | Dimensão | Coluna | O que está errado | Por que importa para o case |
|---|---|---|---|---|
| Q-tk-01 | Consistência | `categoria_atendente` | Em 33,8% dos chamados (1.383 de 4.090 com texto repetido), a categoria difere da mais comum dada ao mesmo texto | Contar "quantos chamados de cobrança" pela categoria erra 1 em cada 3; e o tema do chamado pode ser um sinal de churn (objetivos 2 e 5) |
| Q-tk-02 | Temporalidade | `status`, `resolvido_em` | 41 chamados abertos em setembro foram resolvidos entre 01/10 e 07/10, depois do corte | Em 30/09 eles estavam abertos. Usar "resolvido" seria ver o futuro (D-002) |
| Q-tk-03 | Consistência | `texto_cliente` | 303 textos distintos viram 195 depois de normalizar; 529 chamados (12,0%) diferem da grafia mais comum só por acento ou letra trocada | Contagens por texto ficam fragmentadas |

### Q-tk-01 · A categoria do atendente varia para o mesmo problema

**Em palavras simples:** quem abre o chamado escreve o problema; o atendente escolhe uma categoria. Para a mesma frase, atendentes diferentes escolhem categorias diferentes.

**Exemplo real do arquivo:** "GPS parou de funcionar no meu Android" aparece como técnico, mas também como conteúdo, cancelamento, cobrança, conta e dúvida geral. "Corrida registrada com distância zerada" aparece como técnico, cobrança e dúvida geral.

- **Evidência:**
  - Dos 4.090 chamados cujo texto aparece pelo menos 5 vezes, 1.383 (33,8%) têm uma categoria diferente da mais comum para aquele texto.
  - Os textos mais inconsistentes: "meu pix automático não passou" (52% fora da categoria mais comum), "a rota sai toda torta" (50%) e "corrida registrada com distância zerada" (47%).
- **Opções:**
  - **Corrigir:** sobrescrever a categoria pela mais comum do texto. Efeito: 1.383 categorias alteradas; perde-se a escolha original.
  - **Remover:** tirar a coluna. Efeito: perde-se a informação, mesmo ruidosa.
  - **Marcar:** manter a categoria original e criar `categoria_texto`, derivada do texto do cliente: por enquanto, a categoria mais comum para o mesmo texto normalizado; no objetivo 5, a classificação pela IA, conferida contra uma amostra rotulada à mão. Regra: **análises por tema usam `categoria_texto`**. Efeito: 0 linhas; 1 coluna nova.
- **Recomendação:** **marcar**. O texto do cliente é a fonte mais estável; a categoria original fica para comparação e auditoria.
- **Status:** decidido (D-040, 03/11/2026, Pedro Filardi)

### Q-tk-02 · Chamados resolvidos depois do corte

**Em palavras simples:** 41 chamados abertos no fim de setembro só foram resolvidos no começo de outubro. No dia do corte (30/09), eles ainda estavam abertos.

**Exemplo (ilustrativo):** chamado aberto em 28/09, resolvido em 03/10. O arquivo diz `resolvido`, mas em 30/09 a pessoa ainda esperava resposta.

- **Evidência:** 41 chamados, todos abertos em setembro/2026, com `resolvido_em` entre 01/10 e 07/10.
- **Opções:**
  - **Corrigir:** na cópia processada, criar `status_no_corte`: os 41 ficam `aberto`, e a data de resolução não entra nas variáveis. Efeito: 0 linhas; 41 situações ajustadas; os originais preservados.
  - **Remover:** tirar os 41 chamados. Efeito: perde-se o fato real de que a pessoa abriu um chamado em setembro.
  - **Marcar:** só marcar `resolvido_apos_corte`. Efeito: o status original continua "vendo o futuro".
- **Recomendação:** **corrigir**, com a situação como era em 30/09, pela regra da D-002.
- **Status:** decidido (D-041, 03/11/2026, Pedro Filardi)

### Q-tk-03 · Erros de digitação no texto

**Exemplo real do arquivo:** "quero o reembolso, não uso mais" (241) e "quero o reembolso, nao uso mais" (49), além de outras 9 grafias com letras trocadas.

- **Evidência:** 303 textos distintos viram 195 depois de normalizar (minúsculas, sem acento, sem pontuação); 529 chamados (12,0%) usam uma grafia diferente da mais comum.
- **Opções:**
  - **Corrigir:** sobrescrever pela grafia mais comum. Efeito: 529 textos alterados; perde-se o original.
  - **Remover:** não se aplica.
  - **Marcar:** criar `texto_norm` só para contar e agrupar. A IA lê o original. Efeito: 0 linhas; 1 coluna nova.
- **Recomendação:** **marcar**, como no onboarding (D-007).
- **Status:** decidido (D-042, 03/11/2026, Pedro Filardi)

## Já decidido

- **D-002 (corte):** 0 chamados abertos depois de 30/09/2026 (Q-tk-02 trata das resoluções).
- **D-007:** a mesma regra de texto normalizado do onboarding (Q-tk-03 a aplica aqui).

## O que não é problema

- **Privacidade:** 0 textos com e-mail, telefone, CPF, número de cartão ou "meu nome é".
- **Situação × data:** 100% coerentes. 2.917 `resolvido` com data; 981 `aberto` e 524 `sem_resposta` sem data. Resolução em 3 dias na mediana, máximo de 19.
- **Unicidade:** 0 chamados repetidos (mesma conta, mesmo texto, mesmo dia).
- **Ligações:** 0 contas inexistentes; 0 chamados antes do cadastro; 100% de pessoas que já pagaram alguma vez.

## Observação para a análise (não é problema de qualidade)

**Em 2026, o suporte deixou mais chamados sem solução:**
- **Abertos:** 25,7% em 2026, contra 12,6% em 2025.
- **Sem resposta:** 13,4% em 2026, contra 7,6% em 2025.

Os chamados não resolvidos têm idade mediana de 130 dias, e 10% passam de 340 dias. Pode ser piora real do atendimento ou chamados esquecidos sem fechamento no sistema: o arquivo não permite distinguir. Vale como **hipótese para o objetivo 2** (por que o churn subiu em 2026): testar se quem teve chamado sem resposta sai mais.

## Números conferidos à mão

Contei com o leitor de CSV do Python e com contagem direta:
1. **Linhas:** 4.422. Bate com o dicionário.
2. **`resolvido`:** 2.917.
3. **`resolvido_em` vazio:** 1.505 (981 abertos + 524 sem resposta).
