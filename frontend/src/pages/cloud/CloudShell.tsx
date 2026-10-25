import { useRef, useState, type ReactNode } from 'react'
import { cloudRequest, type CampaignCell } from '@/net/jobs'
import { cellStatus, errorText, modelInfo, type Tone } from './cloudUi'
import '../cloud.css'

const NAV = [
  { href: '/', label: 'Games', match: (path: string, search: string) => path === '/' && !search.includes('archived=true') },
  { href: '/campaigns', label: 'Campaigns', match: (path: string) => path === '/campaigns' || (path.startsWith('/campaigns/') && path !== '/campaigns/new') },
]
const HISTORY = [
  { href: '/?archived=true', label: 'Archived games' },
  { href: '/runs', label: 'Saved runs' },
  { href: '/research', label: 'Research outputs' },
]

export function Shell({ children }: { children: ReactNode }) {
  const { pathname, search } = window.location
  const creating = pathname === '/campaigns/new'
  return <div className="cloud-shell">
    <a className="cb-skip" href="#cloud-main">Skip to content</a>
    <aside>
      <a className="cloud-brand" href="/"><span className="cb-brand-mark" aria-hidden="true" />MonopolyBench</a>
      <a className="cb-btn cb-btn-primary cb-nav-cta" href="/campaigns/new" aria-current={creating ? 'page' : undefined}>Create campaign</a>
      <nav aria-label="Main">
        {NAV.map(item => <a key={item.href} href={item.href} aria-current={item.match(pathname, search) ? 'page' : undefined}>{item.label}</a>)}
      </nav>
      <details className="cb-nav-more" open={HISTORY.some(item => item.href === pathname + search || (item.href !== '/?archived=true' && pathname.startsWith(item.href))) || undefined}>
        <summary>History and research</summary>
        <nav aria-label="History and research">
          {HISTORY.map(item => <a key={item.href} href={item.href}>{item.label}</a>)}
        </nav>
      </details>
      <button className="cb-btn cb-btn-ghost cb-logout" onClick={() => void cloudRequest('/auth/logout', {}).then(() => window.location.assign('/login'))}>Log out</button>
    </aside>
    <main id="cloud-main">{children}</main>
  </div>
}

export function StatusPill({ label, tone }: { label: string; tone: Tone }) {
  return <span className="cb-pill" data-tone={tone}>{label}</span>
}

export function Token({ model, seat }: { model: string; seat?: number }) {
  const info = modelInfo(model)
  return <span className="cb-token" style={{ background: info.color, color: info.ink }} title={seat ? `Seat ${seat}: ${info.name}` : info.name} aria-hidden="true">{info.mark}</span>
}

/** Models in seat order. Seat 1 moves first. */
export function SeatTokens({ models, labelled = false }: { models: string[]; labelled?: boolean }) {
  const names = models.map((m, i) => `seat ${i + 1} ${modelInfo(m).name}`).join(', ')
  return <ol className="cb-seats" data-labelled={labelled || undefined} aria-label={`Seating: ${names}`}>
    {models.map((model, i) => <li key={i}><Token model={model} seat={i + 1} />{labelled ? <span>{modelInfo(model).name}</span> : null}</li>)}
  </ol>
}

/** One tile per game, like the property squares along a board edge. */
export function GameTiles({ cells }: { cells: CampaignCell[] }) {
  const ordered = [...cells].sort((a, b) => a.execution_rank - b.execution_rank)
  return <ol className="cb-tiles" aria-hidden="true">
    {ordered.map(cell => <li key={cell.cell_index} data-tone={cellStatus(cell)[1]} />)}
  </ol>
}

export function Notice({ tone = 'warn', title, children, role }: { tone?: Tone; title: string; children?: ReactNode; role?: 'alert' | 'status' }) {
  return <section className="cb-notice" data-tone={tone} role={role}>
    <h2>{title}</h2>
    {children}
  </section>
}

/** Runs the paid model connection check (preflight). Always asks first. */
export function CheckConnections({ onDone, label = 'Check model connections' }: { onDone?: (passed: boolean) => void; label?: string }) {
  const [busy, setBusy] = useState(false)
  const [result, setResult] = useState('')
  const lock = useRef(false)
  async function run() {
    if (lock.current) return
    if (!window.confirm('This sends one short request to each model through OpenRouter. It is paid from your existing provider funding (your OpenRouter balance, or your own provider account for any connected keys). It can take a few minutes. Continue?')) return
    lock.current = true; setBusy(true); setResult('')
    try {
      const report = await cloudRequest<{ passed?: boolean }>('/preflight/run', {})
      setResult(report?.passed ? 'All model connections passed.' : 'Some model connections failed. Check the OpenRouter key and credits, then try again.')
      onDone?.(Boolean(report?.passed))
    } catch (e) {
      setResult(errorText(e))
      onDone?.(false)
    } finally {
      lock.current = false; setBusy(false)
    }
  }
  return <div className="cb-check">
    <button className="cb-btn cb-btn-secondary" disabled={busy} onClick={() => void run()}>{busy ? 'Checking model connections…' : label}</button>
    <p role="status" aria-live="polite">{result}</p>
  </div>
}

export function Facts({ rows }: { rows: [string, ReactNode][] }) {
  return <dl className="cb-facts">{rows.map(([term, value]) => <div key={term}><dt>{term}</dt><dd>{value}</dd></div>)}</dl>
}
