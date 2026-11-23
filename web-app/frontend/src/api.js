export const API_BASE = (import.meta.env?.VITE_API_BASE_URL || 'http://127.0.0.1:8000').replace(/\/+$/, '')

async function request(path, init) {
  let response
  try {
    response = await fetch(API_BASE + path, init)
  } catch (error) {
    if (error.name === 'AbortError') throw error
    throw new Error('Cannot reach FastAPI at ' + API_BASE + '. Start the backend and check VITE_API_BASE_URL.')
  }
  if (!response.ok) {
    const body = await response.json().catch(() => null)
    const detail = body?.detail
    throw new Error(typeof detail === 'string' ? detail :
      Array.isArray(detail) ? detail.map(item => item.msg).join(' · ') :
        'The API returned HTTP ' + response.status + '.')
  }
  return response.json()
}

export const api = {
  options: signal => request('/api/options', { signal }),
  model: signal => request('/api/model-info', { signal }),
  history: (series, signal) => request('/api/history?' + new URLSearchParams(series), { signal }),
  predict: (series, signal) => request('/api/predict', {
    method: 'POST', headers: { 'Content-Type': 'application/json' }, body: JSON.stringify(series), signal,
  }),
}
