<script setup>
import { computed, ref } from 'vue'
import { RouterLink, RouterView, useRouter } from 'vue-router'

import { useAuthStore } from '@/stores/auth'

const auth = useAuthStore()
const router = useRouter()
const menuAberto = ref(false)

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
    <aside class="menu" :class="{ aberto: menuAberto }">
      <div class="marca">
        <span class="marca-icone">📘</span>
        <span>Acervo Edu IA</span>
      </div>

      <nav>
        <RouterLink
          v-for="item in itens"
          :key="item.nome"
          :to="{ name: item.nome }"
          class="item"
          @click="menuAberto = false"
        >
          <span aria-hidden="true">{{ item.icone }}</span>
          {{ item.rotulo }}
        </RouterLink>
      </nav>

      <div class="rodape-menu">
        <p class="nome">{{ auth.user?.name }}</p>
        <p class="perfil">{{ auth.perfilTexto }}</p>
        <button type="button" class="botao botao-secundario botao-pequeno" @click="sair">
          Sair
        </button>
      </div>
    </aside>

    <div class="conteudo">
      <header class="topo">
        <button
          type="button"
          class="botao botao-secundario botao-pequeno alternar-menu"
          @click="menuAberto = !menuAberto"
        >
          ☰ Menu
        </button>
        <span class="titulo-topo">{{ $route.meta.titulo }}</span>
      </header>
      <main class="principal">
        <RouterView />
      </main>
    </div>
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
  display: flex;
  flex-direction: column;
  gap: 0.25rem;
  flex: 1;
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

.item.router-link-exact-active {
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
