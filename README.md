# Acervo Edu IA

Plataforma web para **armazenar, organizar, pesquisar e compartilhar documentos
educacionais**, com um **Acervo Público** visível a todos os usuários cadastrados e um
**Assistente de IA local** que responde perguntas sobre um documento escolhido.

Projeto de estágio — INFORGENESES.

---

## Sumário

- [O que a plataforma faz](#o-que-a-plataforma-faz)
- [Tecnologias](#tecnologias)
- [Requisitos](#requisitos)
- [Instalação do zero](#instalação-do-zero)
- [Rodando o projeto](#rodando-o-projeto)
- [Dados de exemplo e contas de teste](#dados-de-exemplo-e-contas-de-teste)
- [Assistente de IA (Ollama)](#assistente-de-ia-ollama)
- [Perfis e permissões](#perfis-e-permissões)
- [Telas](#telas)
- [API](#api)
- [Variáveis do `.env`](#variáveis-do-env)
- [Testes](#testes)
- [Segurança](#segurança)
- [LGPD — proteção de dados](#lgpd--proteção-de-dados)
- [Acessibilidade](#acessibilidade)
- [Estrutura de pastas](#estrutura-de-pastas)

---

## O que a plataforma faz

- Cadastro e login por e-mail. Toda conta criada pela tela inicial é um **Aluno**.
- **Meus Documentos**: upload de PDF, DOCX, PPTX e TXT com título, descrição, autor do
  material, instituição → curso → disciplina, categoria e tags. Todo documento nasce
  **privado**.
- **Acervo Público**: documentos publicados, com busca por texto e filtros por
  instituição, curso, disciplina, categoria e autor.
- **Assistente IA**: escolha um documento (seu, do acervo, ou um arquivo enviado só para
  aquela pergunta), escreva um prompt e receba a resposta gerada por um modelo que roda
  na sua própria máquina, via Ollama.
- **Administração**: gestão de usuários, instituições, cursos, disciplinas, categorias e
  moderação das publicações.

---

## Tecnologias

| Camada | Tecnologias |
| --- | --- |
| Frontend | Vue 3, Vite, Vue Router, Pinia, Axios |
| Backend | Python, Django, Django REST Framework, SimpleJWT |
| Banco | PostgreSQL (via Docker Compose) |
| IA local | Ollama, chamado **apenas** pelo backend |
| Extração de texto | pypdf (PDF), python-docx (DOCX), leitura direta (TXT) |

---

## Requisitos

- Python 3.11 ou superior
- Node.js 20 ou superior
- Docker e Docker Compose (para o PostgreSQL)
- [Ollama](https://ollama.com) instalado na máquina (opcional — sem ele, todo o resto
  do sistema continua funcionando)

---

## Instalação do zero

### 1. Clonar e configurar o ambiente

```bash
git clone <url-do-repositorio>
cd Acervo-Edu-IA
cp .env.example .env
```

Abra o `.env` e troque pelo menos o `SECRET_KEY`.

### 2. Subir o banco de dados

```bash
docker compose up -d
```

Isso sobe um PostgreSQL 16 na porta 5432 com os dados do `.env`.

> Sem Docker? Coloque `USE_SQLITE=True` no `.env` para rodar com SQLite. Serve para
> testes e demonstrações rápidas; o modo padrão do projeto é o PostgreSQL.

### 3. Instalar e preparar o backend

```bash
python3 -m venv .venv
source .venv/bin/activate          # Windows: .venv\Scripts\activate
pip install -r backend/requirements.txt

cd backend
python manage.py migrate
python manage.py seed_demo         # dados de exemplo (opcional, mas recomendado)
```

### 4. Instalar o frontend

```bash
cd ../frontend
cp .env.example .env
npm install
```

---

## Rodando o projeto

Abra dois terminais.

**Terminal 1 — backend (porta 8000):**

```bash
source .venv/bin/activate
cd backend
python manage.py runserver
```

**Terminal 2 — frontend (porta 5173):**

```bash
cd frontend
npm run dev
```

Acesse **http://localhost:5173**. A primeira tela é a de Cadastro/Login.

---

## Dados de exemplo e contas de teste

```bash
cd backend
python manage.py seed_demo           # cria usuários, catálogo e documentos
python manage.py seed_demo --limpar  # recria os documentos de exemplo
```

Contas criadas (senha de todas: `acervo123`):

| Perfil | E-mail |
| --- | --- |
| Administrador | `admin@acervo.edu` |
| Gestor | `gestor@acervo.edu` |
| Professor | `professor@acervo.edu` |
| Aluno | `aluno@acervo.edu` |

Para criar um administrador próprio:

```bash
python manage.py createsuperuser
```

---

## Assistente de IA (Ollama)

O Ollama roda na sua máquina e é chamado **somente pelo backend** — o navegador nunca
fala com ele. Assim, a permissão de acesso ao documento é verificada antes de qualquer
consulta ao modelo.

```bash
# instale o Ollama (https://ollama.com), depois baixe o modelo
ollama pull qwen2.5:7b     # ou: ollama pull llama3.1:8b
ollama serve               # deixa o serviço ouvindo em http://localhost:11434
```

Ajuste o modelo no `.env` (`OLLAMA_MODEL`) e reinicie o backend.

Como funciona cada pergunta:

1. O usuário escolhe um documento (de Meus Documentos, do Acervo Público, ou envia um
   arquivo avulso) e escreve o prompt.
2. O backend confere a permissão de acesso e extrai o texto do arquivo.
3. O texto e o prompt vão para o Ollama com a instrução de sistema: *"Responda em
   português do Brasil usando apenas o conteúdo do documento. Se a informação não
   estiver no documento, diga isso."*
4. A resposta aparece na tela e fica salva no histórico do usuário.

Comportamentos previstos:

- Texto maior que `AI_MAX_CHARS` (padrão 12.000): usa só o início e avisa na tela.
- PDF digitalizado, sem texto: *"Não foi possível ler o texto deste documento."*
- Ollama desligado: *"Assistente indisponível no momento."* — **o restante do sistema
  continua funcionando normalmente**.
- O arquivo avulso não entra no acervo: é lido em memória e descartado após a resposta.
- A IA nunca altera documentos ou metadados; ela apenas responde.

---

## Perfis e permissões

| Perfil | O que pode fazer |
| --- | --- |
| **Aluno** | Ver e baixar o Acervo Público; cadastrar documentos privados; usar o Assistente IA |
| **Professor** | Tudo do Aluno + publicar e despublicar os próprios documentos |
| **Gestor** | Tudo do Professor + gerenciar qualquer documento, cursos, disciplinas e categorias |
| **Administrador** | Tudo + gerenciar usuários, perfis e instituições |

Todo cadastro feito pela tela inicial cria um **Aluno**. Só o Administrador altera perfis.

As permissões são **sempre validadas no backend**. O frontend esconde botões apenas por
conforto: cada ação é verificada de novo na API.

---

## Telas

| # | Tela | Rota |
| --- | --- | --- |
| 1 | Cadastro/Login | `/entrar` |
| 2 | Início | `/` |
| 3 | Acervo Público | `/acervo` |
| 4 | Meus Documentos | `/meus-documentos` |
| 5 | Novo/Editar Documento | `/documentos/novo`, `/documentos/:id/editar` |
| 6 | Detalhes do Documento | `/documentos/:id` |
| 7 | Assistente IA | `/assistente` |
| 8 | Meu Perfil | `/perfil` |
| 9 | Administração | `/administracao` (Gestor e Administrador) |
| — | Política de Privacidade | `/privacidade` (aberta, com ou sem login) |
| — | Declaração de Acessibilidade | `/acessibilidade` (aberta, com ou sem login) |

Usuário não autenticado sempre volta para a tela 1. O menu lateral mostra apenas as
telas permitidas ao perfil.

---

## API

Base: `http://localhost:8000/api`. Autenticação por JWT no cabeçalho
`Authorization: Bearer <access>`.

| Rota | Método | Função |
| --- | --- | --- |
| `/auth/register/` | POST | Cadastro (cria um Aluno e devolve os tokens) |
| `/auth/login/` | POST | Login |
| `/auth/refresh/` | POST | Renova o token de acesso |
| `/auth/me/` | GET, PUT | Dados da sessão e edição do próprio nome |
| `/auth/change-password/` | POST | Troca de senha |
| `/auth/me/export/` | GET | Baixa todos os dados do titular em JSON (LGPD, art. 18) |
| `/auth/me/delete/` | POST | Exclui a conta e todos os dados do titular |
| `/auth/consent/` | GET, POST | Versão vigente dos termos e registro de novo aceite |
| `/documents/mine/` | GET, POST | Meus documentos e cadastro com upload |
| `/documents/public/` | GET | Acervo Público com busca e filtros |
| `/documents/all/` | GET | Todos os documentos (Gestor e Admin) |
| `/documents/stats/` | GET | Contadores da tela de Início |
| `/documents/{id}/` | GET, PUT, PATCH, DELETE | Detalhar, editar e excluir |
| `/documents/{id}/publish/` | POST | Publicar |
| `/documents/{id}/unpublish/` | POST | Despublicar |
| `/documents/{id}/file/` | GET | Visualizar/baixar com verificação de acesso |
| `/institutions/`, `/courses/`, `/subjects/`, `/categories/`, `/tags/` | CRUD | Organização acadêmica |
| `/users/` | CRUD | Gestão de usuários (Administrador) |
| `/users/{id}/toggle_active/` | POST | Ativar/desativar conta |
| `/ai/ask/` | POST | Prompt + documento (`document_id` ou `file`) → resposta |
| `/ai/history/` | GET | Histórico de perguntas do usuário |
| `/ai/status/` | GET | Modelo e limites configurados |

Regras de resposta:

- Requisição sem login → **401**.
- Documento privado de outro usuário → **404** (não revela que o registro existe).
- Ação sem permissão sobre documento visível → **403**.
- Assistente indisponível → **503**.

Busca e filtros do Acervo Público:

```
GET /api/documents/public/?search=cálculo&institution=1&course=2&subject=3&category=1&author=Paulo&page=2
```

---

## Variáveis do `.env`

| Variável | Padrão | Descrição |
| --- | --- | --- |
| `SECRET_KEY` | — | Chave do Django. **Troque sempre.** |
| `DEBUG` | `True` | Use `False` em produção |
| `ALLOWED_HOSTS` | `localhost,127.0.0.1` | Hosts aceitos, separados por vírgula |
| `POSTGRES_DB` / `_USER` / `_PASSWORD` / `_HOST` / `_PORT` | `acervo_edu_ia` / `acervo` / `acervo` / `localhost` / `5432` | Conexão com o banco |
| `USE_SQLITE` | `False` | `True` roda com SQLite, sem Docker |
| `FRONTEND_ORIGIN` | `http://localhost:5173` | Origens liberadas no CORS (separe por vírgula) |
| `ACCESS_TOKEN_LIFETIME_MINUTES` | `60` | Validade do token de acesso |
| `REFRESH_TOKEN_LIFETIME_DAYS` | `7` | Validade do token de renovação |
| `MAX_UPLOAD_SIZE_MB` | `25` | Tamanho máximo do arquivo enviado |
| `OLLAMA_URL` | `http://localhost:11434` | Endereço do Ollama |
| `OLLAMA_MODEL` | `qwen2.5:7b` | Modelo usado pelo assistente |
| `AI_MAX_CHARS` | `12000` | Limite de caracteres enviados ao modelo |
| `AI_TIMEOUT_SECONDS` | `120` | Tempo máximo de espera pela resposta |

O frontend tem o seu próprio `.env` com `VITE_API_URL` (padrão
`http://localhost:8000/api`).

Apenas os arquivos `.env.example` são versionados.

---

## Testes

```bash
source .venv/bin/activate
cd backend
python manage.py test                 # suíte completa
python manage.py test apps.documents  # apenas um app
```

Os testes cobrem cadastro e login, permissões por perfil, upload e seus limites,
publicação e despublicação, isolamento de documentos privados, extração de texto, o
comportamento do assistente com o Ollama indisponível e os direitos da LGPD
(consentimento obrigatório, exportação e exclusão de conta).

Para rodar sem Docker: `USE_SQLITE=True python manage.py test`.

Build de produção do frontend:

```bash
cd frontend
npm run build
```

---

## Segurança

- Arquivos **nunca** ficam em URL pública: todo acesso passa por
  `GET /api/documents/{id}/file/`, que verifica a permissão antes de responder. O arquivo
  é gravado em disco com nome aleatório.
- Upload aceita apenas PDF, DOCX, PPTX e TXT, com limite de tamanho vindo do `.env`.
- Senhas com o hash padrão do Django e validadores de força ativados.
- CORS liberado apenas para a origem do frontend.
- Em produção: `DEBUG=False`, cookies seguros e `X-Frame-Options: DENY`.
- Nenhum dado é enviado a serviços externos: a IA roda na própria máquina.

---

## LGPD — proteção de dados

A plataforma trata dados pessoais de estudantes e professores, então segue a
Lei 13.709/2018 desde o código, não apenas no texto da política.

**Minimização (art. 6º, III).** São coletados apenas nome, e-mail e o que o próprio
usuário envia. Não há CPF, telefone, endereço, localização, cookies de rastreamento nem
ferramentas de publicidade.

**Consentimento registrado (art. 8º, § 1º).** O cadastro exige o aceite dos Termos de Uso
e da Política de Privacidade. O sistema guarda a data e a versão aceita em
`accepted_terms_at` e `accepted_terms_version`. Ao mudar o texto da política, basta subir
`TERMS_VERSION` em `backend/apps/accounts/models.py`: o consentimento antigo deixa de
valer e um novo aceite é pedido.

**Direitos do titular (art. 18).** Implementados na tela Meu Perfil:

| Direito | Como é atendido |
| --- | --- |
| Acesso e portabilidade (II e V) | `GET /api/auth/me/export/` devolve um JSON com cadastro, documentos e histórico do assistente |
| Correção (III) | Edição do nome no perfil e dos metadados de cada documento |
| Eliminação e revogação (VI e IX) | `POST /api/auth/me/delete/` apaga conta, documentos, arquivos em disco e histórico |
| Informação sobre compartilhamento (VII) | Política de Privacidade, seção 4 — não há compartilhamento com terceiros |

A exclusão pede senha **e** a palavra `EXCLUIR` digitada, porque é irreversível. Os
arquivos são removidos do disco antes dos registros, para não deixar conteúdo órfão.

**IA sem transferência de dados.** O modelo roda localmente via Ollama. Nenhum documento é
enviado a serviços de IA na nuvem, o que elimina a transferência internacional de dados
(art. 33) e o uso do material de estudantes para treinar modelos de terceiros. Arquivos
enviados apenas para uma pergunta avulsa são lidos em memória e descartados.

**Segurança (art. 46).** Veja a seção [Segurança](#segurança): senhas com hash, arquivos
sem URL pública, permissões validadas no servidor.

A Política de Privacidade completa fica em `/privacidade`, aberta a qualquer pessoa, com
a tabela de dados, finalidade e base legal de cada coleta.

---

## Acessibilidade

Material de estudo precisa chegar a todas as pessoas. A interface segue as diretrizes
**WCAG 2.1 nível AA** e a Lei Brasileira de Inclusão (Lei 13.146/2015, art. 63).

O que está implementado:

- **Navegação completa por teclado**, com link "Pular para o conteúdo" (critério 2.4.1) e
  foco sempre visível, em contorno de 3 px (2.4.7).
- **Estrutura semântica**: regiões de navegação e conteúdo principal, hierarquia de
  títulos sem saltos, tabelas com cabeçalhos e legendas (1.3.1).
- **Avisos anunciados**: erros usam `role="alert"`, confirmações usam `role="status"`, e a
  troca de tela é comunicada por região dinâmica (4.1.3).
- **Formulários**: todo campo tem rótulo associado; erros vêm com texto, ícone e
  `aria-invalid`, ligados ao campo por `aria-describedby` (3.3.1 e 3.3.2).
- **Erro nunca só pela cor** (1.4.1) e **links sublinhados** dentro de texto corrido.
- **Contraste mínimo de 4,5:1** em todo texto (1.4.3), verificado por cálculo.
- **Zoom de 200%** sem rolagem horizontal (1.4.4).
- **`prefers-reduced-motion`** respeitado (2.3.3) e suporte a alto contraste do Windows.
- **Idioma pt-BR declarado** (3.1.1).
- Mensagens de validação escritas pela aplicação, em português — sem depender do texto
  nativo do navegador, que sai no idioma dele.

Como a verificação foi feita:

```bash
# auditoria automatizada com axe-core (0 violações nas 11 telas)
# e checagens de teclado, foco, hierarquia de títulos e zoom
# — os roteiros usados estão descritos em docs/decisoes.md
```

Limitações conhecidas estão declaradas em `/acessibilidade`, com destaque para os PDFs
digitalizados enviados por usuários, que não podem ser lidos por leitores de tela nem
pelo assistente de IA.

---

## Estrutura de pastas

```
Acervo-Edu-IA/
├── docker-compose.yml        # PostgreSQL
├── .env.example              # modelo de configuração
├── docs/decisoes.md          # decisões tomadas no projeto
├── backend/
│   ├── manage.py
│   ├── requirements.txt
│   ├── acervo_edu_ia/        # settings, urls, wsgi
│   └── apps/
│       ├── accounts/         # usuário, perfis, autenticação, LGPD (privacy.py)
│       ├── academics/        # instituições, cursos, disciplinas, categorias, tags
│       ├── documents/        # documentos, upload, publicação, download
│       └── ai/               # extração de texto, Ollama, histórico
└── frontend/
    ├── index.html
    └── src/
        ├── components/       # layout, card de documento, paginação
        ├── router/           # rotas e proteção por perfil
        ├── services/         # Axios, formatações
        ├── stores/           # Pinia (sessão e catálogo)
        └── views/            # telas (inclui privacidade e acessibilidade)
```
