# Como preparar o seu computador para o projeto Vitaliza

Guia para quem nunca usou Git nem Python. A ideia é que **a sua IA** faça o trabalho pesado: você cola um prompt e ela conduz a configuração.

Serve para qualquer IA:
- **IA que mexe no computador** (Claude Code, Codex, Cursor): ela mesma instala, baixa e configura tudo, e pede sua autorização antes de cada passo importante.
- **Chat no navegador** (ChatGPT, Claude, Gemini): ela te guia um passo por vez. Diz exatamente o que digitar, você cola o resultado e ela segue.

Tempo estimado: de 30 minutos a 1 hora, a maior parte esperando instalação.

---

## Antes de começar: 3 coisas que só você pode fazer

**1. Crie uma conta no GitHub** (se ainda não tiver) em [github.com/signup](https://github.com/signup). O GitHub é onde fica o projeto do grupo.

**2. Mande o seu nome de usuário do GitHub para o Pedro.** Ele vai te convidar para o repositório. Você recebe um e-mail do GitHub: clique em **Accept invitation**. O convite vale por 7 dias.

**3. Tenha à mão os arquivos do case**, que o curso disponibilizou. São 3 grupos:
- os **dados**: 12 arquivos `.csv` e `.parquet`, com nomes como `usuarios_9730.csv`;
- os **mapas de calor**: 2 arquivos `.zip`, `heatmaps_2026-07-31_....zip` e `heatmaps_2026-09-30_....zip`;
- os **2 PDFs**: *Vitaliza - Enunciado do case* e *Vitaliza - Dicionário de dados*.

Deixe todos numa mesma pasta, por exemplo `Downloads\Vitaliza`, e anote onde ela está.

---

## Passo 1: crie a pasta do projeto

Crie uma pasta para o MBA **fora do OneDrive, do Google Drive ou do iCloud**. Sincronizadores de nuvem atrapalham o Git e vão tentar subir os 25 mil mapas de calor.

- Windows: `C:\Projetos\MBA`
- Mac: uma pasta `Projetos/MBA` dentro da sua pasta de usuário

## Passo 2: abra a sua IA

- **Claude Code, Codex, Cursor ou outra IA que mexe no computador:** abra com a pasta `C:\Projetos\MBA` como pasta de trabalho.
- **Chat no navegador (ChatGPT, Claude, Gemini):** abra uma conversa nova. Ela vai te ensinar a abrir o PowerShell (Windows) ou o Terminal (Mac) dentro da pasta.

## Passo 3: cole o prompt abaixo

Copie **tudo** que está dentro da caixa e cole na conversa com a IA. Antes de enviar, troque o que está entre `<< >>` pelas suas informações.

```text
Sou iniciante e preciso preparar meu computador para um projeto em grupo do MBA (case Vitaliza). Faça o passo a passo abaixo comigo, explicando cada passo em português simples, em uma ou duas frases.

Como trabalhar comigo:
- Se você consegue rodar comandos no meu computador (por exemplo, Claude Code, Codex ou Cursor), rode você mesmo, mas peça minha autorização antes de instalar qualquer programa.
- Se você é um chat e não consegue rodar comandos no meu computador (por exemplo, ChatGPT, Claude ou Gemini no navegador), me guie UM passo por vez: diga exatamente o que digitar e onde, e espere eu colar o resultado antes de seguir. Comece me ensinando a abrir o PowerShell (Windows) ou o Terminal (Mac) já dentro da minha pasta do projeto. Para copiar e renomear arquivos, pode me dar o comando ou me explicar como fazer pelo Explorador de Arquivos (Windows) ou pelo Finder (Mac).
- Se algo der erro, me explique o que aconteceu e proponha a solução antes de tentar de novo.

Minhas informações:
- Meu sistema: <<Windows ou Mac>>
- Minha pasta do projeto: <<ex.: C:\Projetos\MBA>>
- Pasta onde estão os arquivos do case (dados, zips e PDFs): <<ex.: C:\Users\fulano\Downloads\Vitaliza>>
- Meu nome para os commits: <<ex.: Maria Silva>>
- Meu e-mail para os commits: <<ex.: maria.silva@mba.inteli.edu.br>>

Passos:

1. Verifique se o Git está instalado (git --version). Se não estiver, instale (Windows: winget install --id Git.Git -e; Mac: xcode-select --install). Depois de instalar, pode ser preciso fechar e abrir o PowerShell/Terminal de novo.

2. Verifique se o Python 3.12 está instalado. O projeto usa Python 3.12. Se não estiver, instale (Windows: winget install --id Python.Python.3.12 -e; Mac: instalador do python.org). No Windows, cuidado: o comando "python" pode abrir a Microsoft Store em vez do Python de verdade; use "py -3.12" se precisar.

3. Dentro da minha pasta do projeto, baixe o repositório do grupo:
git clone https://github.com/pedrofilardi-mba-hub/vitaliza_grupo_05.git
Depois entre na pasta vitaliza_grupo_05. Todos os passos seguintes acontecem dentro dela.

4. Se você consegue ler arquivos, leia o README.md e o AGENTS.md do repositório, que têm as regras do projeto, e siga-as daqui em diante. Se não consegue, siga este roteiro.

5. Configure meu nome e e-mail só para este repositório (git config user.name e git config user.email, sem --global).

6. Crie o ambiente Python dentro da pasta do projeto, numa pasta chamada .venv, com o Python 3.12, e instale as bibliotecas com: pip install -r requirements.txt
No Windows, se a ativação do .venv for bloqueada ("execução de scripts foi desabilitada"), NÃO mude configurações de segurança: use direto o Python do ambiente, .venv\Scripts\python.exe (por exemplo: .venv\Scripts\python.exe -m pip install -r requirements.txt).

7. Copie os arquivos do case da minha pasta para o projeto:
- Os 12 arquivos de dados (.csv e .parquet) vão para dados/brutos/, SEM o número no fim do nome. Exemplos: usuarios_9730.csv vira usuarios.csv; atividades_9938.parquet vira atividades.parquet. Os nomes finais devem ser: usuarios.csv, assinaturas.csv, amizades.csv, campanha_ago26.csv, eventos_assinatura.csv, pagamentos.csv, uso_mensal.csv, atividades.parquet, onboarding.csv, pesquisa_saida.csv, feed_posts.csv e tickets_suporte.csv.
- Os 2 zips de mapas de calor vão para dados/brutos/heatmap/ e devem ser descompactados ali. Precisam surgir as pastas 2026-07-31/ (12.426 imagens .png) e 2026-09-30/ (13.047 imagens .png). Se aparecer uma pasta __MACOSX, apague-a: é lixo do Mac, não são mapas.
- Os 2 PDFs vão para docs/case/.
Copie, não mova: os originais ficam onde estão.

8. Confira se tudo deu certo rodando o inventário com o Python do .venv:
.venv\Scripts\python.exe src\inventario.py (no Mac: .venv/bin/python src/inventario.py)
Depois mostre o começo do arquivo saidas/inventario.md e confira se a seção "Principais pontos" começa com "O data room está completo. 12 de 12 arquivos têm exatamente as linhas do dicionário". Se não começar, descubra qual arquivo está faltando ou com nome errado. Como o inventário regenera esse arquivo com a data de hoje, desfaça a mudança no final com: git restore saidas/inventario.md

9. Rode git status e confirme que não há nada para enviar: os dados, o .venv e os PDFs precisam aparecer como ignorados, nunca como arquivos novos.

10. Não faça commit nem push de nada nesta configuração.

No final, me mostre um resumo: o que foi instalado, onde ficou a pasta do projeto, e como eu faço no dia a dia para abrir o Jupyter (com o comando exato para o meu sistema).
```

## Passo 4: acompanhe e autorize

Leia o que a IA explica e siga ou autorize. Se for um chat no navegador, cole de volta o que aparecer no PowerShell/Terminal a cada passo, mesmo que pareça erro. No Windows, o instalador pode abrir uma janela pedindo permissão de administrador: aceite.

Ao final você deve ter:
- a pasta `C:\Projetos\MBA\vitaliza_grupo_05` com o projeto;
- o inventário dizendo **"12 de 12 arquivos"**;
- o `git status` sem nada para enviar.

## Passo 5: o primeiro envio (quando tiver algo seu)

Na primeira vez que você (ou a sua IA) fizer `git push`, vai abrir uma janela ou uma aba do navegador pedindo para entrar no GitHub. Entre com a sua conta e clique em **Authorize**. Isso acontece uma vez só por computador.

> Se a sua IA não conseguir abrir essa janela (ela vai dizer algo como *"terminal prompts disabled"*), rode o `git push` você mesmo, num terminal aberto na pasta do projeto.

---

## No dia a dia

Peça à sua IA, com estas palavras ou parecidas:

- **Ao começar:** *"Atualize o projeto com o que os colegas subiram (git pull)."*
- **Ao terminar:** *"Faça commit do que eu fiz, com uma mensagem clara em português, e envie para o GitHub."*

E três combinados do grupo:
1. **Cada um trabalha nos seus próprios arquivos**, por exemplo um notebook por pessoa ou por objetivo. Duas pessoas editando o mesmo notebook dá conflito difícil de resolver.
2. **Nunca altere nada em `dados/brutos/`.** Dados limpos vão para `dados/processados/`.
3. **Decisões de método vão para o `DECISOES.md`**: o que foi decidido e por quê.

---

## Se der problema

| Sintoma | O que fazer |
|---|---|
| Não recebi o convite do GitHub | Confira a caixa de spam e veja se o Pedro tem o seu usuário certo. O convite também aparece em [github.com/notifications](https://github.com/notifications). |
| `git clone` pede senha ou dá "repository not found" | Aceite o convite primeiro. |
| `git` ou `python` "não é reconhecido" logo depois de instalar | Feche e abra o PowerShell/Terminal de novo. |
| `python` abre a Microsoft Store | Use `py -3.12` no lugar de `python`, ou peça à IA para usar o caminho completo do Python. |
| "Execução de scripts foi desabilitada" ao ativar o `.venv` | Não mude a configuração de segurança: use `.venv\Scripts\python.exe` direto, como está no passo 6 do prompt. |
| `pip install` dá erro de conexão ou de certificado | Provavelmente é o proxy da empresa. Tente na rede de casa, ou peça ajuda à IA mostrando a mensagem de erro. |
| O inventário não diz "12 de 12" | Algum arquivo está faltando ou com o número no nome. Peça à IA para comparar `dados/brutos/` com a lista do passo 7 do prompt. |
| O Git reclama de arquivo travado | A pasta provavelmente está no OneDrive. Mova o projeto para `C:\Projetos\MBA`. |

## Se preferir fazer sem IA

O [README](../README.md) tem os mesmos passos em versão curta, com os comandos para copiar.
