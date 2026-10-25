import { useEffect, useRef, useState, type FormEvent, type ReactNode } from 'react'
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
import { CheckConnections, Facts, Notice, SeatTokens, Shell, StatusPill } from './cloud/CloudShell'
import { ACTION_LABELS, campaignName, duration, errorText, jobStatus, jobTitle, modelInfo, ROSTER, usePoll } from './cloud/cloudUi'
import './cloud.css'

export function LoginPage() {
  const [password, setPassword] = useState('')
  const [error, setError] = useState('')
  const [busy, setBusy] = useState(false)
  async function submit(e: FormEvent) {
    e.preventDefault(); setBusy(true); setError('')
    try { await cloudRequest('/auth/login', { password }); window.location.assign('/') }
    catch (e) { setError(errorText(e)); setBusy(false) }
  }
  return <main className="cloud-login"><form onSubmit={submit}><span className="cb-brand-mark" aria-hidden="true" /><h1>MonopolyBench</h1><p>Sign in to your cloud workspace.</p><label>Password<input autoFocus type="password" autoComplete="current-password" required value={password} onChange={e => setPassword(e.target.value)} /></label><button className="cb-btn cb-btn-primary" disabled={busy}>{busy ? 'Signing in…' : 'Sign in'}</button><p role="alert">{error}</p></form></main>
}

/** Short capped games that check models respond. Separate from research campaigns. */
function TestModelsDialog({ close, onLaunched }: { close: () => void; onLaunched: () => void }) {
  const dialog = useRef<HTMLDialogElement>(null)
  useEffect(() => { dialog.current?.showModal() }, [])
  const [step, setStep] = useState<1 | 2>(1)
  const [seats, setSeats] = useState(ROSTER)
  const [effort, setEffort] = useState('medium')
  const [turns, setTurns] = useState(5)
  const [count, setCount] = useState(1)
  const [prepared, setPrepared] = useState<{ preparation_id: string; configs: CloudConfig[] } | null>(null)
  const [error, setError] = useState('')
  const [busy, setBusy] = useState(false)
  const [launchKey] = useState(() => crypto.randomUUID())
  async function next() {
    if (busy) return
    setError(''); setBusy(true)
    try {
      if (step === 1) { setPrepared(await cloudRequest('/smoke/prepare', { models: seats, effort, max_turns: turns, count })); setStep(2) }
      else if (prepared) { await cloudRequest('/smoke', { preparation_id: prepared.preparation_id, idempotency_key: launchKey }); onLaunched(); close() }
    } catch (e) { setError(errorText(e)) } finally { setBusy(false) }
  }
  return <dialog ref={dialog} onCancel={close} aria-labelledby="test-title" className="cloud-modal">
    <button className="cb-btn cb-btn-ghost cloud-close" onClick={close} aria-label="Close">×</button>
    <h2 id="test-title">Test models</h2>
    <p className="cb-hint">Short games with a turn limit, to check that models respond. They are excluded from research and are separate from campaigns.</p>
    {step === 1 ? <div className="cb-form">
      {seats.map((model, i) => <label className="cb-field" key={i}>Seat {i + 1}<select className="cb-input" value={model} onChange={e => setSeats(seats.map((m, n) => n === i ? e.target.value : m))}>{ROSTER.map(m => <option key={m} value={m}>{modelInfo(m).name}</option>)}</select></label>)}
      <label className="cb-field">Reasoning effort<select className="cb-input" value={effort} onChange={e => setEffort(e.target.value)}>{['low', 'medium', 'high'].map(e => <option key={e} value={e}>{e[0].toUpperCase() + e.slice(1)}</option>)}</select></label>
      <label className="cb-field">Turn limit<input className="cb-input cb-input-short" type="number" min={5} max={10} value={turns} onChange={e => setTurns(Number(e.target.value))} /></label>
      <label className="cb-field">Games<input className="cb-input cb-input-short" type="number" min={1} max={20} value={count} onChange={e => setCount(Number(e.target.value))} /></label>
    </div> : <div>
      <p>These test games start as soon as you confirm. They are paid from your existing provider funding: your OpenRouter balance, or your own provider accounts for any keys connected to OpenRouter. This app adds no spending cap and makes no purchases. Cost depends on the models and how much they reason.</p>
      {prepared?.configs.map((c, i) => <article className="cb-test-row" key={c.run_id}><strong>Test game {i + 1}</strong><SeatTokens models={c.players.map(p => p.openrouter_model_id)} labelled /><small>{c.players[0].reasoning.effort} effort, {c.max_turns} turn limit</small></article>)}
    </div>}
    {error ? <p className="cb-error" role="alert">{error}</p> : null}
    <div className="cb-actions">
      <button className="cb-btn cb-btn-primary" disabled={busy} onClick={() => void next()}>{busy ? 'Working…' : step === 2 ? 'Start test games' : 'Review test games'}</button>
      {step === 2 ? <button className="cb-btn cb-btn-ghost" disabled={busy} onClick={() => setStep(1)}>Back</button> : null}
    </div>
  </dialog>
}

