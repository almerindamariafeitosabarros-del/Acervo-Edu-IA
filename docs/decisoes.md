# Decisões de projeto — Acervo Edu IA

Registro curto das escolhas feitas durante o desenvolvimento. Em caso de dúvida,
optamos sempre pela solução mais simples que atende ao requisito.

## Estrutura

- **Repositório com `backend/` e `frontend/` lado a lado.** O projeto Django que já
  existia foi movido de `acervo_edu_ia/` para `backend/`, mantendo o pacote de
  configuração `backend/acervo_edu_ia/`. Isso deixa claro onde fica cada parte.
- **Apps Django dentro de `backend/apps/`**: `accounts`, `academics`, `documents` e `ai`.
  Um app por assunto, sem camadas extras.

## Banco de dados

- **PostgreSQL via Docker Compose** (`docker-compose.yml` na raiz). Apenas o banco sobe
  em contêiner; backend e frontend rodam direto na máquina, o que simplifica o
  desenvolvimento e a demonstração.
- **`USE_SQLITE=True` no `.env`** permite rodar o projeto e os testes sem Docker.
  É uma saída de emergência, não o modo padrão.

## Usuários e perfis

- **Modelo de usuário customizado** (`accounts.User`) com login por e-mail, campo
  `role` e `is_active`. Evita o `username` do Django, que não é usado em nenhuma tela.
- **Perfis como hierarquia** (`ROLE_LEVEL`): Aluno < Professor < Gestor < Administrador.
  As permissões perguntam "tem pelo menos este nível?", em vez de listar perfis em
  cada verificação.
- **Todo cadastro pela tela inicial cria um Aluno.** O campo `role` é somente leitura
  no endpoint de cadastro e no `me/`; só o Administrador altera perfis em `/api/users/`.
- **Mensagem de login genérica** ("E-mail ou senha inválidos") para não revelar se um
  e-mail existe.

## Documentos

- **Visibilidade com dois valores** (`private`/`public`) em vez de um booleano, porque
  o texto que aparece na tela vem direto do `get_visibility_display()`.
- **Arquivos nunca têm URL pública.** `MEDIA_URL` não é roteada; o download passa por
  `GET /api/documents/{id}/file/`, que verifica o acesso antes de responder. O arquivo
  é gravado com nome aleatório (UUID) dentro da pasta do dono.
- **Documento privado de outro usuário responde 404**, não 403, para não revelar a
  existência do registro. Isso vale para o detalhe, o arquivo e o assistente de IA.
- **Disciplina e categoria são opcionais** no modelo. Assim um documento nunca fica
  bloqueado por falta de catálogo, e a exclusão usa `PROTECT` para não perder vínculos.
- **Tags são criadas na hora** a partir dos nomes digitados (`get_or_create`), sem uma
  tela separada de cadastro obrigatório.

## Assistente de IA

- **O Ollama é chamado apenas pelo backend**, nunca pelo navegador. Assim a verificação
  de acesso ao documento acontece antes de qualquer chamada ao modelo.
- **Endpoint único `POST /api/ai/ask/`** aceita `document_id` (documento do acervo) ou
  `file` (arquivo avulso). O arquivo avulso é lido em memória, nunca é salvo em disco e
  não vira `Document`; só o nome fica registrado no histórico.
- **Falha do Ollama responde 503** com "Assistente indisponível no momento" e nada é
  gravado no histórico. O restante do sistema continua funcionando.
- **Texto acima de `AI_MAX_CHARS` é cortado no início do documento** (sem resumo prévio,
  sem embeddings) e a tela avisa que a resposta considerou parte do material.
- **PPTX não é lido pelo assistente**, embora seja aceito no upload. Adicionar mais uma
  biblioteca só para isso não se justifica agora; a mensagem de erro explica o motivo.

## API e frontend

- **JWT com SimpleJWT** (access + refresh). O token fica no `localStorage` e o Axios
  renova o access automaticamente quando recebe 401.
