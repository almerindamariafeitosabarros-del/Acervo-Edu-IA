import { defineStore } from 'pinia'

import api, { ACCESS_KEY, REFRESH_KEY } from '@/services/api'

export const useAuthStore = defineStore('auth', {
  state: () => ({
    user: null,
    access: localStorage.getItem(ACCESS_KEY) || '',
    carregado: false,
  }),
  getters: {
    autenticado: (state) => Boolean(state.access),
    perfil: (state) => state.user?.role || '',
    perfilTexto: (state) => state.user?.role_display || '',
    podePublicar: (state) => Boolean(state.user?.permissions?.can_publish_own),
    podeGerenciarCatalogo: (state) => Boolean(state.user?.permissions?.can_manage_catalog),
    podeGerenciarUsuarios: (state) => Boolean(state.user?.permissions?.can_manage_users),
    podeModerarMural: (state) => Boolean(state.user?.permissions?.can_moderate_mural),
  },
  actions: {
    guardarSessao({ user, access, refresh }) {
      this.user = user
      this.access = access
      localStorage.setItem(ACCESS_KEY, access)
      localStorage.setItem(REFRESH_KEY, refresh)
      this.carregado = true
    },
    async entrar(credenciais) {
      const { data } = await api.post('/auth/login/', credenciais)
      this.guardarSessao(data)
      return data.user
    },
    async cadastrar(dados) {
      const { data } = await api.post('/auth/register/', dados)
      this.guardarSessao(data)
      return data.user
    },
    async carregarUsuario() {
      if (!this.access) {
        this.carregado = true
        return null
      }
      try {
        const { data } = await api.get('/auth/me/')
        this.user = data
      } catch {
        this.limpar()
      } finally {
        this.carregado = true
      }
      return this.user
    },
    async atualizarPerfil(dados) {
      const { data } = await api.put('/auth/me/', dados)
      this.user = data
      return data
    },
    async trocarSenha(dados) {
      const { data } = await api.post('/auth/change-password/', dados)
      return data
    },
    limpar() {
      this.user = null
      this.access = ''
      localStorage.removeItem(ACCESS_KEY)
      localStorage.removeItem(REFRESH_KEY)
    },
    sair() {
      this.limpar()
    },
  },
})
