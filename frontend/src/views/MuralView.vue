<script setup>
import { onMounted, reactive, ref } from 'vue'
import { RouterLink } from 'vue-router'

import PaginacaoSimples from '@/components/PaginacaoSimples.vue'
import api, { mensagemDeErro } from '@/services/api'
import { formatarData, formatarTamanho } from '@/services/formatos'
import { useAuthStore } from '@/stores/auth'

const auth = useAuthStore()

const posts = ref([])
const total = ref(0)
const pagina = ref(1)
const carregando = ref(true)
const erro = ref('')
const aviso = ref('')

// Composição de uma nova publicação.
const novoTexto = ref('')
const tipoAnexo = ref('nenhum') // nenhum | arquivo | link | documento
const arquivoAnexo = ref(null)
const linkUrl = ref('')
const linkTitulo = ref('')
const buscaAcervo = ref('')
const resultadosAcervo = ref([])
const documentoSelecionado = ref(null)
const publicando = ref(false)

// Comentários carregados por post (id -> lista).
const comentarios = reactive({})
const comentariosAbertos = reactive({})
const novoComentario = reactive({})

// Denúncia em andamento (id do post aberto para denunciar).
const denunciaAberta = ref(null)
const motivoDenuncia = ref('spam')
const detalhesDenuncia = ref('')

const MOTIVOS = [
  { valor: 'spam', rotulo: 'Spam' },
  { valor: 'offensive', rotulo: 'Ofensivo' },
  { valor: 'copyright', rotulo: 'Direitos autorais' },
  { valor: 'other', rotulo: 'Outro' },
]

async function carregar() {
  carregando.value = true
  erro.value = ''
  try {
    const { data } = await api.get('/mural/posts/', { params: { page: pagina.value } })
    posts.value = data.results
    total.value = data.count
  } catch (error) {
    erro.value = mensagemDeErro(error, 'Não foi possível carregar o mural.')
  } finally {
    carregando.value = false
  }
}

function mudarPagina(nova) {
  pagina.value = nova
  carregar()
}

function selecionarArquivo(evento) {
  arquivoAnexo.value = evento.target.files[0] || null
}

async function buscarNoAcervo() {
  if (!buscaAcervo.value.trim()) {
    resultadosAcervo.value = []
    return
  }
  try {
    const { data } = await api.get('/documents/public/', {
      params: { search: buscaAcervo.value, page_size: 5 },
    })
    resultadosAcervo.value = data.results
  } catch {
    resultadosAcervo.value = []
  }
}

function escolherDocumento(documento) {
  documentoSelecionado.value = documento
  resultadosAcervo.value = []
  buscaAcervo.value = documento.title
}

function limparComposicao() {
  novoTexto.value = ''
  tipoAnexo.value = 'nenhum'
  arquivoAnexo.value = null
  linkUrl.value = ''
  linkTitulo.value = ''
  buscaAcervo.value = ''
  resultadosAcervo.value = []
  documentoSelecionado.value = null
}

async function publicar() {
  erro.value = ''
  const dados = new FormData()
  dados.append('text', novoTexto.value)
  if (tipoAnexo.value === 'arquivo' && arquivoAnexo.value) {
    dados.append('attachment_file', arquivoAnexo.value)
  } else if (tipoAnexo.value === 'link' && linkUrl.value) {
    dados.append('attachment_url', linkUrl.value)
    if (linkTitulo.value) dados.append('attachment_link_title', linkTitulo.value)
  } else if (tipoAnexo.value === 'documento' && documentoSelecionado.value) {
    dados.append('attachment_document_id', documentoSelecionado.value.id)
  }

  publicando.value = true
  try {
    await api.post('/mural/posts/', dados)
    limparComposicao()
    aviso.value = 'Publicado no mural.'
    pagina.value = 1
    carregar()
  } catch (error) {
    erro.value = mensagemDeErro(error, 'Não foi possível publicar.')
  } finally {
    publicando.value = false
  }
}

async function alternarComentarios(post) {
  comentariosAbertos[post.id] = !comentariosAbertos[post.id]
  if (comentariosAbertos[post.id] && !comentarios[post.id]) {
    try {
      const { data } = await api.get(`/mural/posts/${post.id}/comments/`)
      comentarios[post.id] = data.results
    } catch (error) {
      erro.value = mensagemDeErro(error, 'Não foi possível carregar os comentários.')
    }
  }
}

async function enviarComentario(post) {
  const texto = (novoComentario[post.id] || '').trim()
  if (!texto) return
  try {
    await api.post('/mural/posts/', { parent: post.id, text: texto })
    novoComentario[post.id] = ''
    const { data } = await api.get(`/mural/posts/${post.id}/comments/`)
    comentarios[post.id] = data.results
    post.comments_count += 1
  } catch (error) {
    erro.value = mensagemDeErro(error, 'Não foi possível comentar.')
  }
}

function abrirDenuncia(post) {
  denunciaAberta.value = denunciaAberta.value === post.id ? null : post.id
  motivoDenuncia.value = 'spam'
  detalhesDenuncia.value = ''
}