- **Paginação padrão de 12 itens** (`PAGE_SIZE`), que cabe bem na grade de cards.
- **Endpoints de catálogo sem paginação** (`pagination_class = None`), porque alimentam
  selects encadeados e listas curtas.
- **Permissões validadas sempre no backend.** O frontend esconde botões apenas por
  conforto: cada ação é verificada de novo na API.

## Ajustes durante a validação

- **`page_size` na query string** (`PaginacaoPadrao`, máximo de 100). Sem isso, a tela do
  Assistente e a lista de usuários da Administração ficariam presas nos 12 primeiros
  registros, já que o DRF ignora o parâmetro por padrão.
- **`FRONTEND_ORIGIN` aceita várias origens** separadas por vírgula. `localhost:5173` e
  `127.0.0.1:5173` são endereços diferentes para o CORS, e trocar um pelo outro no
  navegador bloqueava as chamadas.
- **Conta desativada recebe a mesma mensagem de senha errada.** O `authenticate()` do
  Django já recusa contas inativas, e repetir a mensagem genérica evita revelar quais
  e-mails existem.

## LGPD (Lei 13.709/2018)

- **Consentimento com data e versão**, não apenas um booleano. Guardar
  `accepted_terms_at` + `accepted_terms_version` permite provar *quando* e *a qual texto*
  o titular consentiu (art. 8º, § 1º). Subir `TERMS_VERSION` invalida os aceites antigos
  e faz o sistema pedir um novo — sem migração de dados.
- **Exportação em JSON, pela própria API.** Um endpoint que devolve o arquivo pronto
  (`Content-Disposition: attachment`) resolve acesso e portabilidade (art. 18, II e V) sem
  depender de processo manual. Os arquivos enviados ficam de fora do relatório: são
  binários grandes, e a tela Meus Documentos já permite baixá-los um a um.
- **Exclusão pede senha e a palavra `EXCLUIR`.** Duas barreiras, porque a operação é
  irreversível e leva junto documentos e histórico. Os arquivos saem do disco antes dos
  registros, para não restar conteúdo órfão em `MEDIA_ROOT`.
- **Exclusão de verdade, não anonimização.** Para um acervo educacional, manter registros
  "anonimizados" traria pouco valor e mais risco; o art. 18, VI fala em eliminação, e é
  isso que o sistema faz.
- **A IA local é um argumento de privacidade, não só de custo.** Rodar o modelo na máquina
  da instituição evita transferência internacional de dados (art. 33) e impede que
  material de estudantes alimente modelos de terceiros.

## Acessibilidade (WCAG 2.1 AA / Lei 13.146/2015)

- **Validação escrita pela aplicação, não pelo navegador.** A mensagem nativa do
  `required` sai no idioma do navegador — apareceu em inglês nos testes. O aceite dos
  termos passou a ser validado no código, com mensagem em português, `aria-invalid` e
  `aria-describedby` ligando o erro ao campo.
- **`aria-current="page"` também serve de gancho de estilo** no menu, no lugar da classe
  do Vue Router. Assim o destaque visual e a informação para o leitor de tela vêm da
  mesma fonte e não podem divergir.
- **Listas começam em "Carregando…", não em "0 documentos".** Com `aria-live`, o zero
  inicial era anunciado como se fosse o resultado da busca.
- **Contraste conferido por cálculo, não a olho.** O verde do selo "Público" estava em
  4,49:1 — reprovava por 0,01. Foi para `#146b33` (5,91:1).
- **Links sublinhados dentro de texto corrido** (critério 1.4.1); em menus e botões o
  formato já distingue, então ali o sublinhado fica de fora.
- **Emojis decorativos com `aria-hidden`**, para o leitor de tela não anunciar "livro
  aberto" antes de cada título.
- **Verificação:** auditoria com axe-core nas 11 telas (0 violações WCAG 2.1 A/AA) mais
  checagens de teclado — skip link, foco visível, rótulos, hierarquia de títulos, zoom de
  200% sem rolagem horizontal e anúncio de troca de tela.
