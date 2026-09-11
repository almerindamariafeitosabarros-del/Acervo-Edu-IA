<script setup>
import { onMounted, reactive, ref } from 'vue'

import api, { mensagemDeErro } from '@/services/api'
import { formatarData } from '@/services/formatos'
import { useAuthStore } from '@/stores/auth'

const auth = useAuthStore()

const usuarios = ref([])
const busca = ref('')
const carregando = ref(true)
const erro = ref('')
const aviso = ref('')

const perfis = [
  { valor: 'student', rotulo: 'Aluno' },
  { valor: 'teacher', rotulo: 'Professor' },
  { valor: 'manager', rotulo: 'Gestor' },
  { valor: 'admin', rotulo: 'Administrador' },
]

const novo = reactive({ name: '', email: '', role: 'student', password: '' })
const criando = ref(false)

async function carregar() {
  carregando.value = true
  try {
    const params = { page_size: 100 }
    if (busca.value) params.search = busca.value
    const { data } = await api.get('/users/', { params })
    usuarios.value = data.results || data
  } catch (error) {
    erro.value = mensagemDeErro(error, 'Não foi possível carregar os usuários.')
  } finally {
    carregando.value = false
  }
}

async function alterarPerfil(usuario, role) {
  erro.value = ''
  try {
    await api.patch(`/users/${usuario.id}/`, { role })
    aviso.value = `Perfil de ${usuario.name} alterado.`
    carregar()
  } catch (error) {
    erro.value = mensagemDeErro(error, 'Não foi possível alterar o perfil.')
  }
}

async function alternarAtivo(usuario) {
  erro.value = ''
  try {
    await api.post(`/users/${usuario.id}/toggle_active/`)
    aviso.value = `Conta de ${usuario.name} ${usuario.is_active ? 'desativada' : 'ativada'}.`
    carregar()
  } catch (error) {
    erro.value = mensagemDeErro(error, 'Não foi possível alterar a situação da conta.')
  }
}

async function criarUsuario() {
  erro.value = ''
  criando.value = true
  try {
    await api.post('/users/', { ...novo })
    aviso.value = 'Usuário criado.'
    Object.assign(novo, { name: '', email: '', role: 'student', password: '' })
    carregar()
  } catch (error) {
    erro.value = mensagemDeErro(error, 'Não foi possível criar o usuário.')
  } finally {
    criando.value = false
  }
}

onMounted(carregar)
</script>

<template>
  <div class="pilha">
    <p v-if="erro" class="mensagem mensagem-erro">{{ erro }}</p>
    <p v-if="aviso" class="mensagem mensagem-sucesso">{{ aviso }}</p>

    <section class="cartao">
      <h2>Novo usuário</h2>
      <form class="linha-campos" @submit.prevent="criarUsuario">
        <div class="campo">
          <label for="u-nome">Nome</label>
          <input id="u-nome" v-model.trim="novo.name" type="text" required />
        </div>
        <div class="campo">
          <label for="u-email">E-mail</label>
          <input id="u-email" v-model.trim="novo.email" type="email" required />
        </div>
        <div class="campo">
          <label for="u-perfil">Perfil</label>
          <select id="u-perfil" v-model="novo.role">
            <option v-for="p in perfis" :key="p.valor" :value="p.valor">{{ p.rotulo }}</option>
          </select>
        </div>
        <div class="campo">
          <label for="u-senha">Senha inicial</label>
          <input id="u-senha" v-model="novo.password" type="text" minlength="8" required />
        </div>
        <div class="campo">
          <label>&nbsp;</label>
          <button class="botao" type="submit" :disabled="criando">Criar</button>
        </div>
      </form>
    </section>

    <section class="cartao">
      <div class="entre cabecalho">
        <h2>Usuários</h2>
        <form @submit.prevent="carregar">
          <input v-model.trim="busca" type="search" placeholder="Buscar por nome ou e-mail" />
        </form>
      </div>

      <p v-if="carregando" class="texto-suave">Carregando…</p>
      <div v-else class="rolagem-horizontal">
        <table class="tabela">
          <thead>
            <tr>
              <th>Nome</th>
              <th>E-mail</th>
              <th>Perfil</th>
              <th>Documentos</th>
              <th>Cadastro</th>
              <th>Situação</th>
            </tr>
          </thead>
          <tbody>
            <tr v-for="usuario in usuarios" :key="usuario.id">
              <td>{{ usuario.name }}</td>
              <td class="texto-suave">{{ usuario.email }}</td>
              <td>
                <select
                  :value="usuario.role"
                  :disabled="usuario.id === auth.user?.id"
                  @change="alterarPerfil(usuario, $event.target.value)"
                >
                  <option v-for="p in perfis" :key="p.valor" :value="p.valor">{{ p.rotulo }}</option>
                </select>
              </td>
              <td class="texto-suave">{{ usuario.documents_count }}</td>
              <td class="texto-suave">{{ formatarData(usuario.date_joined) }}</td>
              <td>
                <div class="acoes">
                  <span class="selo" :class="usuario.is_active ? 'selo-publico' : 'selo-privado'">
                    {{ usuario.is_active ? 'Ativo' : 'Inativo' }}
                  </span>
                  <button
                    v-if="usuario.id !== auth.user?.id"
                    type="button"
                    class="botao botao-secundario botao-pequeno"
                    @click="alternarAtivo(usuario)"
                  >
                    {{ usuario.is_active ? 'Desativar' : 'Ativar' }}
                  </button>
                </div>
              </td>
            </tr>
          </tbody>
        </table>
      </div>
    </section>
  </div>
</template>

<style scoped>
.cabecalho {
  margin-bottom: 1rem;
}
</style>
