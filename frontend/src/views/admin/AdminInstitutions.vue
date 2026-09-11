<script setup>
import { onMounted, reactive, ref } from 'vue'

import api, { mensagemDeErro } from '@/services/api'
import { useCatalogoStore } from '@/stores/catalogo'

const catalogo = useCatalogoStore()

const nova = reactive({ name: '', acronym: '' })
const erro = ref('')
const aviso = ref('')
const carregando = ref(true)

async function carregar() {
  carregando.value = true
  try {
    await catalogo.carregar(true)
  } catch (error) {
    erro.value = mensagemDeErro(error, 'Não foi possível carregar as instituições.')
  } finally {
    carregando.value = false
  }
}

async function criar() {
  erro.value = ''
  try {
    await api.post('/institutions/', { ...nova })
    aviso.value = 'Instituição cadastrada.'
    Object.assign(nova, { name: '', acronym: '' })
    carregar()
  } catch (error) {
    erro.value = mensagemDeErro(error, 'Não foi possível cadastrar a instituição.')
  }
}

async function excluir(instituicao) {
  if (!window.confirm(`Excluir "${instituicao.name}"?`)) return
  erro.value = ''
  try {
    await api.delete(`/institutions/${instituicao.id}/`)
    aviso.value = 'Instituição excluída.'
    carregar()
  } catch (error) {
    erro.value = mensagemDeErro(error, 'Não foi possível excluir a instituição.')
  }
}

onMounted(carregar)
</script>

<template>
  <div class="pilha">
    <p v-if="erro" class="mensagem mensagem-erro">{{ erro }}</p>
    <p v-if="aviso" class="mensagem mensagem-sucesso">{{ aviso }}</p>

    <section class="cartao">
      <h2>Nova instituição</h2>
      <form class="linha-campos" @submit.prevent="criar">
        <div class="campo">
          <label for="i-nome">Nome</label>
          <input id="i-nome" v-model.trim="nova.name" type="text" required />
        </div>
        <div class="campo">
          <label for="i-sigla">Sigla</label>
          <input id="i-sigla" v-model.trim="nova.acronym" type="text" maxlength="20" />
        </div>
        <div class="campo">
          <label>&nbsp;</label>
          <button class="botao" type="submit">Cadastrar</button>
        </div>
      </form>
    </section>

    <section class="cartao">
      <h2>Instituições</h2>
      <p v-if="carregando" class="texto-suave">Carregando…</p>
      <p v-else-if="!catalogo.instituicoes.length" class="vazio">Nenhuma instituição cadastrada.</p>
      <div v-else class="rolagem-horizontal">
        <table class="tabela">
          <thead>
            <tr>
              <th>Nome</th>
              <th>Sigla</th>
              <th>Cursos</th>
              <th></th>
            </tr>
          </thead>
          <tbody>
            <tr v-for="instituicao in catalogo.instituicoes" :key="instituicao.id">
              <td>{{ instituicao.name }}</td>
              <td class="texto-suave">{{ instituicao.acronym || '—' }}</td>
              <td class="texto-suave">{{ instituicao.courses_count }}</td>
              <td>
                <button
                  type="button"
                  class="botao botao-perigo botao-pequeno"
                  @click="excluir(instituicao)"
                >
                  Excluir
                </button>
              </td>
            </tr>
          </tbody>
        </table>
      </div>
    </section>
  </div>
</template>
