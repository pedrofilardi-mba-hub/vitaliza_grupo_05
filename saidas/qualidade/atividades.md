# Qualidade: `atividades.parquet`

Uma linha por treino · 1.254.475 linhas · 11 colunas · de 01/01 a 30/09/2026 · avaliado em 03/11/2026 com a skill `qualidade-dados` · medidas em [atividades_evidencias.md](atividades_evidencias.md)

## Resumo

É a fonte de "quanto e como cada pessoa treina" em 2026 (D-029). A estrutura está íntegra: um `atividade_id` por linha, todas as contas existem em `usuarios.csv`, e o "treinou com" sempre aponta para contas reais. Os seis problemas são os que a Aula 2 já mostrou (slides 30 a 34), mais dois achados novos, o GPS falho e a duração zero recuperável. **Em quatro deles o valor certo é recuperável**, porque as colunas se confirmam umas às outras: ritmo × distância = duração.

| Número da Aula 2 | Nosso | Aula |
|---|---:|---:|
| Treinos acima de 200 km | 951 | 951 |
| Treinos com duração zero | 3.649 | 3.649 |
| Tipos com nome em inglês | 376.930 (30%) | 376.930 (30%) |
| Treinos em dobro (app × relógio) | 9.383 | 9.383 |

**Situação em 03/11/2026:** os 6 problemas foram decididos (D-030 a D-035 no `DECISOES.md`), todos para aplicar numa cópia em `dados/processados/`. Os brutos não mudam. A limpeza ainda não foi feita.

## Problemas para decidir

| ID | Dimensão | Coluna | O que está errado | Por que importa para o case |
|---|---|---|---|---|
| Q-atv-01 | Temporalidade | `inicio` | Os treinos do Garmin (207.954) estão no horário de Londres (UTC), 3 horas à frente | Horários errados; 34 treinos de 30/09 à noite caem em "outubro"; e a duplicata com o app não é encontrada sem acertar o fuso |
| Q-atv-02 | Unicidade | linha inteira | 9.383 treinos chegaram duas vezes: pelo app e pelo relógio (4.184 Apple Health e 5.199 Garmin) | Inflam a contagem de treinos e minutos de quem tem relógio, que parece treinar mais do que treina |
| Q-atv-03 | Consistência | `tipo` | 11 nomes para 7 tipos: `run` = corrida, `walk` = caminhada, `strength` = força, `ride` = pedal; 376.930 treinos (30%) em inglês, todos registrados pelo app | Contar "só corrida" deixa de fora 162.108 corridas |
| Q-atv-04 | Validade | `distancia_km` | 951 treinos acima de 200 km (máximo de 10.013 km), cerca de 100 vezes a distância real | Qualquer média de distância fica absurda |
| Q-atv-05 | Validade | `duracao_min` | 3.649 treinos com 0 minuto; 1.972 deles têm distância e ritmo, os outros 1.677 não | Minutos de treino ficam subestimados |
| Q-atv-06 | Validade | `distancia_km`, `gps_ok` | Nos 14.779 treinos com GPS falho, 7.455 têm uma distância gravada, cortada (mediana de 0,6 km) e sem ritmo | Distâncias falsamente curtas puxam as médias para baixo |

### Q-atv-01 · O relógio Garmin anota no horário de Londres

**Em palavras simples:** é o mesmo problema dos outros arquivos, agora só nos treinos do Garmin.

**Exemplo (ilustrativo):** quem corre às 6h da manhã com Garmin aparece correndo às 9h. Quem treina às 22h de 30/09 aparece treinando à 1h de 01/10.

- **Evidência:**
  - App e Apple Health têm o pico de início às 6h (38% dos treinos entre 5h e 7h) e nenhum treino de madrugada.
  - O Garmin tem o pico às 9h, 0% entre 5h e 7h, e 2,8% entre 0h e 4h. É o mesmo padrão, deslocado 3 horas.
  - Os 34 treinos de "01/10/2026" são todos do Garmin, entre 0h e 1h.
- **Opções:**
  - **Corrigir:** subtrair 3 horas dos treinos do Garmin e guardar o original em `inicio_original`. Efeito: 1.254.475 → 1.254.475 treinos; 207.954 horários ajustados; os 34 de "outubro" voltam para 30/09.
  - **Remover:** tirar os 34 de outubro. Efeito: perde 34 treinos reais e deixa os outros 207.920 com o horário errado.
  - **Marcar:** só anotar o fuso. Efeito: o horário continua errado.
