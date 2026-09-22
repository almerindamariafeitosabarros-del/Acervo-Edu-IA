<script setup>
import { computed, onMounted, ref } from 'vue'
import { useRoute } from 'vue-router'

import api, { mensagemDeErro } from '@/services/api'
import { formatarDataHora, formatarDuracao } from '@/services/formatos'

const route = useRoute()

const origem = ref('meus')
const documentoId = ref('')
const arquivo = ref(null)
const prompt = ref('')

const meusDocumentos = ref([])
const publicos = ref([])
const historico = ref([])

const resposta = ref(null)
const aviso = ref('')
const erro = ref('')
const enviando = ref(false)
const infoModelo = ref(null)

const sugestoes = [
  'Resuma este material em até 10 linhas.',
  'Crie 5 questões sobre o capítulo 2.',
  'Liste os principais conceitos explicados no documento.',
  'Explique o conteúdo com palavras simples.',
]

const documentosDisponiveis = computed(() =>
  origem.value === 'publico' ? publicos.value : meusDocumentos.value,
)

function selecionarArquivo(evento) {
  arquivo.value = evento.target.files[0] || null
}

async function carregarHistorico() {
  const { data } = await api.get('/ai/history/')
  historico.value = data.results
}

async function enviar() {
  erro.value = ''
  aviso.value = ''
  resposta.value = null

  if (origem.value === 'upload' && !arquivo.value) {
    erro.value = 'Escolha um arquivo do seu computador.'
    return
  }
  if (origem.value !== 'upload' && !documentoId.value) {
    erro.value = 'Escolha um documento.'
    return
  }

  enviando.value = true
  try {
    let dados
    if (origem.value === 'upload') {
      dados = new FormData()
      dados.append('file', arquivo.value)
      dados.append('prompt', prompt.value)
    } else {
      dados = { document_id: documentoId.value, prompt: prompt.value }
    }
    const { data } = await api.post('/ai/ask/', dados)
    resposta.value = data
    aviso.value = data.notice || ''
    await carregarHistorico()
  } catch (error) {
    erro.value =
      error?.response?.status === 503
        ? 'Assistente indisponível no momento.'
        : mensagemDeErro(error, 'Não foi possível obter a resposta.')
  } finally {
    enviando.value = false
  }
}

function reaproveitar(item) {
  prompt.value = item.prompt
  if (item.document) {
    documentoId.value = String(item.document)
    origem.value = meusDocumentos.value.some((d) => d.id === item.document) ? 'meus' : 'publico'
  }
}

onMounted(async () => {
  try {
    const [meus, publicados, historicoResposta, status] = await Promise.all([
      api.get('/documents/mine/', { params: { page_size: 100 } }),
      api.get('/documents/public/', { params: { page_size: 100 } }),
      api.get('/ai/history/'),
      api.get('/ai/status/'),
    ])
    meusDocumentos.value = meus.data.results
    publicos.value = publicados.data.results
    historico.value = historicoResposta.data.results
    infoModelo.value = status.data

    // Veio de "Perguntar à IA" com o documento já escolhido.
    const preSelecionado = route.query.documento
    if (preSelecionado) {
      documentoId.value = String(preSelecionado)
      const ehMeu = meusDocumentos.value.some((d) => d.id === Number(preSelecionado))
      origem.value = ehMeu ? 'meus' : 'publico'
    }
  } catch (error) {
    erro.value = mensagemDeErro(error, 'Não foi possível carregar o assistente.')
  }
})
</script>

