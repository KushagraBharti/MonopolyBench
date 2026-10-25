import { useRef, useState, type ReactNode } from 'react'
import { CLOUD_API, cloudRequest, type CloudCampaign } from '@/net/jobs'
import { CheckConnections, Facts, GameTiles, Notice, SeatTokens, Shell, StatusPill } from './CloudShell'
import { boardNumbers, campaignName, campaignStatus, cellCounts, cellStatus, errorText, needsConnectionCheck, usePoll } from './cloudUi'

export function CampaignsRoute() {
  const id = window.location.pathname.split('/')[2]
  return id ? <CampaignDetailPage id={decodeURIComponent(id)} /> : <CampaignListPage />
}

function CampaignListPage() {
  const { data, error } = usePoll<CloudCampaign[]>('/campaigns')
  const campaigns = (data ?? []).map(c => ({ ...c, cells: c.cells ?? [] }))
  const saved = campaigns.filter(c => c.status !== 'draft')
  const drafts = campaigns.filter(c => c.status === 'draft')
  return <Shell>
    <div className="cb-page">
      <header className="cb-page-head">
        <div><h1>Campaigns</h1><p>A campaign is a planned set of research games, saved before anything is played.</p></div>
        <a className="cb-btn cb-btn-primary" href="/campaigns/new">Create campaign</a>
      </header>
      {error ? <p className="cb-error" role="alert">{error}</p> : null}
      {data && saved.length === 0 ? <div className="cb-empty"><h2>No saved campaigns yet</h2><p>Create one to choose how many games to play. You’ll review it before saving, and games only start when you say so.</p><a className="cb-btn cb-btn-primary" href="/campaigns/new">Create campaign</a></div> : null}
      <div className="cb-campaign-grid">
        {saved.map(c => <CampaignCard key={c.campaign_id} campaign={c} />)}
      </div>
      {drafts.length ? <details className="cb-disclosure">
        <summary>Campaign files from the repository ({drafts.length})</summary>
        <p className="cb-hint">Older campaigns defined as files. Open one to freeze it for running.</p>
        <ul className="cb-plain-list">{drafts.map(c => <li key={c.campaign_id}><a href={`/campaigns/${encodeURIComponent(c.campaign_id)}`}>{campaignName(c)}</a></li>)}</ul>
      </details> : null}
    </div>
  </Shell>
}

function CampaignCard({ campaign }: { campaign: CloudCampaign }) {
  const [label, tone] = campaignStatus(campaign)
  const counts = cellCounts(campaign.cells)
  const href = `/campaigns/${encodeURIComponent(campaign.campaign_id)}`
  return <article className="cb-card cb-campaign-card">
    <header><StatusPill label={label} tone={tone} /></header>
    <h2><a href={href}>{campaignName(campaign)}</a></h2>
    <GameTiles cells={campaign.cells} />
    <p className="cb-count"><strong>{counts.finished}</strong> of {counts.total} games finished</p>
    <p className="cb-meta">{[counts.playing && `${counts.playing} playing.`, counts.paused && `${counts.paused} paused.`, counts.stopped && `${counts.stopped} stopped (failed or cancelled).`, counts.notStarted && `${counts.notStarted} not started.`].filter(Boolean).join(' ')}</p>
    {campaign.readiness && !campaign.readiness.can_start && counts.notStarted > 0 && campaign.status !== 'running'
      ? <p className="cb-meta">{campaign.readiness.reasons[0]}</p> : null}
  </article>
}

