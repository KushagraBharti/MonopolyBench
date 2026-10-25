import { useEffect, useState } from 'react'
import { CLOUD_API, cloudRequest, type CloudCampaign, type CloudDashboard, type CloudJob } from '@/net/jobs'
import { CheckConnections, Facts, GameTiles, Notice, SeatTokens, Shell, StatusPill } from './CloudShell'
import { campaignName, campaignStatus, cellCounts, errorText, exportDownload, exportKindLabel, exportName, exportSource, fileSize, jobStatus, jobTitle, usePoll, when } from './cloudUi'

/** Workspace overview. Counts come from the server over every saved row; the lists are the latest few. */
export function DashboardPage() {
  const { data, error, refresh } = usePoll<CloudDashboard>('/dashboard')
  const { data: names } = usePoll<Pick<CloudCampaign, 'campaign_id' | 'display_name'>[]>('/campaigns?summary=true')
  const [actionError, setActionError] = useState('')
  const [now, setNow] = useState(() => Date.now() / 1000)
  useEffect(() => {
    const timer = window.setInterval(() => setNow(Date.now() / 1000), 30000)
    return () => window.clearInterval(timer)
  }, [])
  const campaignNames = new Map((names ?? []).map(c => [c.campaign_id, campaignName(c)]))
  const status = data?.status
  const activity = data?.activity
  const checkExpired = Boolean(status?.preflight?.passed && (!status.preflight.created_at || now - status.preflight.created_at > 21600))
  return <Shell section="dashboard">
    <div className="cb-page">
      <header className="cb-page-head">
        <div><h1>Dashboard</h1><p>{status ? `${status.active_workers} ${status.active_workers === 1 ? 'game' : 'games'} playing now.` : ' '}</p></div>
        <nav className="cb-quick" aria-label="Quick actions">
          <a className="cb-btn cb-btn-secondary" href="/games/new">New game</a>
          <a className="cb-btn cb-btn-secondary" href="/campaigns/new">New campaign</a>
          <a className="cb-btn cb-btn-secondary" href="/tests/new">New test</a>
        </nav>
      </header>
      {error ? <p className="cb-error" role="alert">{error}</p> : null}
      {!data && !error ? <p className="cb-meta" role="status">Loading…</p> : null}
      {status?.account_stop ? <Notice tone="bad" title="All games are paused" role="alert"><p>OpenRouter stopped accepting requests. Check your key and credits, then resume.</p><button className="cb-btn cb-btn-secondary" onClick={() => void cloudRequest('/resume-all', {}).then(refresh).catch(e => setActionError(errorText(e)))}>Resume all games</button></Notice> : null}
      {status && (!status.preflight?.passed || checkExpired) ? <Notice tone="warn" title="Model connections need a check"><p>A passing check on the current code within six hours is required to save or start campaigns.</p><CheckConnections onDone={() => refresh()} /></Notice> : null}
      {actionError ? <p className="cb-error" role="alert">{actionError}</p> : null}

      {data ? <>
        <section aria-label="Totals" className="cb-totals">
          <a className="cb-total" href="/games"><strong>{data.totals.games}</strong><span>Games</span><small>Standalone games</small></a>
          <a className="cb-total" href="/campaigns"><strong>{data.totals.campaigns}</strong><span>Campaigns</span><small>Saved research studies</small></a>
          <a className="cb-total" href="/tests"><strong>{data.totals.tests}</strong><span>Tests</span><small>Short model checks</small></a>
          <a className="cb-total" href="/exports"><strong>{data.totals.exports}</strong><span>Exports</span><small>Downloadable packages</small></a>
        </section>
        {activity ? <p className="cb-activity" aria-label="Activity across all runs">
          <span><strong>{activity.running}</strong> playing</span>
          <span><strong>{activity.queued}</strong> waiting for a slot</span>
          <span><strong>{activity.paused}</strong> paused</span>
          <span><strong>{activity.finalizing}</strong> wrapping up</span>
          {activity.recovering ? <span><strong>{activity.recovering}</strong> recovering</span> : null}
        </p> : null}

        <div className="cb-dash">
          <section className="cb-panel" aria-labelledby="recent-runs">
            <header><h2 id="recent-runs">Recent runs</h2></header>
            {data.recent_jobs.length ? <ul className="cb-rows">{data.recent_jobs.map(job => <RecentJob key={job.job_id} job={job} campaignNames={campaignNames} />)}</ul>
              : <p className="cb-hint">No runs yet. <a href="/games/new">Run a game</a> or <a href="/tests/new">test the models</a>.</p>}
          </section>

          <section className="cb-panel" aria-labelledby="recent-campaigns">
            <header><h2 id="recent-campaigns">Campaigns</h2><a href="/campaigns">All campaigns</a></header>
            {data.recent_campaigns.length ? <ul className="cb-rows">{data.recent_campaigns.map(c => <RecentCampaign key={c.campaign_id} campaign={c} />)}</ul>
              : <p className="cb-hint">No saved campaigns yet. <a href="/campaigns/new">Create one</a> to plan a balanced set of research games.</p>}
          </section>

          <section className="cb-panel" aria-labelledby="recent-exports">
            <header><h2 id="recent-exports">Latest exports</h2><a href="/exports">All exports</a></header>
            {data.recent_exports.length ? <ul className="cb-rows">{data.recent_exports.map(item => {
              const source = exportSource(item)
              return <li key={item.export_id}>
                <span className="cb-row-main"><strong>{exportName(item)}</strong><span className="cb-meta">{exportKindLabel(item)} · {fileSize(item.bytes)} · {when(item.created_at)}</span></span>
                {source ? <a className="cb-btn cb-btn-ghost" href={source.href}>{source.label}</a> : null}
                <a className="cb-btn cb-btn-secondary" href={exportDownload(item)} download aria-label={`Download ${exportName(item)}`}>Download</a>
              </li>
            })}</ul> : <p className="cb-hint">Nothing to download yet. A game’s package appears here once it finishes.</p>}
          </section>

          <section className="cb-panel" aria-labelledby="readiness">
            <header><h2 id="readiness">Readiness</h2></header>
            <Facts rows={[
              ['Model connection check', status?.preflight ? `${checkExpired ? 'Expired' : status.preflight.passed ? 'Passed' : 'Failed'}${status.preflight.created_at ? `, ${when(status.preflight.created_at)}` : ''}` : 'Not run yet'],
              ['Maintenance', status?.drain ? 'Paused for maintenance' : 'Off'],
              ['Account pause', status?.account_stop ? 'Active, check keys and funding' : 'None'],
              ['Playing now', status?.active_workers ?? '—'],
              ['Free disk', status ? `${(status.free_disk / 1e9).toFixed(1)} GB` : '—'],
            ]} />
          </section>
        </div>
      </> : null}
    </div>
  </Shell>
}

