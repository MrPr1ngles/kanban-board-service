// Обёртка над fetch: JWT в заголовке, единая обработка 401 и ошибок API
let onUnauthorized = () => {}
export function setUnauthorizedHandler(fn) { onUnauthorized = fn }

export async function api(path, { method = 'GET', body } = {}) {
  const token = localStorage.getItem('token')
  const res = await fetch(`/api${path}`, {
    method,
    headers: {
      'Content-Type': 'application/json',
      ...(token ? { Authorization: `Bearer ${token}` } : {}),
    },
    body: body ? JSON.stringify(body) : undefined,
  })
  if (res.status === 401) {
    onUnauthorized()
    throw new ApiError(401, 'Требуется вход')
  }
  if (res.status === 204) return null
  const data = await res.json().catch(() => null)
  if (!res.ok) throw new ApiError(res.status, data?.detail || 'Ошибка запроса')
  return data
}

export class ApiError extends Error {
  constructor(status, message) {
    super(message)
    this.status = status
  }
}
