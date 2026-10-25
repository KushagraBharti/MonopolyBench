import { useState, type FormEvent, type ReactNode } from 'react'
import { CLOUD_API, cloudRequest, type CloudJob, type CloudCampaign, type CloudStatus } from '@/net/jobs'
import { JobControls } from './cloud/JobControls'
import { Board } from '@/components/board/Board'
import { Facts, Notice, SeatTokens, Shell, StatusPill } from './cloud/CloudShell'
import { campaignName, downloadWait, duration, errorText, jobStatus, jobTitle, modelInfo, playerModels, settingsLine, usePoll, waitingText } from './cloud/cloudUi'
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


function JobCard({ job, campaignNames, onChanged }: { job: CloudJob; campaignNames: Map<string, string>; onChanged: () => void }) {
  const [label, tone] = jobStatus(job.status)
  const turn = job.snapshot?.turn_index
  const winner = job.outcome?.winner_player_id ? job.config.players.find(p => p.player_id === job.outcome?.winner_player_id) : null
  return <article className="cb-card cb-job">
    <header><StatusPill label={label} tone={tone} />{turn != null ? <span className="cb-meta">Turn {turn}</span> : null}</header>
    <a className="cb-job-board" href={`/games/${job.job_id}`} tabIndex={-1} aria-hidden="true">
      {job.snapshot ? <div className="cloud-thumbnail"><Board spaces={job.snapshot.board} players={job.snapshot.players} activePlayerId={job.status === 'running' || job.status === 'paused' ? job.snapshot.active_player_id : null} phase={job.snapshot.phase} playerModels={playerModels(job.config)} /></div> : <div className="cloud-placeholder">{waitingText(job.status)}</div>}
    </a>
    <h2><a href={`/games/${job.job_id}`}>{jobTitle(job)}</a></h2>
    {job.campaign_id ? <p className="cb-meta"><a href={`/campaigns/${encodeURIComponent(job.campaign_id)}`}>{campaignNames.get(job.campaign_id) ?? 'Open campaign'}</a></p> : null}
    <SeatTokens models={job.config.players.map(p => p.openrouter_model_id)} labelled />
    <p className="cb-meta">{settingsLine(job.config)}</p>
    <p className="cb-meta">
      {job.elapsed_seconds !== null ? `${duration(job.elapsed_seconds)} elapsed.` : 'Not started yet.'}
      {job.progress_age_seconds !== null && job.status === 'running' ? ` Last move ${duration(job.progress_age_seconds)} ago.` : ''}
    </p>
    {job.slow ? <p className="cb-flag" data-tone="warn">Slow: no move in over 5 minutes.</p> : null}
    {(turn ?? 0) > 300 ? <p className="cb-flag" data-tone="idle">Long game: over 300 turns.</p> : null}
    {job.outcome ? <p className="cb-outcome">{winner ? `Winner: ${modelInfo(winner.openrouter_model_id).name}` : 'No winner'}{job.outcome.reason ? ` (${job.outcome.reason.toLowerCase().replace(/_/g, ' ')})` : ''}</p> : null}
    {job.pause_reason ? <p className="cb-flag" data-tone="warn">Paused: {job.pause_reason.replace(/_/g, ' ')}</p> : null}
    <div className="cloud-actions">
      <a className="cb-btn cb-btn-secondary" href={`/games/${job.job_id}`}>{job.status === 'running' ? 'Watch' : 'Open'}</a>
      {job.export_status === 'ready' ? <a className="cb-btn cb-btn-secondary" href={`${CLOUD_API}/jobs/${job.job_id}/export`}>Download game</a> : null}
      <JobControls job={job} onChanged={onChanged} />
    </div>
    {downloadWait(job) ? <p className="cb-wait">{downloadWait(job)}</p> : null}
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

type ListKind = 'single' | 'smoke'
const LIST_COPY: Record<ListKind, { base: string; title: string; archivedTitle: string; lede: string; newHref: string; newLabel: string; noun: string; search: string; empty: string; emptyText: string }> = {
  single: {
    base: '/games', title: 'Games', archivedTitle: 'Archived games', newHref: '/games/new', newLabel: 'New game', noun: 'game',
    lede: 'Standalone games with the models and settings you chose. Campaign games live under Campaigns, model tests under Tests.',
    search: 'Search by model or run ID', empty: 'No games here yet', emptyText: 'Run one game with any four models and settings. Nothing starts until you review and press Start.',
  },
  smoke: {
    base: '/tests', title: 'Model tests', archivedTitle: 'Archived model tests', newHref: '/tests/new', newLabel: 'New test', noun: 'test game',
    lede: 'Short games of 5 to 10 turns that check every model responds. Tests are excluded from research.',
    search: 'Search by model or run ID', empty: 'No model tests here yet', emptyText: 'Run a short test to check every model responds before a long game or campaign.',
  },
}

/** Standalone games (kind single) or model tests (kind smoke). Never mixes in campaign games. */
export function JobListPage({ kind }: { kind: ListKind }) {
  const copy = LIST_COPY[kind]
  const [search, setSearch] = useState('')
  const [cursor, setCursor] = useState(0)
  const params = new URLSearchParams(window.location.search)
  const archived = params.get('archived') === 'true'
  const activeFilter = params.get('status')
  const query = new URLSearchParams()
  if (activeFilter) query.set('status', activeFilter)
  if (archived) query.set('archived', 'true')
  query.set('kind', kind); query.set('search', search); query.set('cursor', String(cursor))
  const { data, error, refresh } = usePoll<{ jobs: CloudJob[]; next_cursor: number | null }>(`/jobs?${query}`)
  const { data: status, refresh: refreshStatus } = usePoll<CloudStatus>('/status')
  const { data: campaigns } = usePoll<Pick<CloudCampaign, 'campaign_id' | 'display_name'>[]>('/campaigns?summary=true')
  const campaignNames = new Map((campaigns ?? []).map(c => [c.campaign_id, campaignName(c)]))
  const [actionError, setActionError] = useState('')
  return <Shell section={kind === 'smoke' ? 'tests' : 'games'}>
    <div className="cb-page">
      <header className="cb-page-head">
        <div><h1>{archived ? copy.archivedTitle : copy.title}</h1><p>{copy.lede}</p></div>
        {!archived ? <a className="cb-btn cb-btn-primary" href={copy.newHref}>{copy.newLabel}</a> : null}
      </header>
      {status?.demo ? <Notice tone="idle" title="Demo mode" role="status"><p>Games use local mock models. Nothing is charged and nothing counts toward research.</p></Notice> : null}
      {status?.account_stop ? <Notice tone="bad" title="All games are paused" role="alert"><p>OpenRouter stopped accepting requests. Check your key and credits, then resume.</p><button className="cb-btn cb-btn-secondary" onClick={() => void cloudRequest('/resume-all', {}).then(() => { refresh(); refreshStatus() }).catch(e => setActionError(errorText(e)))}>Resume all games</button></Notice> : null}
      <div className="cb-toolbar">
        {!archived ? <nav className="cb-segmented" aria-label={`Filter ${copy.title.toLowerCase()}`}>
          {FILTERS.map(f => <a key={f.label} href={f.status ? `${copy.base}?status=${f.status}` : copy.base} aria-current={activeFilter === f.status ? 'page' : undefined}>{f.label}</a>)}
          <a href={`${copy.base}?archived=true`}>Archived</a>
        </nav> : <a className="cb-back" href={copy.base}>All {copy.title.toLowerCase()}</a>}
        <label className="cb-search"><span className="cb-sr">Search {copy.title.toLowerCase()}</span><input className="cb-input" type="search" value={search} onChange={e => { setSearch(e.target.value); setCursor(0) }} placeholder={copy.search} /></label>
      </div>
      {error || actionError ? <p className="cb-error" role="alert">{error || actionError}</p> : null}
      {!data && !error ? <p className="cb-meta" role="status">Loading…</p> : null}
      <div className="cloud-grid">{data?.jobs.map(job => <JobCard key={job.job_id} job={job} campaignNames={campaignNames} onChanged={refresh} />)}</div>
      {data?.jobs.length === 0 ? <div className="cb-empty">
        <h2>{search ? `No ${copy.noun}s match “${search}”` : archived ? `No archived ${copy.noun}s` : activeFilter ? `No ${copy.noun}s with this status` : copy.empty}</h2>
        {!search && !archived && !activeFilter ? <><p>{copy.emptyText}</p><a className="cb-btn cb-btn-primary" href={copy.newHref}>{copy.newLabel}</a></> : null}
      </div> : null}
      {cursor > 0 || data?.next_cursor != null ? <div className="cb-actions"><button className="cb-btn cb-btn-ghost" disabled={cursor === 0} onClick={() => setCursor(Math.max(0, cursor - 50))}>Previous</button><button className="cb-btn cb-btn-ghost" disabled={data?.next_cursor == null} onClick={() => setCursor(data?.next_cursor ?? 0)}>Next</button></div> : null}
      {status ? <details className="cb-disclosure cb-disclosure-small">
        <summary>Workspace details</summary>
        <Facts rows={[['Playing now', status.active_workers], ['Recorded spend, all runs', `$${status.cost.known_total.toFixed(2)}`], ['Free disk', `${(status.free_disk / 1e9).toFixed(1)} GB`], ['New games', status.drain ? 'Paused for maintenance' : 'Accepted']]} />
      </details> : null}
    </div>
  </Shell>
}

export function GamesPage() {
  return <JobListPage kind="single" />
}

export function TestsPage() {
  return <JobListPage kind="smoke" />
}

export { GamePage } from './cloud/game/GamePage'
