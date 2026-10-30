# Qualidade: `assinaturas.csv`

Uma linha por assinatura (na prática, uma por pessoa que já pagou) · 32.643 linhas · 9 colunas · retrato de 01/10/2026 · avaliado em 29/10/2026 com a skill `qualidade-dados` · medidas em [assinaturas_evidencias.md](assinaturas_evidencias.md)

## Resumo

O arquivo é **coerente com o histórico de eventos em 100% dos casos**: situação, plano, canal, renovação, data de início e motivo da saída batem com `eventos_assinatura.csv`. Também bate com os números do enunciado:
- 14.753 pagantes ativos;
- 8.540 ativos no início de 2025;
- cerca de 4.500 no fim de 2023.

Os problemas não são de dado errado, mas de **como usar o arquivo sem tirar conclusões falsas**:
1. **60 contas internas** (`cortesia`) não são pagantes.
2. **Só estão as assinaturas que existiam a partir de julho de 2024.** Quem saiu antes disso sumiu do arquivo.
3. É uma **foto de 01/10**, que não serve para descrever o passado nem para alimentar um modelo de previsão.
4. **42 assinaturas começam antes do cadastro da conta.** O erro está no cadastro, não aqui.

**Situação em 29/10/2026:** os 4 problemas foram decididos (D-013 a D-016 no `DECISOES.md`), todos para aplicar numa cópia em `dados/processados/`. Os brutos não mudam. A limpeza ainda não foi feita.

## Problemas para decidir

| ID | Dimensão | Coluna | O que está errado | Por que importa para o case |
|---|---|---|---|---|
| Q-ass-01 | Validade | `plano_atual`, `canal_cobranca` | 60 assinaturas `cortesia` / `interno`, ativas, sem nenhum evento e sem cobrança; o dicionário só prevê `mensal`/`anual` | Contadas como assinantes, inflam a base de 14.753 para 14.813 e distorcem o churn e a receita |
| Q-ass-02 | Completude · Temporalidade | arquivo inteiro | Nenhuma assinatura terminou antes de 07/07/2024. As 5.200 iniciadas antes de 07/2024 são só as que sobreviveram até lá | Medir churn por ano de entrada ou por tempo de casa daria uma conclusão falsa: os clientes antigos pareceriam muito fiéis só porque os que saíram foram apagados |
| Q-ass-03 | Temporalidade (vazamento) | `status_atual`, `renovacao_automatica`, `data_fim`, `motivo_fim` | Descrevem o dia 01/10/2026, não o passado | Usar essas colunas para prever saída é "colar a resposta": o modelo veria quem já saiu |
| Q-ass-04 | Validade · Consistência | `inicio` × `usuarios.data_cadastro` | 42 assinaturas ativas começam antes do cadastro da conta (de 8 a 612 dias antes; mediana de 335) | Cálculos de "dias entre cadastro e assinatura" ficam negativos |

### Q-ass-01 · As 60 contas de cortesia

**Em palavras simples:** são contas internas da Vitaliza, provavelmente funcionários ou testes. Usam o app sem pagar.

**Exemplo:** uma conta com plano `cortesia`, canal `interno`, situação `ativa`. Nunca teve uma cobrança nem um evento de assinatura. No `usuarios.csv`, o canal de aquisição dela também é `interno`.

- **Evidência:**
  - Todas as 60 estão ativas e sem eventos.
  - Somadas aos 14.753 pagantes, dão os 14.813 "ativos" do arquivo.
  - O enunciado fala em 14.753 pagantes.
- **Opções:**
  - **Corrigir:** não há o que corrigir; o dado está certo, só não é pagante.
  - **Remover:** tirar as 60 da cópia processada. Efeito: 32.643 → 32.583 assinaturas.
  - **Marcar:** criar a coluna `pagante` (sim/não) e excluir os `não` de toda conta de assinantes, churn e receita. Efeito: 32.643 → 32.643 linhas; pagantes ativos = 14.753.
- **Recomendação:** **marcar**. Fica registrado quem são, e nenhuma métrica de negócio as conta.
- **Status:** decidido (D-013, 29/10/2026, Pedro Filardi)

### Q-ass-02 · Só os sobreviventes de antes de julho de 2024

**Em palavras simples:** o sistema guarda só as assinaturas que ainda existiam em julho de 2024, quando começa o histórico de eventos. Quem assinou em 2021 e cancelou em 2023 não aparece.

**Exemplo:** das assinaturas de 2021 que estão no arquivo, 34% ainda estão ativas cinco anos depois. Parece uma fidelidade incrível, mas é só porque as de 2021 que saíram antes de 2024 foram apagadas. É como julgar a segurança de um avião olhando só os que voltaram.

- **Evidência:**
  - A data de fim mais antiga é 07/07/2024.
  - Das 5.200 assinaturas iniciadas antes de 07/2024, 0 terminaram antes dessa data.
  - Os ativos pela foto batem com o enunciado: 4.510 no início de 2024 (enunciado: cerca de 4.500) e 8.540 no início de 2025 (enunciado: 8.540).
