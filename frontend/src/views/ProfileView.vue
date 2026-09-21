<script setup>
import { reactive, ref } from 'vue'
import { RouterLink, useRouter } from 'vue-router'

import api, { mensagemDeErro } from '@/services/api'
import { formatarData, formatarDataHora } from '@/services/formatos'
import { useAuthStore } from '@/stores/auth'

const auth = useAuthStore()
const router = useRouter()

const perfil = reactive({ name: auth.user?.name || '' })
const senha = reactive({ current_password: '', new_password: '', new_password_confirm: '' })

const erroPerfil = ref('')
const avisoPerfil = ref('')
const erroSenha = ref('')
const avisoSenha = ref('')
const salvando = ref(false)
const trocando = ref(false)

async function salvarPerfil() {
  erroPerfil.value = ''
  avisoPerfil.value = ''
  salvando.value = true
  try {
    await auth.atualizarPerfil({ name: perfil.name })
    avisoPerfil.value = 'Dados atualizados.'
  } catch (error) {
    erroPerfil.value = mensagemDeErro(error, 'Não foi possível salvar seus dados.')
  } finally {
    salvando.value = false
  }
}

async function trocarSenha() {
  erroSenha.value = ''
  avisoSenha.value = ''
  if (senha.new_password !== senha.new_password_confirm) {
    erroSenha.value = 'As senhas não conferem.'
    return
  }
  trocando.value = true
  try {
    await auth.trocarSenha({ ...senha })
    avisoSenha.value = 'Senha alterada com sucesso.'
    Object.keys(senha).forEach((chave) => {
      senha[chave] = ''
    })
  } catch (error) {
    erroSenha.value = mensagemDeErro(error, 'Não foi possível trocar a senha.')
  } finally {
    trocando.value = false
  }
}

function sair() {
  auth.sair()
  router.push({ name: 'entrar' })
}

// ---------------------------------------------------------------- LGPD
const exportando = ref(false)
const erroDados = ref('')
const avisoDados = ref('')

const exclusao = reactive({ password: '', confirmation: '' })
const formExclusaoAberto = ref(false)
const excluindo = ref(false)
const erroExclusao = ref('')

/** Direito de acesso e portabilidade (LGPD, art. 18, II e V). */
async function baixarMeusDados() {
  erroDados.value = ''
  avisoDados.value = ''
  exportando.value = true
  try {
    const { data } = await api.get('/auth/me/export/', { responseType: 'blob' })
    const url = URL.createObjectURL(data)
    const link = document.createElement('a')
    link.href = url
    link.download = `meus-dados-acervo-edu-ia-${new Date().toISOString().slice(0, 10)}.json`
    link.click()
    URL.revokeObjectURL(url)
    avisoDados.value = 'Download iniciado. O arquivo traz seus dados em formato JSON.'
  } catch (error) {
    erroDados.value = mensagemDeErro(error, 'Não foi possível exportar seus dados.')
  } finally {
    exportando.value = false
  }
}

/** Direito de eliminação (LGPD, art. 18, VI). */
async function excluirConta() {
  erroExclusao.value = ''
  excluindo.value = true
  try {
    await api.post('/auth/me/delete/', { ...exclusao })
    auth.limpar()
    router.push({ name: 'entrar' })
  } catch (error) {
    erroExclusao.value = mensagemDeErro(error, 'Não foi possível excluir a conta.')
  } finally {
    excluindo.value = false
  }
}
</script>

