// app/utils/api.ts — thin fetch wrapper for the TempCover API

function getBase(): string {
  try {
    const config = useRuntimeConfig()
    return (config.public.apiBase as string) || ''
  } catch {
    return process.env.NUXT_PUBLIC_API_BASE || ''
  }
}

async function request<T = any>(
  method: string,
  endpoint: string,
  body?: any,
  token?: string,
): Promise<T> {
  const headers: Record<string, string> = {}
  if (token) headers['Authorization'] = `Bearer ${token}`
  if (body !== undefined) headers['Content-Type'] = 'application/json'

  const res = await fetch(`${getBase()}${endpoint}`, {
    method,
    headers,
    body: body !== undefined ? JSON.stringify(body) : undefined,
  })

  if (res.status === 204) return {} as T

  // Token expired / invalid — drop the session and go back to the admin login
  if (res.status === 401) {
    if (typeof window !== 'undefined') {
      localStorage.clear()
      window.location.href = '/admin/login'
    }
    throw new Error('Session expired. Please sign in again.')
  }

  const data = await res.json().catch(() => ({}))

  // Expired or suspended agent account (403 from the auth dependency) — end the session too
  if (res.status === 403 && typeof data.detail === 'string' && /expired|suspended/i.test(data.detail)) {
    if (typeof window !== 'undefined') {
      localStorage.clear()
      window.location.href = '/admin/login?reason=expired'
    }
    throw new Error(data.detail)
  }

  if (!res.ok) {
    const detail = data.detail
    throw new Error(
      typeof detail === 'string' ? detail
      : Array.isArray(detail) ? detail.map((d: any) => d.msg).join(', ')
      : data.message || 'Request failed',
    )
  }
  return data as T
}

export const api = {
  get<T = any>(endpoint: string, token?: string): Promise<T> {
    return request<T>('GET', endpoint, undefined, token)
  },
  post<T = any>(endpoint: string, body: any, token?: string): Promise<T> {
    return request<T>('POST', endpoint, body, token)
  },
  patch<T = any>(endpoint: string, body: any, token?: string): Promise<T> {
    return request<T>('PATCH', endpoint, body, token)
  },
  delete<T = any>(endpoint: string, token?: string): Promise<T> {
    return request<T>('DELETE', endpoint, undefined, token)
  },
  /** Absolute URL for links that open API resources directly (PDFs, uploads). */
  url(endpoint: string): string {
    return `${getBase()}${endpoint}`
  },
}
