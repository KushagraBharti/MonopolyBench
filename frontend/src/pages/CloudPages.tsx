import { useEffect, useRef, useState, type ReactNode, type FormEvent } from 'react'
import { CLOUD_API, cloudRequest, type CloudJob, type CloudCampaign, type CloudLive, type CloudConfig } from '@/net/jobs'
import { Board } from '@/components/board/Board'
import { PlayerStackPanel } from '@/components/panels/PlayerStackPanel'
import { useGameStore } from '@/state/store'
import { useCloudStore } from '@/state/cloud'
import { EventFeed } from '@/components/feed/EventFeed'
import { ChatFeed } from '@/components/feed/ChatFeed'
import { Inspector } from '@/components/panels/Inspector'
import { AuctionPanel } from '@/components/panels/AuctionPanel'
import { TradeInspectorPanel } from '@/components/panels/TradeInspectorPanel'
import { LlmIoPanel } from '@/components/panels/LlmIoPanel'
import { ThoughtsPanel } from '@/components/panels/ThoughtsPanel'
import './cloud.css'

function usePoll<T>(path: string) {
  const [data, setData] = useState<T | null>(null)
  const [error, setError] = useState('')
  useEffect(() => {
    let active = true
    let timer: ReturnType<typeof setTimeout>
    const load = async () => {
      try { const value = await cloudRequest<T>(path); if (active) { setData(value); setError('') } }
      catch (e) { if (active) setError(String(e)) }
      finally { if (active) timer = setTimeout(load, 5000) }
    }
    void load()
    return () => { active = false; clearTimeout(timer) }
  }, [path])
  return { data, error }
}

function Shell({ children }: { children: ReactNode }) {
  return <div className="cloud-shell"><aside><a className="cloud-brand" href="/">MonopolyBench</a><p>Cloud workspace</p><nav><a href="/">All games</a><a href="/?status=running">Active</a><a href="/?status=completed">Completed</a><a href="/?archived=true">Archived</a><a href="/campaigns">Campaigns</a><a href="/runs">Saved runs</a><a href="/research">Research</a></nav><button onClick={() => void cloudRequest('/auth/logout', {}).then(() => window.location.assign('/login'))}>Log out</button></aside><main>{children}</main></div>
}

export function LoginPage() {
  const [password, setPassword] = useState('')
  const [error, setError] = useState('')
  const [busy, setBusy] = useState(false)
  async function submit(e: FormEvent) {
    e.preventDefault(); setBusy(true); setError('')
    try { await cloudRequest('/auth/login', { password }); window.location.assign('/') }
    catch (e) { setError(String(e)); setBusy(false) }
  }
  return <main className="cloud-login"><form onSubmit={submit}><h1>MonopolyBench</h1><p>Sign in to your cloud workspace.</p><label>Password<input autoFocus type="password" autoComplete="current-password" required value={password} onChange={e => setPassword(e.target.value)} /></label><button disabled={busy}>{busy ? 'Signing in…' : 'Sign in'}</button><p role="alert">{error}</p></form></main>
}

