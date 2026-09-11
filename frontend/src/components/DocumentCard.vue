<script setup>
import { RouterLink } from 'vue-router'

import { formatarData } from '@/services/formatos'

defineProps({
  documento: { type: Object, required: true },
  mostrarVisibilidade: { type: Boolean, default: false },
})
</script>

<template>
  <article class="cartao cartao-documento">
    <header class="entre">
      <RouterLink :to="{ name: 'documento-detalhes', params: { id: documento.id } }" class="titulo">
        {{ documento.title }}
      </RouterLink>
      <span
        v-if="mostrarVisibilidade"
        class="selo"
        :class="documento.visibility === 'public' ? 'selo-publico' : 'selo-privado'"
      >
        {{ documento.visibility === 'public' ? 'Público' : 'Privado' }}
      </span>
    </header>

    <p class="texto-suave autor">{{ documento.material_author || documento.owner_name }}</p>

    <ul class="metadados">
      <li v-if="documento.category_name">
        <span class="selo selo-neutro">{{ documento.category_name }}</span>
      </li>
      <li v-if="documento.subject_name" class="texto-suave">{{ documento.subject_name }}</li>
    </ul>

    <footer class="entre rodape">
      <span class="texto-suave">
        {{ formatarData(documento.published_at || documento.created_at) }}
      </span>
      <RouterLink
        class="botao botao-secundario botao-pequeno"
        :to="{ name: 'documento-detalhes', params: { id: documento.id } }"
      >
        Ver detalhes
      </RouterLink>
    </footer>
  </article>
</template>

<style scoped>
.cartao-documento {
  display: flex;
  flex-direction: column;
  gap: 0.5rem;
}

.titulo {
  font-weight: 600;
  font-size: 1rem;
}

.autor {
  margin: 0;
  font-size: 0.85rem;
}

.metadados {
  list-style: none;
  margin: 0;
  padding: 0;
  display: flex;
  flex-wrap: wrap;
  align-items: center;
  gap: 0.5rem;
  font-size: 0.85rem;
}

.rodape {
  margin-top: auto;
  padding-top: 0.5rem;
  font-size: 0.8rem;
}
</style>