- **Recomendação:** **corrigir**. É a mesma regra das D-009 e D-026, confirmada pelo padrão de horário, e é pré-condição para achar as duplicatas (Q-atv-02).
- **Status:** decidido (D-030, 03/11/2026, Pedro Filardi)

### Q-atv-02 · O mesmo treino registrado duas vezes

**Em palavras simples:** quem tem relógio às vezes registra o treino no app **e** no relógio, e ele chega duas vezes.

**Exemplo (ilustrativo):** uma corrida de 41 minutos às 6h10 aparece uma vez com origem `app` e outra com origem `garmin`, com o mesmo tipo, a mesma duração e a mesma distância.

- **Evidência:**
  - Com a regra da aula (mesma conta, mesmo tipo, mesma duração, início a até 5 minutos, uma do app e outra do relógio) e o fuso do Garmin corrigido: 9.383 pares (4.184 Apple Health e 5.199 Garmin).
  - Nos pares, a distância também é igual.
  - Sem corrigir o fuso, só aparecem os 4.184 do Apple Health.
- **Opções:**
  - **Corrigir:** não há valor a corrigir.
  - **Remover:** tirar a cópia vinda do **app** e manter a do relógio, que traz a frequência cardíaca. Efeito: 1.254.475 → 1.245.092 treinos.
  - **Marcar:** criar `treino_duplicado`. Efeito: 0 linhas; toda contagem precisa lembrar do filtro.
- **Recomendação:** **remover a cópia do app**. O relógio tem os mesmos dados e mais a frequência cardíaca.
- **Status:** decidido (D-031, 03/11/2026, Pedro Filardi)

### Q-atv-03 · Tipos em português e em inglês

**Exemplo:** "corrida" aparece como `corrida` (223.818) e como `run` (162.108).

- **Evidência:**
  - Os nomes em inglês só aparecem em treinos registrados pelo app: `run` 162.108, `walk` 88.509, `strength` 85.548 e `ride` 40.765.
  - A proporção é a mesma em todas as versões do app (de 42% a 45%) e nos dois sistemas. Não é um defeito de uma versão; são rótulos diferentes para o mesmo tipo.
  - `hiit` e `yoga` não têm versão em outra língua.
- **Opções:**
  - **Corrigir:** mapear para os 7 tipos em português (corrida, caminhada, pedal, força, funcional, hiit e yoga), criando a coluna `modalidade` com "ar livre" ou "vídeo". Efeito: 0 treinos a menos; 376.930 tipos reescritos.
  - **Remover:** não se aplica.
  - **Marcar:** manter os 11 nomes. Efeito: contagens por tipo partidas.
- **Recomendação:** **corrigir**. O mapeamento é inequívoco.
- **Status:** decidido (D-032, 03/11/2026, Pedro Filardi)

### Q-atv-04 · Distâncias de centenas ou milhares de km

**Em palavras simples:** em 951 treinos, a distância ficou cerca de 100 vezes maior que a real. A duração e o ritmo estão certos, e com eles dá para calcular a distância verdadeira.

**Exemplo (ilustrativo):** uma corrida de 45 minutos com ritmo de 6:40 por km foi de cerca de 6,7 km, mas aparece gravada como algo perto de 700 km.

- **Evidência:**
  - Nas linhas normais, ritmo = duração ÷ distância em 99,6% dos casos.
  - Nas 951, isso não fecha. Recalculando a distância como duração ÷ ritmo, os valores ficam no padrão de cada tipo: corrida 6,67 km (típico 6,51), caminhada 5,59 (5,24) e pedal 29,18 (25,81).
  - A distância gravada é, na mediana, 106 vezes a recalculada. Não é só "metros no lugar de km": dividir por mil daria corridas de 660 metros.
- **Opções:**
  - **Corrigir:** substituir pela distância recalculada (duração ÷ ritmo) e guardar a original. Efeito: 0 treinos a menos; 951 distâncias reescritas.
  - **Remover:** tirar esses treinos. Efeito: −951 treinos reais.
  - **Marcar:** deixar a distância vazia e marcar. Efeito: 0 treinos; perde-se uma distância recuperável.