const models = ['anthropic/claude-opus-5.5', 'openai/gpt-6.1-sol', 'google/gemini-4-argon', 'x-ai/grok-4.7']
function RunModal({ close }: { close: () => void }) {
  const dialog = useRef<HTMLDialogElement>(null)
  useEffect(() => { dialog.current?.showModal() }, [])
  const [step, setStep] = useState(1)
  const [kind, setKind] = useState('smoke')
  const [seats, setSeats] = useState(models)
  const [effort, setEffort] = useState('medium')
  const [turns, setTurns] = useState(5)
  const [count, setCount] = useState(1)
  const [prepared, setPrepared] = useState<{ preparation_id: string; configs: CloudConfig[] } | null>(null)
  const [error, setError] = useState('')
  const [busy, setBusy] = useState(false)
  const [launchKey] = useState(() => crypto.randomUUID())
  async function next() {
    setError(''); setBusy(true)
    try {
      if (step === 1 && kind === 'campaign') { window.location.assign('/campaigns'); return }
      if (step === 2) setPrepared(await cloudRequest('/smoke/prepare', { models: seats, effort, max_turns: turns, count }))
      if (step === 3 && prepared) { await cloudRequest('/smoke', { preparation_id: prepared.preparation_id, idempotency_key: launchKey }); close(); return }
      setStep(step + 1)
    } catch (e) { setError(String(e)) } finally { setBusy(false) }
  }
  return <dialog ref={dialog} onCancel={close} aria-labelledby="run-title" className="cloud-modal"><button className="cloud-close" onClick={close} aria-label="Close">×</button><h2 id="run-title">Run games · {step} / 3</h2>
    {step === 1 ? <><p>What would you like to run?</p><label><input type="radio" checked={kind === 'campaign'} onChange={() => setKind('campaign')} /> Frozen campaign</label><label><input type="radio" checked={kind === 'smoke'} onChange={() => setKind('smoke')} /> Smoke games · excluded from research</label></> : null}
    {step === 2 ? <>{seats.map((model, i) => <label key={i}>Seat {i + 1}<select value={model} onChange={e => setSeats(seats.map((m, n) => n === i ? e.target.value : m))}>{models.map(m => <option key={m}>{m}</option>)}</select></label>)}<label>Provider-native effort<select value={effort} onChange={e => setEffort(e.target.value)}>{['low', 'medium', 'high'].map(e => <option key={e}>{e}</option>)}</select></label><label>Turn cap<input type="number" min={5} max={10} value={turns} onChange={e => setTurns(Number(e.target.value))} /></label><label>Games<input type="number" min={1} max={20} value={count} onChange={e => setCount(Number(e.target.value))} /></label></> : null}
    {step === 3 ? <><p>Smoke games use the same execution and recovery path as campaign games.</p>{prepared?.configs.map(c => <article key={c.run_id}><strong>Seed {c.seed}</strong><p>{c.players.map(p => p.name).join(' → ')}</p><small>{c.players[0].reasoning.effort} effort · {c.max_turns} turns · code {c.git_sha.slice(0, 8)}</small></article>)}</> : null}
    <p role="alert">{error}</p><button disabled={busy} onClick={() => void next()}>{busy ? 'Working…' : step === 3 ? 'Launch' : 'Continue'}</button>{step > 1 ? <button disabled={busy} onClick={() => setStep(step - 1)}>Back</button> : null}
  </dialog>
}

function JobActions({ job }: { job: CloudJob }) {
  const [error, setError] = useState('')
  const [busy, setBusy] = useState(false)
  async function act(action: string) {
    setBusy(true); setError('')
    try { await cloudRequest(`/jobs/${job.job_id}/${action}`, {}) }
    catch (e) { setError(String(e)) }
    finally { setBusy(false) }
  }
  return <><div className="cloud-actions">{job.export_status === 'ready' ? <a href={`${CLOUD_API}/jobs/${job.job_id}/export`}>Export</a> : null}{job.allowed_actions.map(action => <button disabled={busy} key={action} onClick={() => void act(action)}>{action}</button>)}</div><p role="alert">{error}</p></>
}

function JobCard({ job }: { job: CloudJob }) {
  const [error, setError] = useState('')
  const slow = job.slow
  return <article className="cloud-card"><div className="cloud-card-head"><strong>{job.status}</strong><span>{job.kind}</span></div>{job.snapshot ? <div className="cloud-thumbnail"><Board spaces={job.snapshot.board} players={job.snapshot.players} activePlayerId={job.snapshot.active_player_id} /></div> : <div className="cloud-placeholder">Waiting to begin</div>}<h2><a href={`/games/${job.job_id}`}>{job.run_id}</a></h2><p>Seed {job.config.seed} · Turn {job.snapshot?.turn_index ?? '—'} {slow ? '· Slow' : ''} {(job.snapshot?.turn_index ?? 0) > 300 ? '· Long' : ''}</p><div className="cloud-chips">{job.config.players.map(p => <span key={p.player_id}>{p.name} · {p.reasoning.effort}</span>)}</div><p>${job.cost.known_total.toFixed(2)} recorded {job.cost.unknown_calls + job.cost.missing_calls > 0 ? '· incomplete cost' : ''}</p><p>{job.pause_reason}{job.repaired ? ' · Repaired' : job.recovered ? ' · Recovered' : ''}</p><small>Replay: {job.replay_status || 'pending'} · Export: {job.export_status || 'pending'}</small><div className="cloud-actions"><a href={`/games/${job.job_id}`}>Watch</a>{job.export_status === 'ready' ? <a href={`${CLOUD_API}/jobs/${job.job_id}/export`}>Export</a> : null}{job.allowed_actions.map(action => <button key={action} onClick={() => void cloudRequest(`/jobs/${job.job_id}/${action}`, {}).catch(e => setError(String(e)))}>{action}</button>)}</div><p role="alert">{error}</p></article>
}