function useJobAction(job: CloudJob, onChanged?: (job: CloudJob) => void) {
  const [error, setError] = useState('')
  const [busy, setBusy] = useState('')
  const lock = useRef(false)
  async function act(action: string) {
    if (lock.current) return
    if (action === 'cancel' && !window.confirm('Cancel this game? It stops for good and can’t be resumed.')) return
    lock.current = true; setBusy(action); setError('')
    try { onChanged?.(await cloudRequest<CloudJob>(`/jobs/${job.job_id}/${action}`, {})) }
    catch (e) { setError(errorText(e)) }
    finally { lock.current = false; setBusy('') }
  }
  return { act, error, busy }
}

function JobControls({ job, onChanged }: { job: CloudJob; onChanged?: (job: CloudJob) => void }) {
  const { act, error, busy } = useJobAction(job, onChanged)
  return <>
    {job.allowed_actions.map(action => <button key={action} className={`cb-btn ${action === 'cancel' ? 'cb-btn-danger' : 'cb-btn-ghost'}`} disabled={Boolean(busy)} onClick={() => void act(action)}>{busy === action ? 'Working…' : ACTION_LABELS[action] ?? action}</button>)}
    {error ? <p className="cb-error" role="alert">{error}</p> : null}
  </>
}

function JobActions({ job, onChanged }: { job: CloudJob; onChanged?: (job: CloudJob) => void }) {
  return <div className="cloud-actions">{job.export_status === 'ready' ? <a className="cb-btn cb-btn-ghost" href={`${CLOUD_API}/jobs/${job.job_id}/export`}>Download game</a> : null}<JobControls job={job} onChanged={onChanged} /></div>
}

