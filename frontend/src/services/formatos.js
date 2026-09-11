/** Formatações usadas nas telas. */

export function formatarData(valor) {
  if (!valor) return '—'
  return new Date(valor).toLocaleDateString('pt-BR')
}

export function formatarDataHora(valor) {
  if (!valor) return '—'
  return new Date(valor).toLocaleString('pt-BR', {
    day: '2-digit',
    month: '2-digit',
    year: 'numeric',
    hour: '2-digit',
    minute: '2-digit',
  })
}

export function formatarTamanho(bytes) {
  if (!bytes) return '—'
  const mb = bytes / (1024 * 1024)
  if (mb >= 1) return `${mb.toFixed(1).replace('.', ',')} MB`
  return `${Math.max(1, Math.round(bytes / 1024))} KB`
}

export function formatarDuracao(ms) {
  if (!ms) return '—'
  return `${(ms / 1000).toFixed(1).replace('.', ',')} s`
}