async function confirmarDenuncia(post) {
  try {
    await api.post(`/mural/posts/${post.id}/report/`, {
      reason: motivoDenuncia.value,
      details: detalhesDenuncia.value,
    })
    aviso.value = 'Denúncia registrada. Obrigado por ajudar a manter o mural seguro.'
    denunciaAberta.value = null
  } catch (error) {
    erro.value = mensagemDeErro(error, 'Não foi possível registrar a denúncia.')
  }
}

async function excluirPost(post) {
  if (!window.confirm('Excluir esta publicação? Esta ação não pode ser desfeita.')) return
  try {
    await api.delete(`/mural/posts/${post.id}/`)
    aviso.value = 'Publicação excluída.'
    carregar()
  } catch (error) {
    erro.value = mensagemDeErro(error, 'Não foi possível excluir a publicação.')
  }
}

function urlArquivo(anexo, download) {
  const base = api.defaults.baseURL.replace(/\/$/, '')
  return `${base}/mural/attachments/${anexo.id}/file/${download ? '?download=1' : ''}`
}

onMounted(carregar)
</script>

<template>
  <div class="pilha">
    <header>
      <h1>Mural Público</h1>
      <p class="texto-suave">
        Visível para todos, inclusive visitantes sem login. Seja respeitoso e compartilhe apenas
        o que você tem direito de compartilhar.
      </p>
    </header>

    <p v-if="erro" class="mensagem mensagem-erro" role="alert">{{ erro }}</p>
    <p v-if="aviso" class="mensagem mensagem-sucesso" role="status">{{ aviso }}</p>

    <form v-if="auth.autenticado" class="cartao" @submit.prevent="publicar">
      <div class="campo">
        <label for="mural-texto">Compartilhar algo</label>
        <textarea
          id="mural-texto"
          v-model.trim="novoTexto"
          rows="3"
          placeholder="Compartilhe um documento, artigo ou link…"
        ></textarea>
      </div>

      <fieldset class="campo">
        <legend>Anexo (opcional)</legend>
        <div class="opcoes-anexo">
          <label><input v-model="tipoAnexo" type="radio" value="nenhum" /> Nenhum</label>
          <label><input v-model="tipoAnexo" type="radio" value="arquivo" /> Arquivo</label>
          <label><input v-model="tipoAnexo" type="radio" value="link" /> Link</label>
          <label><input v-model="tipoAnexo" type="radio" value="documento" /> Documento do acervo</label>
        </div>
      </fieldset>

      <div v-if="tipoAnexo === 'arquivo'" class="campo">
        <label for="mural-arquivo">Arquivo (até 20 MB)</label>
        <input
          id="mural-arquivo"
          type="file"
          accept=".pdf,.docx,.pptx,.xlsx,.txt,.png,.jpg,.jpeg,.gif,.webp"
          @change="selecionarArquivo"
        />
      </div>

      <div v-else-if="tipoAnexo === 'link'" class="linha-campos">
        <div class="campo">
          <label for="mural-link-url">URL</label>
          <input id="mural-link-url" v-model.trim="linkUrl" type="url" placeholder="https://…" />
        </div>
        <div class="campo">
          <label for="mural-link-titulo">Título do link (opcional)</label>
          <input id="mural-link-titulo" v-model.trim="linkTitulo" type="text" maxlength="255" />
        </div>
      </div>

      <div v-else-if="tipoAnexo === 'documento'" class="campo">
        <label for="mural-busca-acervo">Buscar no Acervo Público</label>
        <input
          id="mural-busca-acervo"
          v-model.trim="buscaAcervo"
          type="search"
          placeholder="Título do documento"
          @input="buscarNoAcervo"
        />
        <p v-if="documentoSelecionado" class="campo-ajuda">
          Selecionado: <strong>{{ documentoSelecionado.title }}</strong>
        </p>
        <ul v-if="resultadosAcervo.length" class="lista-resultados">
          <li v-for="documento in resultadosAcervo" :key="documento.id">
            <button type="button" class="botao-link" @click="escolherDocumento(documento)">
              {{ documento.title }}
            </button>
          </li>
        </ul>
        <p class="campo-ajuda">Só documentos do Acervo Público podem ser compartilhados.</p>
      </div>

      <div class="acoes">
        <button class="botao" type="submit" :disabled="publicando">
          {{ publicando ? 'Publicando…' : 'Publicar' }}
        </button>
      </div>
    </form>
    <p v-else class="mensagem mensagem-aviso">
      <RouterLink :to="{ name: 'entrar' }">Entre</RouterLink> para publicar ou comentar no mural.
    </p>

    <p v-if="carregando" class="texto-suave" role="status">Carregando…</p>
    <p v-else-if="!posts.length" class="vazio">Ainda não há publicações no mural.</p>

    <article v-for="post in posts" :key="post.id" class="cartao publicacao-mural">
      <header class="entre">
        <div>
          <strong>{{ post.author_name }}</strong>
          <span v-if="post.author_institution" class="texto-suave"> · {{ post.author_institution }}</span>
          <p class="texto-suave">{{ formatarData(post.created_at) }}</p>
        </div>
        <div class="acoes">
          <button
            v-if="post.permissions.can_edit"
            type="button"
            class="botao botao-perigo botao-pequeno"
            @click="excluirPost(post)"
          >
            Excluir
          </button>
          <button
            v-if="auth.autenticado && !post.permissions.can_edit"
            type="button"
            class="botao botao-secundario botao-pequeno"
            @click="abrirDenuncia(post)"
          >
            Denunciar
          </button>
        </div>
      </header>

      <p v-if="post.text">{{ post.text }}</p>

      <div v-if="post.attachments.length" class="anexos-mural">
        <div v-for="anexo in post.attachments" :key="anexo.id" class="anexo-mural">
          <template v-if="anexo.kind === 'file'">
            <a :href="urlArquivo(anexo, false)" target="_blank" rel="noopener">
              📎 {{ anexo.original_filename }}
            </a>
            <span class="texto-suave"> · {{ formatarTamanho(anexo.size_bytes) }}</span>
          </template>
          <template v-else-if="anexo.kind === 'link'">
            <a :href="anexo.url" target="_blank" rel="noopener nofollow">
              🔗 {{ anexo.link_title || anexo.url }}
            </a>
          </template>
          <template v-else-if="anexo.kind === 'document'">
            <RouterLink :to="{ name: 'documento-detalhes', params: { id: anexo.document } }">
              📄 {{ anexo.document_title }}
            </RouterLink>
          </template>
        </div>
      </div>

      <div v-if="denunciaAberta === post.id" class="cartao denuncia-mural">
        <div class="campo">
          <label :for="`motivo-${post.id}`">Motivo</label>
          <select :id="`motivo-${post.id}`" v-model="motivoDenuncia">
            <option v-for="m in MOTIVOS" :key="m.valor" :value="m.valor">{{ m.rotulo }}</option>
          </select>
        </div>
        <div class="campo">
          <label :for="`detalhes-${post.id}`">Detalhes (opcional)</label>
          <textarea :id="`detalhes-${post.id}`" v-model.trim="detalhesDenuncia" rows="2"></textarea>
        </div>
        <div class="acoes">
          <button class="botao botao-perigo botao-pequeno" type="button" @click="confirmarDenuncia(post)">
            Enviar denúncia
          </button>
          <button class="botao botao-secundario botao-pequeno" type="button" @click="denunciaAberta = null">
            Cancelar
          </button>
        </div>
      </div>

      <button type="button" class="botao-link" @click="alternarComentarios(post)">
        {{ comentariosAbertos[post.id] ? 'Ocultar' : 'Ver' }} comentários ({{ post.comments_count }})
      </button>

      <div v-if="comentariosAbertos[post.id]" class="comentarios-mural">
        <p v-for="comentario in comentarios[post.id] || []" :key="comentario.id" class="comentario-mural">
          <strong>{{ comentario.author_name }}</strong> · <span class="texto-suave">{{ formatarData(comentario.created_at) }}</span>
          <br />
          {{ comentario.text }}
        </p>
        <form v-if="auth.autenticado" class="linha-comentario" @submit.prevent="enviarComentario(post)">
          <input
            v-model.trim="novoComentario[post.id]"
            type="text"
            placeholder="Escreva um comentário…"
            maxlength="2000"
          />
          <button class="botao botao-secundario botao-pequeno" type="submit">Comentar</button>
        </form>
      </div>
    </article>

    <PaginacaoSimples :pagina="pagina" :total="total" @mudar="mudarPagina" />
  </div>