<template>
  <div class="pilha">
    <header>
      <h1>Meu Perfil</h1>
      <p class="texto-suave">
        Perfil <strong>{{ auth.perfilTexto }}</strong> · conta criada em
        {{ formatarData(auth.user?.date_joined) }}
      </p>
    </header>

    <section class="cartao">
      <h2>Dados da conta</h2>
      <p v-if="erroPerfil" class="mensagem mensagem-erro" role="alert">{{ erroPerfil }}</p>
      <p v-if="avisoPerfil" class="mensagem mensagem-sucesso" role="status">{{ avisoPerfil }}</p>
      <form @submit.prevent="salvarPerfil">
        <div class="campo">
          <label for="nome">Nome</label>
          <input id="nome" v-model.trim="perfil.name" type="text" required />
        </div>
        <div class="campo">
          <label for="email">E-mail</label>
          <input id="email" :value="auth.user?.email" type="email" disabled />
          <p class="campo-ajuda">O e-mail de login não pode ser alterado.</p>
        </div>
        <button class="botao" type="submit" :disabled="salvando">
          {{ salvando ? 'Salvando…' : 'Salvar' }}
        </button>
      </form>
    </section>

    <section class="cartao">
      <h2>Trocar senha</h2>
      <p v-if="erroSenha" class="mensagem mensagem-erro" role="alert">{{ erroSenha }}</p>
      <p v-if="avisoSenha" class="mensagem mensagem-sucesso" role="status">{{ avisoSenha }}</p>
      <form @submit.prevent="trocarSenha">
        <div class="campo">
          <label for="senha-atual">Senha atual</label>
          <input
            id="senha-atual"
            v-model="senha.current_password"
            type="password"
            required
            autocomplete="current-password"
          />
        </div>
        <div class="linha-campos">
          <div class="campo">
            <label for="senha-nova">Nova senha</label>
            <input
              id="senha-nova"
              v-model="senha.new_password"
              type="password"
              required
              minlength="8"
              autocomplete="new-password"
            />
          </div>
          <div class="campo">
            <label for="senha-nova2">Confirmar nova senha</label>
            <input
              id="senha-nova2"
              v-model="senha.new_password_confirm"
              type="password"
              required
              autocomplete="new-password"
            />
          </div>
        </div>
        <button class="botao" type="submit" :disabled="trocando">
          {{ trocando ? 'Alterando…' : 'Trocar senha' }}
        </button>
      </form>
    </section>

    <section class="cartao" aria-labelledby="titulo-dados">
      <h2 id="titulo-dados">Meus dados pessoais</h2>
      <p class="texto-suave">
        Direitos garantidos pela LGPD (Lei 13.709/2018, art. 18). Leia a
        <RouterLink :to="{ name: 'privacidade' }">Política de Privacidade</RouterLink>
        para saber o que guardamos e por quê.
      </p>

      <p v-if="erroDados" class="mensagem mensagem-erro" role="alert">{{ erroDados }}</p>
      <p v-if="avisoDados" class="mensagem mensagem-sucesso" role="status">{{ avisoDados }}</p>

      <div class="bloco-direito">
        <div>
          <h3>Baixar meus dados</h3>
          <p class="texto-suave">
            Um arquivo JSON com seu cadastro, a lista dos seus documentos e o histórico de
            perguntas ao assistente.
          </p>
        </div>
        <button
          class="botao botao-secundario"
          type="button"
          :disabled="exportando"
          @click="baixarMeusDados"
        >
          {{ exportando ? 'Preparando…' : '⬇ Baixar meus dados' }}
        </button>
      </div>

      <p v-if="auth.user?.accepted_terms_at" class="texto-suave consentimento-info">
        Consentimento registrado em
        {{ formatarDataHora(auth.user.accepted_terms_at) }} (versão
        {{ auth.user.accepted_terms_version }}).
      </p>
    </section>

    <section class="cartao perigo" aria-labelledby="titulo-exclusao">
      <h2 id="titulo-exclusao">Excluir minha conta</h2>
      <p>
        Apaga <strong>em definitivo</strong> seu cadastro, todos os documentos que você
        enviou (inclusive os arquivos) e todo o histórico do assistente.
        <strong>Não há como desfazer.</strong>
      </p>
      <p class="texto-suave">
        Se quiser guardar seu material, baixe os documentos antes pela tela
        <RouterLink :to="{ name: 'meus-documentos' }">Meus Documentos</RouterLink>.
      </p>

      <button
        v-if="!formExclusaoAberto"
        class="botao botao-perigo"
        type="button"
        @click="formExclusaoAberto = true"
      >
        Quero excluir minha conta
      </button>

      <form v-else @submit.prevent="excluirConta">
        <p v-if="erroExclusao" class="mensagem mensagem-erro" role="alert">
          {{ erroExclusao }}
        </p>

        <div class="campo">
          <label for="exclusao-senha">Sua senha <span class="obrigatorio" aria-hidden="true">*</span></label>
          <input
            id="exclusao-senha"
            v-model="exclusao.password"
            type="password"
            required
            autocomplete="current-password"
          />
        </div>

        <div class="campo">
          <label for="exclusao-confirmacao">
            Digite <strong>EXCLUIR</strong> para confirmar
            <span class="obrigatorio" aria-hidden="true">*</span>
          </label>
          <input
            id="exclusao-confirmacao"
            v-model="exclusao.confirmation"
            type="text"
            required
            aria-describedby="ajuda-exclusao"
          />
          <p id="ajuda-exclusao" class="campo-ajuda">
            A confirmação escrita evita exclusões por engano.
          </p>
        </div>

        <div class="acoes">
          <button class="botao botao-perigo" type="submit" :disabled="excluindo">
            {{ excluindo ? 'Excluindo…' : 'Excluir definitivamente' }}
          </button>
          <button
            class="botao botao-secundario"
            type="button"
            @click="formExclusaoAberto = false"
          >
            Cancelar
          </button>
        </div>
      </form>
    </section>

    <section class="cartao">
      <h2>Encerrar sessão</h2>
      <p class="texto-suave">Você voltará para a tela de Cadastro/Login.</p>
      <button class="botao botao-perigo" type="button" @click="sair">Sair</button>
    </section>
  </div>
</template>

<style scoped>
.bloco-direito {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 1rem;
  flex-wrap: wrap;
  border: 1px solid var(--cor-borda);
  border-radius: var(--raio);
  padding: 0.9rem;
  margin-top: 1rem;
}

.bloco-direito h3 {
  margin-bottom: 0.2rem;
}

.bloco-direito p {
  margin: 0;
  font-size: 0.88rem;
  max-width: 52ch;
}

.consentimento-info {
  font-size: 0.82rem;
  margin: 1rem 0 0;
}

.perigo {
  border-color: var(--cor-erro);
  border-width: 2px;
}
</style>
