# Vitaliza: grupo 05

Trabalho do grupo 05 no Módulo 2 do MBA em IA e Dados para Negócios (Inteli). O case é o da **Vitaliza**, um app de treino por assinatura que está perdendo assinantes. O objetivo é descobrir quem vai sair, em quem vale a pena agir, com qual mensagem e quanto isso rende.

O contexto completo e as regras do projeto estão no [AGENTS.md](AGENTS.md). As decisões do grupo estão no [DECISOES.md](DECISOES.md).

## Como começar (uma vez só)

Você precisa ter instalados o [Git](https://git-scm.com/downloads) e o [Python 3.12](https://www.python.org/downloads/).

**1. Baixe o repositório** para o seu computador:

```
git clone https://github.com/pedrofilardi-mba-hub/vitaliza_grupo_05.git
cd vitaliza_grupo_05
```

**2. Copie os arquivos do case.** Eles não ficam no GitHub porque são grandes e têm dados pessoais.

- **Os dados** vão para `dados/brutos/`. **Tire o número do fim do nome**: `usuarios_9730.csv` vira `usuarios.csv`, `atividades_9938.parquet` vira `atividades.parquet`, e assim por diante. O código do grupo usa os nomes sem número.
- **Os mapas de calor** vão para `dados/brutos/heatmap/`. Descompacte os dois zips ali: devem surgir as pastas `2026-07-31/` (12.431 imagens) e `2026-09-30/` (13.047 imagens).
- **Os PDFs** (enunciado e dicionário de dados) vão para `docs/case/`.

**3. Crie o ambiente Python e instale as bibliotecas.** O ambiente é uma pasta `.venv` com as bibliotecas do projeto, separada do resto do computador.

Windows:
```
python -m venv .venv
.venv\Scripts\activate
pip install -r requirements.txt
```

Mac ou Linux:
```
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

**4. Abra os notebooks:**
```
jupyter lab
```

Nas próximas vezes, basta ativar o ambiente (a segunda linha do passo 3) e rodar `jupyter lab`.

## No dia a dia

- **Antes de começar:** rode `git pull` para baixar o que os colegas subiram.
- **Para subir o seu trabalho:**
  ```
  git add .
  git commit -m "o que você fez, em uma frase"
  git push
  ```
- **Trabalhe nos seus próprios arquivos**, por exemplo um notebook por pessoa ou por objetivo. Duas pessoas editando o mesmo notebook geram conflitos difíceis de resolver.
- **Chaves de API** (para a IA generativa) vão num arquivo `.env` na raiz do projeto. Ele nunca sobe para o GitHub.

## Pastas

| Pasta | O que vai nela |
|---|---|
| `dados/brutos/` | Dados do case, como vieram. Não alterar e não sobe para o GitHub |
| `dados/processados/` | Dados limpos, gerados pelos scripts |
| `src/` | Código reutilizável (funções de limpeza, modelos) |
| `notebooks/` | Análises |
| `saidas/` | Gráficos, tabelas e resultados finais |
| `docs/` | Documentação e material de entrega |
