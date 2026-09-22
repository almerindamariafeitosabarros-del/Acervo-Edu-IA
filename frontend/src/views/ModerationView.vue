<script setup>
import { onMounted, ref } from 'vue'

import api, { mensagemDeErro } from '@/services/api'
import { formatarData } from '@/services/formatos'

const itens = ref([])
const carregando = ref(true)
const erro = ref('')
const aviso = ref('')

async function carregar() {
  carregando.value = true
  erro.value = ''
  try {
    const { data } = await api.get('/mural/moderation/')
    itens.value = data.results
  } catch (error) {
    erro.value = mensagemDeErro(error, 'Não foi possível carregar a fila de moderação.')
  } finally {
    carregando.value = false
  }
}

async function decidir(post, decision) {
  try {
    await api.post(`/mural/moderation/${post.id}/decidir/`, { decision })
    aviso.value = decision === 'hide' ? 'Publicação ocultada.' : 'Publicação mantida.'
    carregar()
  } catch (error) {
    erro.value = mensagemDeErro(error, 'Não foi possível registrar a decisão.')
  }
}

onMounted(carregar)
</script>

<template>
  <div class="pilha">
    <header>
      <h1>Moderação do Mural Público</h1>
      <p class="texto-suave">
        Publicações com 5 ou mais denúncias ficam ocultas automaticamente até a análise. Toda
        decisão fica registrada (moderador, data e motivo).
      </p>
    </header>

    <p v-if="erro" class="mensagem mensagem-erro" role="alert">{{ erro }}</p>
    <p v-if="aviso" class="mensagem mensagem-sucesso" role="status">{{ aviso }}</p>

    <p v-if="carregando" class="texto-suave" role="status">Carregando…</p>
    <p v-else-if="!itens.length" class="vazio">Nenhuma denúncia pendente.</p>

    <section v-else class="cartao rolagem-horizontal">
      <table class="tabela">
        <caption class="apenas-leitor-de-tela">
          Publicações denunciadas no mural, pendentes de análise
        </caption>
        <thead>
          <tr>
            <th>Publicação</th>
            <th>Autor</th>
            <th>Motivo</th>
            <th>Denúncias</th>
            <th>Data</th>
            <th>Ações</th>
          </tr>
        </thead>
        <tbody>
          <tr v-for="post in itens" :key="post.id">
            <td class="celula-texto">{{ post.text || '(sem texto — apenas anexo)' }}</td>
            <td class="texto-suave">{{ post.author_name }}</td>
            <td class="texto-suave">
              {{ post.reports.map((r) => r.reason_display).join(', ') || '—' }}
            </td>
            <td>
              <span class="selo selo-neutro">{{ post.report_count }}</span>
            </td>
            <td class="texto-suave">{{ formatarData(post.created_at) }}</td>
            <td>
              <div class="acoes">
                <button
                  type="button"
                  class="botao botao-secundario botao-pequeno"
                  @click="decidir(post, 'keep')"
                >
                  Manter
                </button>
                <button
                  type="button"
                  class="botao botao-perigo botao-pequeno"
                  @click="decidir(post, 'hide')"
                >
                  Ocultar
                </button>
              </div>
            </td>
          </tr>
        </tbody>
      </table>
    </section>
  </div>
</template>

<style scoped>
.celula-texto {
  max-width: 24rem;
}
</style>
