// app/utils/format.ts — display helpers
// Policy times are stored in UTC and shown in UK time (Europe/London) everywhere — the same
// wall clock the agent typed and the one printed in the PDF documents and emails.

const TZ = 'Europe/London'

const GB = 'en-GB'

export function fmtDateTime(iso?: string | null): string {
  if (!iso) return '—'
  const d = new Date(iso)
  if (isNaN(d.getTime())) return String(iso)
  return d.toLocaleString(GB, { day: '2-digit', month: 'short', year: 'numeric', hour: '2-digit', minute: '2-digit', timeZone: TZ })
}

export function fmtDateTimeLong(iso?: string | null): string {
  if (!iso) return '—'
  const d = new Date(iso)
  if (isNaN(d.getTime())) return String(iso)
  return d.toLocaleString(GB, { weekday: 'long', day: '2-digit', month: 'long', year: 'numeric', hour: '2-digit', minute: '2-digit', timeZone: TZ })
}

export function fmtDate(iso?: string | null): string {
  if (!iso) return '—'
  const d = new Date(iso)
  if (isNaN(d.getTime())) return String(iso)
  return d.toLocaleDateString(GB, { day: '2-digit', month: 'short', year: 'numeric', timeZone: TZ })
}

/** "YYYY-MM-DD" -> "12 March 1990" (no timezone shifting) */
export function fmtDOB(ymd?: string | null): string {
  if (!ymd) return '—'
  const [y, m, d] = ymd.split('-').map(Number)
  if (!y || !m || !d) return ymd
  return new Date(Date.UTC(y, m - 1, d)).toLocaleDateString(GB, { day: '2-digit', month: 'long', year: 'numeric', timeZone: 'UTC' })
}

export function fmtMoney(v: number | string | null | undefined): string {
  const n = Number(v)
  return isNaN(n) ? '—' : `£${n.toFixed(2)}`
}

/** Human "ends in" text for an active policy, e.g. "2d 5h left"; '' if in the past */
export function timeLeft(iso?: string | null): string {
  if (!iso) return ''
  const ms = new Date(iso).getTime() - Date.now()
  if (ms <= 0) return ''
  const h = Math.floor(ms / 3600000)
  const d = Math.floor(h / 24)
  if (d >= 1) return `${d}d ${h % 24}h left`
  const m = Math.floor((ms % 3600000) / 60000)
  return h >= 1 ? `${h}h ${m}m left` : `${m}m left`
}

/** ISO datetime -> { date: 'YYYY-MM-DD', time: 'HH:MM' } in UK time (round-trips what the agent entered) */
export function splitDateTime(iso?: string | null): { date: string; time: string } {
  if (!iso) return { date: '', time: '' }
  const d = new Date(iso)
  if (isNaN(d.getTime())) return { date: '', time: '' }
  const parts = new Intl.DateTimeFormat('en-GB', {
    timeZone: TZ, year: 'numeric', month: '2-digit', day: '2-digit', hour: '2-digit', minute: '2-digit', hourCycle: 'h23',
  }).formatToParts(d)
  const get = (t: string) => parts.find(x => x.type === t)?.value ?? ''
  return { date: `${get('year')}-${get('month')}-${get('day')}`, time: `${get('hour')}:${get('minute')}` }
}

/** Human "starts in" text for a pending policy; '' once started */
export function timeUntil(iso?: string | null): string {
  if (!iso) return ''
  const ms = new Date(iso).getTime() - Date.now()
  if (ms <= 0) return ''
  const h = Math.floor(ms / 3600000)
  const d = Math.floor(h / 24)
  if (d >= 1) return `starts in ${d}d ${h % 24}h`
  const m = Math.floor((ms % 3600000) / 60000)
  return h >= 1 ? `starts in ${h}h ${m}m` : `starts in ${m}m`
}
