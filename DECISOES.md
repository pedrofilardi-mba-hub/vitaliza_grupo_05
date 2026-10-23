# Registro de decisões: Vitaliza, grupo 05

Cada decisão que muda um número, um método ou o escopo entra aqui, da mais antiga para a mais recente. Uma decisão revista não é apagada: ela ganha o status "substituída por D-XXX".

Modelo:

```
## D-XXX: título curto
- Data: AAAA-MM-DD · Responsável: nome · Status: proposta | aceita | substituída por D-YYY
- Contexto: o que motivou a decisão
- Decisão: o que foi decidido
- Alternativas consideradas: e por que foram descartadas
- Impacto: o que muda (arquivos, números, objetivos do case afetados)
```

---

## D-001: Dados brutos fora do repositório
- Data: 2026-10-22 · Responsável: grupo · Status: aceita
- Contexto: o data room tem cerca de 200 MB, com dois zips de heatmaps e dados pessoais (e-mail, data de nascimento).
- Decisão: `dados/brutos/` entra no `.gitignore`. Cada integrante copia os arquivos do data room para essa pasta, e eles não são alterados.
- Alternativas consideradas: versionar os dados com Git LFS. Foi descartado pelo tamanho e por causa dos dados pessoais.
- Impacto: todo arquivo de `dados/processados/` precisa poder ser recriado a partir de um script em `src/`.

## D-002: Data de corte e horizonte de previsão
- Data: 2026-10-22 · Responsável: grupo · Status: aceita
- Contexto: o enunciado fixa o corte da base em 30/09/2026 e pede a probabilidade de saída nos 60 dias seguintes.
- Decisão: corte em 30/09/2026 e alvo de churn na janela de 01/10 a 29/11/2026. Nenhuma variável usa dado posterior ao corte.
- Alternativas consideradas: nenhuma, porque é premissa do case.
- Impacto: os objetivos 4 a 7. A validação do modelo usa separação no tempo.
