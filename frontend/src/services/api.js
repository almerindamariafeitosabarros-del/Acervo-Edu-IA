import axios from 'axios'

const baseURL = import.meta.env.VITE_API_URL || 'http://localhost:8000/api'

export const ACCESS_KEY = 'acervo_access'
export const REFRESH_KEY = 'acervo_refresh'

const api = axios.create({ baseURL })

api.interceptors.request.use((config) => {
  const token = localStorage.getItem(ACCESS_KEY)
  if (token) {
    config.headers.Authorization = `Bearer ${token}`
  }
  return config
})

// Renova o token automaticamente quando a API responde 401.
let refreshing = null

api.interceptors.response.use(
  (response) => response,
  async (error) => {
    const original = error.config
    const status = error.response?.status
    const isAuthRoute = original?.url?.includes('/auth/login') || original?.url?.includes('/auth/refresh')

    if (status === 401 && !original?._retried && !isAuthRoute) {
      const refresh = localStorage.getItem(REFRESH_KEY)
      if (!refresh) {
        forceLogout()
        return Promise.reject(error)
      }
      original._retried = true
      try {
        refreshing =
          refreshing ||
          axios.post(`${baseURL}/auth/refresh/`, { refresh }).finally(() => {
            refreshing = null
          })
        const { data } = await refreshing
        localStorage.setItem(ACCESS_KEY, data.access)
        original.headers.Authorization = `Bearer ${data.access}`
        return api(original)
      } catch (refreshError) {
        forceLogout()
        return Promise.reject(refreshError)
      }
    }
    return Promise.reject(error)
  },
)

function forceLogout() {
  localStorage.removeItem(ACCESS_KEY)
  localStorage.removeItem(REFRESH_KEY)
  if (window.location.pathname !== '/entrar') {
    window.location.assign('/entrar')
  }
}

/** Transforma o erro da API em uma mensagem em português para a tela. */
export function mensagemDeErro(error, padrao = 'Não foi possível concluir a ação.') {
  const data = error?.response?.data
  if (!data) {
    if (error?.code === 'ERR_NETWORK') return 'Não foi possível falar com o servidor.'
    return padrao
  }
  if (typeof data === 'string') return data
  if (data.detail) return data.detail
  const primeiro = Object.values(data)[0]
  if (Array.isArray(primeiro)) return String(primeiro[0])
  if (typeof primeiro === 'string') return primeiro
  return padrao
}

export default api