function JobCard({ job, campaignNames, onChanged }: { job: CloudJob; campaignNames: Map<string, string>; onChanged: () => void }) {
  const [label, tone] = jobStatus(job.status)
  const turn = job.snapshot?.turn_index
  const winner = job.outcome?.winner_player_id ? job.config.players.find(p => p.player_id === job.outcome?.winner_player_id) : null
  return <article className="cb-card cb-job">
    <header><StatusPill label={label} tone={tone} />{turn != null ? <span className="cb-meta">Turn {turn}</span> : null}</header>
    <a className="cb-job-board" href={`/games/${job.job_id}`} tabIndex={-1} aria-hidden="true">
      {job.snapshot ? <div className="cloud-thumbnail"><Board spaces={job.snapshot.board} players={job.snapshot.players} activePlayerId={job.snapshot.active_player_id} /></div> : <div className="cloud-placeholder">{job.status === 'queued' ? 'Waiting for a slot' : 'No moves yet'}</div>}
    </a>
    <h2><a href={`/games/${job.job_id}`}>{jobTitle(job)}</a></h2>
    {job.campaign_id ? <p className="cb-meta"><a href={`/campaigns/${encodeURIComponent(job.campaign_id)}`}>{campaignNames.get(job.campaign_id) ?? 'Open campaign'}</a></p> : null}
    <SeatTokens models={job.config.players.map(p => p.openrouter_model_id)} labelled />
    <p className="cb-meta">
      {job.elapsed_seconds !== null ? `${duration(job.elapsed_seconds)} elapsed.` : 'Not started yet.'}
      {job.progress_age_seconds !== null && job.status === 'running' ? ` Last move ${duration(job.progress_age_seconds)} ago.` : ''}
    </p>
    {job.slow ? <p className="cb-flag" data-tone="warn">Slow: no move in over 5 minutes.</p> : null}
    {(turn ?? 0) > 300 ? <p className="cb-flag" data-tone="idle">Long game: over 300 turns.</p> : null}
    {job.outcome ? <p className="cb-outcome">{winner ? `Winner: ${modelInfo(winner.openrouter_model_id).name}` : 'No winner'}{job.outcome.reason ? ` (${job.outcome.reason.toLowerCase().replace(/_/g, ' ')})` : ''}</p> : null}
    {job.pause_reason ? <p className="cb-flag" data-tone="warn">Paused: {job.pause_reason.replace(/_/g, ' ')}</p> : null}
    <div className="cloud-actions"><a className="cb-btn cb-btn-secondary" href={`/games/${job.job_id}`}>{job.status === 'running' ? 'Watch' : 'Open'}</a><JobControls job={job} onChanged={onChanged} /></div>
    <details className="cb-disclosure cb-disclosure-small">
      <summary>Research details</summary>
      <Facts rows={[
        ['Run ID', <code>{job.run_id}</code>],
        ['Seed', <code>{job.config.seed}</code>],
        ['Recorded cost', `$${job.cost.known_total.toFixed(2)}${job.cost.unknown_calls + job.cost.missing_calls > 0 ? ' (incomplete)' : ''}`],
        ['Replay check', job.replay_status || 'Pending'],
        ['Download', job.export_status === 'ready' ? <a href={`${CLOUD_API}/jobs/${job.job_id}/export`}>Ready</a> : job.export_status || 'Pending'],
        ['Recovery', job.repaired ? 'Repaired' : job.recovered ? 'Recovered' : 'None'],
        ...(job.rerun_of_job_id ? [['Rerun of', <a href={`/games/${job.rerun_of_job_id}`}>Original game</a>] as [string, ReactNode]] : []),
      ]} />
    </details>
  </article>
}

const FILTERS = [
  { label: 'All', status: null },
  { label: 'Playing', status: 'running' },
  { label: 'Paused', status: 'paused' },
  { label: 'Finished', status: 'completed' },
]

interface CloudStatus { demo: boolean; account_stop: unknown; drain?: boolean; free_disk: number; active_workers: number; cost: { known_total: number }; preflight: { passed: boolean; created_at?: number } | null }