function RecentJob({ job, campaignNames }: { job: CloudJob; campaignNames: Map<string, string> }) {
  const [label, tone] = jobStatus(job.status)
  const turn = job.snapshot_kind === 'committed' ? job.snapshot?.turn_index : null
  const context = job.kind === 'smoke' ? 'Model test' : job.kind === 'campaign' ? (job.campaign_id ? campaignNames.get(job.campaign_id) ?? 'Campaign' : 'Campaign') : 'Game'
  return <li>
    <span className="cb-row-main">
      <a href={`/games/${job.job_id}`}>{jobTitle(job)}</a>
      <span className="cb-meta">{[context !== jobTitle(job) ? context : null, turn != null ? `Turn ${turn}` : null, when(job.created_at)].filter(Boolean).join(' · ')}</span>
    </span>
    <SeatTokens models={job.config.players.map(p => p.openrouter_model_id)} />
    <StatusPill label={label} tone={tone} />
    {job.export_status === 'ready' ? <a className="cb-btn cb-btn-ghost" href={`${CLOUD_API}/jobs/${job.job_id}/export`} download>Download</a> : null}
  </li>
}

function RecentCampaign({ campaign }: { campaign: CloudCampaign }) {
  const cells = campaign.cells ?? []
  const [label, tone] = campaignStatus({ ...campaign, cells })
  const counts = cellCounts(cells)
  return <li>
    <span className="cb-row-main">
      <a href={`/campaigns/${encodeURIComponent(campaign.campaign_id)}`}>{campaignName(campaign)}</a>
      <GameTiles cells={cells} />
      <span className="cb-meta">{counts.finished} of {counts.total} games finished{counts.playing ? ` · ${counts.playing} playing` : ''}{counts.paused ? ` · ${counts.paused} paused` : ''}</span>
    </span>
    <StatusPill label={label} tone={tone} />
  </li>
}
