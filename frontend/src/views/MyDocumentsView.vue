<script setup>
import { onMounted, ref } from 'vue'
import { RouterLink, useRouter } from 'vue-router'

import PaginacaoSimples from '@/components/PaginacaoSimples.vue'
import api, { mensagemDeErro } from '@/services/api'
import { formatarData, formatarTamanho } from '@/services/formatos'
import { useAuthStore } from '@/stores/auth'

const auth = useAuthStore()
const router = useRouter()

const documentos = ref([])
const total = ref(0)
const pagina = ref(1)
const busca = ref('')
const visibilidade = ref('')
const carregando = ref(true)
const erro = ref('')
const aviso = ref('')

async function carregar() {
  carregando.value = true
  erro.value = ''
  try {
    const params = { page: pagina.value }
    if (busca.value) params.search = busca.value
    if (visibilidade.value) params.visibility = visibilidade.value
    const { data } = await api.get('/documents/mine/', { params })
    documentos.value = data.results
    total.value = data.count
  } catch (error) {
    erro.value = mensagemDeErro(error, 'Não foi possível carregar seus documentos.')
  } finally {
    carregando.value = false
  }
}

function buscar() {
  pagina.value = 1
  carregar()
}

function mudarPagina(nova) {
  pagina.value = nova
  carregar()
}

async function alternarPublicacao(documento) {
  const publicar = documento.visibility !== 'public'
  if (publicar) {
    const confirmado = window.confirm(
      'Todos os usuários cadastrados poderão ver e baixar este documento.',
    )
    if (!confirmado) return
  }
  try {
    await api.post(`/documents/${documento.id}/${publicar ? 'publish' : 'unpublish'}/`)
    aviso.value = publicar
      ? 'Documento publicado no Acervo Público.'
      : 'Documento removido do Acervo Público.'
    carregar()
  } catch (error) {
    erro.value = mensagemDeErro(error, 'Não foi possível alterar a publicação.')
  }
}

async function excluir(documento) {
  if (!window.confirm(`Excluir "${documento.title}"? Esta ação não pode ser desfeita.`)) return
  try {
    await api.delete(`/documents/${documento.id}/`)
    aviso.value = 'Documento excluído.'
    carregar()
  } catch (error) {
    erro.value = mensagemDeErro(error, 'Não foi possível excluir o documento.')
  }
}

function perguntarIA(documento) {
  router.push({ name: 'assistente', query: { documento: documento.id } })
}

onMounted(carregar)
</script>

<template>
  <div class="pilha">
    <header class="entre">
      <div>
        <h1>Meus Documentos</h1>
        <p class="texto-suave">Seus materiais. Todo documento novo nasce privado.</p>
      </div>
      <RouterLink class="botao" :to="{ name: 'documento-novo' }">+ Novo documento</RouterLink>
    </header>

    <p v-if="erro" class="mensagem mensagem-erro">{{ erro }}</p>
    <p v-if="aviso" class="mensagem mensagem-sucesso">{{ aviso }}</p>

    <form class="cartao filtros" @submit.prevent="buscar">
      <div class="campo sem-margem">
        <label for="busca-meus">Buscar</label>
        <input id="busca-meus" v-model.trim="busca" type="search" placeholder="Título ou descrição" />
      </div>
      <div class="campo sem-margem">
        <label for="visibilidade">Visibilidade</label>
        <select id="visibilidade" v-model="visibilidade" @change="buscar">
          <option value="">Todos</option>
          <option value="private">Privados</option>
          <option value="public">Públicos</option>
        </select>
      </div>
      <button class="botao" type="submit">Buscar</button>
    </form>

    <p v-if="carregando" class="texto-suave">Carregando…</p>
    <p v-else-if="!documentos.length" class="vazio">
      Você ainda não cadastrou documentos.
      <RouterLink :to="{ name: 'documento-novo' }">Cadastre o primeiro</RouterLink>.
    </p>

    <div v-else class="cartao rolagem-horizontal">
      <table class="tabela">
        <thead>
          <tr>
            <th>Título</th>
            <th>Disciplina</th>
            <th>Situação</th>
            <th>Tamanho</th>
            <th>Criado em</th>
            <th>Ações</th>
          </tr>
        </thead>
        <tbody>
          <tr v-for="documento in documentos" :key="documento.id">
            <td>
              <RouterLink :to="{ name: 'documento-detalhes', params: { id: documento.id } }">
                {{ documento.title }}
              </RouterLink>
            </td>
            <td class="texto-suave">{{ documento.subject_name || '—' }}</td>
            <td>
              <span
                class="selo"
                :class="documento.visibility === 'public' ? 'selo-publico' : 'selo-privado'"
              >
                {{ documento.visibility === 'public' ? 'Público' : 'Privado' }}
              </span>
            </td>
            <td class="texto-suave">{{ formatarTamanho(documento.file_size) }}</td>
            <td class="texto-suave">{{ formatarData(documento.created_at) }}</td>
            <td>
              <div class="acoes">
                <RouterLink
                  class="botao botao-secundario botao-pequeno"
                  :to="{ name: 'documento-editar', params: { id: documento.id } }"
                >
                  Editar
                </RouterLink>
                <button
                  v-if="auth.podePublicar"
                  type="button"
                  class="botao botao-secundario botao-pequeno"
                  @click="alternarPublicacao(documento)"
                >
                  {{ documento.visibility === 'public' ? 'Despublicar' : 'Publicar' }}
                </button>
                <button
                  type="button"
                  class="botao botao-secundario botao-pequeno"
                  @click="perguntarIA(documento)"
                >
                  Perguntar à IA
                </button>
                <button
                  type="button"
                  class="botao botao-perigo botao-pequeno"
                  @click="excluir(documento)"
                >
                  Excluir
                </button>
              </div>
            </td>
          </tr>
        </tbody>
      </table>
    </div>

    <PaginacaoSimples :pagina="pagina" :total="total" @mudar="mudarPagina" />
  </div>
</template>

<style scoped>
.filtros {
  display: flex;
  flex-wrap: wrap;
  align-items: flex-end;
  gap: 1rem;
}

.filtros .campo {
  flex: 1;
  min-width: 180px;
}

.sem-margem {
  margin-bottom: 0;
}
</style>
