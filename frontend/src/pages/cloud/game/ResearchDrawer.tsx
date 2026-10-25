import { useEffect, useRef, useState, type ReactNode } from 'react'
import { CLOUD_API, cloudRequest, type CloudJob } from '@/net/jobs'
import { LlmIoPanel } from '@/components/panels/LlmIoPanel'
import { useGameStore } from '@/state/store'
import { trapTab } from '@/components/ui/focusTrap'
import type { StateSnapshot } from '@/net/contracts'
import { DeedTable } from './DeedTable'
import type { Seat } from './gameModel'
import { Facts } from '../CloudShell'
import { downloadWait, errorText, exportFailed, fileSize, modelInfo, settingsLine } from '../cloudUi'

export const DRAWER_TABS = ['Deeds', 'Overview', 'Decisions', 'Artifacts', 'Replay', 'Analysis'] as const
export type DrawerTab = typeof DRAWER_TABS[number]

type Artifact = { path: string; bytes: number }
const ANALYSIS = /analysis|summary|scorecard|review|usage|cost|report/i
const PAGE = 50

function ArtifactList({ id, rows, empty }: { id: string; rows: Artifact[]; empty: string }) {
  if (rows.length === 0) return <p className="mbg-muted">{empty}</p>
  return <ul className="mbd-files">{rows.map(r => <li key={r.path}><a href={`${CLOUD_API}/jobs/${id}/artifacts?path=${encodeURIComponent(r.path)}`}>{r.path}</a><span>{fileSize(r.bytes)}</span></li>)}</ul>
}

