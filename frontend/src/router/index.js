import { createRouter, createWebHistory } from 'vue-router'

import { useAuthStore } from '@/stores/auth'

const routes = [
  {
    path: '/entrar',
    name: 'entrar',
    component: () => import('@/views/AuthView.vue'),
    meta: { publico: true, titulo: 'Entrar' },
  },
  {
    path: '/privacidade',
    name: 'privacidade',
    component: () => import('@/views/PrivacyView.vue'),
    meta: { publico: true, semSessao: true, titulo: 'Política de Privacidade' },
  },
  {
    path: '/acessibilidade',
    name: 'acessibilidade',
    component: () => import('@/views/AccessibilityView.vue'),
    meta: { publico: true, semSessao: true, titulo: 'Declaração de Acessibilidade' },
  },
  {
    path: '/',
    component: () => import('@/components/AppLayout.vue'),
    children: [
      {
        path: '',
        name: 'inicio',
        component: () => import('@/views/HomeView.vue'),
        meta: { titulo: 'Início' },
      },
      {
        path: 'acervo',
        name: 'acervo',
        component: () => import('@/views/PublicLibraryView.vue'),
        meta: { titulo: 'Acervo Público' },
      },
      {
        path: 'meus-documentos',
        name: 'meus-documentos',
        component: () => import('@/views/MyDocumentsView.vue'),
        meta: { titulo: 'Meus Documentos' },
      },
      {
        path: 'documentos/novo',
        name: 'documento-novo',
        component: () => import('@/views/DocumentFormView.vue'),
        meta: { titulo: 'Novo documento' },
      },
      {
        path: 'documentos/:id/editar',
        name: 'documento-editar',
        component: () => import('@/views/DocumentFormView.vue'),
        meta: { titulo: 'Editar documento' },
      },
      {
        path: 'documentos/:id',
        name: 'documento-detalhes',
        component: () => import('@/views/DocumentDetailView.vue'),
        meta: { titulo: 'Detalhes do documento' },
      },
      {
        path: 'assistente',
        name: 'assistente',
        component: () => import('@/views/AssistantView.vue'),
        meta: { titulo: 'Assistente IA' },
      },
      {
        path: 'perfil',
        name: 'perfil',
        component: () => import('@/views/ProfileView.vue'),
        meta: { titulo: 'Meu Perfil' },
      },
      {
        path: 'administracao',
        name: 'administracao',
        component: () => import('@/views/AdminView.vue'),
        meta: { titulo: 'Administração', exigePerfil: 'catalogo' },
      },
    ],
  },
  { path: '/:pathMatch(.*)*', redirect: { name: 'inicio' } },
]

const router = createRouter({
  history: createWebHistory(),
  routes,
  scrollBehavior: () => ({ top: 0 }),
})

// Usuário não autenticado sempre volta para a tela de Cadastro/Login.
router.beforeEach(async (to) => {
  const auth = useAuthStore()

  if (!auth.carregado) {
    await auth.carregarUsuario()
  }

  // Privacidade e acessibilidade abrem para qualquer pessoa, logada ou não.
  if (to.meta.semSessao) {
    return true
  }

  if (to.meta.publico) {
    return auth.autenticado ? { name: 'inicio' } : true
  }

  if (!auth.autenticado) {
    return { name: 'entrar', query: { proxima: to.fullPath } }
  }

  if (to.meta.exigePerfil === 'catalogo' && !auth.podeGerenciarCatalogo) {
    return { name: 'inicio' }
  }

  return true
})

router.afterEach((to) => {
  document.title = to.meta.titulo ? `${to.meta.titulo} — Acervo Edu IA` : 'Acervo Edu IA'
})

export default router
