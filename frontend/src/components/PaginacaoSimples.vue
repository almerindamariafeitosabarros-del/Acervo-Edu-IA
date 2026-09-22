<script setup>
const props = defineProps({
  pagina: { type: Number, required: true },
  total: { type: Number, required: true },
  porPagina: { type: Number, default: 12 },
})

const emit = defineEmits(['mudar'])

function totalPaginas() {
  return Math.max(1, Math.ceil(props.total / props.porPagina))
}
</script>

<template>
  <div v-if="total > porPagina" class="paginacao">
    <button
      type="button"
      class="botao botao-secundario botao-pequeno"
      :disabled="pagina <= 1"
      @click="emit('mudar', pagina - 1)"
    >
      Anterior
    </button>
    <span class="texto-suave">Página {{ pagina }} de {{ totalPaginas() }}</span>
    <button
      type="button"
      class="botao botao-secundario botao-pequeno"
      :disabled="pagina >= totalPaginas()"
      @click="emit('mudar', pagina + 1)"
    >
      Próxima
    </button>
  </div>
</template>

<style scoped>
.paginacao {
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 1rem;
  margin-top: 1.25rem;
}
</style>
