# AGENTS.md: instruções para agentes de IA neste repositório

Projeto do grupo 05 no Módulo 2 do MBA em IA e Dados para Negócios (Inteli): o case **Vitaliza**, sobre o churn de um app de treino por assinatura.

## O desafio, em uma frase

Usar a base da Vitaliza para responder **quem vai sair, em quem vale a pena agir, com qual mensagem e quanto isso rende**. A resposta é um sistema de cinco peças: dados → extração com IA generativa → previsão de churn → regra de decisão → mensagem gerada por IA.

Referências do case: *Vitaliza: enunciado do case* e *Vitaliza: dicionário de dados*. Os PDFs ficam em `docs/case/`, na máquina de cada integrante, e não sobem para o repositório.

## Estrutura

| Pasta | Conteúdo |
|---|---|
| `dados/brutos/` | Arquivos do data room como foram entregues. **Somente leitura, fora do git.** |
| `dados/processados/` | Tabelas limpas e integradas, geradas pelos scripts de `src/` |
| `src/` | Código reutilizável: limpeza, integração, features, modelos |
| `notebooks/` | Análises exploratórias e apresentação de resultados |
| `saidas/` | Gráficos, tabelas e listas finais (ex.: ranking de risco, regra de contato) |
| `docs/` | Documentação e material de entrega |
| `DECISOES.md` | Registro das decisões do grupo |

## Regras de dados

- **Nunca altere `dados/brutos/`.** Toda limpeza gera um arquivo novo em `dados/processados/`, a partir de um script versionado.
- **Data de corte: 30/09/2026.** Nenhuma variável do modelo pode usar informação posterior ao corte. Isso vale também para `assinaturas.csv`, que é um retrato de 01/10/2026 e não um histórico. O alvo é a saída nos 60 dias seguintes, até 29/11/2026.
- **Situação histórica de um assinante:** reconstrua sempre a partir de `eventos_assinatura.csv`, que começa em 01/07/2024, e não do status atual.
- **Chave de integração:** `user_id` liga todos os arquivos.
- **Fusos horários:** em `eventos_assinatura.csv`, as lojas gravam em UTC (sufixo `Z`) e o site grava no horário de Brasília. Converta tudo para Brasília antes de contar por dia ou por mês.
- **Problemas de qualidade já vistos:**
  - Valores em `34.90` e em `R$ 34,90`.
  - `sexo` e `sistema` escritos de vários jeitos.
  - `dias_por_semana` em texto livre.
  - Tipos de treino em português e em inglês (`corrida` e `run`).
  - Distâncias absurdas em `atividades.parquet`.
  - Plano `cortesia`, canal `interno`, que não é pagante.
- **Experimento:** `campanha_ago26.csv` é o único sorteio da base, a fonte para medir o uplift. Compare cada grupo com o `controle` pela saída, não pela abertura nem pelo clique.
- **Dados pessoais:** `usuarios.csv` traz e-mail e data de nascimento. Não envie esses campos a APIs de LLM e não os grave em `saidas/`.

## IA generativa

- O custo de LLM sai do orçamento de CRM, de R$ 40.000 por mês. **Estime o custo antes de rodar em toda a base**: teste numa amostra e registre o custo por assinante.
- Cada extração tem um esquema de saída fixo (nome e formato de cada campo) e é conferida contra uma amostra rotulada à mão.
- Chaves de API ficam no `.env`, que está fora do git. Nunca no código nem nos notebooks.

## Ambiente

- Python 3.12. As bibliotecas, com as versões fixadas, estão no `requirements.txt`; o passo a passo de instalação está no `README.md`. Se precisar de uma biblioteca nova, adicione-a ao `requirements.txt` no mesmo commit.
- No Windows, ao imprimir texto com emoji (posts, tickets), use `sys.stdout.reconfigure(encoding='utf-8')`.

## Convenções

- Código, nomes de colunas e textos em português, sem acento nos identificadores (ex.: `churn_60d`, `canal_cobranca`).
- Toda decisão de método que muda um número (regra de churn, tratamento de outlier, escolha de variável, limiar de contato) vai para o `DECISOES.md`, com o motivo.
- Resultados em dinheiro usam a receita **líquida** (sem as taxas da loja ou do meio de pagamento) e só contam o efeito incremental do contato.
