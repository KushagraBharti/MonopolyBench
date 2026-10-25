import { useId, useRef, useState, type CSSProperties, type ReactNode } from 'react'
import { LabLogo } from '@/components/LabLogo'
import { getSeatColor } from '@/domain/monopoly/colors'
import { cloudRequest, type CampaignCell } from '@/net/jobs'
import { cellStatus, errorText, modelInfo, parseBudget, type Tone } from './cloudUi'
import '../cloud.css'

export type Section = 'dashboard' | 'games' | 'campaigns' | 'tests' | 'exports'
const NAV: { href: string; label: string; section: Section }[] = [
  { href: '/', label: 'Dashboard', section: 'dashboard' },
  { href: '/games', label: 'Games', section: 'games' },
  { href: '/campaigns', label: 'Campaigns', section: 'campaigns' },
  { href: '/tests', label: 'Tests', section: 'tests' },
  { href: '/exports', label: 'Exports', section: 'exports' },
]

function sectionFor(path: string): Section | null {
  if (path === '/' || path === '/dashboard') return 'dashboard'
  for (const item of NAV.slice(1)) if (path === item.href || path.startsWith(item.href + '/')) return item.section
  return null
}

/** Workspace frame. `section` overrides the path match, e.g. a model test opened under /games/{id}. */
export function Shell({ children, section }: { children: ReactNode; section?: Section | null }) {
  const { pathname } = window.location
  const current = section ?? sectionFor(pathname)
  const [menuOpen, setMenuOpen] = useState(false)
  return <div className="cloud-shell">
    <a className="cb-skip" href="#cloud-main">Skip to content</a>
    <aside>
      <div className="cb-side-top">
        <a className="cloud-brand" href="/"><span className="cb-brand-mark" aria-hidden="true" />MonopolyBench</a>
        <button type="button" className="cb-btn cb-btn-ghost cb-menu-toggle" aria-expanded={menuOpen} aria-controls="cloud-menu" onClick={() => setMenuOpen(open => !open)}>{menuOpen ? 'Close menu' : 'Menu'}</button>
      </div>
      <div className="cb-side-menu" id="cloud-menu" data-open={menuOpen || undefined}>
        <nav aria-label="Main">
          {NAV.map(item => <a key={item.href} href={item.href} aria-current={item.section === current ? (pathname === item.href || (item.section === 'dashboard' && pathname === '/dashboard') ? 'page' : 'true') : undefined}>{item.label}</a>)}
        </nav>
        <button className="cb-btn cb-btn-ghost cb-logout" onClick={() => void cloudRequest('/auth/logout', {}).then(() => window.location.assign('/login'))}>Log out</button>
      </div>
    </aside>
    <main id="cloud-main">{children}</main>
  </div>
}

export function StatusPill({ label, tone }: { label: string; tone: Tone }) {
  return <span className="cb-pill" data-tone={tone}>{label}</span>
}

export function Token({ model, seat }: { model: string; seat?: number }) {
  const info = modelInfo(model)
  // Logo comes from the model id; the ring color comes from the seat, so repeated models stay distinct.
  const style = seat ? { '--cb-seat': getSeatColor(seat - 1) } as CSSProperties : undefined
  return <span className="cb-token" data-seat={seat || undefined} style={style} title={seat ? `Seat ${seat}: ${info.name}` : info.name} aria-hidden="true"><LabLogo model={model} decorative /></span>
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

/** Optional pause threshold on recorded spend. Explains that it is not a hard cap. */
export function BudgetField({ value, onChange, scope = 'game' }: { value: string; onChange: (text: string) => void; scope?: 'game' | 'each game' | 'campaign' }) {
  const id = useId()
  const { problem } = parseBudget(value)
  return <div className="cb-field">
    <label htmlFor={`${id}-budget`}>Pause at recorded spend <span className="cb-optional">(optional)</span></label>
    <p className="cb-hint" id={`${id}-budget-hint`}>{scope === 'campaign' ? 'Share this threshold across the whole campaign.' : 'Apply this threshold to each game.'} Further requests pause when recorded spend reaches this US dollar amount. Leave empty for no spend pause.</p>
    <div className="cb-money"><span aria-hidden="true">$</span><input id={`${id}-budget`} className="cb-input cb-input-short" inputMode="decimal" autoComplete="off" placeholder="None" value={value} aria-invalid={Boolean(problem) || undefined} aria-describedby={`${id}-budget-hint ${id}-budget-note`} onChange={e => onChange(e.target.value)} /></div>
    {problem ? <p className="cb-error" role="alert">{problem}</p> : null}
    <BudgetNote id={`${id}-budget-note`} />
  </div>
}

export function BudgetNote({ id }: { id?: string }) {
  return <details className="cb-disclosure cb-disclosure-small" id={id}>
    <summary>How the spend pause works</summary>
    <ul className="cb-reasons cb-hint">
      <li>This is not a guaranteed hard cap. Model requests already in flight can finish and push spend past the amount.</li>
      <li>Recorded spend counts the provider and OpenRouter charges reported for each call. It isn’t your free quota or your final invoice.</li>
      <li>If a call’s cost isn’t reported, the game pauses to be safe.</li>
      <li>The threshold is saved with the run settings. Resume cannot bypass a reached threshold.</li>
      <li>Games use your existing provider funding. This app makes no purchases.</li>
    </ul>
  </details>
}
