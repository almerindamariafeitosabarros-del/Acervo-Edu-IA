<script setup>
import { onMounted, onUnmounted, ref } from 'vue'
import { RouterLink, useRoute, useRouter } from 'vue-router'

import api, { mensagemDeErro } from '@/services/api'
import { formatarDataHora, formatarTamanho } from '@/services/formatos'

const route = useRoute()
const router = useRouter()

const documento = ref(null)
const carregando = ref(true)
const erro = ref('')
const aviso = ref('')
const urlVisualizacao = ref('')
const carregandoArquivo = ref(false)

/** O arquivo só é obtido pela API autenticada, nunca por URL pública. */
async function baixarArquivo(download) {
  const { data } = await api.get(`/documents/${route.params.id}/file/`, {
    params: download ? { download: 1 } : {},
    responseType: 'blob',
  })
  return data
}

async function abrirVisualizacao() {
  carregandoArquivo.value = true
  try {
    const blob = await baixarArquivo(false)
    urlVisualizacao.value = URL.createObjectURL(blob)
  } catch (error) {
    erro.value = mensagemDeErro(error, 'Não foi possível abrir o arquivo.')
  } finally {
    carregandoArquivo.value = false
  }
}

async function baixar() {
  carregandoArquivo.value = true
  try {
    const blob = await baixarArquivo(true)
    const url = URL.createObjectURL(blob)
    const link = document.createElement('a')
    link.href = url
    link.download = documento.value.original_filename || `documento-${documento.value.id}`
    link.click()
    URL.revokeObjectURL(url)
  } catch (error) {
    erro.value = mensagemDeErro(error, 'Não foi possível baixar o arquivo.')
  } finally {
    carregandoArquivo.value = false
  }
}

async function alternarPublicacao() {
  const publicar = documento.value.visibility !== 'public'
  if (publicar) {
    const confirmado = window.confirm(
      'Todos os usuários cadastrados poderão ver e baixar este documento.',
    )
    if (!confirmado) return
  }
  try {
    const { data } = await api.post(
      `/documents/${documento.value.id}/${publicar ? 'publish' : 'unpublish'}/`,
    )
    documento.value = data
    aviso.value = publicar
      ? 'Documento publicado no Acervo Público.'
      : 'Documento removido do Acervo Público.'
  } catch (error) {
    erro.value = mensagemDeErro(error, 'Não foi possível alterar a publicação.')
  }
}

async function excluir() {
  if (!window.confirm(`Excluir "${documento.value.title}"? Esta ação não pode ser desfeita.`)) return
  try {
    await api.delete(`/documents/${documento.value.id}/`)
    router.push({ name: 'meus-documentos' })
  } catch (error) {
    erro.value = mensagemDeErro(error, 'Não foi possível excluir o documento.')
  }
}

onMounted(async () => {
  try {
    const { data } = await api.get(`/documents/${route.params.id}/`)
    documento.value = data
    if (data.extension === 'pdf') await abrirVisualizacao()
  } catch (error) {
    erro.value =
      error?.response?.status === 404
        ? 'Documento não encontrado ou sem permissão de acesso.'
        : mensagemDeErro(error, 'Não foi possível carregar o documento.')
  } finally {
    carregando.value = false
  }
})

onUnmounted(() => {
  if (urlVisualizacao.value) URL.revokeObjectURL(urlVisualizacao.value)
})
</script>

