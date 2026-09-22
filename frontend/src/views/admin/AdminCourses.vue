<script setup>
import { onMounted, reactive, ref } from 'vue'

import api, { mensagemDeErro } from '@/services/api'
import { useCatalogoStore } from '@/stores/catalogo'

const catalogo = useCatalogoStore()

const novoCurso = reactive({ name: '', institution: '' })
const novaDisciplina = reactive({ name: '', course: '' })
const filtroInstituicao = ref('')
const erro = ref('')
const aviso = ref('')
const carregando = ref(true)

async function carregar() {
  carregando.value = true
  try {
    await catalogo.carregar(true)
  } catch (error) {
    erro.value = mensagemDeErro(error, 'Não foi possível carregar o catálogo.')
  } finally {
    carregando.value = false
  }
}

async function criarCurso() {
  erro.value = ''
  try {
    await api.post('/courses/', { ...novoCurso })
    aviso.value = 'Curso cadastrado.'
    Object.assign(novoCurso, { name: '', institution: '' })
    carregar()
  } catch (error) {
    erro.value = mensagemDeErro(error, 'Não foi possível cadastrar o curso.')
  }
}

async function criarDisciplina() {
  erro.value = ''
  try {
    await api.post('/subjects/', { ...novaDisciplina })
    aviso.value = 'Disciplina cadastrada.'
    Object.assign(novaDisciplina, { name: '', course: '' })
    carregar()
  } catch (error) {
    erro.value = mensagemDeErro(error, 'Não foi possível cadastrar a disciplina.')
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

    <div class="duas-colunas">
      <section class="cartao">
        <h2>Novo curso</h2>
        <form @submit.prevent="criarCurso">
          <div class="campo">
            <label for="c-instituicao">Instituição</label>
            <select id="c-instituicao" v-model="novoCurso.institution" required>
              <option value="">Selecione</option>
              <option v-for="i in catalogo.instituicoes" :key="i.id" :value="i.id">
                {{ i.name }}
              </option>
            </select>
          </div>
          <div class="campo">
            <label for="c-nome">Nome do curso</label>
            <input id="c-nome" v-model.trim="novoCurso.name" type="text" required />
          </div>
          <button class="botao" type="submit">Cadastrar curso</button>
        </form>
      </section>

      <section class="cartao">
        <h2>Nova disciplina</h2>
        <form @submit.prevent="criarDisciplina">
          <div class="campo">
            <label for="d-curso">Curso</label>
            <select id="d-curso" v-model="novaDisciplina.course" required>
              <option value="">Selecione</option>
              <option v-for="c in catalogo.cursos" :key="c.id" :value="c.id">
                {{ c.name }} — {{ c.institution_name }}
              </option>
            </select>
          </div>
          <div class="campo">
            <label for="d-nome">Nome da disciplina</label>
            <input id="d-nome" v-model.trim="novaDisciplina.name" type="text" required />
          </div>
          <button class="botao" type="submit">Cadastrar disciplina</button>
        </form>
      </section>
    </div>

    <section class="cartao">
      <div class="entre cabecalho">
        <h2>Cursos e disciplinas</h2>
        <select v-model="filtroInstituicao" class="filtro">
          <option value="">Todas as instituições</option>
          <option v-for="i in catalogo.instituicoes" :key="i.id" :value="i.id">{{ i.name }}</option>
        </select>
      </div>

      <p v-if="carregando" class="texto-suave">Carregando…</p>
      <div v-else class="pilha">
        <article
          v-for="curso in catalogo.cursosDaInstituicao(filtroInstituicao)"
          :key="curso.id"
          class="curso"
        >
          <div class="entre">
            <div>
              <h3>{{ curso.name }}</h3>
              <p class="texto-suave">{{ curso.institution_name }}</p>
            </div>
            <button
              type="button"
              class="botao botao-perigo botao-pequeno"
              @click="excluir('courses', curso)"
            >
              Excluir curso
            </button>
          </div>
          <ul class="disciplinas">
            <li v-for="disciplina in catalogo.disciplinasDoCurso(curso.id)" :key="disciplina.id">
              <span>{{ disciplina.name }}</span>
              <button
                type="button"
                class="botao botao-secundario botao-pequeno"
                @click="excluir('subjects', disciplina)"
              >
                Excluir
              </button>
            </li>
            <li v-if="!catalogo.disciplinasDoCurso(curso.id).length" class="texto-suave">
              Nenhuma disciplina cadastrada.
            </li>
          </ul>
        </article>
      </div>
    </section>
  </div>
</template>

<style scoped>
.duas-colunas {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 1rem;
}

.cabecalho {
  margin-bottom: 1rem;
}

.filtro {
  max-width: 260px;
}

.curso {
  border: 1px solid var(--cor-borda);
  border-radius: var(--raio);
  padding: 0.9rem;
}

.disciplinas {
  list-style: none;
  margin: 0.5rem 0 0;
  padding: 0;
  display: flex;
  flex-direction: column;
  gap: 0.35rem;
}

.disciplinas li {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 1rem;
  font-size: 0.9rem;
}

@media (max-width: 860px) {
  .duas-colunas {
    grid-template-columns: 1fr;
  }
}
</style>