/** Deeds, research and settings for one game. Read-only views plus the existing inspector. */
export function ResearchDrawer({ job, snapshot, seats, open, tab, onTab, onClose }: { job: CloudJob; snapshot: StateSnapshot | null; seats: Seat[]; open: boolean; tab: DrawerTab; onTab: (tab: DrawerTab) => void; onClose: () => void }) {
  const id = job.job_id
  const closeRef = useRef<HTMLButtonElement>(null)
  const panelRef = useRef<HTMLElement>(null)
  // The inspector opens above the drawer; while it is up the drawer is inert and ignores keys.
  const inspectorOpen = useGameStore(s => s.inspectorOpen)
  const [rows, setRows] = useState<Artifact[] | null>(null)
  const [error, setError] = useState('')
  const [cursor, setCursor] = useState(0)
  const [pageSize, setPageSize] = useState(0)
  const [nonce, setNonce] = useState(0)
  const needsFiles = open && (tab === 'Artifacts' || tab === 'Replay' || tab === 'Analysis')

  useEffect(() => {
    if (!open) return
    closeRef.current?.focus()
    const onKey = (e: KeyboardEvent) => {
      if (e.defaultPrevented || useGameStore.getState().inspectorOpen) return
      if (e.key === 'Escape') { e.preventDefault(); onClose() }
      else trapTab(e, panelRef.current)
    }
    window.addEventListener('keydown', onKey)
    return () => window.removeEventListener('keydown', onKey)
  }, [open, onClose])

  useEffect(() => {
    if (!needsFiles) return
    let active = true
    cloudRequest<Artifact[]>(`/jobs/${id}/artifacts`)
      .then(value => { if (active) { setRows(Array.isArray(value) ? value : []); setError('') } })
      .catch(e => { if (active) setError(errorText(e)) })
    return () => { active = false }
  }, [id, needsFiles, nonce])

  if (!open) return null
  const exportReady = job.export_status === 'ready'
  const fallbacks = Object.entries(job.config.response_policy?.fallback_models ?? {})
  const wait = downloadWait(job)
  const download = exportReady ? <a className="cb-btn cb-btn-secondary" href={`${CLOUD_API}/jobs/${id}/export`}>Download game with analysis</a> : <p className={exportFailed(job) ? 'cb-error' : 'cb-wait'} role={exportFailed(job) ? 'alert' : undefined}>{wait}</p>

  let body: ReactNode
  if (tab === 'Deeds') {
    body = snapshot ? <DeedTable snapshot={snapshot} seats={seats} /> : <p className="mbg-muted">No saved board yet.</p>
  } else if (tab === 'Overview') {
    body = <>
      <Facts rows={[
        ['Settings', settingsLine(job.config)],
        ['Run ID', <code>{job.run_id}</code>],
        ['Seed', <code>{job.config.seed}</code>],
        ['Code version', <code>{job.config.git_sha || '—'}</code>],
        ['Recorded cost', `$${job.cost.known_total.toFixed(2)}${job.cost.unknown_calls + job.cost.missing_calls > 0 ? ' (some calls unreported)' : ''}`],
        ['Model calls', String(job.cost.calls)],
        ['Replay check', job.replay_status || 'Pending'],
        ['Download', exportReady ? 'Ready' : job.export_status || 'Pending'],
        ['Recovery', job.repaired ? 'Repaired' : job.recovered ? 'Recovered' : 'None'],
        ...(job.rerun_of_job_id ? [['Rerun of', <a href={`/games/${job.rerun_of_job_id}`}>Original game</a>] as [string, ReactNode]] : []),
      ]} />
      <h3>Seats</h3>
      <ol className="mbd-seats">{job.config.players.map((p, i) => <li key={p.player_id}>
        <strong>Seat {i + 1}</strong> {modelInfo(p.openrouter_model_id).name} <code>{p.openrouter_model_id}</code> · {p.reasoning.effort} effort
        {job.config.response_policy?.fallback_models[p.openrouter_model_id] ? <span className="mbg-muted"> · configured fallback {job.config.response_policy.fallback_models[p.openrouter_model_id]} (used only if needed; see Decisions)</span> : null}
      </li>)}</ol>
      {fallbacks.length === 0 ? <p className="mbg-muted">No fallback models configured.</p> : null}
      <div className="cb-actions">
        {download}
        <button type="button" className="cb-btn cb-btn-ghost" onClick={() => { useGameStore.getState().setInspectorOpen(true) }}>Open system inspector</button>
      </div>
    </>
  } else if (tab === 'Decisions') {
    body = <div className="mbd-decisions">
      <div className="mbd-decisions-panel"><LlmIoPanel jobId={id} cursor={cursor} revision={job.commit_seq} onPageSize={setPageSize} /></div>
      <div className="cb-actions">
        <button type="button" className="cb-btn cb-btn-ghost" disabled={cursor === 0} onClick={() => setCursor(Math.max(0, cursor - PAGE))}>Previous decisions</button>
        <button type="button" className="cb-btn cb-btn-ghost" disabled={pageSize < PAGE} onClick={() => setCursor(cursor + PAGE)}>Next decisions</button>
      </div>
    </div>
  } else {
    const all = rows ?? []
    const shown = tab === 'Replay' ? all.filter(r => r.path.includes('replay')) : tab === 'Analysis' ? all.filter(r => ANALYSIS.test(r.path)) : all
    body = <>
      {tab === 'Replay' ? <p>Replay verdict: <strong>{job.replay_status || 'pending'}</strong></p> : null}
      {tab === 'Analysis' ? download : null}
      {error ? <p className="cb-error" role="alert">{error}</p> : null}
      {rows === null && !error ? <p className="mbg-muted" role="status">Loading files…</p> : <ArtifactList id={id} rows={shown} empty={tab === 'Replay' ? 'No replay files yet.' : tab === 'Analysis' ? 'No analysis files yet. They are written when the game finishes.' : 'No files yet.'} />}
      <button type="button" className="cb-btn cb-btn-ghost" onClick={() => setNonce(n => n + 1)}>Refresh files</button>
    </>
  }

  return <div className="mbd-backdrop" inert={inspectorOpen || undefined} onMouseDown={e => { if (e.target === e.currentTarget) onClose() }}>
    <aside ref={panelRef} className="mbd" role="dialog" aria-modal="true" aria-labelledby="mbd-title" tabIndex={-1}>
      <header className="mbd-head">
        <h2 id="mbd-title">Game details and research</h2>
        <button ref={closeRef} type="button" className="cb-btn cb-btn-ghost" onClick={onClose}>Close</button>
      </header>
      <nav className="mbd-tabs" aria-label="Research sections">
        {DRAWER_TABS.map(name => <button key={name} type="button" aria-pressed={tab === name} onClick={() => { onTab(name); setCursor(0) }}>{name}</button>)}
      </nav>
      <div className="mbd-body" data-tab={tab}>{body}</div>
    </aside>
  </div>
}