export function GamesPage() {
  const [search, setSearch] = useState('')
  const [cursor, setCursor] = useState(0)
  const [testing, setTesting] = useState(false)
  const params = new URLSearchParams(window.location.search)
  const archived = params.get('archived') === 'true'
  const activeFilter = params.get('status')
  const query = new URLSearchParams(params)
  query.set('search', search); query.set('cursor', String(cursor))
  const { data, error, refresh } = usePoll<{ jobs: CloudJob[]; next_cursor: number | null }>(`/jobs?${query}`)
  const { data: status, refresh: refreshStatus } = usePoll<CloudStatus>('/status')
  const { data: campaigns } = usePoll<Pick<CloudCampaign, 'campaign_id' | 'display_name'>[]>('/campaigns?summary=true')
  const campaignNames = new Map((campaigns ?? []).map(c => [c.campaign_id, campaignName(c)]))
  const [actionError, setActionError] = useState('')
  const preflightStale = !status?.preflight?.passed
  return <Shell>
    <div className="cb-page">
      <header className="cb-page-head">
        <div><h1>{archived ? 'Archived games' : 'Games'}</h1><p>{status ? `${status.active_workers} ${status.active_workers === 1 ? 'game' : 'games'} playing now.` : ' '}</p></div>
        <div className="cb-actions">
          <a className="cb-btn cb-btn-primary" href="/campaigns/new">Create campaign</a>
          <button className="cb-btn cb-btn-ghost" onClick={() => setTesting(true)}>Test models</button>
        </div>
      </header>
      {status?.demo ? <Notice tone="idle" title="Demo mode" role="status"><p>Games use local mock models. Nothing is charged and nothing counts toward research.</p></Notice> : null}
      {status?.account_stop ? <Notice tone="bad" title="All games are paused" role="alert"><p>OpenRouter stopped accepting requests. Check your key and credits, then resume.</p><button className="cb-btn cb-btn-secondary" onClick={() => void cloudRequest('/resume-all', {}).then(() => { refresh(); refreshStatus() }).catch(e => setActionError(errorText(e)))}>Resume all games</button></Notice> : null}
      {status && preflightStale ? <Notice tone="warn" title="Model connections need a check"><p>The latest model connection check hasn’t passed. Campaigns can’t be saved or started until a check passes on the current code.</p><CheckConnections onDone={() => refreshStatus()} /></Notice> : null}
      <div className="cb-toolbar">
        {!archived ? <nav className="cb-segmented" aria-label="Filter games">
          {FILTERS.map(f => <a key={f.label} href={f.status ? `/?status=${f.status}` : '/'} aria-current={activeFilter === f.status ? 'page' : undefined}>{f.label}</a>)}
        </nav> : <a className="cb-back" href="/">All games</a>}
        <label className="cb-search"><span className="cb-sr">Search games</span><input className="cb-input" type="search" value={search} onChange={e => { setSearch(e.target.value); setCursor(0) }} placeholder="Search by model or campaign" /></label>
      </div>
      {error || actionError ? <p className="cb-error" role="alert">{error || actionError}</p> : null}
      <div className="cloud-grid">{data?.jobs.map(job => <JobCard key={job.job_id} job={job} campaignNames={campaignNames} onChanged={refresh} />)}</div>
      {data?.jobs.length === 0 ? <div className="cb-empty"><h2>No games here yet</h2><p>Create a campaign to plan a set of research games, or test the models with a short game.</p><a className="cb-btn cb-btn-primary" href="/campaigns/new">Create campaign</a></div> : null}
      {cursor > 0 || data?.next_cursor != null ? <div className="cb-actions"><button className="cb-btn cb-btn-ghost" disabled={cursor === 0} onClick={() => setCursor(Math.max(0, cursor - 50))}>Previous</button><button className="cb-btn cb-btn-ghost" disabled={data?.next_cursor == null} onClick={() => setCursor(data?.next_cursor ?? 0)}>Next</button></div> : null}
      {status ? <details className="cb-disclosure cb-disclosure-small">
        <summary>Workspace details</summary>
        <Facts rows={[['Recorded spend', `$${status.cost.known_total.toFixed(2)}`], ['Free disk', `${(status.free_disk / 1e9).toFixed(1)} GB`], ['New games', status.drain ? 'Paused for maintenance' : 'Accepted']]} />
      </details> : null}
      {testing ? <TestModelsDialog close={() => setTesting(false)} onLaunched={refresh} /> : null}
    </div>
  </Shell>
}

