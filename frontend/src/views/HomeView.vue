<script setup>
import { onMounted, ref } from 'vue'
import { RouterLink } from 'vue-router'

import DocumentCard from '@/components/DocumentCard.vue'
import api, { mensagemDeErro } from '@/services/api'
import { useAuthStore } from '@/stores/auth'

const auth = useAuthStore()
const contadores = ref(null)
const recentes = ref([])
const carregando = ref(true)
const erro = ref('')

const atalhos = [
  {
    nome: 'acervo',
    titulo: 'Acervo Público',
    texto: 'Pesquise materiais publicados por outros usuários.',
    icone: '📚',
  },
  {
    nome: 'meus-documentos',
    titulo: 'Meus Documentos',
    texto: 'Cadastre e organize seus próprios materiais.',
    icone: '📁',
  },
  {
    nome: 'assistente',
    titulo: 'Assistente IA',
    texto: 'Pergunte sobre um documento e receba a resposta na hora.',
    icone: '🤖',
  },
]

onMounted(async () => {
  try {
    const [stats, publicos] = await Promise.all([
      api.get('/documents/stats/'),
      api.get('/documents/public/', { params: { page_size: 6 } }),
    ])
    contadores.value = stats.data
    recentes.value = publicos.data.results.slice(0, 6)
  } catch (error) {
    erro.value = mensagemDeErro(error, 'Não foi possível carregar a tela de início.')
  } finally {
    carregando.value = false
  }
})
</script>

<template>
  <div class="pilha">
    <header>
      <h1>Olá, {{ auth.user?.name?.split(' ')[0] }}! 👋</h1>
      <p class="texto-suave">
        Você está no perfil <strong>{{ auth.perfilTexto }}</strong
        >.
      </p>
    </header>

    <p v-if="erro" class="mensagem mensagem-erro">{{ erro }}</p>

    <section v-if="contadores" class="contadores">
      <div class="cartao contador">
        <span class="numero">{{ contadores.my_documents }}</span>
        <span class="texto-suave">Meus documentos</span>
      </div>
      <div class="cartao contador">
        <span class="numero">{{ contadores.my_published }}</span>
        <span class="texto-suave">Meus publicados</span>
      </div>
      <div class="cartao contador">
        <span class="numero">{{ contadores.public_documents }}</span>
        <span class="texto-suave">No Acervo Público</span>
      </div>
      <template v-if="auth.podeGerenciarCatalogo">
        <div class="cartao contador">
          <span class="numero">{{ contadores.total_documents }}</span>
          <span class="texto-suave">Total de documentos</span>
        </div>
        <div class="cartao contador">
          <span class="numero">{{ contadores.total_users }}</span>
          <span class="texto-suave">Usuários ativos</span>
        </div>
      </template>
    </section>

    <section class="grade-cartoes">
      <RouterLink
        v-for="atalho in atalhos"
        :key="atalho.nome"
        :to="{ name: atalho.nome }"
        class="cartao atalho"
      >
        <span class="icone" aria-hidden="true">{{ atalho.icone }}</span>
        <h3>{{ atalho.titulo }}</h3>
        <p class="texto-suave">{{ atalho.texto }}</p>
      </RouterLink>
    </section>

    <section>
      <div class="entre">
        <h2>Últimos publicados</h2>
        <RouterLink :to="{ name: 'acervo' }">Ver todo o acervo →</RouterLink>
      </div>
      <p v-if="carregando" class="texto-suave">Carregando…</p>
      <p v-else-if="!recentes.length" class="vazio">Ainda não há documentos publicados.</p>
      <div v-else class="grade-cartoes">
        <DocumentCard v-for="documento in recentes" :key="documento.id" :documento="documento" />
      </div>
    </section>
  </div>
</template>

<style scoped>
.contadores {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(150px, 1fr));
  gap: 1rem;
}

.contador {
  display: flex;
  flex-direction: column;
  gap: 0.15rem;
  padding: 1rem;
}

.numero {
  font-size: 1.8rem;
  font-weight: 700;
  color: var(--cor-primaria);
}

.atalho {
  color: inherit;
  display: block;
}

.atalho:hover {
  border-color: var(--cor-primaria);
  text-decoration: none;
}

.icone {
  font-size: 1.6rem;
}
</style>
