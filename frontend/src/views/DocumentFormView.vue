<script setup>
import { computed, nextTick, onMounted, reactive, ref, watch } from 'vue'
import { useRoute, useRouter } from 'vue-router'

import api, { mensagemDeErro } from '@/services/api'
import { useCatalogoStore } from '@/stores/catalogo'

const route = useRoute()
const router = useRouter()
const catalogo = useCatalogoStore()

const editando = computed(() => Boolean(route.params.id))
const carregando = ref(true)
const enviando = ref(false)
const erro = ref('')
const arquivoAtual = ref('')
const arquivo = ref(null)

const form = reactive({
  title: '',
  description: '',
  material_author: '',
  institution: '',
  course: '',
  subject: '',
  category: '',
  tags: '',
  visibility: 'community',
})

// Enquanto o formulário é preenchido a partir da API, os campos encadeados
// não podem ser zerados pelos watchers.
const preenchendo = ref(false)

watch(
  () => form.institution,
  () => {
    if (preenchendo.value) return
    form.course = ''
    form.subject = ''
  },
)

watch(
  () => form.course,
  () => {
    if (preenchendo.value) return
    form.subject = ''
  },
)

function selecionarArquivo(evento) {
  arquivo.value = evento.target.files[0] || null
}

async function carregarDocumento() {
  const { data } = await api.get(`/documents/${route.params.id}/`)
  preenchendo.value = true
  form.title = data.title
  form.description = data.description || ''
  form.material_author = data.material_author || ''
  form.category = data.category || ''
  form.tags = (data.tags || []).join(', ')
  form.visibility = data.visibility
  arquivoAtual.value = data.original_filename

  if (data.subject) {
    const disciplina = catalogo.disciplinaPorId(data.subject)
    form.institution = disciplina?.institution || ''
    form.course = disciplina?.course || ''
    form.subject = data.subject
  }
  await nextTick()
  preenchendo.value = false
}

async function salvar() {
  erro.value = ''
  if (!editando.value && !arquivo.value) {
    erro.value = 'Escolha o arquivo do documento.'
    return
  }
  if (form.visibility === 'restricted' && !form.subject) {
    erro.value = 'Visibilidade "Restrito" exige uma disciplina.'
    return
  }

  const dados = new FormData()
  dados.append('title', form.title)
  dados.append('description', form.description)
  dados.append('material_author', form.material_author)
  dados.append('visibility', form.visibility)
  if (form.subject) dados.append('subject', form.subject)
  if (form.category) dados.append('category', form.category)
  if (form.tags) dados.append('tags', form.tags)
  if (arquivo.value) dados.append('file', arquivo.value)

  enviando.value = true
  try {
    const resposta = editando.value
      ? await api.patch(`/documents/${route.params.id}/`, dados)
      : await api.post('/documents/mine/', dados)
    router.push({ name: 'documento-detalhes', params: { id: resposta.data.id } })
  } catch (error) {
    erro.value = mensagemDeErro(error, 'Não foi possível salvar o documento.')
  } finally {
    enviando.value = false
  }
}

onMounted(async () => {
  try {
    await catalogo.carregar()
    if (editando.value) await carregarDocumento()
  } catch (error) {
    erro.value = mensagemDeErro(error, 'Não foi possível carregar o formulário.')
  } finally {
    carregando.value = false
  }
})
</script>

