<script setup>
import { computed, onMounted, ref } from 'vue'
import { RouterLink } from 'vue-router'

import DocumentCard from '@/components/DocumentCard.vue'
import api, { mensagemDeErro } from '@/services/api'
import { formatarData } from '@/services/formatos'
import { useAuthStore } from '@/stores/auth'

const auth = useAuthStore()
const contadores = ref(null)
const recentes = ref([])
const muralRecente = ref([])
const carregando = ref(true)
const erro = ref('')

const atalhos = computed(() => {
  const base = [
    {
      nome: 'acervo',
      titulo: 'Acervo Público',
      texto: 'Pesquise materiais publicados por outras instituições.',
      icone: '📚',
    },
    {
      nome: 'mural',
      titulo: 'Mural Público',
      texto: 'Veja o que a comunidade está compartilhando.',
      icone: '📣',
    },
  ]
  if (auth.autenticado) {
    base.push(
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
    )
  }
  return base
})

onMounted(async () => {
  try {
    const chamadas = [
      api.get('/documents/public/', { params: { page_size: 6 } }),
      api.get('/mural/posts/', { params: { page_size: 3 } }),
    ]
    if (auth.autenticado) chamadas.push(api.get('/documents/stats/'))

    const [publicos, mural, stats] = await Promise.all(chamadas)
    recentes.value = publicos.data.results.slice(0, 6)
    muralRecente.value = mural.data.results
    if (stats) contadores.value = stats.data
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
      <template v-if="auth.autenticado">
        <h1>Olá, {{ auth.user?.name?.split(' ')[0] }}! <span aria-hidden="true">👋</span></h1>
        <p class="texto-suave">
          Você está no perfil <strong>{{ auth.perfilTexto }}</strong
          >.
        </p>
      </template>
      <template v-else>
        <h1>Conhecimento organizado e acessível</h1>
        <p class="texto-suave">
          Acervo educacional para instituições públicas e privadas — documentos abertos e mural
          público de compartilhamento. Sem login você vê os documentos <strong>públicos</strong> e o
          <strong>mural público</strong>. <RouterLink :to="{ name: 'entrar' }">Entre</RouterLink>
          para acessar o acervo da sua instituição.
        </p>
      </template>
    </header>

    <p v-if="erro" class="mensagem mensagem-erro" role="alert">{{ erro }}</p>

    <section v-if="contadores" class="contadores" aria-labelledby="titulo-contadores">
      <h2 id="titulo-contadores" class="apenas-leitor-de-tela">Resumo da sua conta</h2>
      <div class="cartao contador">
        <span class="icone-contador cor-azul" aria-hidden="true">📁</span>
        <span class="numero">{{ contadores.my_documents }}</span>
        <span class="texto-suave">Meus documentos</span>
      </div>
      <div class="cartao contador">
        <span class="icone-contador cor-verde" aria-hidden="true">✅</span>
        <span class="numero">{{ contadores.my_published }}</span>
        <span class="texto-suave">Meus publicados</span>
      </div>
      <div class="cartao contador">
        <span class="icone-contador cor-roxo" aria-hidden="true">📚</span>
        <span class="numero">{{ contadores.public_documents }}</span>
        <span class="texto-suave">No Acervo Público</span>
      </div>
      <template v-if="auth.podeGerenciarCatalogo">
        <div class="cartao contador">
          <span class="icone-contador cor-laranja" aria-hidden="true">🗂️</span>
          <span class="numero">{{ contadores.total_documents }}</span>
          <span class="texto-suave">Total de documentos</span>
        </div>
        <div class="cartao contador">
          <span class="icone-contador cor-azul" aria-hidden="true">👥</span>
          <span class="numero">{{ contadores.total_users }}</span>
          <span class="texto-suave">Usuários ativos</span>
        </div>
      </template>
    </section>

    <section aria-labelledby="titulo-atalhos">
      <h2 id="titulo-atalhos" class="apenas-leitor-de-tela">Atalhos</h2>
      <div class="grade-cartoes">
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
      </div>
    </section>

    <section aria-labelledby="titulo-recentes">
      <div class="entre">
        <h2 id="titulo-recentes">Últimos publicados</h2>
        <RouterLink :to="{ name: 'acervo' }">Ver todo o acervo →</RouterLink>
      </div>
      <p v-if="carregando" class="texto-suave" role="status">Carregando…</p>
      <p v-else-if="!recentes.length" class="vazio">Ainda não há documentos publicados.</p>
      <div v-else class="grade-cartoes">
        <DocumentCard v-for="documento in recentes" :key="documento.id" :documento="documento" />
      </div>
    </section>

    <section aria-labelledby="titulo-mural">
      <div class="entre">
        <h2 id="titulo-mural">Mural público</h2>
        <RouterLink :to="{ name: 'mural' }">Abrir mural →</RouterLink>
      </div>
      <p v-if="!carregando && !muralRecente.length" class="vazio">Ainda não há publicações.</p>
      <ul v-else class="lista-mural-previa">
        <li v-for="post in muralRecente" :key="post.id" class="cartao">
          <strong>{{ post.author_name }}</strong>
          <span class="texto-suave"> · {{ formatarData(post.created_at) }}</span>
          <p>{{ post.text || '(publicação com anexo)' }}</p>
        </li>
      </ul>
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

.icone-contador {
  width: 2.4rem;
  height: 2.4rem;
  display: flex;
  align-items: center;
  justify-content: center;
  border-radius: var(--raio);
  font-size: 1.15rem;
  margin-bottom: 0.5rem;
}

.icone-contador.cor-azul {
  background: var(--selo-comunidade-fundo);
}

.icone-contador.cor-verde {
  background: var(--selo-publico-fundo);
}

.icone-contador.cor-roxo {
  background: #ece4fa;
}

.icone-contador.cor-laranja {
  background: var(--selo-restrito-fundo);
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

.lista-mural-previa {
  list-style: none;
  margin: 0;
  padding: 0;
  display: flex;
  flex-direction: column;
  gap: 0.6rem;
}

.lista-mural-previa p {
  margin: 0.35rem 0 0;
}
</style>