export function GamePage() {
  const id = window.location.pathname.split('/')[2]
  const { data: job, error, replace } = usePoll<CloudJob>(`/jobs/${id}`)
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
    if (job) useGameStore.getState().setRunStatus({ runId: job.run_id, running: job.status === 'running', paused: job.status === 'paused', players: job.config.players.map(p => {
      const fallback = job.config.response_policy?.fallback_models[p.openrouter_model_id]
      return { ...p, model_display_name: fallback ? `${p.name} with ${fallback.split('/').pop()} fallback` : p.name }
    }) })
  }, [job])
  useEffect(() => {
    if (tab === 'Live' || tab === 'Decisions') return
    let active = true
    const path = '/artifacts'
    void cloudRequest(`/jobs/${id}${path}`).then(value => { if (active) { setRows(value); setTabError('') } }).catch(e => { if (active) setTabError(String(e)) })
    return () => { active = false }
  }, [id, tab, cursor])
  const current = snapshot?.run_id === job?.run_id ? snapshot : job?.snapshot
  const [statusLabel, statusTone] = jobStatus(job?.status)
  return <Shell><div className="cb-game-head">{job?.campaign_id ? <a className="cb-back" href={`/campaigns/${encodeURIComponent(job.campaign_id)}`}>Campaign</a> : <a className="cb-back" href="/">Games</a>}<h1>{job ? jobTitle(job) : 'Loading game…'}</h1>{job ? <p className="cb-game-status"><StatusPill label={statusLabel} tone={statusTone} /><span className="cb-meta" role="status">{connected ? 'Live' : 'Reconnecting…'}</span>{job.snapshot ? <span className="cb-meta">Turn {job.snapshot.turn_index}</span> : null}</p> : null}{job ? <SeatTokens models={job.config.players.map(p => p.openrouter_model_id)} labelled /> : null}{job ? <JobActions job={job} onChanged={replace} /> : null}{job ? <details className="cb-disclosure cb-disclosure-small"><summary>Research details</summary><Facts rows={[['Run ID', <code>{job.run_id}</code>], ['Seed', <code>{job.config.seed}</code>], ['Recorded cost', `$${job.cost.known_total.toFixed(2)}`], ['Replay check', job.replay_status || 'Pending']]} /></details> : null}</div>{error || tabError ? <p className="cb-error" role="alert">{error || tabError}</p> : null}<nav className="cloud-tabs">{['Live', 'Decisions', 'Artifacts', 'Replay', 'Analysis'].map(name => <button aria-pressed={tab === name} key={name} onClick={() => { setTab(name); setCursor(0) }}>{name}</button>)}</nav>{tab === 'Live' ? <>{current ? <div className="cloud-live"><Board spaces={current.board} players={current.players} activePlayerId={current.active_player_id} /><PlayerStackPanel /></div> : <p>Waiting for the first committed snapshot.</p>}<AuctionPanel visible /><TradeInspectorPanel visible /><div className="cloud-live cloud-feed-panels"><EventFeed /><ChatFeed /></div><Inspector /></> : tab === 'Decisions' ? <><div className="cloud-decisions"><LlmIoPanel jobId={id} cursor={cursor} revision={job?.commit_seq} onPageSize={setDecisionPageSize} /></div><button disabled={cursor === 0} onClick={() => setCursor(Math.max(0, cursor-50))}>Previous</button><button disabled={decisionPageSize < 50} onClick={() => setCursor(cursor+50)}>Next</button></> : <><p>{tab === 'Replay' ? `Replay verdict: ${job?.replay_status || 'pending'}` : 'Open an artifact to inspect its contents.'}</p>{Array.isArray(rows) ? rows.filter((r: { path: string }) => tab === 'Replay' ? r.path.includes('replay') : true).map((r: { path: string; bytes: number }) => <p key={r.path}><a href={`${CLOUD_API}/jobs/${id}/artifacts?path=${encodeURIComponent(r.path)}`}>{r.path}</a> · {r.bytes} bytes</p>) : null}{job?.export_status === 'ready' ? <a href={`${CLOUD_API}/jobs/${id}/export`}>Download game with analysis</a> : null}</>}</Shell>
}