<template>
  <div class="pilha">
    <header>
      <h1>{{ editando ? 'Editar documento' : 'Novo documento' }}</h1>
      <p v-if="!editando" class="texto-suave">
        O documento nasce <strong>privado</strong>. Depois você pode publicá-lo no Acervo Público.
      </p>
    </header>

    <p v-if="erro" class="mensagem mensagem-erro" role="alert">{{ erro }}</p>
    <p v-if="carregando" class="texto-suave" role="status">Carregando…</p>

    <form v-else class="cartao" @submit.prevent="salvar">
      <div class="campo">
        <label for="titulo">Título <span class="obrigatorio" aria-hidden="true">*</span><span class="apenas-leitor-de-tela"> (obrigatório)</span></label>
        <input id="titulo" v-model.trim="form.title" type="text" required maxlength="200" />
      </div>

      <div class="campo">
        <label for="descricao">Descrição</label>
        <textarea id="descricao" v-model.trim="form.description" rows="3"></textarea>
      </div>

      <div class="campo">
        <label for="autor">Autor do material</label>
        <input id="autor" v-model.trim="form.material_author" type="text" maxlength="200" />
        <p class="campo-ajuda">Quem escreveu o material, se for diferente de você.</p>
      </div>

      <div class="linha-campos">
        <div class="campo">
          <label for="instituicao">Instituição</label>
          <select id="instituicao" v-model="form.institution">
            <option value="">Selecione</option>
            <option v-for="i in catalogo.instituicoes" :key="i.id" :value="i.id">{{ i.name }}</option>
          </select>
        </div>

        <div class="campo">
          <label for="curso">Curso</label>
          <select id="curso" v-model="form.course" :disabled="!form.institution">
            <option value="">Selecione</option>
            <option
              v-for="c in catalogo.cursosDaInstituicao(form.institution)"
              :key="c.id"
              :value="c.id"
            >
              {{ c.name }}
            </option>
          </select>
        </div>

        <div class="campo">
          <label for="disciplina">Disciplina</label>
          <select id="disciplina" v-model="form.subject" :disabled="!form.course">
            <option value="">Selecione</option>
            <option v-for="d in catalogo.disciplinasDoCurso(form.course)" :key="d.id" :value="d.id">
              {{ d.name }}
            </option>
          </select>
        </div>

        <div class="campo">
          <label for="categoria">Categoria</label>
          <select id="categoria" v-model="form.category">
            <option value="">Selecione</option>
            <option v-for="c in catalogo.categorias" :key="c.id" :value="c.id">{{ c.name }}</option>
          </select>
        </div>
      </div>

      <div class="campo">
        <label for="tags">Tags</label>
        <input id="tags" v-model.trim="form.tags" type="text" placeholder="prova, revisão, cálculo" />
        <p class="campo-ajuda">Separe por vírgula.</p>
      </div>

      <fieldset class="campo">
        <legend>Quem pode ver?</legend>
        <label class="opcao-visibilidade">
          <input v-model="form.visibility" type="radio" value="public" />
          <span><strong>Público</strong> — qualquer pessoa, inclusive sem login.</span>
        </label>
        <label class="opcao-visibilidade">
          <input v-model="form.visibility" type="radio" value="community" />
          <span
            ><strong>Comunidade da instituição</strong>
            <span class="selo selo-neutro">padrão</span> — alunos, professores e equipe
            autenticados.</span
          >
        </label>
        <label class="opcao-visibilidade">
          <input v-model="form.visibility" type="radio" value="restricted" />
          <span><strong>Restrito</strong> — somente a turma/disciplina escolhida e os gestores.</span>
        </label>
        <p v-if="form.visibility === 'restricted' && !form.subject" class="campo-erro">
          Escolha uma disciplina acima para usar a visibilidade Restrito.
        </p>
      </fieldset>

      <div class="campo">
        <label for="arquivo">
          Arquivo
          <span v-if="!editando" class="obrigatorio" aria-hidden="true">*</span>
          <span v-if="!editando" class="apenas-leitor-de-tela">(obrigatório)</span>
        </label>
        <input
          id="arquivo"
          type="file"
          accept=".pdf,.docx,.pptx,.txt"
          aria-describedby="ajuda-arquivo"
          @change="selecionarArquivo"
        />
        <p id="ajuda-arquivo" class="campo-ajuda">
          Formatos aceitos: PDF, DOCX, PPTX e TXT.
          <template v-if="editando && arquivoAtual">
            Arquivo atual: <strong>{{ arquivoAtual }}</strong
            >. Envie outro apenas se quiser substituí-lo.
          </template>
        </p>
      </div>

      <div class="acoes">
        <button class="botao" type="submit" :disabled="enviando">
          {{ enviando ? 'Salvando…' : 'Salvar' }}
        </button>
        <button class="botao botao-secundario" type="button" @click="router.back()">Cancelar</button>
      </div>
    </form>
  </div>
</template>

<style scoped>
.opcao-visibilidade {
  display: flex;
  align-items: flex-start;
  gap: 0.5rem;
  font-weight: 400;
  margin-bottom: 0.5rem;
}

.opcao-visibilidade input {
  margin-top: 0.2rem;
}
</style>