function CampaignDetailPage({ id }: { id: string }) {
  const path = `/campaigns/${encodeURIComponent(id)}`
  const { data, error, refresh, replace } = usePoll<CloudCampaign>(path)
  const [actionError, setActionError] = useState('')
  const [busy, setBusy] = useState('')
  const [confirming, setConfirming] = useState(false)
  const [exportId, setExportId] = useState('')
  const lock = useRef(false)
  const startButton = useRef<HTMLButtonElement>(null)
  const justSaved = new URLSearchParams(window.location.search).get('saved') === '1'

  async function act(action: 'run' | 'pause' | 'freeze' | 'export') {
    if (lock.current) return
    lock.current = true; setBusy(action); setActionError('')
    try {
      const result = await cloudRequest<CloudCampaign & { export_id?: string }>(`${path}/${action}`, {})
      if (action === 'export' && result.export_id) setExportId(result.export_id)
      else if (Array.isArray(result?.cells)) replace(result)
      refresh()
    } catch (e) {
      setActionError(errorText(e))
      refresh()
    } finally {
      lock.current = false; setBusy(''); setConfirming(false)
    }
  }

  if (!data) return <Shell><div className="cb-page"><a className="cb-back" href="/campaigns">Campaigns</a>{error ? <p className="cb-error" role="alert">{error}</p> : <p>Loading campaign…</p>}</div></Shell>

  const campaign = { ...data, cells: data.cells ?? [] }
  const [label, tone] = campaignStatus(campaign)
  const counts = cellCounts(campaign.cells)
  const boards = boardNumbers(campaign.cells)
  const campaignDone = campaign.status === 'done'
  const readiness = campaign.readiness
  // Fail closed: Start stays disabled unless the server confirms games can start.
  const canStart = readiness?.can_start === true
  const startable = !campaignDone && counts.notStarted > 0 && (campaign.status === 'frozen' || campaign.status === 'paused')
  const reasons = readiness ? readiness.reasons : ['The server didn’t report whether games can start, so starting is turned off. Refresh the page, or update the server if this continues.']
  const resuming = campaign.status === 'paused'
  const stillPlaying = counts.playing + counts.paused
  const freeze = campaign.config?.research_freeze

  return <Shell>
    <div className="cb-page">
      <a className="cb-back" href="/campaigns">Campaigns</a>
      <header className="cb-page-head">
        <div><h1>{campaignName(campaign)}</h1><StatusPill label={label} tone={tone} /></div>
      </header>
      {justSaved && campaign.status === 'frozen' && counts.notStarted === counts.total
        ? <Notice tone="done" title="Campaign saved" role="status"><p>No games have started. Start them below when you’re ready.</p></Notice> : null}
      {error ? <p className="cb-error" role="alert">{error}</p> : null}

      <section className="cb-control" aria-labelledby="progress-title">
        <div className="cb-control-progress">
          <h2 id="progress-title" className="cb-count"><strong>{counts.finished}</strong> of {counts.total} games finished</h2>
          <GameTiles cells={campaign.cells} />
          <Facts rows={[
            ['Playing', counts.playing],
            ...(counts.paused ? [['Paused', counts.paused] as [string, number]] : []),
            ['Not started', counts.notStarted],
            ...(counts.stopped ? [['Stopped (failed or cancelled)', counts.stopped] as [string, number]] : []),
            ['At the same time', String(campaign.config?.concurrency ?? '—')],
          ]} />
        </div>
        <div className="cb-control-actions">
          {campaign.status === 'draft' ? <>
            <p>This campaign comes from a repository file. Freezing records it for running and needs a passing model connection check from the last 6 hours.</p>
            <button className="cb-btn cb-btn-secondary" disabled={Boolean(busy)} onClick={() => void act('freeze')}>{busy === 'freeze' ? 'Freezing…' : 'Freeze campaign'}</button>
          </> : campaignDone ? (counts.stopped
              ? <p>No games are left to start. {counts.finished} finished and {counts.stopped} stopped (failed or cancelled).</p>
              : <p className="cb-ok">All games have finished.</p>)
            : campaign.status === 'running' ? <>
              <p>Games are playing. Pausing stops new games from starting. Games already playing continue until they finish.</p>
              <button className="cb-btn cb-btn-secondary" disabled={Boolean(busy)} onClick={() => void act('pause')}>{busy === 'pause' ? 'Pausing…' : 'Pause new games'}</button>
            </> : startable ? <>
              {resuming && stillPlaying ? <p>New games are paused. {stillPlaying} {stillPlaying === 1 ? 'game is' : 'games are'} still in progress and will continue until finished.</p> : null}
              {confirming
                ? <div className="cb-confirm" role="group" aria-label="Confirm start">
                    <p>{resuming ? 'Resume starting the remaining' : 'Start'} {counts.notStarted} {counts.notStarted === 1 ? 'game' : 'games'}? They are paid from your existing provider funding (your OpenRouter balance, or your own provider accounts for connected keys). This app adds no spending cap and makes no purchases.</p>
                    <div className="cb-actions">
                      <button className="cb-btn cb-btn-primary" autoFocus disabled={Boolean(busy)} onClick={() => void act('run')}>{busy === 'run' ? 'Starting games…' : resuming ? 'Yes, resume new games' : 'Yes, start games'}</button>
                      <button className="cb-btn cb-btn-ghost" disabled={Boolean(busy)} onClick={() => { setConfirming(false); requestAnimationFrame(() => startButton.current?.focus()) }}>Not yet</button>
                    </div>
                  </div>
                : <button ref={startButton} className="cb-btn cb-btn-primary cb-btn-large" disabled={!canStart || Boolean(busy)} aria-describedby={!canStart ? 'start-blockers' : undefined} onClick={() => setConfirming(true)}>{resuming ? 'Resume new games' : 'Start games'}</button>}
              {!canStart ? <div id="start-blockers" className="cb-blockers">
                <p>{readiness ? 'Games can’t start yet:' : 'Can’t confirm games can start:'}</p>
                <ul className="cb-reasons">{reasons.map(r => <li key={r}>{r}</li>)}</ul>
              </div> : null}
              {readiness && !canStart && reasons.some(needsConnectionCheck) ? <CheckConnections onDone={() => refresh()} /> : null}
            </> : resuming ? <p>New games are paused. {stillPlaying} {stillPlaying === 1 ? 'game is' : 'games are'} still in progress and will continue until finished.</p> : null}
          {actionError ? <div role="alert">
            <p className="cb-error">{actionError}</p>
            {needsConnectionCheck(actionError) && !reasons.some(needsConnectionCheck) ? <CheckConnections onDone={() => refresh()} /> : null}
          </div> : null}
        </div>
      </section>

      {campaign.cells.length ? <section className="cb-section">
        <h2>Games</h2>
        <div className="cb-table-wrap">
          <table className="cb-table">
            <thead><tr><th scope="col">Order</th><th scope="col">Board</th><th scope="col">Seats</th><th scope="col">Status</th><th scope="col"><span className="cb-sr">Open</span></th></tr></thead>
            <tbody>{[...campaign.cells].sort((a, b) => a.execution_rank - b.execution_rank).map(cell => {
              const [statusLabel, statusTone] = cellStatus(cell)
              return <tr key={cell.cell_index}>
                <td>{cell.execution_rank + 1}</td>
                <td>Board {boards.get(cell.seed)}</td>
                <td>{cell.models_by_seat ? <SeatTokens models={cell.models_by_seat} /> : '—'}</td>
                <td><StatusPill label={statusLabel} tone={statusTone} />{cell.rerun_count ? <small className="cb-meta"> Technical rerun {cell.rerun_count}×</small> : null}</td>
                <td>{cell.job_id ? <a href={`/games/${cell.job_id}`}>{cell.job_status === 'running' ? 'Watch' : 'Open'}</a> : null}</td>
              </tr>
            })}</tbody>
          </table>
        </div>
      </section> : null}

      <details className="cb-disclosure">
        <summary>Research details</summary>
        <Facts rows={[
          ['Campaign ID', <code>{campaign.campaign_id}</code>],
          ...(campaign.config_sha256 ? [['Config hash', <code>{campaign.config_sha256}</code>] as [string, ReactNode]] : []),
          ...(campaign.git_sha ? [['Code version', <code>{campaign.git_sha}</code>] as [string, ReactNode]] : []),
          ...(campaign.image_digest ? [['Image', <code>{campaign.image_digest}</code>] as [string, ReactNode]] : []),
          ['Board seeds', <code>{[...boards.keys()].join(', ') || (campaign.config?.seeds ?? []).join(', ') || '—'}</code>],
          ['Seat rule', <code>{String(campaign.config?.seat_permutation ?? '—')}</code>],
          ['Model roster', <code>{String(campaign.config?.model_roster ?? '—')}</code>],
          ['Budget policy', <code>{String(campaign.config?.budget_policy ?? '—')}</code>],
        ]} />
        {freeze ? <ul className="cb-plain-list">{Object.entries(freeze).map(([name, entry]) => <li key={name}><strong>{name.replace(/_/g, ' ')}</strong> <code>{entry.path}</code> <code>sha256 {entry.sha256.slice(0, 12)}</code></li>)}</ul> : null}
        {campaign.cells.length ? <div className="cb-table-wrap"><table className="cb-table cb-table-compact">
          <caption>Run identifiers</caption>
          <thead><tr><th scope="col">Order</th><th scope="col">Cell</th><th scope="col">Seed</th><th scope="col">Run ID</th><th scope="col">Technical reruns</th></tr></thead>
          <tbody>{[...campaign.cells].sort((a, b) => a.execution_rank - b.execution_rank).map(cell => <tr key={cell.cell_index}><td>{cell.execution_rank + 1}</td><td>{cell.cell_index}</td><td><code>{cell.seed}</code></td><td><code>{cell.run_id ?? '—'}</code></td><td>{cell.rerun_count}</td></tr>)}</tbody>
        </table></div> : null}
        {campaign.status !== 'draft' ? <div className="cb-actions">
          <button className="cb-btn cb-btn-ghost" disabled={Boolean(busy)} onClick={() => void act('export')}>{busy === 'export' ? 'Preparing download…' : 'Prepare campaign download'}</button>
          {exportId ? <a className="cb-btn cb-btn-secondary" href={`${CLOUD_API}/exports/${exportId}/download`}>Download campaign</a> : null}
        </div> : null}
      </details>
    </div>
  </Shell>
}
