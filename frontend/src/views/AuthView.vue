<script setup>
import { reactive, ref } from 'vue'
import { RouterLink, useRoute, useRouter } from 'vue-router'

import { mensagemDeErro } from '@/services/api'
import { useAuthStore } from '@/stores/auth'
import LogoMarca from '@/components/marca/LogoMarca.vue'

const auth = useAuthStore()
const router = useRouter()
const route = useRoute()

const aba = ref('entrar')
const erro = ref('')
// Validado aqui, e não pelo required do HTML, porque a mensagem nativa do
// navegador sai no idioma dele — a interface precisa falar português.
const erroTermos = ref('')
const enviando = ref(false)

const login = reactive({ email: '', password: '' })
const cadastro = reactive({
  name: '',
  email: '',
  password: '',
  password_confirm: '',
  accept_terms: false,
})

function trocarAba(nova) {
  aba.value = nova
  erro.value = ''
  erroTermos.value = ''
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
  if (!cadastro.accept_terms) {
    erroTermos.value = 'É preciso aceitar os Termos de Uso e a Política de Privacidade para criar a conta.'
    document.getElementById('cad-termos')?.focus()
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
  <main class="tela">
    <section class="apresentacao" aria-labelledby="titulo-app">
      <h1 id="titulo-app" class="titulo-com-logo"><LogoMarca :tamanho="44" /> Acervo Edu IA</h1>
      <p class="slogan">Conhecimento que transforma</p>
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

    <section class="cartao caixa" aria-label="Acesso à plataforma">
      <div class="abas" role="tablist" aria-label="Entrar ou criar conta">
        <button
          id="aba-entrar"
          type="button"
          role="tab"
          :class="{ ativa: aba === 'entrar' }"
          :aria-selected="aba === 'entrar'"
          aria-controls="painel-entrar"
          :tabindex="aba === 'entrar' ? 0 : -1"
          @click="trocarAba('entrar')"
        >
          Entrar
        </button>
        <button
          id="aba-criar"
          type="button"
          role="tab"
          :class="{ ativa: aba === 'criar' }"
          :aria-selected="aba === 'criar'"
          aria-controls="painel-criar"
          :tabindex="aba === 'criar' ? 0 : -1"
          @click="trocarAba('criar')"
        >
          Criar conta
        </button>
      </div>

      <p v-if="erro" class="mensagem mensagem-erro" role="alert">
        <span aria-hidden="true">⚠ </span>{{ erro }}
      </p>

      <form v-if="aba === 'entrar'" id="painel-entrar" role="tabpanel" aria-labelledby="aba-entrar" @submit.prevent="entrar">
        <div class="campo">
          <label for="login-email">E-mail <span class="obrigatorio" aria-hidden="true">*</span></label>
          <input id="login-email" v-model.trim="login.email" type="email" required autocomplete="email" />
        </div>
        <div class="campo">
          <label for="login-senha">Senha <span class="obrigatorio" aria-hidden="true">*</span></label>
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

      <form v-else id="painel-criar" role="tabpanel" aria-labelledby="aba-criar" @submit.prevent="criarConta">
        <div class="campo">
          <label for="cad-nome">Nome <span class="obrigatorio" aria-hidden="true">*</span></label>
          <input id="cad-nome" v-model.trim="cadastro.name" type="text" required />
        </div>
        <div class="campo">
          <label for="cad-email">E-mail <span class="obrigatorio" aria-hidden="true">*</span></label>
          <input id="cad-email" v-model.trim="cadastro.email" type="email" required autocomplete="email" />
        </div>
        <div class="campo">
          <label for="cad-senha">Senha <span class="obrigatorio" aria-hidden="true">*</span></label>
          <input
            id="cad-senha"
            v-model="cadastro.password"
            type="password"
            required
            minlength="8"
            autocomplete="new-password"
            aria-describedby="ajuda-senha"
          />
          <p id="ajuda-senha" class="campo-ajuda">
            Use ao menos 8 caracteres, com letras e números.
          </p>
        </div>
        <div class="campo">
          <label for="cad-senha2">Confirmar senha <span class="obrigatorio" aria-hidden="true">*</span></label>
          <input
            id="cad-senha2"
            v-model="cadastro.password_confirm"
            type="password"
            required
            autocomplete="new-password"
          />
        </div>
        <div class="campo consentimento" :class="{ 'consentimento-erro': erroTermos }">
          <label for="cad-termos" class="rotulo-consentimento">
            <input
              id="cad-termos"
              v-model="cadastro.accept_terms"
              type="checkbox"
              :aria-invalid="erroTermos ? 'true' : undefined"
              :aria-describedby="erroTermos ? 'erro-termos ajuda-termos' : 'ajuda-termos'"
              @change="erroTermos = ''"
            />
            <span>
              Li e aceito os
              <RouterLink :to="{ name: 'privacidade' }" target="_blank">
                Termos de Uso e a Política de Privacidade
                <span class="apenas-leitor-de-tela">(abre em nova aba)</span>
              </RouterLink>
            </span>
          </label>
          <p v-if="erroTermos" id="erro-termos" class="campo-erro" role="alert">
            <span aria-hidden="true">⚠</span>{{ erroTermos }}
          </p>
          <p id="ajuda-termos" class="campo-ajuda">
            Guardamos apenas nome e e-mail. O assistente de IA roda na máquina da
            instituição — nenhum documento é enviado a serviços externos.
          </p>
        </div>

        <button class="botao largura-total" type="submit" :disabled="enviando">
          {{ enviando ? 'Criando conta…' : 'Criar conta' }}
        </button>
        <p class="campo-ajuda centralizado">Toda conta nova começa com o perfil Aluno.</p>
      </form>
      <p class="campo-ajuda centralizado links-legais">
        <RouterLink :to="{ name: 'privacidade' }">Política de Privacidade</RouterLink>
        <span aria-hidden="true"> · </span>
        <RouterLink :to="{ name: 'acessibilidade' }">Acessibilidade</RouterLink>
      </p>
    </section>
  </main>
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

.apresentacao {
  background: var(--degrade-institucional);
  color: #ffffff;
  padding: 2.5rem;
  border-radius: var(--raio-xl);
}

.titulo-com-logo {
  display: flex;
  align-items: center;
  gap: 0.65rem;
}

.slogan {
  font-weight: 600;
  color: var(--cor-texto-sobre-marinho);
  margin-top: -0.5rem;
}

.apresentacao h1 {
  font-size: 2rem;
  color: #ffffff;
}

.apresentacao p {
  color: var(--cor-texto-sobre-marinho);
  max-width: 42ch;
}

.apresentacao ul {
  list-style: none;
  padding: 0;
  display: flex;
  flex-direction: column;
  gap: 0.5rem;
  color: var(--cor-texto-sobre-marinho);
  font-weight: 600;
}

.caixa {
  padding: 1.5rem;
  border-radius: var(--raio-xl);
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

.consentimento {
  background: var(--cor-fundo);
  border-radius: var(--raio);
  padding: 0.8rem;
  border: 2px solid transparent;
}

.consentimento-erro {
  border-color: var(--cor-erro);
  background: var(--cor-erro-clara);
}

.rotulo-consentimento {
  display: flex;
  align-items: flex-start;
  gap: 0.6rem;
  font-weight: 400;
  font-size: 0.88rem;
  line-height: 1.45;
  cursor: pointer;
  margin-bottom: 0;
}

.rotulo-consentimento input {
  width: 20px;
  height: 20px;
  min-width: 20px;
  margin-top: 0.1rem;
  cursor: pointer;
  accent-color: var(--cor-primaria);
}

.centralizado {
  text-align: center;
}

.links-legais {
  margin-top: 1rem;
  padding-top: 0.75rem;
  border-top: 1px solid var(--cor-borda);
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
