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
