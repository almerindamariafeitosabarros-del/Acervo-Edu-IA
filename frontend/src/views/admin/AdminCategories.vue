<script setup>
import { onMounted, reactive, ref } from 'vue'

import api, { mensagemDeErro } from '@/services/api'
import { useCatalogoStore } from '@/stores/catalogo'

const catalogo = useCatalogoStore()

const nova = reactive({ name: '', description: '' })
const erro = ref('')
const aviso = ref('')
const carregando = ref(true)

async function carregar() {
  carregando.value = true
  try {
    await catalogo.carregar(true)
  } catch (error) {
    erro.value = mensagemDeErro(error, 'Não foi possível carregar as categorias.')
  } finally {
    carregando.value = false
  }
}

async function criar() {
  erro.value = ''
  try {
    await api.post('/categories/', { ...nova })
    aviso.value = 'Categoria cadastrada.'
    Object.assign(nova, { name: '', description: '' })
    carregar()
  } catch (error) {
    erro.value = mensagemDeErro(error, 'Não foi possível cadastrar a categoria.')
  }
}

async function excluir(tipo, item) {
  if (!window.confirm(`Excluir "${item.name}"?`)) return
  erro.value = ''
  try {
    await api.delete(`/${tipo}/${item.id}/`)
    aviso.value = 'Registro excluído.'
    carregar()
  } catch (error) {
    erro.value = mensagemDeErro(error, 'Não foi possível excluir o registro.')
  }
}

onMounted(carregar)
</script>

<template>
  <div class="pilha">
    <p v-if="erro" class="mensagem mensagem-erro" role="alert">{{ erro }}</p>
    <p v-if="aviso" class="mensagem mensagem-sucesso" role="status">{{ aviso }}</p>

    <section class="cartao">
      <h2>Nova categoria</h2>
      <form class="linha-campos" @submit.prevent="criar">
        <div class="campo">
          <label for="cat-nome">Nome</label>
          <input id="cat-nome" v-model.trim="nova.name" type="text" required />
        </div>
        <div class="campo">
          <label for="cat-descricao">Descrição</label>
          <input id="cat-descricao" v-model.trim="nova.description" type="text" maxlength="255" />
        </div>
        <div class="campo">
          <span class="rotulo-vazio" aria-hidden="true"></span>
          <button class="botao" type="submit">Cadastrar</button>
        </div>
      </form>
    </section>

    <section class="cartao">
      <h2>Categorias</h2>
      <p v-if="carregando" class="texto-suave">Carregando…</p>
      <div v-else class="rolagem-horizontal">
        <table class="tabela">
          <thead>
            <tr>
              <th>Nome</th>
              <th>Descrição</th>
              <th></th>
            </tr>
          </thead>
          <tbody>
            <tr v-for="categoria in catalogo.categorias" :key="categoria.id">
              <td>{{ categoria.name }}</td>
              <td class="texto-suave">{{ categoria.description || '—' }}</td>
              <td>
                <button
                  type="button"
                  class="botao botao-perigo botao-pequeno"
                  @click="excluir('categories', categoria)"
                >
                  Excluir
                </button>
              </td>
            </tr>
          </tbody>
        </table>
      </div>
    </section>

    <section class="cartao">
      <h2>Tags</h2>
      <p class="texto-suave">
        As tags são criadas automaticamente quando alguém cadastra um documento.
      </p>
      <div class="tags">
        <span v-for="tag in catalogo.tags" :key="tag.id" class="selo selo-neutro tag">
          {{ tag.name }}
          <button type="button" class="remover" title="Excluir tag" @click="excluir('tags', tag)">
            ×
          </button>
        </span>
        <span v-if="!catalogo.tags.length" class="texto-suave">Nenhuma tag cadastrada.</span>
      </div>
    </section>
  </div>
</template>

<style scoped>
.tags {
  display: flex;
  flex-wrap: wrap;
  gap: 0.4rem;
}

.tag {
  display: inline-flex;
  align-items: center;
  gap: 0.3rem;
}

.remover {
  border: none;
  background: none;
  cursor: pointer;
  color: inherit;
  font-size: 1rem;
  line-height: 1;
  padding: 0;
}
</style>
