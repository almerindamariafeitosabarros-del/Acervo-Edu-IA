<script setup>
import { computed, ref, watch } from 'vue'
import { RouterLink, RouterView, useRoute, useRouter } from 'vue-router'

import { useAuthStore } from '@/stores/auth'
import LogoMarca from '@/components/marca/LogoMarca.vue'

const auth = useAuthStore()
const router = useRouter()
const route = useRoute()
const menuAberto = ref(false)
const buscaTopo = ref('')

const iniciais = computed(() => {
  const nome = auth.user?.name || ''
  return nome
    .split(' ')
    .filter(Boolean)
    .slice(0, 2)
    .map((parte) => parte[0]?.toUpperCase())
    .join('')
})

function buscarNoTopo() {
  if (!buscaTopo.value.trim()) return
  router.push({ name: 'acervo', query: { search: buscaTopo.value.trim() } })
  menuAberto.value = false
}

// Leitores de tela não percebem a troca de página em uma SPA: avisamos aqui.
const anuncio = ref('')
watch(
  () => route.name,
  () => {
    anuncio.value = `${route.meta.titulo || 'Página'} carregada.`
  },
)

// O menu mostra apenas as telas permitidas ao perfil. Início, Acervo Público
// e Mural também abrem para visitantes sem login (RF18, RF20).
const itens = computed(() => {
  const base = [
    { nome: 'inicio', rotulo: 'Início', icone: '🏠' },
    { nome: 'acervo', rotulo: 'Acervo Público', icone: '📚' },
    { nome: 'mural', rotulo: 'Mural Público', icone: '📣' },
  ]
  if (auth.autenticado) {
    base.push(
      { nome: 'meus-documentos', rotulo: 'Meus Documentos', icone: '📁' },
      { nome: 'assistente', rotulo: 'Assistente IA', icone: '🤖' },
      { nome: 'perfil', rotulo: 'Meu Perfil', icone: '👤' },
    )
  }
  if (auth.podeModerarMural) {
    base.push({ nome: 'moderacao', rotulo: 'Moderação', icone: '🚩' })
  }
  if (auth.podeGerenciarCatalogo) {
    base.push({ nome: 'administracao', rotulo: 'Administração', icone: '⚙️' })
  }
  return base
})

function sair() {
  auth.sair()
  router.push({ name: 'entrar' })
}
</script>

<template>
  <div class="layout">
    <!-- Primeiro elemento focável da página: permite pular o menu (WCAG 2.4.1). -->
    <a href="#conteudo-principal" class="pular-conteudo">Pular para o conteúdo</a>

    <aside id="menu-lateral" class="menu" :class="{ aberto: menuAberto }">
      <nav aria-label="Menu principal">
        <ul class="lista-menu">
          <li v-for="item in itens" :key="item.nome">
            <RouterLink
              :to="{ name: item.nome }"
              class="item"
              :aria-current="$route.name === item.nome ? 'page' : undefined"
              @click="menuAberto = false"
            >
              <span aria-hidden="true">{{ item.icone }}</span>
              {{ item.rotulo }}
            </RouterLink>
          </li>
        </ul>
      </nav>

      <div class="rodape-menu">
        <p class="links-legais">
          <RouterLink :to="{ name: 'privacidade' }">Privacidade</RouterLink>
          <span aria-hidden="true">·</span>
          <RouterLink :to="{ name: 'acessibilidade' }">Acessibilidade</RouterLink>
        </p>
      </div>
    </aside>

    <div class="conteudo">
      <header class="topo">
        <button
          type="button"
          class="botao botao-secundario botao-pequeno alternar-menu"
          :aria-expanded="menuAberto"
          aria-controls="menu-lateral"
          @click="menuAberto = !menuAberto"
        >
          <span aria-hidden="true">☰</span>
          <span class="apenas-leitor-de-tela">Menu</span>
        </button>

        <RouterLink :to="{ name: 'inicio' }" class="marca">
          <LogoMarca :tamanho="34" />
          <span class="nome-marca"
            ><span class="marca-marinho">Acervo Edu</span> <span class="marca-azul">IA</span></span
          >
        </RouterLink>

        <form class="busca-topo" role="search" @submit.prevent="buscarNoTopo">
          <label for="busca-topo" class="apenas-leitor-de-tela">Pesquisar no acervo</label>
          <span aria-hidden="true" class="icone-busca">🔍</span>
          <input
            id="busca-topo"
            v-model.trim="buscaTopo"
            type="search"
            placeholder="Pesquise por documentos, assuntos, autores…"
          />
        </form>

        <div class="usuario-topo">
          <template v-if="auth.autenticado">
            <RouterLink :to="{ name: 'perfil' }" class="cartao-usuario">
              <span class="avatar" aria-hidden="true">{{ iniciais || '?' }}</span>
              <span class="dados-usuario">
                <span class="nome-usuario">{{ auth.user?.name }}</span>
                <span class="perfil-usuario">{{ auth.perfilTexto }}</span>
              </span>
            </RouterLink>
            <button type="button" class="botao botao-secundario botao-pequeno" @click="sair">
              Sair
            </button>
          </template>
          <RouterLink v-else class="botao botao-pequeno" :to="{ name: 'entrar' }">Entrar</RouterLink>
        </div>
      </header>

      <main id="conteudo-principal" class="principal" tabindex="-1">
        <RouterView />
      </main>
    </div>

    <!-- Anuncia a troca de tela para quem usa leitor de tela (WCAG 4.1.3). -->
    <p aria-live="polite" class="apenas-leitor-de-tela">{{ anuncio }}</p>
  </div>
