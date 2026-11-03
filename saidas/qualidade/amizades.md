# Qualidade: `amizades.csv`

Uma linha por relação "fulano segue beltrano" · 113.480 linhas · 3 colunas · avaliado em 03/11/2026 com a skill `qualidade-dados` · medidas em [amizades_evidencias.md](amizades_evidencias.md)

## Resumo

O arquivo mais limpo do data room:
- ninguém segue a si mesmo;
- nenhuma relação repetida;
- todas as contas existem em `usuarios.csv`;
- nenhuma relação começa antes de as duas contas existirem;
- nenhuma conta interna ou "do futuro" (D-021) aparece.

**O único problema: 273 relações com data depois do corte.**

**Situação em 03/11/2026:** o problema foi decidido (D-039 no `DECISOES.md`), para aplicar numa cópia em `dados/processados/`. Os brutos não mudam.

## Problemas para decidir

| ID | Dimensão | Coluna | O que está errado | Por que importa para o case |
|---|---|---|---|---|
| Q-amz-01 | Temporalidade | `desde` | 273 relações (0,2%) começam entre 01/10 e 09/10/2026, depois do corte (30/09) e até depois da exportação (01/10) | Usar essas relações faria o modelo "enxergar o futuro" (D-002): saber quem a pessoa vai seguir depois do corte |

### Q-amz-01 · Relações que começam depois do corte

**Em palavras simples:** 273 pessoas "começaram a seguir" alguém entre 1º e 9 de outubro, mas os dados vão só até 30/09.

**Exemplo:** uma relação com `desde` = 05/10/2026. Na data em que a previsão seria feita (30/09), ela ainda não existia.

- **Evidência:**
  - Por dia de outubro: 1º 54, dia 2 48, dia 3 48, dia 4 35, dia 5 39, dia 6 15, dia 7 21, dia 8 10, dia 9 3.
  - O volume vai caindo, como se o registro continuasse sendo atualizado depois da exportação.
  - Nos últimos dias de setembro, o ritmo era de cerca de 140 por dia.
- **Opções:**
  - **Corrigir:** não há data certa conhecida.
  - **Remover:** tirar as 273 da cópia processada. Efeito: 113.480 → 113.207 relações.
  - **Marcar:** criar `apos_corte` e filtrar em toda análise. Efeito: 0 linhas; risco de alguém esquecer o filtro.
- **Recomendação:** **remover**, pela mesma regra da D-021 (contas criadas depois do corte) e da D-002.
- **Status:** decidido (D-039, 03/11/2026, Pedro Filardi)

## Já decidido

- **D-002:** nenhuma informação posterior a 30/09/2026 entra nas variáveis.
- **D-021:** as contas com cadastro depois do corte não aparecem neste arquivo.
- **D-013:** as contas internas não aparecem neste arquivo.

## O que não é problema

- **Unicidade:** 0 pares repetidos e 0 contas seguindo a si mesmas.
- **Ligações:** 0 contas inexistentes, dos dois lados da relação.
- **Datas:** 0 relações antes do cadastro de qualquer das duas contas; 0 antes do lançamento do app.
- **Reciprocidade:** 85.044 linhas fazem parte de pares em que os dois se seguem. É uma característica da rede, não um erro: seguir é de mão única, e se Ana segue Bruno e Bruno segue Ana são duas linhas (dicionário).
- **Tamanho:** 54.162 contas aparecem na rede. Cada uma segue e é seguida, na mediana, por 2 contas, e no máximo por 13. Não há "influenciador" com milhares de seguidores distorcendo a rede.

## Números conferidos à mão

1. **Linhas:** 113.480, contadas com o leitor de CSV do Python, sem pandas. Bate com o dicionário.
2. **Relações depois do corte:** 273. Bate com o inventário (`saidas/inventario.md`).
3. **Soma das relações de outubro por dia:** 54 + 48 + 48 + 35 + 39 + 15 + 21 + 10 + 3 = 273.
