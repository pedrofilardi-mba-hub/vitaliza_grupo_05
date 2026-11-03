# Conferência da limpeza

Gerado por `src/limpeza.py` em 03/11/2026 20:52. Cada linha compara o efeito registrado no `DECISOES.md` com o que o script obteve. A cópia limpa fica em `dados/processados/` (fora do Git pelo tamanho, D-050; recriada por este script); os brutos não foram alterados. Quando o número difere do registrado, a coluna Esperado explica por quê.

| Arquivo | Decisão | Medida | Esperado | Obtido |
|---|---|---|---|---|
| usuarios | D-021 | contas | 64.948 → 64.829 | 64948 → 64829 |
| usuarios | D-017 | cidades fora da grafia oficial (antes da D-021) | 13.601 | 13601 |
| usuarios | D-018 | sexo F / M / não informado (antes da D-021) | 32.507 / 29.299 / 3.142 | {'F': 32507, 'M': 29299, 'nao_informado': 3142} |
| usuarios | D-017 | cidades distintas | 13 | 13 |
| usuarios | D-017 | cidades reescritas (depois da D-021) | 13.601 menos as das 119 contas removidas | 13572 |
| usuarios | D-018 | sexo F / M / não informado (depois da D-021) | menos as 119 contas removidas | {'F': 32454, 'M': 29240, 'nao_informado': 3135} |
| usuarios | D-019 | sistemas | android, ios | ['android', 'ios'] |
| usuarios | D-020 | nascimentos falsos | 606 | 606 |
| usuarios | D-020 | contas menores de 18 | 1 | 1 |
| usuarios | D-022 | pessoas distintas | 63.989 antes da D-021 | 63989 |
| assinaturas | D-013 | ativas pagantes | 14.753 | 14753 |
| assinaturas | D-014 | iniciadas antes de 07/2024 | 5.200 | 5200 |
| assinaturas | D-023 | coluna cadastro_inconsistente criada? | não | não |
| eventos | D-009 | horários convertidos | 186.323 | 186323 |
| eventos | D-009 | eventos que mudam de mês | 753 | 753 |
| eventos | D-010 | eventos em fase teste | 72.873 | 72873 |
| eventos | D-011 | expirações com motivo | 17.830 | 17830 |
| eventos | D-012 | eventos em sequência atípica | 611 | 611 |
| eventos | D-012 | renovações fora do ciclo | 1.154 | 1154 |
| eventos | D-012 | assinantes ativos em 30/09 | 14.753 | 14753 |
| pagamentos | D-025 | valores convertidos de texto | 19.750 | 19750 |
| pagamentos | D-024 | linhas | 165.548 → 163.607 | 165548 → 163607 |
| pagamentos | D-024 | cobranças aprovadas | 159.989 | 159989 |
| pagamentos | D-051 | retentativas reais (corrige a D-027) | 1.881 | 1881 |
| pagamentos | D-024/25/26 | faturamento set/2026 (bruto aprovado / líquido) | R$ 492.572 / R$ 436.442 (Aula 2) | R$ 492,571.70 / R$ 436,442.35 |
| onboarding | D-003 | objetivo preenchido | 44.694 | 44694 |
| onboarding | D-005 | nível não informado | 4.513 | 4513 |
| onboarding | D-006 | dias por semana: preenchidos / vazios / fora de 1-7 | 57.561 / 6.368 / 0 | 57561 / 6368 / 0 |
| atividades | D-030 | horários do Garmin ajustados | 207.954 | 207954 |
| atividades | D-030 | treinos depois do corte | 0 | 0 |
| atividades | D-031 | pares app × relógio | 9.383 | 9383 |
| atividades | D-031 | treinos | 1.254.475 → 1.245.092 | 1254475 → 1245092 |
| atividades | D-032 | tipos distintos | 7 | 7 |
| atividades | D-033 | distâncias recalculadas | 951 (menos as que estavam em cópias do app removidas na D-031) | 944 |
| atividades | D-034 | durações recalculadas / marcadas | 1.972 / 1.677 (menos as cópias do app removidas na D-031) | 1961 / 1670 |
| atividades | D-035 | treinos com GPS falho / distâncias apagadas | 14.779 / 7.455 (menos as cópias do app removidas na D-031) | 14779 / 7454 |
| uso_mensal | D-028 | linhas do painel em jan/2025 / set/2026 | ≈ 8,5 mil / ≈ 15,4 mil | 8745 / 15470 |
| uso_mensal | D-028 | assinantes sem treino no mês (2025 / 2026) | parecidos nos dois anos | 15.2% / 13.7% |
| uso_mensal | D-028 | linhas do resumo original mantidas | 591.662 | 591662 |
| campanha | D-036 | sorteados / em teste no envio | 14.120 / 48 | 14120 / 48 |
| campanha | D-037 | cliques (soma do booleano) | 1.604 | 1604 |
| amizades | D-039 | relações | 113.480 → 113.207 | 113480 → 113207 |
| feed_posts | D-043 | posts | 119.309 → 119.187 | 119309 → 119187 |
| feed_posts | D-044 | posts antes do horário de cadastro | 692 | 692 |
| tickets | D-040 | categoria do texto ≠ do atendente | ≈ 1/3 | 32.6% |
| tickets | D-041 | resolvidos depois do corte (viram abertos no corte) | 41 | 41 |
| pesquisa | D-046 | respostas com motivo "objetivo cumprido" | ≈ 190 na avaliação; a regra de palavras-chave é provisória (IA no objetivo 5) | 230 |
| pesquisa | D-048 | respostas / pessoas | 643 / 641 | 643 / 641 |
