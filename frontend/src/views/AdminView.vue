<script setup>
import { computed, ref } from 'vue'

import AdminCategories from '@/views/admin/AdminCategories.vue'
import AdminCourses from '@/views/admin/AdminCourses.vue'
import AdminDocuments from '@/views/admin/AdminDocuments.vue'
import AdminInstitutions from '@/views/admin/AdminInstitutions.vue'
import AdminUsers from '@/views/admin/AdminUsers.vue'
import { useAuthStore } from '@/stores/auth'

const auth = useAuthStore()

// Usuários e Instituições são exclusivos do Administrador.
const abas = computed(() => {
  const lista = []
  if (auth.podeGerenciarUsuarios) {
    lista.push({ id: 'usuarios', rotulo: 'Usuários', componente: AdminUsers })
    lista.push({ id: 'instituicoes', rotulo: 'Instituições', componente: AdminInstitutions })
  }
  lista.push({ id: 'cursos', rotulo: 'Cursos e Disciplinas', componente: AdminCourses })
  lista.push({ id: 'categorias', rotulo: 'Categorias', componente: AdminCategories })
  lista.push({ id: 'documentos', rotulo: 'Todos os Documentos', componente: AdminDocuments })
  return lista
})

const abaAtual = ref(abas.value[0].id)
const componenteAtual = computed(
  () => abas.value.find((aba) => aba.id === abaAtual.value)?.componente,
)
</script>

<template>
  <div class="pilha">
    <header>
      <h1>Administração</h1>
      <p class="texto-suave">
        Gerencie o catálogo acadêmico e modere as publicações do acervo.
      </p>
    </header>

    <nav class="abas">
      <button
        v-for="aba in abas"
        :key="aba.id"
        type="button"
        :class="{ ativa: abaAtual === aba.id }"
        @click="abaAtual = aba.id"
      >
        {{ aba.rotulo }}
      </button>
    </nav>

    <component :is="componenteAtual" />
  </div>
</template>

<style scoped>
.abas {
  display: flex;
  flex-wrap: wrap;
  gap: 0.5rem;
  border-bottom: 1px solid var(--cor-borda);
}

.abas button {
  padding: 0.6rem 0.9rem;
  border: none;
  background: none;
  font: inherit;
  font-weight: 600;
  color: var(--cor-texto-suave);
  cursor: pointer;
  border-bottom: 2px solid transparent;
}

.abas button.ativa {
  color: var(--cor-primaria);
  border-bottom-color: var(--cor-primaria);
}
</style>
