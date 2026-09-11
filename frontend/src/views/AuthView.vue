<script setup>
import { reactive, ref } from 'vue'
import { useRoute, useRouter } from 'vue-router'

import { mensagemDeErro } from '@/services/api'
import { useAuthStore } from '@/stores/auth'

const auth = useAuthStore()
const router = useRouter()
const route = useRoute()

const aba = ref('entrar')
const erro = ref('')
const enviando = ref(false)

const login = reactive({ email: '', password: '' })
const cadastro = reactive({ name: '', email: '', password: '', password_confirm: '' })

function trocarAba(nova) {
  aba.value = nova
  erro.value = ''
}

async function concluir() {
  const proxima = route.query.proxima
  await router.push(typeof proxima === 'string' ? proxima : { name: 'inicio' })
}

async function entrar() {
  erro.value = ''
  enviando.value = true
  try {
    await auth.entrar({ email: login.email, password: login.password })
    await concluir()
  } catch (error) {
    erro.value = mensagemDeErro(error, 'E-mail ou senha inválidos.')
  } finally {
    enviando.value = false
  }
}

async function criarConta() {
  erro.value = ''
  if (cadastro.password !== cadastro.password_confirm) {
    erro.value = 'As senhas não conferem.'
    return
  }
  enviando.value = true
  try {
    await auth.cadastrar({ ...cadastro })
    await concluir()
  } catch (error) {
    erro.value = mensagemDeErro(error, 'Não foi possível criar a conta.')
  } finally {
    enviando.value = false
  }
}
</script>

<template>
  <div class="tela">
    <section class="apresentacao">
      <h1>📘 Acervo Edu IA</h1>
      <p>
        Guarde, organize e compartilhe materiais educacionais. Publique no Acervo Público
        e use o assistente de IA local para entender seus documentos.
      </p>
      <ul>
        <li>📁 Documentos privados por padrão</li>
        <li>📚 Acervo Público para todos os cadastrados</li>
        <li>🤖 Assistente de IA que responde sobre o material escolhido</li>
      </ul>
    </section>

    <section class="cartao caixa">
      <div class="abas" role="tablist">
        <button
          type="button"
          role="tab"
          :class="{ ativa: aba === 'entrar' }"
          :aria-selected="aba === 'entrar'"
          @click="trocarAba('entrar')"
        >
          Entrar
        </button>
        <button
          type="button"
          role="tab"
          :class="{ ativa: aba === 'criar' }"
          :aria-selected="aba === 'criar'"
          @click="trocarAba('criar')"
        >
          Criar conta
        </button>
      </div>

      <p v-if="erro" class="mensagem mensagem-erro">{{ erro }}</p>

      <form v-if="aba === 'entrar'" @submit.prevent="entrar">
        <div class="campo">
          <label for="login-email">E-mail</label>
          <input id="login-email" v-model.trim="login.email" type="email" required autocomplete="email" />
        </div>
        <div class="campo">
          <label for="login-senha">Senha</label>
          <input
            id="login-senha"
            v-model="login.password"
            type="password"
            required
            autocomplete="current-password"
          />
        </div>
        <button class="botao largura-total" type="submit" :disabled="enviando">
          {{ enviando ? 'Entrando…' : 'Entrar' }}
        </button>
      </form>

      <form v-else @submit.prevent="criarConta">
        <div class="campo">
          <label for="cad-nome">Nome</label>
          <input id="cad-nome" v-model.trim="cadastro.name" type="text" required />
        </div>
        <div class="campo">
          <label for="cad-email">E-mail</label>
          <input id="cad-email" v-model.trim="cadastro.email" type="email" required autocomplete="email" />
        </div>
        <div class="campo">
          <label for="cad-senha">Senha</label>
          <input
            id="cad-senha"
            v-model="cadastro.password"
            type="password"
            required
            minlength="8"
            autocomplete="new-password"
          />
          <p class="campo-ajuda">Use ao menos 8 caracteres, com letras e números.</p>
        </div>
        <div class="campo">
          <label for="cad-senha2">Confirmar senha</label>
          <input
            id="cad-senha2"
            v-model="cadastro.password_confirm"
            type="password"
            required
            autocomplete="new-password"
          />
        </div>
        <button class="botao largura-total" type="submit" :disabled="enviando">
          {{ enviando ? 'Criando conta…' : 'Criar conta' }}
        </button>
        <p class="campo-ajuda centralizado">Toda conta nova começa com o perfil Aluno.</p>
      </form>
    </section>
  </div>
</template>

<style scoped>
.tela {
  min-height: 100vh;
  display: grid;
  grid-template-columns: 1fr 1fr;
  align-items: center;
  gap: 3rem;
  padding: 2rem;
  max-width: 1100px;
  margin: 0 auto;
}

.apresentacao h1 {
  font-size: 2rem;
}

.apresentacao p {
  color: var(--cor-texto-suave);
  max-width: 42ch;
}

.apresentacao ul {
  list-style: none;
  padding: 0;
  display: flex;
  flex-direction: column;
  gap: 0.5rem;
  color: var(--cor-texto-suave);
}

.caixa {
  padding: 1.5rem;
}

.abas {
  display: flex;
  gap: 0.5rem;
  margin-bottom: 1.25rem;
  border-bottom: 1px solid var(--cor-borda);
}

.abas button {
  flex: 1;
  padding: 0.6rem;
  border: none;
  background: none;
  font: inherit;
  font-weight: 600;
  color: var(--cor-texto-suave);
  cursor: pointer;
  border-bottom: 2px solid transparent;
}

.abas button.ativa {
  color: var(--cor-primaria);
  border-bottom-color: var(--cor-primaria);
}

.largura-total {
  width: 100%;
}

.centralizado {
  text-align: center;
}

@media (max-width: 860px) {
  .tela {
    grid-template-columns: 1fr;
    gap: 1.5rem;
    padding: 1.5rem 1rem;
  }

  .apresentacao ul {
    display: none;
  }
}
</style>
