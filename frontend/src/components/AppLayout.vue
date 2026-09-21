<script setup>
import { computed, ref, watch } from 'vue'
import { RouterLink, RouterView, useRoute, useRouter } from 'vue-router'

import { useAuthStore } from '@/stores/auth'

const auth = useAuthStore()
const router = useRouter()
const route = useRoute()
const menuAberto = ref(false)

// Leitores de tela não percebem a troca de página em uma SPA: avisamos aqui.
const anuncio = ref('')
watch(
  () => route.name,
  () => {
    anuncio.value = `${route.meta.titulo || 'Página'} carregada.`
  },
)

// O menu mostra apenas as telas permitidas ao perfil.
const itens = computed(() => {
  const base = [
    { nome: 'inicio', rotulo: 'Início', icone: '🏠' },
    { nome: 'acervo', rotulo: 'Acervo Público', icone: '📚' },
    { nome: 'meus-documentos', rotulo: 'Meus Documentos', icone: '📁' },
    { nome: 'assistente', rotulo: 'Assistente IA', icone: '🤖' },
    { nome: 'perfil', rotulo: 'Meu Perfil', icone: '👤' },
  ]
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
      <p class="marca">
        <span class="marca-icone" aria-hidden="true">📘</span>
        <span>Acervo Edu IA</span>
      </p>

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
        <p class="nome">{{ auth.user?.name }}</p>
        <p class="perfil">{{ auth.perfilTexto }}</p>
        <button type="button" class="botao botao-secundario botao-pequeno" @click="sair">
          Sair
        </button>
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
          <span aria-hidden="true">☰</span> Menu
        </button>
        <span class="titulo-topo">{{ $route.meta.titulo }}</span>
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
  background: var(--cor-superficie);
  border-right: 1px solid var(--cor-borda);
  display: flex;
  flex-direction: column;
  padding: 1.25rem 1rem;
  gap: 1.5rem;
}

.marca {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  font-weight: 700;
  font-size: 1.05rem;
}

.marca-icone {
  font-size: 1.3rem;
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

.marca {
  margin: 0;
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
  color: var(--cor-texto);
  font-weight: 500;
}

.item:hover {
  background: var(--cor-fundo);
  text-decoration: none;
}

.item[aria-current='page'] {
  background: var(--cor-primaria-clara);
  color: var(--cor-primaria-escura);
  font-weight: 600;
}

.rodape-menu {
  border-top: 1px solid var(--cor-borda);
  padding-top: 1rem;
}

.nome {
  margin: 0;
  font-weight: 600;
  font-size: 0.9rem;
}

.perfil {
  margin: 0 0 0.6rem;
  font-size: 0.8rem;
  color: var(--cor-texto-suave);
}

.conteudo {
  flex: 1;
  min-width: 0;
  display: flex;
  flex-direction: column;
}

.topo {
  display: none;
  align-items: center;
  gap: 0.75rem;
  padding: 0.75rem 1rem;
  background: var(--cor-superficie);
  border-bottom: 1px solid var(--cor-borda);
}

.titulo-topo {
  font-weight: 600;
}

.principal {
  padding: 1.5rem;
  max-width: 1180px;
  width: 100%;
}

@media (max-width: 860px) {
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

  .topo {
    display: flex;
  }

  .principal {
    padding: 1rem;
  }
}
</style>