</template>

<style scoped>
.layout {
  display: flex;
  min-height: 100vh;
}

.menu {
  width: 240px;
  flex-shrink: 0;
  background: var(--cor-marinho);
  color: #ffffff;
  border-right: none;
  display: flex;
  flex-direction: column;
  padding: 1.25rem 1rem;
  gap: 1.5rem;
}

/* O azul da marca contrasta pouco com o marinho do menu (2,3:1, manual seção
   08): o foco por teclado precisa de um anel próprio aqui para continuar
   visível (WCAG 2.4.7 / 1.4.11). */
.menu :focus-visible {
  outline-color: #ffffff;
}

nav {
  flex: 1;
}

.lista-menu {
  list-style: none;
  margin: 0;
  padding: 0;
  display: flex;
  flex-direction: column;
  gap: 0.25rem;
}

.links-legais {
  margin: 0.75rem 0 0;
  font-size: 0.78rem;
  display: flex;
  gap: 0.35rem;
  flex-wrap: wrap;
}

.item {
  display: flex;
  align-items: center;
  gap: 0.6rem;
  padding: 0.6rem 0.7rem;
  border-radius: var(--raio);
  color: var(--cor-texto-sobre-marinho);
  font-weight: 500;
}

.item:hover {
  background: rgba(255, 255, 255, 0.1);
  color: #ffffff;
  text-decoration: none;
}

.item[aria-current='page'] {
  background: var(--cor-azul);
  color: #ffffff;
  font-weight: 600;
}

.rodape-menu {
  border-top: 1px solid rgba(255, 255, 255, 0.18);
  padding-top: 1rem;
}

.links-legais a {
  color: var(--cor-texto-sobre-marinho);
}

.conteudo {
  flex: 1;
  min-width: 0;
  display: flex;
  flex-direction: column;
}

.topo {
  display: flex;
  align-items: center;
  gap: 1.25rem;
  padding: 0.75rem 1.5rem;
  background: var(--cor-superficie);
  border-bottom: 1px solid var(--cor-borda);
}

.alternar-menu {
  display: none;
}

.marca {
  display: flex;
  align-items: center;
  gap: 0.55rem;
  color: inherit;
  flex-shrink: 0;
}

.marca:hover {
  text-decoration: none;
}

.nome-marca {
  font-weight: 800;
  font-size: 1.05rem;
  letter-spacing: -0.01em;
}

.marca-marinho {
  color: var(--cor-marinho);
}

.marca-azul {
  color: var(--cor-azul);
}

.busca-topo {
  flex: 1;
  max-width: 34rem;
  position: relative;
  display: flex;
  align-items: center;
}

.busca-topo .icone-busca {
  position: absolute;
  left: 0.85rem;
  font-size: 0.9rem;
  opacity: 0.6;
}

.busca-topo input {
  width: 100%;
  padding: 0.55rem 0.9rem 0.55rem 2.2rem;
  border-radius: var(--raio-pill);
  border: 1px solid var(--cor-borda);
  background: var(--cor-fundo);
  font: inherit;
}

.usuario-topo {
  display: flex;
  align-items: center;
  gap: 0.75rem;
  margin-left: auto;
  flex-shrink: 0;
}

.cartao-usuario {
  display: flex;
  align-items: center;
  gap: 0.6rem;
  color: inherit;
}

.cartao-usuario:hover {
  text-decoration: none;
}

.avatar {
  width: 2.1rem;
  height: 2.1rem;
  flex-shrink: 0;
  border-radius: 50%;
  background: var(--degrade-institucional);
  color: #ffffff;
  display: flex;
  align-items: center;
  justify-content: center;
  font-weight: 700;
  font-size: 0.8rem;
}

.dados-usuario {
  display: none;
  flex-direction: column;
  line-height: 1.25;
}

.nome-usuario {
  font-weight: 600;
  font-size: 0.85rem;
}

.perfil-usuario {
  font-size: 0.75rem;
  color: var(--cor-texto-suave);
}

.principal {
  padding: 1.5rem;
  max-width: 1180px;
  width: 100%;
}

@media (min-width: 640px) {
  .dados-usuario {
    display: flex;
  }
}

@media (max-width: 860px) {
  .busca-topo {
    display: none;
  }

  .alternar-menu {
    display: inline-flex;
  }

  .layout {
    flex-direction: column;
  }

  .menu {
    width: 100%;
    display: none;
  }

  .menu.aberto {
    display: flex;
  }

  .principal {
    padding: 1rem;
  }
}
</style>