</template>

<style scoped>
.opcoes-anexo {
  display: flex;
  flex-wrap: wrap;
  gap: 1rem;
}

.opcoes-anexo label {
  display: flex;
  align-items: center;
  gap: 0.35rem;
  font-weight: 400;
}

.lista-resultados {
  list-style: none;
  margin: 0.35rem 0 0;
  padding: 0;
  display: flex;
  flex-direction: column;
  gap: 0.25rem;
}

.botao-link {
  background: none;
  border: none;
  color: var(--cor-primaria, #1976a8);
  cursor: pointer;
  padding: 0.35rem 0;
  text-align: left;
  text-decoration: underline;
  font: inherit;
}

.publicacao-mural {
  display: flex;
  flex-direction: column;
  gap: 0.6rem;
}

.anexos-mural {
  display: flex;
  flex-direction: column;
  gap: 0.4rem;
}

.anexo-mural {
  padding: 0.5rem 0.75rem;
  border: 1px solid var(--cor-borda, #d8dee6);
  border-radius: 0.5rem;
}

.denuncia-mural {
  background: var(--cor-fundo-suave, #f4f6f8);
}

.comentarios-mural {
  display: flex;
  flex-direction: column;
  gap: 0.5rem;
  border-top: 1px solid var(--cor-borda, #d8dee6);
  padding-top: 0.5rem;
}

.comentario-mural {
  margin: 0;
}

.linha-comentario {
  display: flex;
  gap: 0.5rem;
}

.linha-comentario input {
  flex: 1;
}
</style>
