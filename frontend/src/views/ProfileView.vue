<script setup>
import { reactive, ref } from 'vue'
import { useRouter } from 'vue-router'

import { mensagemDeErro } from '@/services/api'
import { formatarData } from '@/services/formatos'
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
      <p v-if="erroPerfil" class="mensagem mensagem-erro">{{ erroPerfil }}</p>
      <p v-if="avisoPerfil" class="mensagem mensagem-sucesso">{{ avisoPerfil }}</p>
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
      <p v-if="erroSenha" class="mensagem mensagem-erro">{{ erroSenha }}</p>
      <p v-if="avisoSenha" class="mensagem mensagem-sucesso">{{ avisoSenha }}</p>
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

    <section class="cartao">
      <h2>Encerrar sessão</h2>
      <p class="texto-suave">Você voltará para a tela de Cadastro/Login.</p>
      <button class="botao botao-perigo" type="button" @click="sair">Sair</button>
    </section>
  </div>
</template>