<template>
  <div class="pilha">
    <p v-if="carregando" class="texto-suave" role="status">Carregando…</p>
    <p v-else-if="erro && !documento" class="mensagem mensagem-erro" role="alert">{{ erro }}</p>

    <template v-else-if="documento">
      <header class="entre">
        <div>
          <h1>{{ documento.title }}</h1>
          <p class="texto-suave">
            Enviado por {{ documento.owner_name }} em {{ formatarDataHora(documento.created_at) }}
          </p>
        </div>
        <span
          class="selo"
          :class="documento.visibility === 'public' ? 'selo-publico' : 'selo-privado'"
        >
          {{ documento.visibility_display }}
        </span>
      </header>

      <p v-if="erro" class="mensagem mensagem-erro" role="alert">{{ erro }}</p>
      <p v-if="aviso" class="mensagem mensagem-sucesso" role="status">{{ aviso }}</p>

      <div class="acoes">
        <button class="botao" type="button" :disabled="carregandoArquivo" @click="baixar">
          ⬇ Baixar
        </button>
        <RouterLink
          class="botao botao-secundario"
          :to="{ name: 'assistente', query: { documento: documento.id } }"
        >
          🤖 Perguntar à IA
        </RouterLink>
        <RouterLink
          v-if="documento.permissions.can_edit"
          class="botao botao-secundario"
          :to="{ name: 'documento-editar', params: { id: documento.id } }"
        >
          Editar
        </RouterLink>
        <button
          v-if="documento.permissions.can_publish"
          class="botao botao-secundario"
          type="button"
          @click="alternarPublicacao"
        >
          {{ documento.visibility === 'public' ? 'Remover do Acervo Público' : 'Publicar' }}
        </button>
        <button
          v-if="documento.permissions.can_edit"
          class="botao botao-perigo"
          type="button"
          @click="excluir"
        >
          Excluir
        </button>
      </div>

      <section class="cartao">
        <h2>Informações</h2>
        <dl class="metadados">
          <div><dt>Descrição</dt><dd>{{ documento.description || '—' }}</dd></div>
          <div><dt>Autor do material</dt><dd>{{ documento.material_author || '—' }}</dd></div>
          <div><dt>Instituição</dt><dd>{{ documento.institution_name || '—' }}</dd></div>
          <div><dt>Curso</dt><dd>{{ documento.course_name || '—' }}</dd></div>
          <div><dt>Disciplina</dt><dd>{{ documento.subject_name || '—' }}</dd></div>
          <div><dt>Categoria</dt><dd>{{ documento.category_name || '—' }}</dd></div>
          <div>
            <dt>Tags</dt>
            <dd>
              <span v-if="!documento.tags.length">—</span>
              <span v-for="tag in documento.tags" :key="tag" class="selo selo-neutro tag">
                {{ tag }}
              </span>
            </dd>
          </div>
          <div>
            <dt>Arquivo</dt>
            <dd>
              {{ documento.original_filename }} ({{ formatarTamanho(documento.file_size) }})
            </dd>
          </div>
          <div>
            <dt>Publicado em</dt>
            <dd>{{ documento.published_at ? formatarDataHora(documento.published_at) : '—' }}</dd>
          </div>
        </dl>
      </section>

      <section class="cartao">
        <h2>Visualização</h2>
        <iframe
          v-if="documento.extension === 'pdf' && urlVisualizacao"
          :src="urlVisualizacao"
          title="Visualização do documento"
          class="visualizador"
        ></iframe>
        <p v-else-if="documento.extension === 'pdf'" class="texto-suave">
          Carregando a visualização…
        </p>
        <p v-else class="texto-suave">
          A visualização na tela está disponível apenas para arquivos PDF. Use o botão
          <strong>Baixar</strong> para abrir este arquivo no seu computador.
        </p>
      </section>
    </template>
  </div>
</template>

<style scoped>
.metadados {
  margin: 0;
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(230px, 1fr));
  gap: 0.9rem;
}

.metadados dt {
  font-size: 0.78rem;
  text-transform: uppercase;
  letter-spacing: 0.02em;
  color: var(--cor-texto-suave);
  font-weight: 600;
}

.metadados dd {
  margin: 0.15rem 0 0;
}

.tag {
  margin-right: 0.3rem;
}

.visualizador {
  width: 100%;
  height: 620px;
  border: 1px solid var(--cor-borda);
  border-radius: var(--raio);
}
</style>
