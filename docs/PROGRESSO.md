# Onde estamos: projeto Vitaliza (grupo 05)

Atualizado em 03/11/2026.

## Em uma frase

**A base está limpa, conferida e montada.** Avaliamos os 12 arquivos do data room, registramos 51 decisões de limpeza (cada uma com motivo e efeito nos números) e montamos a base integrada no corte de 30/09/2026. Ela bate com todos os números do enunciado e da Aula 2. Os arquivos originais nunca foram alterados.

Com isso, **o que a Aula 2 pede para a entrega de 13/11 está pronto**: a base integrada no corte e o registro de decisões.

---

## O que foi feito

1. **Repositório organizado no GitHub:** pastas, regras do projeto ([AGENTS.md](../AGENTS.md)), registro de decisões ([DECISOES.md](../DECISOES.md)) e guia para configurar a máquina ([CONFIGURAR_MAQUINA.md](CONFIGURAR_MAQUINA.md)).
2. **Inventário dos arquivos** comparado com o dicionário de dados ([saidas/inventario.md](../saidas/inventario.md)). O data room está completo: os 12 arquivos têm as linhas e colunas que o dicionário descreve.
3. **Skill de qualidade de dados** ([.claude/skills/qualidade-dados](../.claude/skills/qualidade-dados/SKILL.md)). Segue o método da Aula 2:
   - avalia cada arquivo nas **5 dimensões** (completude, validade, consistência, unicidade e temporalidade);
   - transforma cada problema numa decisão de **corrigir, remover ou marcar**;
   - registra a escolha no `DECISOES.md`.

   Funciona no Claude Code e, lendo o arquivo, no Codex ou em outra IA.
4. **Os 12 arquivos avaliados**, com um relatório por arquivo em [saidas/qualidade/](../saidas/qualidade/).
5. **Limpeza aplicada** ([src/limpeza.py](../src/limpeza.py)). O script lê os originais, aplica as 51 decisões e grava a cópia limpa. A conferência de cada número está em [saidas/limpeza_conferencia.md](../saidas/limpeza_conferencia.md).
6. **Base integrada no corte** ([src/base_integrada.py](../src/base_integrada.py)): uma linha por assinante ativo em 30/09, com 49 informações. Resumo em [saidas/base_integrada.md](../saidas/base_integrada.md).

## Os números que provam que a base está certa

| O que conferimos | Nossa base | Referência |
|---|---|---|
| Assinantes pagantes ativos em 30/09/2026 | 14.753 | Enunciado: 14.753 |
| Plano anual / mensal | 57,5% / 42,5% | Enunciado: 57% / 43% |
| App Store / Google Play / cartão / Pix | 36,6% / 33,6% / 20,3% / 9,5% | Enunciado: os mesmos |
| Faturamento de setembro/2026 (bruto aprovado → líquido) | R$ 492.571,70 → R$ 436.442,35 | Aula 2, slide 9: R$ 492.572 → R$ 436.442 |
| Treinos em dobro (app e relógio) | 9.383 | Aula 2, slide 34 |
| Distâncias acima de 200 km / treinos de 0 minuto | 951 / 3.649 | Aula 2, slide 32 |
| Mês sem treino: média de minutos em dez/2025 → jan/2026 | 265 → 118 min | Aula 2, slide 35 |

## O que cada arquivo tinha de errado (resumo)

| Arquivo | Principal problema | O que decidimos | Relatório |
|---|---|---|---|
| Onboarding | 30% dos "objetivos" estão vazios ou são "nada", "x", "asdf", emoji | Viram vazio, com uma marca de "não respondeu" | [onboarding](../saidas/qualidade/onboarding.md) |
| Eventos de assinatura | As lojas gravam no horário de Londres: 753 eventos caem no mês errado | Tudo convertido para o horário de Brasília | [eventos](../saidas/qualidade/eventos_assinatura.md) |
| Assinaturas | 60 contas internas não pagam; só há "sobreviventes" de antes de jul/2024; é uma foto de 01/10 | Contas internas fora das métricas; churn só a partir de jul/2024; a foto nunca serve para prever | [assinaturas](../saidas/qualidade/assinaturas.md) |
| Usuários | Cidade escrita de 36 jeitos; nascimentos em 1900; 959 pessoas com duas contas; 119 contas "do futuro" | Padronização; datas falsas viram vazio; código de pessoa; as 119 saem | [usuarios](../saidas/qualidade/usuarios.md) |
| Pagamentos | 1.941 cobranças gravadas duas vezes; valores como texto ("R$ 34,90") | Cópias removidas, valores convertidos (fecha com a aula) | [pagamentos](../saidas/qualidade/pagamentos.md) |
| Uso mensal | Em 2025 quem não treinou não aparece; em 2026 aparece com zero | Painel padronizado: uma linha por assinante ativo por mês | [uso_mensal](../saidas/qualidade/uso_mensal.md) |
| Treinos (atividades) | Treinos em dobro, distâncias de 10 mil km, Garmin no horário de Londres, tipos em inglês | Distâncias e durações recalculadas pelo ritmo; cópias e fuso corrigidos | [atividades](../saidas/qualidade/atividades.md) |
| Campanha de agosto | O sorteio foi bem feito: os 4 grupos eram iguais antes | Regra para medir o efeito: grupo inteiro contra o controle, pela saída | [campanha](../saidas/qualidade/campanha_ago26.md) |
| Amizades | 273 relações com data depois do corte | Removidas | [amizades](../saidas/qualidade/amizades.md) |
| Chamados de suporte | A categoria do atendente varia para o mesmo problema em 1 de cada 3 chamados | Nova categoria tirada do texto do cliente | [tickets](../saidas/qualidade/tickets_suporte.md) |
| Posts | 122 posts depois do corte | Removidos | [posts](../saidas/qualidade/feed_posts.md) |
| Pesquisa de saída | O motivo marcado não combina com o comentário; só responde quem cancela pelo site | Motivo revisado com "objetivo cumprido"; nunca generalizar | [pesquisa](../saidas/qualidade/pesquisa_saida.md) |