export function GamesPage() {
  const [search, setSearch] = useState('')
  const [cursor, setCursor] = useState(0)
  const [modal, setModal] = useState(false)
  const query = new URLSearchParams(window.location.search)
  query.set('search', search); query.set('cursor', String(cursor))
  const { data, error } = usePoll<{ jobs: CloudJob[]; next_cursor: number | null }>(`/jobs?${query}`)
  const { data: status } = usePoll<{ account_stop: unknown; free_disk: number; active_workers: number; cost: { known_total: number }; preflight: { passed: boolean } | null }>('/status')
  const [actionError, setActionError] = useState('')
  return <Shell><header><div><h1>All games</h1><p>{status?.active_workers ?? 0} running · ${status?.cost.known_total.toFixed(2) ?? '0.00'} recorded · {((status?.free_disk ?? 0)/1e9).toFixed(1)} GB free</p></div><button onClick={() => setModal(true)}>Run games</button></header>{status?.account_stop ? <div role="alert" className="cloud-banner">Account paused. Check your OpenRouter key and credits. <button onClick={() => void cloudRequest('/resume-all', {}).catch(e => setActionError(String(e)))}>Resume all</button></div> : null}{!status?.preflight?.passed ? <div className="cloud-banner">Preflight has not passed. New games wait in the queue. <button onClick={() => void cloudRequest('/preflight/run', {}).catch(e => setActionError(String(e)))}>Run preflight</button></div> : null}<label>Search<input type="search" value={search} onChange={e => { setSearch(e.target.value); setCursor(0) }} placeholder="Run, seed, model, campaign" /></label><p role="alert">{error || actionError}</p><div className="cloud-grid">{data?.jobs.map(job => <JobCard key={job.job_id} job={job} />)}</div>{data?.jobs.length === 0 ? <p>No games here yet. Start a smoke game or open a frozen campaign.</p> : null}<div className="cloud-actions"><button disabled={cursor === 0} onClick={() => setCursor(Math.max(0, cursor - 50))}>Previous</button><button disabled={data?.next_cursor == null} onClick={() => setCursor(data?.next_cursor ?? 0)}>Next</button></div>{modal ? <RunModal close={() => setModal(false)} /> : null}</Shell>
}

export function CampaignPage() {
  const id = window.location.pathname.split('/')[2]
  const { data, error } = usePoll<CloudCampaign | CloudCampaign[]>(id ? `/campaigns/${id}` : '/campaigns')
  const [actionError, setActionError] = useState('')
  const [exportId, setExportId] = useState('')
  const [exporting, setExporting] = useState(false)
  async function prepareExport() {
    setExporting(true); setActionError('')
    try { setExportId((await cloudRequest<{ export_id: string }>(`/campaigns/${id}/export`, {})).export_id) }
    catch (e) { setActionError(String(e)) }
    finally { setExporting(false) }
  }
  const campaign = data && !Array.isArray(data) ? data : null
  return <Shell><h1>{id || 'Campaigns'}</h1><p role="alert">{error || actionError}</p>{Array.isArray(data) ? data.map(c => <article className="cloud-card" key={c.campaign_id}><a href={`/campaigns/${c.campaign_id}`}>{c.campaign_id}</a><p>{c.status}</p></article>) : null}{campaign ? <><p>{campaign.status} · {campaign.cells.length} cells</p><div className="cloud-actions">{(campaign.status === 'draft' ? ['freeze'] : ['run', 'pause']).map(action => <button key={action} onClick={() => void cloudRequest(`/campaigns/${id}/${action}`, {}).catch(e => setActionError(String(e)))}>{action}</button>)}{campaign.status !== 'draft' ? <button disabled={exporting} onClick={() => void prepareExport()}>{exporting ? 'Preparing export…' : 'Prepare campaign export'}</button> : null}{exportId ? <a href={`${CLOUD_API}/exports/${exportId}/download`}>Download campaign</a> : null}</div><div className="cloud-grid">{campaign.cells.map(cell => <article className="cloud-card" key={cell.cell_index}><h2>Cell {cell.cell_index + 1}</h2><p>Seed {cell.seed} · {cell.job_status || 'queued'}</p><p>Launch rank {cell.execution_rank + 1} · Reruns {cell.rerun_count}</p>{cell.job_id ? <a href={`/games/${cell.job_id}`}>Open game</a> : null}</article>)}</div></> : null}</Shell>
}