- **Opções:**
  - **Corrigir:** impossível; as assinaturas que faltam não existem em nenhum arquivo.
  - **Remover:** tirar as 5.200 iniciadas antes de 07/2024. Efeito: 32.643 → 27.443; tira também 1.462 assinantes ativos reais, 1 em cada 10.
  - **Marcar:** criar a coluna `inicio_antes_historico` (sim/não) e adotar uma regra: **taxas de churn só a partir de 07/2024**, e análises por ano de entrada ou tempo de casa sempre com a ressalva. Efeito: 0 linhas; 1 coluna nova.
- **Recomendação:** **marcar**. A série de churn que o case pede (2025 e 2026) está inteira no período coberto. O cuidado vale para o "tempo de casa" no modelo e nos segmentos.
- **Status:** decidido (D-014, 29/10/2026, Pedro Filardi)

### Q-ass-03 · Uma foto de 01/10, não um filme

**Em palavras simples:** cada vez que algo muda, o sistema apaga o valor antigo e escreve o novo. O arquivo mostra só como tudo estava em 01/10.

**Exemplo:** uma assinante desligou a renovação em 15/09. No arquivo, `renovacao_automatica` = `nao`. Se usarmos essa coluna para "prever" quem sai nos próximos 60 dias, o modelo vai parecer genial, porque está lendo a resposta, e na vida real não terá esse aviso a tempo de agir.

- **Evidência:**
  - O dicionário descreve o arquivo como retrato de 01/10/2026.
  - As quatro colunas mudam com o tempo.
  - A situação em qualquer data passada se reconstrói pelos eventos: em 30/09 dá exatamente 14.753 ativos.
- **Opções:**
  - **Corrigir:** não se aplica.
  - **Remover:** tirar as quatro colunas da cópia processada. Efeito: 0 linhas; perde o motivo da saída, que já completou o D-011.
  - **Marcar:** manter as colunas, com nome que avise (prefixo `retrato_0110_`), e uma regra: **nunca usar como variável de previsão**; situação no passado só pelos eventos. Efeito: 0 linhas; 4 colunas renomeadas.
- **Recomendação:** **marcar**. O nome da coluna lembra o risco a quem for usá-la, inclusive a IA dos colegas.
- **Status:** decidido (D-015, 29/10/2026, Pedro Filardi)

### Q-ass-04 · Assinatura antes do cadastro

**Em palavras simples:** 42 pessoas aparecem assinando antes de criar a conta, o que é impossível.

**Exemplo real do arquivo:** uma assinatura começa em 10/01/2025, mas a conta aparece criada em 22/12/2025, 346 dias depois.

- **Evidência:**
  - Todas as 42 estão ativas.
  - A data de início bate com o evento `assinatura_iniciada` em 100% dos casos com evento. **O errado é o cadastro.**
  - Os cadastros dessas contas são de 2025 (23) e 2026 (19). Provavelmente o cadastro foi regravado, por exemplo numa troca de celular ou de e-mail.
- **Opções:**
  - **Corrigir:** usar a data de início como limite e trocar o cadastro pela data do início. Efeito: 42 datas de cadastro alteradas; a decisão é do `usuarios.csv`.
  - **Remover:** tirar as 42. Efeito: −42 assinantes ativos reais.
  - **Marcar:** criar `cadastro_inconsistente` e decidir a correção na avaliação de `usuarios.csv`. Efeito: 0 linhas; 1 coluna nova.
- **Recomendação:** **marcar agora** e corrigir o cadastro quando avaliarmos o `usuarios.csv`, onde já há outros problemas de data, como cadastros em 2027.
- **Status:** decidido (D-016, 29/10/2026, Pedro Filardi)

## Já decidido

- **D-002 (corte):** 0 datas depois de 30/09/2026.
- **D-011:** este arquivo é a fonte do motivo da saída usado nos eventos. A concordância é de 100%.

## O que não é problema

- **Unicidade:** 32.643 assinaturas de 32.643 pessoas diferentes, sem repetição. Ninguém saiu e voltou, embora o dicionário diga que isso pode acontecer.
- **Coerência com os eventos:**
  - situação (ativa ou expirada) bate em 100%;
  - plano e canal batem em 100%;
  - renovação ligada ou desligada bate com o último aviso das lojas e do site em 100%;
  - início bate com `assinatura_iniciada` em 27.383 de 27.383.
- **Valores de `status_atual` não descritos no dicionário** (`ativa`, `expirada`, `reembolsada`): o significado é claro e coerente com `motivo_fim`. As 72 `reembolsada` são exatamente as 72 com motivo `reembolso`.
- **Vazios em `data_fim` e `motivo_fim`:** 14.813, exatamente as assinaturas ativas. Vazio esperado.

## Números conferidos à mão

Contei com o leitor de CSV do Python, sem pandas:
1. **Linhas:** 32.643. Bate com o dicionário.
2. **Cortesias:** 60.
3. **Ativas pagantes (sem cortesia):** 14.753. Bate com o enunciado e com a reconstrução pelos eventos.
