---
name: qualidade-dados
description: Explora a qualidade de um arquivo do data room da Vitaliza nas cinco dimensões (completude, validade, consistência, unicidade, temporalidade), leva cada problema ao grupo como uma decisão (corrigir, remover ou marcar) e registra as decisões tomadas no DECISOES.md. Use quando pedirem para avaliar, auditar, explorar ou "olhar a qualidade" de um arquivo de dados/brutos/, antes de limpar um arquivo, ou para retomar decisões de qualidade pendentes.
---

# Qualidade de dados: problema → decisão → registro

Esta skill aplica o método da Aula 2 (Trilha de Tecnologia, 22/10/2026). Ele tem três ideias:

- **Cinco dimensões de qualidade** (Wang; Strong, 1996). Cada uma faz uma pergunta diferente ao arquivo.
- **Limpar é decidir** (Redman, 2016). Todo problema tem três saídas: **corrigir**, **remover** ou **marcar**. Cada escolha entra no `DECISOES.md` com o motivo e o efeito na contagem.
- **Conferir antes de acreditar.** O agente acelera a parte mecânica, e o grupo julga.

A skill **não limpa nada sozinha**. Ela entrega o diagnóstico, leva as escolhas ao usuário e registra o que ele decidir. A limpeza em si vem depois, só se pedirem, e segue as decisões registradas.

## Regras que não mudam

1. **Nunca altere `dados/brutos/`.** Só leitura.
2. **Mostre o plano antes de rodar** e espere aprovação, como pede o `AGENTS.md`.
3. **Não decida pelo grupo.** Recomende, mas a escolha é do usuário. "Pode seguir a sua recomendação" conta como decisão, e quem decidiu é o usuário.
4. **Nada pessoal em `saidas/`.** `email`, `data_nascimento`, `cidade` e `cep_prefixo` aparecem só como contagem. Valor de texto livre só aparece se se repete 5 vezes ou mais. O repositório é público.
5. **Não use informação posterior ao corte (30/09/2026)** para julgar o que é válido.
6. **Não repita decisões já tomadas.** Leia o `DECISOES.md` antes: o que já foi decidido para o arquivo aparece no relatório como "já decidido (D-XXX)", e não volta como pergunta.

## As cinco dimensões

| Dimensão | Pergunta | O que procurar | Exemplo da aula |
|---|---|---|---|
| **Completude** | Quanto falta, e o vazio é opcional ou é problema? | Nulos, textos só com espaços, **vazios disfarçados** (`nada`, `x`, `.`, `nao sei`, emoji), contas sem linha no arquivo. Compare com o que o dicionário marca como opcional. | `onboarding.csv`: 8,6% sem `objetivo_texto` (opcional); `nivel` (7,1%) e `dias_por_semana` (10,0%) também vazios, e o dicionário não diz que são opcionais |
| **Validade** | O valor pode existir no mundo real e no domínio do dicionário? | Fora da faixa física (treino de 10.013 km, duração zero), fora da lista de categorias, número que não converte, data impossível ou fora do período. | `atividades.parquet`: 951 treinos acima de 200 km, 3.649 com duração zero |
| **Consistência** | A mesma informação está registrada do mesmo jeito? | Grafias diferentes da mesma categoria (maiúsculas, acento, idioma), formatos de número e de data misturados, conflito entre arquivos. | `corrida` e `run` no mesmo campo `tipo` |
| **Unicidade** | Cada coisa aparece uma vez só? | Linhas repetidas, chave repetida, a mesma entidade chegando por duas fontes (com tolerância de horário e fuso). | 9.383 treinos que chegaram pelo app e pelo relógio |
| **Temporalidade** | A forma de registrar mudou com o tempo? O dado é do período certo? | Mudança de padrão entre anos ou meses (formato, vazios, zeros), datas depois do corte, fusos (UTC × Brasília), atraso de registro. | `uso_mensal.csv`: mês sem treino ausente em 2025 e com linha zerada em 2026 (a média cai de 265 para 118 minutos só por isso) |

Granularidade não é uma dimensão, mas vem antes de todas: diga sempre **o que é uma linha** do arquivo (conta, assinatura, evento, treino ou mês).

## Passo a passo

### 1. Ler o contexto

- `AGENTS.md`: regras do projeto, data de corte e fusos.
- `DECISOES.md`: decisões já tomadas, e qual é o próximo número D-XXX.
- O dicionário de dados:
  - o PDF em `docs/case/` (fica na máquina de cada um, fora do Git);
  - a especificação em código em `src/inventario.py` (`DICIONARIO`) e `src/qualidade.py` (`EXTRAS`), que traz colunas opcionais, faixas e unicidade por conta.
- `saidas/inventario.md`: o que já se sabe do arquivo.
- `saidas/qualidade/<arquivo>.md`: se existir, é uma rodada anterior. Retome as pendências em vez de recomeçar.

### 2. Mostrar o plano

Em poucas linhas, diga:
- qual arquivo será avaliado e o que é uma linha dele;
- quais checagens faz cada dimensão, incluindo as específicas desse arquivo, do passo 4;
- o que será gravado.

Espere o "ok".

### 3. Rodar as evidências

```
.venv\Scripts\python.exe src\qualidade.py <arquivo>      (Mac: .venv/bin/python src/qualidade.py <arquivo>)
```

