<script setup>
import { onMounted, reactive, ref, watch } from 'vue'
import { useRoute } from 'vue-router'

import DocumentCard from '@/components/DocumentCard.vue'
import PaginacaoSimples from '@/components/PaginacaoSimples.vue'
import api, { mensagemDeErro } from '@/services/api'
import { useCatalogoStore } from '@/stores/catalogo'

const catalogo = useCatalogoStore()
const route = useRoute()

const documentos = ref([])
const total = ref(0)
const pagina = ref(1)
// Começa carregando: sem isso a tela mostra "0 documentos" por um instante,
// e o leitor de tela anuncia esse zero como se fosse o resultado real.
const carregando = ref(true)
const erro = ref('')

const filtros = reactive({
  search: '',
  institution: '',
  course: '',
  subject: '',
  category: '',
  author: '',
})

async function buscar() {
  carregando.value = true
  erro.value = ''
  try {
    const params = { page: pagina.value }
    Object.entries(filtros).forEach(([chave, valor]) => {
      if (valor) params[chave] = valor
    })
    const { data } = await api.get('/documents/public/', { params })
    documentos.value = data.results
    total.value = data.count
  } catch (error) {
    erro.value = mensagemDeErro(error, 'Não foi possível carregar o acervo.')
  } finally {
    carregando.value = false
  }
}

function aplicarFiltros() {
  pagina.value = 1
  buscar()
}

function limpar() {
  Object.keys(filtros).forEach((chave) => {
    filtros[chave] = ''
  })
  aplicarFiltros()
}

// Os selects são encadeados: trocar a instituição zera curso e disciplina.
watch(
  () => filtros.institution,
  () => {
    filtros.course = ''
    filtros.subject = ''
  },
)

watch(
  () => filtros.course,
  () => {
    filtros.subject = ''
  },
)

function mudarPagina(nova) {
  pagina.value = nova
  buscar()
}

onMounted(async () => {
  // Busca vinda da caixa de pesquisa do topo (AppLayout), via ?search=.
  if (typeof route.query.search === 'string') {
    filtros.search = route.query.search
  }
  await catalogo.carregar().catch(() => {})
  buscar()
})
</script>

<template>
  <div class="pilha">
    <header>
      <h1>Acervo Público</h1>
      <p class="texto-suave">Materiais publicados e disponíveis para todos os cadastrados.</p>
    </header>

    <form class="cartao" @submit.prevent="aplicarFiltros">
      <div class="campo">
        <label for="busca">Buscar</label>
        <input
          id="busca"
          v-model.trim="filtros.search"
          type="search"
          placeholder="Título, descrição, autor ou tag"
        />
      </div>

      <div class="linha-campos">
        <div class="campo">
          <label for="f-instituicao">Instituição</label>
          <select id="f-instituicao" v-model="filtros.institution">
            <option value="">Todas</option>
            <option v-for="i in catalogo.instituicoes" :key="i.id" :value="i.id">{{ i.name }}</option>
          </select>
        </div>
        <div class="campo">
          <label for="f-curso">Curso</label>
          <select id="f-curso" v-model="filtros.course">
            <option value="">Todos</option>
            <option
              v-for="c in catalogo.cursosDaInstituicao(filtros.institution)"
              :key="c.id"
              :value="c.id"
            >
              {{ c.name }}
            </option>
          </select>
        </div>
        <div class="campo">
          <label for="f-disciplina">Disciplina</label>
          <select id="f-disciplina" v-model="filtros.subject">
            <option value="">Todas</option>
            <option
              v-for="d in catalogo.disciplinasDoCurso(filtros.course)"
              :key="d.id"
              :value="d.id"
            >
              {{ d.name }}
            </option>
          </select>
        </div>
        <div class="campo">
          <label for="f-categoria">Categoria</label>
          <select id="f-categoria" v-model="filtros.category">
            <option value="">Todas</option>
            <option v-for="c in catalogo.categorias" :key="c.id" :value="c.id">{{ c.name }}</option>
          </select>
        </div>
        <div class="campo">
          <label for="f-autor">Autor do material</label>
          <input id="f-autor" v-model.trim="filtros.author" type="text" placeholder="Nome do autor" />
        </div>
      </div>

      <div class="acoes">
        <button class="botao" type="submit" :disabled="carregando">Buscar</button>
        <button class="botao botao-secundario" type="button" @click="limpar">Limpar filtros</button>
      </div>
    </form>

    <p v-if="erro" class="mensagem mensagem-erro" role="alert">{{ erro }}</p>

    <section>
      <p class="texto-suave resultado" role="status" aria-live="polite">
        {{ carregando ? 'Carregando…' : `${total} documento(s) encontrado(s)` }}
      </p>
      <div v-if="documentos.length" class="grade-cartoes">
        <DocumentCard v-for="documento in documentos" :key="documento.id" :documento="documento" />
      </div>
      <p v-else-if="!carregando" class="vazio">
        Nenhum documento encontrado. Tente outra busca ou limpe os filtros.
      </p>
      <PaginacaoSimples :pagina="pagina" :total="total" @mudar="mudarPagina" />
    </section>
  </div>
</template>

<style scoped>
.resultado {
  margin-bottom: 0.75rem;
}
</style>