## Achados que já ajudam nas próximas etapas

Ainda não são conclusões. São pistas para testar:

- **15% dos assinantes já tinham desligado a renovação em 30/09** (2.250 pessoas). Eles vão sair, a não ser que algo mude. Precisamos decidir se entram no modelo ou numa regra à parte.
- **"Objetivo cumprido" é um motivo de saída forte e escondido.** Na pesquisa, cerca de 190 pessoas saíram depois de fazer a prova ou a maratona, mas marcaram "preço" ou "outro" porque essa opção não existia. Desconto não segura essa pessoa; um novo desafio talvez segure.
- **O suporte deixou o dobro de chamados sem solução em 2026** (25,7% abertos, contra 12,6% em 2025). É uma hipótese para explicar a subida do churn em 2026.
- **58% dos cartões recusados são recuperados** numa nova tentativa, em cerca de 4 dias. Ajuda a separar o churn voluntário do involuntário.
- **A queda de uso na virada de 2025 para 2026 é falsa:** é mudança no jeito de registrar, não pessoas treinando menos.
- **331 posts falam em cancelar, parar ou desistir:** um sinal que só o texto mostra (objetivo 5).
- **A campanha de agosto foi bem sorteada.** Dá para medir de verdade qual mensagem segura cada tipo de cliente (objetivo 6).

## Transparência: erros que corrigimos no caminho

Seguindo a regra da aula, nenhuma decisão foi apagada. As erradas ganharam o status "substituída", e uma nova decisão explica a correção:
- **D-016 → D-023:** as 42 assinaturas "antes do cadastro" eram contas internas, e não assinantes reais.
- **D-027 → D-051:** as retentativas reais de cartão são 1.881, e não 54.

## Como trazer tudo isso para o seu computador

Abra a sua IA (Claude Code, Codex, Cursor ou um chat como ChatGPT ou Claude) e cole o texto abaixo. Ela faz os passos com você.

```text
Quero atualizar o projeto do grupo Vitaliza no meu computador. A pasta do projeto é <<ex.: C:\Projetos\MBA\vitaliza_grupo_05>>.
Explique cada passo em português simples. Se você não consegue rodar comandos no meu computador, me diga exatamente o que digitar, um passo por vez, e espere eu colar o resultado.

1. Entre na pasta do projeto e veja se eu tenho alterações minhas ainda não salvas (git status). Se tiver, me mostre quais são e pergunte o que fazer antes de seguir. Não descarte nada.
2. Baixe as novidades do grupo (git pull). Se aparecer conflito, pare e me explique; não escolha nada sozinho.
3. Instale as bibliotecas novas, se houver: use o Python do .venv com pip install -r requirements.txt.
4. Gere a cópia limpa e a base, com o Python do .venv:
   python src/limpeza.py
   python src/base_integrada.py
   (no Windows, o Python do .venv é .venv\Scripts\python.exe; no Mac, .venv/bin/python). Leva alguns minutos.
5. Abra saidas/base_integrada.md e me confirme se aparece "Assinantes: 14.753".
6. Não envie nada para o GitHub (sem commit, sem push).

No final, me diga em 3 frases o que mudou no projeto.
```

**Para avaliar a qualidade de um arquivo**, peça à sua IA:
- no Claude Code: *"use a skill qualidade-dados no arquivo X"*;
- no Codex ou em outra IA: *"leia o arquivo .claude/skills/qualidade-dados/SKILL.md e siga o passo a passo para o arquivo X"*.

## Próximos passos e pendências

| O quê | Para quê | Status |
|---|---|---|
| Montar a base num corte anterior (ex.: 31/07/2026) e marcar quem saiu nos 60 dias seguintes | Treinar o modelo de churn (objetivo 4). A saída depois de 30/09 ainda não está nos dados | A fazer |
| Decidir o que fazer com os 2.250 que já anunciaram a saída | Evitar que o modelo "acerte o óbvio" | Decisão do grupo |
| Explicar a subida do churn em 2026, testando preço, canal, suporte e uso | Objetivo 2 | A fazer |
| Segmentação (clusterização) | Objetivo 3 | A fazer |
| Ler textos e mapas de calor com IA, conferindo contra uma amostra feita à mão | Objetivo 5 | A fazer |
| Perguntar ao professor: a diferença entre o resumo de uso e o detalhe de treinos (D-029) é proposital? | Saber qual fonte é a "verdade" para 2025 | Pendente |
| Tarefa da Aula 3 (negócios): 2 segmentos validados | Entrega de 03/11 | Verificar com o grupo |