<template>
  <div class="pilha">
    <header>
      <h1>Assistente IA</h1>
      <p class="texto-suave">
        Escolha um documento e faça uma pergunta. A resposta usa apenas o conteúdo do
        material, processado por um modelo que roda na máquina da instituição —
        <strong>nenhum documento é enviado a serviços externos</strong>.
      </p>
    </header>

    <div class="colunas">
      <section class="cartao" aria-labelledby="titulo-pergunta">
        <h2 id="titulo-pergunta" class="apenas-leitor-de-tela">Fazer uma pergunta</h2>
        <form @submit.prevent="enviar">
          <div class="campo">
            <label for="origem">Documento</label>
            <select id="origem" v-model="origem">
              <option value="meus">Meus Documentos</option>
              <option value="publico">Acervo Público</option>
              <option value="upload">Enviar arquivo do computador</option>
            </select>
          </div>

          <div v-if="origem !== 'upload'" class="campo">
            <label for="documento">Escolha o documento</label>
            <select id="documento" v-model="documentoId" required>
              <option value="">Selecione</option>
              <option v-for="d in documentosDisponiveis" :key="d.id" :value="String(d.id)">
                {{ d.title }}
              </option>
            </select>
            <p v-if="!documentosDisponiveis.length" class="campo-ajuda">
              Nenhum documento disponível nesta origem.
            </p>
          </div>

          <div v-else class="campo">
            <label for="arquivo-ia">Arquivo</label>
            <input
              id="arquivo-ia"
              type="file"
              accept=".pdf,.docx,.txt"
              @change="selecionarArquivo"
            />
            <p class="campo-ajuda">
              O arquivo é usado só para esta pergunta: ele não entra no acervo.
            </p>
          </div>

          <div class="campo">
            <label for="prompt">Sua pergunta</label>
            <textarea
              id="prompt"
              v-model.trim="prompt"
              rows="4"
              required
              placeholder="Ex.: Resuma este material"
            ></textarea>
            <div class="sugestoes">
              <p id="rotulo-sugestoes" class="campo-ajuda">Sugestões de pergunta:</p>
              <div class="lista-sugestoes" role="group" aria-labelledby="rotulo-sugestoes">
                <button
                  v-for="sugestao in sugestoes"
                  :key="sugestao"
                  type="button"
                  class="botao botao-secundario botao-pequeno"
                  @click="prompt = sugestao"
                >
                  {{ sugestao }}
                </button>
              </div>
            </div>
          </div>

          <button class="botao" type="submit" :disabled="enviando">
            {{ enviando ? 'Consultando o assistente…' : 'Enviar' }}
          </button>
          <p v-if="infoModelo" class="campo-ajuda">
            Modelo: <strong>{{ infoModelo.model }}</strong> · tempo máximo de espera:
            {{ infoModelo.timeout_seconds }}s
          </p>
        </form>

        <p v-if="erro" class="mensagem mensagem-erro margem-topo">{{ erro }}</p>
        <p v-if="aviso" class="mensagem mensagem-aviso margem-topo">{{ aviso }}</p>

        <div v-if="enviando" class="carregando" role="status">
          <span class="girando" aria-hidden="true">⏳</span>
          Lendo o documento e gerando a resposta…
        </div>

        <article v-else-if="resposta" class="resposta" aria-live="polite" tabindex="-1">
          <h2>Resposta</h2>
          <p class="texto-suave detalhes">
            {{ resposta.document_title }} · {{ resposta.model }} ·
            {{ formatarDuracao(resposta.response_time_ms) }}
          </p>
          <p class="conteudo">{{ resposta.answer }}</p>
        </article>
      </section>

      <section class="cartao" aria-labelledby="titulo-historico">
        <h2 id="titulo-historico">Histórico</h2>
        <p v-if="!historico.length" class="texto-suave">
          Suas perguntas aparecem aqui depois da primeira consulta.
        </p>
        <ul v-else class="historico" aria-label="Suas perguntas anteriores">
          <li v-for="item in historico" :key="item.id">
            <p class="pergunta">{{ item.prompt }}</p>
            <p class="texto-suave detalhes">
              {{ item.document_title }} · {{ formatarDataHora(item.created_at) }}
            </p>
            <details>
              <summary>Ver resposta</summary>
              <p class="conteudo">{{ item.answer }}</p>
            </details>
            <button
              type="button"
              class="botao botao-secundario botao-pequeno"
              @click="reaproveitar(item)"
            >
              Usar esta pergunta
            </button>
          </li>
        </ul>
      </section>
    </div>
  </div>
</template>

<style scoped>
.colunas {
  display: grid;
  grid-template-columns: 1.4fr 1fr;
  gap: 1rem;
  align-items: start;
}

.sugestoes {
  margin-top: 0.5rem;
}

.lista-sugestoes {
  display: flex;
  flex-wrap: wrap;
  gap: 0.4rem;
  margin-top: 0.3rem;
}

.margem-topo {
  margin-top: 1rem;
}

.carregando {
  margin-top: 1.25rem;
  padding: 1rem;
  background: var(--cor-primaria-clara);
  border-radius: var(--raio);
  color: var(--cor-primaria-escura);
  font-weight: 600;
}

.girando {
  display: inline-block;
  animation: girar 1.6s linear infinite;
}

@keyframes girar {
  to {
    transform: rotate(360deg);
  }
}

.resposta {
  margin-top: 1.25rem;
  border-top: 1px solid var(--cor-borda);
  padding-top: 1rem;
}

.conteudo {
  white-space: pre-wrap;
  line-height: 1.6;
}

.detalhes {
  font-size: 0.8rem;
  margin: 0 0 0.5rem;
}

.historico {
  list-style: none;
  margin: 0;
  padding: 0;
  display: flex;
  flex-direction: column;
  gap: 1rem;
  max-height: 640px;
  overflow-y: auto;
}

.historico li {
  border-bottom: 1px solid var(--cor-borda);
  padding-bottom: 0.9rem;
}

.pergunta {
  margin: 0;
  font-weight: 600;
}

summary {
  cursor: pointer;
  font-size: 0.85rem;
  color: var(--cor-primaria);
  margin-bottom: 0.4rem;
}

@media (max-width: 960px) {
  .colunas {
    grid-template-columns: 1fr;
  }
}
</style>