- **Recomendação:** **corrigir**. Ritmo e duração se confirmam no resto do arquivo, e a distância recalculada é plausível.
- **Status:** decidido (D-033, 03/11/2026, Pedro Filardi)

### Q-atv-05 · Treinos de zero minuto

**Em palavras simples:** 3.649 treinos aparecem com duração zero. Em pouco mais da metade deles, a distância e o ritmo existem, e a duração certa se calcula (ritmo × distância). Nos outros, não há como saber.

**Exemplo (ilustrativo):** uma corrida de 6,5 km com ritmo de 6 min/km durou cerca de 39 minutos, mas aparece com 0.

- **Evidência:**
  - 1.972 com distância e ritmo, logo recuperáveis.
  - 1.677 sem distância e ritmo (força, funcional, yoga e outros), sem como recuperar.
  - Por origem: app 2.540, Garmin 607 e Apple Health 502.
- **Opções:**
  - **Corrigir:** calcular a duração dos 1.972 (ritmo × distância). Os 1.677 restantes ficam com duração vazia e a marca `duracao_invalida`, e contam como treino, mas não entram na soma de minutos. Efeito: 0 treinos a menos.
  - **Remover:** tirar os 3.649. Efeito: perde treinos reais, e o "quantas vezes treinou" fica menor.
  - **Marcar:** só marcar os 3.649. Efeito: perde 1.972 durações recuperáveis.
- **Recomendação:** **corrigir os recuperáveis e marcar o resto**.
- **Status:** decidido (D-034, 03/11/2026, Pedro Filardi)

### Q-atv-06 · Distância de GPS que falhou

**Em palavras simples:** quando o GPS falha no meio do treino, às vezes fica gravada só a parte medida antes da falha.

**Exemplo (ilustrativo):** uma corrida de 40 minutos com GPS falho aparece com 0,6 km.

- **Evidência:**
  - `gps_ok = falso` em 14.779 treinos, todos ao ar livre. Destes, 7.324 estão sem distância e 7.455 têm uma distância.
  - Essas distâncias têm mediana de 0,6 km, contra 6,5 km nas corridas normais, e nenhuma tem ritmo.
- **Opções:**
  - **Corrigir:** não dá para recalcular, porque não há ritmo.
  - **Remover:** tirar os treinos. Efeito: −14.779 treinos reais; o "treinou" é verdadeiro, só a distância não é.
  - **Marcar:** a distância dos 7.455 vira vazia, e fica a marca `gps_falhou` nos 14.779. O treino e a duração continuam valendo. Efeito: 0 treinos a menos; 7.455 distâncias apagadas na cópia.
- **Recomendação:** **marcar**. O treino aconteceu; só a distância não é confiável.
- **Status:** decidido (D-035, 03/11/2026, Pedro Filardi)

## Já decidido

- **D-029:** este arquivo é a fonte de treinos, minutos e dias ativos de 2026, depois destas decisões.
- **D-009 e D-026:** a mesma regra de fuso (UTC para Brasília), agora aplicada ao Garmin.

## O que não é problema

- **Chave e ligações:** 1.254.475 `atividade_id` distintos. Todas as contas existem em `usuarios.csv`. O `treino_com` (14.137 preenchidos) sempre aponta para uma conta existente e nunca para a própria pessoa.
- **`treino_com` vazio:** os 98,9% vazios vêm como texto vazio, não como nulo. Na cópia processada, viram nulo; é só formato.
- **Distância vazia:** 100% vazia nos treinos em vídeo (força, funcional, hiit e yoga), como esperado. Nos treinos ao ar livre, só falta quando o GPS falhou.
- **Frequência cardíaca:** sempre presente nos treinos de relógio, e vazia em 86,8% dos do app, que não têm sensor. Entre 61 e 195 bpm, faixa possível.
- **Ritmo:** entre 1,8 e 13 min/km, coerente com a distância e a duração em 99,6% das linhas boas.

## Números conferidos à mão

Contei com o pyarrow, direto do arquivo, sem pandas:
1. **Linhas:** 1.254.475.
2. **Tipos em inglês:** 376.930.
3. **Duração zero:** 3.649. E **distância acima de 200 km:** 951.

Os quatro batem com o dicionário e com a Aula 2.
