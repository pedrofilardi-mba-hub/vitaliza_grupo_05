# Dimensões novas: o que aprendemos

03/11/2026 · Leitura dos resultados de `src/dimensoes.py`. A tabela completa, com todas as dimensões, está em [dimensoes_novas.md](dimensoes_novas.md).

## O que fizemos

Para saber se uma informação ajuda a prever quem sai, precisamos de um **gabarito**: gente que de fato saiu. Como a saída depois de 30/09 ainda não está nos dados, **voltamos no tempo**:
- montamos a base de assinantes como ela era em **31/05/2026**, só com o que se sabia até aquele dia;
- conferimos quem saiu nos 60 dias seguintes (junho e julho);
- repetimos tudo em **31/07/2026**, para conferir se o resultado se repete. Essa janela tem a campanha de 10/08 no meio, por isso é só conferência.

Criamos **19 dimensões novas** a partir dos dados, em quatro famílias (contrato, comportamento, rede social, pagamento e suporte), e medimos quanto cada uma, **sozinha**, separa quem sai de quem fica. A régua é a do slide 9 da Aula 2: 0,50 = não separa nada; 1,00 = separa perfeitamente.

| Corte | Assinantes | Saíram em 60 dias |
|---|---:|---:|
| 31/05/2026 | 14.102 | 12,1% |
| 31/07/2026 | 14.032 | 10,5% |

## O que aprendemos

### 1. Quem já desligou a renovação vai sair, e isso não precisa de modelo

Entre os **mensais** que já tinham desligado a renovação, **99% saíram** nos 60 dias. Entre os anuais nessa situação, 21%, porque muitos só renovam depois da janela. Esse grupo é 15% da base e já está avisado: não adianta "prever" o que já se sabe.

👉 **Decidido (D-052):** esse grupo vai para uma **regra à parte** (a ação é tentar reverter a decisão antes do fim do período pago) e sai do modelo. Assim o modelo se concentra em quem **ainda não decidiu**: em 30/09, são 12.503 no modelo e 2.250 na regra à parte.

### 2. O contrato manda mais que o comportamento

- **A dimensão nova mais forte é "renova nos próximos 60 dias?"** (0,76 em 31/05 e 0,74 em 31/07). Um anual que só renova daqui a meses **não tem como sair** na janela. O modelo precisa saber disso, ou vai gastar contato com quem não pode sair.
- **Tempo de casa** separa nos dois grupos: mensais com até 1 mês saem 23%; com mais de 1 ano, 11%. É o "paradoxo do início" da Aula 3, também na Vitaliza.
- **Canal de pagamento:** entre os mensais, quem paga pelo Google Play sai mais (18,5%) que quem paga pela App Store (12,5%). É uma pista para o objetivo 2.

### 3. O uso importa, mas de jeitos diferentes em cada plano

- **Anuais que renovam na janela:** o uso pesa bastante.
  - "dias desde o último treino": 0,74 em 31/07;
  - "treinos nas últimas 4 semanas": 0,73;
  - "semanas ativas nas últimas 8" (nova): 0,69.

  Para essa pessoa, a renovação é o momento de decidir, e quem parou de treinar não renova.
- **Mensais:** o uso só separa nos extremos.
  - Quem não treinou nada em 4 semanas saiu 44%; quem treinou 1 ou 2 vezes, 23%.
  - Quase todo mensal treina bastante: dos 5.688, só 247 treinaram 2 vezes ou menos. Para a maioria, treinar mais ou menos não muda a chance de sair (15% a 17%).

### 4. Algumas ideias não se confirmaram

Isso também é informação. As dimensões abaixo **não separam** quem sai (AUC perto de 0,50) nas duas datas:
- **"Contágio" social:** amigos que saíram, parceiro de treino que saiu.
- **Suporte:** chamado sem solução, reclamação do app.
- **Pagamento:** cartão recusado no último mês.
- **Cupom de influenciador** renovando pelo preço cheio.

A hipótese de que "o suporte piorou em 2026 e isso explica o churn" **perde força**: quem ficou com chamado sem solução não saiu mais.

### 5. Um cuidado: o reajuste de preço

"Mensal afetado pelo reajuste de março" parece forte na base toda (0,65). Mas, entre os mensais, **quem não foi afetado sai mais**. São os que entraram depois de março, ou seja, mais novos, e os mais novos saem mais. Uma coisa se mistura com a outra. Para testar se o reajuste aumentou o churn (objetivo 2), é preciso comparar pessoas com o **mesmo tempo de casa**.

## O que isso muda nos próximos passos

1. **Detalhar a regra à parte** para quem já desligou a renovação (D-052): qual mensagem, por qual canal e com qual oferta. Isso entra no objetivo 6.
2. **O modelo de churn** (objetivo 4) deve usar, no mínimo:
   - plano e "renova em 60 dias";
   - tempo de casa;
   - canal;
   - as dimensões de uso para os anuais.

   Como nenhuma dimensão sozinha separa bem os mensais, o modelo precisa **combinar várias**. É aí que entram as árvores e o boosting do módulo.
3. **Os mensais precisam de informação nova.** As dimensões de **necessidade** (o texto do onboarding, como "treinar para uma prova", e os posts) são as candidatas mais fortes, pelo que vimos na pesquisa de saída ("objetivo cumprido"). Elas exigem leitura com IA (objetivo 5) e uma amostra conferida à mão.
4. **Objetivo 2:** testar o reajuste e o canal (Google Play × App Store) comparando grupos com o mesmo tempo de casa.
