import { defineStore } from 'pinia'

import api from '@/services/api'

/** Instituições, cursos, disciplinas, categorias e tags usados nos filtros e formulários. */
export const useCatalogoStore = defineStore('catalogo', {
  state: () => ({
    instituicoes: [],
    cursos: [],
    disciplinas: [],
    categorias: [],
    tags: [],
    carregado: false,
  }),
  actions: {
    async carregar(forcar = false) {
      if (this.carregado && !forcar) return
      const [instituicoes, cursos, disciplinas, categorias, tags] = await Promise.all([
        api.get('/institutions/'),
        api.get('/courses/'),
        api.get('/subjects/'),
        api.get('/categories/'),
        api.get('/tags/'),
      ])
      this.instituicoes = instituicoes.data
      this.cursos = cursos.data
      this.disciplinas = disciplinas.data
      this.categorias = categorias.data
      this.tags = tags.data
      this.carregado = true
    },
    cursosDaInstituicao(institutionId) {
      if (!institutionId) return this.cursos
      return this.cursos.filter((curso) => curso.institution === Number(institutionId))
    },
    disciplinasDoCurso(courseId) {
      if (!courseId) return this.disciplinas
      return this.disciplinas.filter((disciplina) => disciplina.course === Number(courseId))
    },
    disciplinaPorId(subjectId) {
      return this.disciplinas.find((disciplina) => disciplina.id === Number(subjectId)) || null
    },
  },
})
