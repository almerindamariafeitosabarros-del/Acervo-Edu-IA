<script setup>
import { onMounted, reactive, ref } from 'vue'
import { RouterLink } from 'vue-router'

import PaginacaoSimples from '@/components/PaginacaoSimples.vue'
import api, { mensagemDeErro } from '@/services/api'
import { formatarData } from '@/services/formatos'
import { useCatalogoStore } from '@/stores/catalogo'

const catalogo = useCatalogoStore()

const documentos = ref([])
const total = ref(0)
const pagina = ref(1)
const carregando = ref(true)
const erro = ref('')
const aviso = ref('')

const filtros = reactive({ search: '', visibility: '', institution: '', category: '' })

async function carregar() {
  carregando.value = true
  erro.value = ''
  try {
    const params = { page: pagina.value }
    Object.entries(filtros).forEach(([chave, valor]) => {
      if (valor) params[chave] = valor
    })
    const { data } = await api.get('/documents/all/', { params })
    documentos.value = data.results
    total.value = data.count
  } catch (error) {
    erro.value = mensagemDeErro(error, 'Não foi possível carregar os documentos.')
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
    aviso.value = publicar ? 'Documento publicado.' : 'Documento removido do Acervo Público.'
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

onMounted(async () => {
  await catalogo.carregar().catch(() => {})
  carregar()
})
</script>

<template>
  <div class="pilha">
    <p v-if="erro" class="mensagem mensagem-erro">{{ erro }}</p>
    <p v-if="aviso" class="mensagem mensagem-sucesso">{{ aviso }}</p>

    <form class="cartao linha-campos" @submit.prevent="buscar">
      <div class="campo">
        <label for="a-busca">Buscar</label>
        <input id="a-busca" v-model.trim="filtros.search" type="search" placeholder="Título ou dono" />
      </div>
      <div class="campo">
        <label for="a-visibilidade">Visibilidade</label>
        <select id="a-visibilidade" v-model="filtros.visibility">
          <option value="">Todas</option>
          <option value="private">Privados</option>
          <option value="public">Públicos</option>
        </select>
      </div>
      <div class="campo">
        <label for="a-instituicao">Instituição</label>
        <select id="a-instituicao" v-model="filtros.institution">
          <option value="">Todas</option>
          <option v-for="i in catalogo.instituicoes" :key="i.id" :value="i.id">{{ i.name }}</option>
        </select>
      </div>
      <div class="campo">
        <label for="a-categoria">Categoria</label>
        <select id="a-categoria" v-model="filtros.category">
          <option value="">Todas</option>
          <option v-for="c in catalogo.categorias" :key="c.id" :value="c.id">{{ c.name }}</option>
        </select>
      </div>
      <div class="campo">
        <label>&nbsp;</label>
        <button class="botao" type="submit">Buscar</button>
      </div>
    </form>

    <section class="cartao">
      <p class="texto-suave">
        {{ carregando ? 'Carregando…' : `${total} documento(s)` }}
      </p>
      <div class="rolagem-horizontal">
        <table class="tabela">
          <thead>
            <tr>
              <th>Título</th>
              <th>Dono</th>
              <th>Disciplina</th>
              <th>Situação</th>
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
              <td class="texto-suave">{{ documento.owner_name }}</td>
              <td class="texto-suave">{{ documento.subject_name || '—' }}</td>
              <td>
                <span
                  class="selo"
                  :class="documento.visibility === 'public' ? 'selo-publico' : 'selo-privado'"
                >
                  {{ documento.visibility_display }}
                </span>
              </td>
              <td class="texto-suave">{{ formatarData(documento.created_at) }}</td>
              <td>
                <div class="acoes">
                  <button
                    type="button"
                    class="botao botao-secundario botao-pequeno"
                    @click="alternarPublicacao(documento)"
                  >
                    {{ documento.visibility === 'public' ? 'Despublicar' : 'Publicar' }}
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
    </section>
  </div>
</template>