O script grava `saidas/qualidade/<arquivo>_evidencias.md` com as medidas das cinco dimensões. Ele só mede. Se o arquivo não estiver no `DICIONARIO`, pare e avise.

### 4. Ir além do script

O script cobre o genérico. Para cada dimensão, pergunte o que é específico daquele arquivo e meça com pandas, sem alterar nada. Exemplos:
- **Consistência entre arquivos.** Por exemplo, `onboarding.como_conheceu` × `usuarios.canal_aquisicao`, ou `assinaturas.status_atual` × `eventos_assinatura`.
- **Unicidade com tolerância.** A mesma conta, o mesmo tipo e a mesma duração, com início a até 5 minutos e o fuso corrigido.
- **Temporalidade com o mês certo.** Converta UTC (`...Z`) para Brasília antes de agrupar por dia ou mês.
- **Vazio que é informação.** Não responder pode ser sinal de baixo engajamento. Compare a taxa de saída de quem respondeu e de quem não respondeu, sem tirar conclusão causal.

### 5. Conferir antes de acreditar

Antes de escrever o relatório:
- Confira **três números à mão**, com uma contagem independente do script.
- Compare as contagens com o dicionário.
- Se algum número não bater, investigue antes de seguir.
- No relatório, diga quais números foram conferidos.

### 6. Escrever o relatório de decisão

Grave `saidas/qualidade/<arquivo>.md` neste formato:

```markdown
# Qualidade: <arquivo>

<Uma linha por ___ · N linhas · data da avaliação · evidências em <arquivo>_evidencias.md>

## Resumo
3 a 5 frases: o arquivo está utilizável? Quais problemas mudam número? O que precisa de decisão?

## Problemas para decidir
| ID | Dimensão | Coluna | O que está errado (com n e %) | Por que importa para o case |
|---|---|---|---|---|
| Q-<arq>-01 | ... | ... | ... | ... |

### Q-<arq>-01 · <título curto>
- **Evidência:** números, exemplos que se repetem e onde conferir.
- **Opções:**
  - **Corrigir:** como, e o efeito na contagem (linhas e valores que mudam).
  - **Remover:** quais linhas, e o efeito na contagem (de N para M).
  - **Marcar:** qual coluna de marcação, e o efeito na contagem (nenhuma linha sai).
- **Recomendação:** a opção e o porquê, em uma ou duas frases.
- **Status:** pendente | decidido (D-XXX)

## Já decidido
Problemas deste arquivo cobertos por decisões anteriores (D-XXX).

## O que não é problema
O que parecia problema e foi descartado, com o motivo.

## Números conferidos à mão
Os três números e como foram conferidos.
```

Como recomendar:
- **Corrigir** quando o valor certo é recuperável sem ambiguidade. Exemplos: `3x` vira `3`; `Fem` vira `F`; UTC vira Brasília.
- **Remover** quando o registro é inválido, não carrega informação e tirá-lo não enviesa a base. Mostre que não enviesa: de qual grupo saem as linhas?
- **Marcar** quando há dúvida ou quando o próprio problema pode ser sinal. "Não respondeu o objetivo" pode prever churn, e apagar a linha jogaria esse sinal fora. Marcar é a opção segura quando não se sabe.
- **Não imputar a média** em variável assimétrica. Se precisar imputar, prefira a mediana e marque a linha.
- **Diga o efeito em número.** "Remove 917 linhas (1,4%)" é melhor que "remove algumas linhas".

### 7. Levar as decisões ao usuário

- Apresente o resumo e pergunte **uma decisão por problema**, com as opções e a recomendação primeiro. Se houver ferramenta de perguntas com botões, use-a, com até 4 problemas por vez.
- Aceite também: "decidir depois", que mantém o problema pendente, ou uma alternativa do usuário.
- Pergunte o nome de quem decide, se ainda não souber. Ele vai no campo Responsável.

### 8. Registrar no DECISOES.md

Para cada problema decidido, acrescente **uma** entrada no fim do `DECISOES.md`, com o próximo número livre:

```markdown
## D-XXX: <arquivo> · <título curto do problema>
- Data: AAAA-MM-DD · Responsável: <nome> · Status: aceita
- Dimensão: <completude | validade | consistência | unicidade | temporalidade> · Problema: Q-<arq>-NN (saidas/qualidade/<arquivo>.md)
- Contexto: <o problema em uma frase, com n e %>
- Decisão: <corrigir | remover | marcar>: <como, exatamente>
- Motivo: <por que esta opção>
- Alternativas consideradas: <as outras opções e por que não>
- Efeito na contagem: <linhas antes → depois; valores alterados; colunas novas>
- Impacto: <quais objetivos do case ou arquivos isso afeta>
```

Problemas parecidos decididos juntos podem ir numa entrada só, mas cada um mantém seu Q-ID. Depois de registrar, atualize o **Status** no relatório (`decidido (D-XXX)`). Ao final, diga o que ficou pendente.

### 9. Depois, só se pedirem

- **Limpeza:** um script `src/limpeza_<arquivo>.py` que lê `dados/brutos/`, aplica **só** as decisões registradas e grava em `dados/processados/`. Ao final, ele imprime as contagens antes e depois, que precisam bater com o "Efeito na contagem" de cada decisão.
- **Commit:** só quando o usuário pedir.