export function GamePage() {
  const id = window.location.pathname.split('/')[2]
  const { data: job, error } = usePoll<CloudJob>(`/jobs/${id}`)
  const [tab, setTab] = useState('Live')
  const [connected, setConnected] = useState(false)
  const snapshot = useCloudStore(s => s.views[id]?.snapshot)
  const [rows, setRows] = useState<unknown>(null)
  const [cursor, setCursor] = useState(0)
  const [decisionPageSize, setDecisionPageSize] = useState(0)
  const [tabError, setTabError] = useState('')
  useEffect(() => {
    let active = true
    let socket: WebSocket
    let timer: ReturnType<typeof setTimeout>
    let commit = 0, generation = -1
    useGameStore.getState().resetLogs()
    const connect = () => {
      const url = new URL(`${CLOUD_API}/jobs/${id}/ws`, window.location.href)
      url.protocol = url.protocol === 'https:' ? 'wss:' : 'ws:'
      url.searchParams.set('after', String(commit)); url.searchParams.set('generation', String(generation))
      socket = new WebSocket(url)
      socket.onopen = () => setConnected(true)
      socket.onmessage = message => {
        const envelope: CloudLive = JSON.parse(message.data)
        if (envelope.type === 'HELLO' || envelope.job_id !== id) return
        useCloudStore.getState().receive(envelope)
        const store = useGameStore.getState()
        if (envelope.reset) store.resetEvents()
        if (envelope.snapshot) store.setSnapshot(envelope.snapshot)
        envelope.events.forEach(event => store.pushEvent(event))
        commit = envelope.commit_seq; generation = envelope.recovery_generation
      }
      socket.onclose = event => { setConnected(false); if (event.code === 4401) window.location.assign('/login'); else if (active) timer = setTimeout(connect, 2000) }
    }
    connect()
    return () => { active = false; clearTimeout(timer); socket?.close() }
  }, [id])
  useEffect(() => {
    if (job) useGameStore.getState().setRunStatus({ runId: job.run_id, running: job.status === 'running', paused: job.status === 'paused', players: job.config.players.map(p => ({ ...p, model_display_name: p.name })) })
  }, [job])
  useEffect(() => {
    if (tab === 'Live' || tab === 'Decisions') return
    let active = true
    const path = '/artifacts'
    void cloudRequest(`/jobs/${id}${path}`).then(value => { if (active) { setRows(value); setTabError('') } }).catch(e => { if (active) setTabError(String(e)) })
    return () => { active = false }
  }, [id, tab, cursor])
  const current = snapshot?.run_id === job?.run_id ? snapshot : job?.snapshot
  return <Shell><h1>{job?.run_id || 'Loading game…'}</h1><p>{job?.status} · {connected ? 'Live connection' : 'Reconnecting…'}</p>{job ? <JobActions job={job} /> : null}<p role="alert">{error || tabError}</p><nav className="cloud-tabs">{['Live', 'Decisions', 'Artifacts', 'Replay', 'Analysis'].map(name => <button aria-pressed={tab === name} key={name} onClick={() => { setTab(name); setCursor(0) }}>{name}</button>)}</nav>{tab === 'Live' ? <>{current ? <div className="cloud-live"><Board spaces={current.board} players={current.players} activePlayerId={current.active_player_id} /><PlayerStackPanel /></div> : <p>Waiting for the first committed snapshot.</p>}<AuctionPanel visible /><TradeInspectorPanel visible /><div className="cloud-live cloud-feed-panels"><EventFeed /><ChatFeed /></div><ThoughtsPanel /><Inspector /></> : tab === 'Decisions' ? <><LlmIoPanel jobId={id} cursor={cursor} revision={job?.commit_seq} onPageSize={setDecisionPageSize} /><button disabled={cursor === 0} onClick={() => setCursor(Math.max(0, cursor-50))}>Previous</button><button disabled={decisionPageSize < 50} onClick={() => setCursor(cursor+50)}>Next</button></> : <><p>{tab === 'Replay' ? `Replay verdict: ${job?.replay_status || 'pending'}` : 'Open an artifact to inspect its contents.'}</p>{Array.isArray(rows) ? rows.filter((r: { path: string }) => tab === 'Replay' ? r.path.includes('replay') : true).map((r: { path: string; bytes: number }) => <p key={r.path}><a href={`${CLOUD_API}/jobs/${id}/artifacts?path=${encodeURIComponent(r.path)}`}>{r.path}</a> · {r.bytes} bytes</p>) : null}{job?.export_status === 'ready' ? <a href={`${CLOUD_API}/jobs/${id}/export`}>Download game with analysis</a> : null}</>}</Shell>
}
