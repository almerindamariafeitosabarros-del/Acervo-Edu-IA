<script setup>
// Símbolo do Acervo Edu IA: livro aberto em degradê marinho→azul, com o
// aglomerado de quadrados (dados/IA) no canto superior esquerdo.
defineProps({
  tamanho: { type: Number, default: 32 },
})
</script>

<template>
  <svg
    class="logo-marca"
    :width="tamanho"
    :height="tamanho"
    viewBox="0 0 100 100"
    aria-hidden="true"
    focusable="false"
  >
    <defs>
      <linearGradient id="logoAcervoDegrade" x1="10" y1="10" x2="90" y2="95" gradientUnits="userSpaceOnUse">
        <stop offset="0" stop-color="var(--cor-marinho)" />
        <stop offset="1" stop-color="var(--cor-azul)" />
      </linearGradient>
    </defs>

    <rect x="4" y="2" width="15" height="15" rx="3.5" fill="var(--cor-azul)" opacity="0.5" />
    <rect x="21" y="2" width="11" height="11" rx="2.5" fill="var(--cor-azul)" opacity="0.85" />
    <rect x="4" y="19" width="11" height="11" rx="2.5" fill="var(--cor-marinho)" opacity="0.65" />
    <rect x="17" y="17" width="8" height="8" rx="2" fill="var(--cor-azul)" />

    <path
      d="M50 40 C50 31 42 25 31 25 L15 25 C10.5 25 8 27.5 8 32 L8 76 C8 80.5 10.5 83 15 83
         L31 83 C40 83 50 87.5 50 95 Z"
      fill="url(#logoAcervoDegrade)"
    />
    <path
      d="M50 40 C50 31 58 25 69 25 L85 25 C89.5 25 92 27.5 92 32 L92 76 C92 80.5 89.5 83 85 83
         L69 83 C60 83 50 87.5 50 95 Z"
      fill="url(#logoAcervoDegrade)"
      opacity="0.88"
    />
    <path d="M50 40 L50 95" stroke="#ffffff" stroke-width="1.6" opacity="0.45" stroke-linecap="round" />
    <path
      d="M17 34 L38 34 M17 42 L38 42 M17 50 L34 50"
      stroke="#ffffff"
      stroke-width="2"
      opacity="0.4"
      stroke-linecap="round"
    />
    <path
      d="M62 34 L83 34 M66 42 L83 42 M68 50 L83 50"
      stroke="#ffffff"
      stroke-width="2"
      opacity="0.4"
      stroke-linecap="round"
    />
  </svg>
</template>

<style scoped>
.logo-marca {
  display: inline-block;
  flex-shrink: 0;
}
</style>
