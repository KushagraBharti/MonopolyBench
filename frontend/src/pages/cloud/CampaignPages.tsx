import { useRef, useState, type ReactNode } from 'react'
import { CLOUD_API, cloudRequest, type CampaignCell, type CloudCampaign, type CloudJob } from '@/net/jobs'
import { Board } from '@/components/board/Board'
import { CheckConnections, Facts, GameTiles, Notice, SeatTokens, Shell, StatusPill } from './CloudShell'
import { ACTION_LABELS, boardNumbers, campaignName, campaignStatus, cellCounts, cellJobId, cellStatus, duration, errorText, money, needsConnectionCheck, settingsLine, usePoll, waitingText } from './cloudUi'

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
    <p className="cb-meta">{[counts.playing && `${counts.playing} playing.`, counts.waiting && `${counts.waiting} waiting for a slot.`, counts.paused && `${counts.paused} paused.`, counts.stopped && `${counts.stopped} stopped (failed or cancelled).`, counts.notStarted && `${counts.notStarted} not started.`].filter(Boolean).join(' ')}</p>
    {campaign.readiness && !campaign.readiness.can_start && counts.notStarted > 0 && campaign.status !== 'running'
      ? <p className="cb-meta">{campaign.readiness.reasons[0]}</p> : null}
  </article>
}

function CampaignDetailPage({ id }: { id: string }) {
  const path = `/campaigns/${encodeURIComponent(id)}`
  const { data, error, refresh, replace } = usePoll<CloudCampaign>(path)
  const [actionError, setActionError] = useState('')
  const [busy, setBusy] = useState('')
  const [confirming, setConfirming] = useState<'' | 'run' | 'cancel'>('')
  const [exportId, setExportId] = useState('')
  const lock = useRef(false)
  const startButton = useRef<HTMLButtonElement>(null)
  const justSaved = new URLSearchParams(window.location.search).get('saved') === '1'

  async function act(action: 'run' | 'pause' | 'cancel' | 'freeze' | 'export') {
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
      lock.current = false; setBusy(''); setConfirming('')
    }
  }

  function closeConfirm() {
    setConfirming('')
    requestAnimationFrame(() => startButton.current?.focus())
  }

  if (!data) return <Shell><div className="cb-page"><a className="cb-back" href="/campaigns">Campaigns</a>{error ? <p className="cb-error" role="alert">{error}</p> : <p>Loading campaign…</p>}</div></Shell>

  const campaign = { ...data, cells: data.cells ?? [] }
  const [label, tone] = campaignStatus(campaign)
  const counts = cellCounts(campaign.cells)
  const boards = boardNumbers(campaign.cells)
  const finished = campaign.status === 'done' || campaign.status === 'cancelled'
  const readiness = campaign.readiness
  // Fail closed: starting or resuming stays disabled unless the server confirms games can start.
  const canStart = readiness?.can_start === true
  const resuming = campaign.status === 'paused'
  // Resume covers paused campaigns; otherwise Start launches any games not yet started, even after some were started one by one.
  const startable = !finished && (resuming || ((campaign.status === 'frozen' || campaign.status === 'running') && counts.notStarted > 0))
  const cancellable = !finished && campaign.status !== 'draft' && counts.active + counts.notStarted > 0
  const reasons = readiness ? readiness.reasons : ['The server didn’t report whether games can start, so starting is turned off. Refresh the page, or update the server if this continues.']
  const freeze = campaign.config?.research_freeze
  const budget = typeof campaign.config?.cost_budget === 'number' ? campaign.config.cost_budget : null
  const startCount = counts.notStarted === counts.total ? `all ${counts.total}` : `the remaining ${counts.notStarted}`
  const ordered = [...campaign.cells].sort((a, b) => a.cell_index - b.cell_index)

  return <Shell>
    <div className="cb-page">
      <a className="cb-back" href="/campaigns">Campaigns</a>
      <header className="cb-page-head">
        <div><h1>{campaignName(campaign)}</h1><StatusPill label={label} tone={tone} /></div>
      </header>
      {justSaved && campaign.status === 'frozen' && counts.notStarted === counts.total
        ? <Notice tone="done" title="Campaign saved" role="status"><p>No games have started. Start them all below, or start a single game from its card.</p></Notice> : null}
      {error ? <p className="cb-error" role="alert">{error}</p> : null}

      <section className="cb-control" aria-labelledby="progress-title">
        <div className="cb-control-progress">
          <h2 id="progress-title" className="cb-count"><strong>{counts.finished}</strong> of {counts.total} games finished</h2>
          <GameTiles cells={campaign.cells} />
          <Facts rows={[
            ['Playing', counts.playing],
            ['Waiting for a slot', counts.waiting],
            ...(counts.paused ? [['Paused', counts.paused] as [string, number]] : []),
            ['Not started', counts.notStarted],
            ...(counts.stopped ? [['Stopped (failed or cancelled)', counts.stopped] as [string, number]] : []),
            ['At the same time', String(campaign.config?.concurrency ?? '—')],
            ['Spend pause', budget == null ? 'None' : `${money(budget)} across campaign`],
          ]} />
        </div>
        <div className="cb-control-actions">
          {campaign.status === 'draft' ? <>
            <p>This campaign comes from a repository file. Freezing records it for running and needs a passing model connection check from the last 6 hours.</p>
            <button className="cb-btn cb-btn-secondary" disabled={Boolean(busy)} onClick={() => void act('freeze')}>{busy === 'freeze' ? 'Freezing…' : 'Freeze campaign'}</button>
          </> : finished ? (campaign.status === 'cancelled'
              ? <p>This campaign was cancelled. {counts.finished} {counts.finished === 1 ? 'game' : 'games'} finished before that.</p>
              : counts.stopped
                ? <p>No games are left to start. {counts.finished} finished and {counts.stopped} stopped (failed or cancelled).</p>
                : <p className="cb-ok">All games have finished.</p>)
            : <>
              {campaign.status === 'running' || (campaign.status === 'frozen' && counts.active > 0) ? <>
                <p>The campaign is active. Pausing stops every game at its next safe point and keeps waiting games from launching. A model request already in flight may finish first.</p>
                <button className="cb-btn cb-btn-secondary" disabled={Boolean(busy)} onClick={() => void act('pause')}>{busy === 'pause' ? 'Pausing…' : 'Pause campaign'}</button>
              </> : null}
              {resuming ? <p>The campaign is paused. Resuming restarts the games that were paused with the campaign. Games you paused one by one stay paused until you resume them.</p> : null}
              {startable ? <>
                {confirming === 'run'
                  ? <div className="cb-confirm" role="group" aria-label={resuming ? 'Confirm resume' : 'Confirm start'}>
                      <p>{resuming ? 'Resume the campaign?' : `Start ${startCount} ${counts.notStarted === 1 ? 'game' : 'games'}?`} {resuming ? '' : `Up to ${campaign.config?.concurrency ?? 'the set number of'} play at once; the rest wait for a slot. `}Games are paid from your existing provider funding (your OpenRouter balance, or your own provider accounts for connected keys). This app makes no purchases.</p>
                      <div className="cb-actions">
                        <button className="cb-btn cb-btn-primary" autoFocus disabled={Boolean(busy)} onClick={() => void act('run')}>{busy === 'run' ? (resuming ? 'Resuming…' : 'Starting games…') : resuming ? 'Yes, resume campaign' : 'Yes, start games'}</button>
                        <button className="cb-btn cb-btn-ghost" disabled={Boolean(busy)} onClick={closeConfirm}>Not yet</button>
                      </div>
                    </div>
                  : <button ref={startButton} className="cb-btn cb-btn-primary cb-btn-large" disabled={!canStart || Boolean(busy)} aria-describedby={!canStart ? 'start-blockers' : undefined} onClick={() => setConfirming('run')}>{resuming ? 'Resume campaign' : `Start ${startCount} games`}</button>}
                {!canStart ? <div id="start-blockers" className="cb-blockers">
                  <p>{readiness ? 'Games can’t start yet:' : 'Can’t confirm games can start:'}</p>
                  <ul className="cb-reasons">{reasons.map(r => <li key={r}>{r}</li>)}</ul>
                </div> : null}
                {readiness && !canStart && reasons.some(needsConnectionCheck) ? <CheckConnections onDone={() => refresh()} /> : null}
              </> : null}
              {cancellable ? confirming === 'cancel'
                ? <div className="cb-confirm cb-confirm-danger" role="group" aria-label="Confirm cancel">
                    <p>Cancel the whole campaign? Every game that is waiting, playing or paused stops for good, and games that haven’t started never will. Finished games and their files are kept. This can’t be undone.</p>
                    <div className="cb-actions">
                      <button className="cb-btn cb-btn-danger" autoFocus disabled={Boolean(busy)} onClick={() => void act('cancel')}>{busy === 'cancel' ? 'Cancelling…' : 'Yes, cancel campaign'}</button>
                      <button className="cb-btn cb-btn-ghost" disabled={Boolean(busy)} onClick={() => setConfirming('')}>Keep campaign</button>
                    </div>
                  </div>
                : <button className="cb-btn cb-btn-danger" disabled={Boolean(busy)} onClick={() => setConfirming('cancel')}>Cancel campaign</button> : null}
            </>}
          {actionError ? <div role="alert">
            <p className="cb-error">{actionError}</p>
            {needsConnectionCheck(actionError) && !reasons.some(needsConnectionCheck) ? <CheckConnections onDone={() => refresh()} /> : null}
          </div> : null}
        </div>
      </section>

      {ordered.length ? <section className="cb-section cb-section-wide" aria-labelledby="games-title">
        <h2 id="games-title">Games</h2>
        <p className="cb-hint">Open any game to watch its board live. You can also start, pause, resume or cancel games one at a time.</p>
        <div className="cb-cell-grid">
          {ordered.map(cell => <CellCard key={cell.cell_index} cell={cell} board={boards.get(cell.seed)} campaignPath={path} canStart={canStart} campaignBusy={Boolean(busy)} onCampaign={replace} onChanged={refresh} />)}
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

const CELL_ACTIONS = ['start', 'pause', 'resume', 'cancel']

/** One campaign game: live board thumbnail, a link to watch it, and its own controls. */
function CellCard({ cell, board, campaignPath, canStart, campaignBusy, onCampaign, onChanged }: {
  cell: CampaignCell; board?: number; campaignPath: string; canStart: boolean; campaignBusy: boolean
  onCampaign: (campaign: CloudCampaign) => void; onChanged: () => void
}) {
  const [busy, setBusy] = useState('')
  const [error, setError] = useState('')
  const lock = useRef(false)
  const [statusLabel, statusTone] = cellStatus(cell)
  const jobId = cellJobId(cell)
  const game = cell.game ?? null
  const actions = (cell.allowed_actions ?? game?.allowed_actions ?? []).filter(a => CELL_ACTIONS.includes(a))
  const number = cell.cell_index + 1
  const watchHref = jobId ? `/games/${jobId}` : null
  const turn = game?.snapshot?.turn_index

  async function act(action: string) {
    if (lock.current) return
    if (action === 'start' && !window.confirm(`Start game ${number} now? Only this game starts; the others stay as they are. It is paid from your existing provider funding.`)) return
    if (action === 'cancel' && !window.confirm(`Cancel game ${number}? It stops for good and can’t be resumed.`)) return
    lock.current = true; setBusy(action); setError('')
    try {
      if (action === 'start') {
        const campaign = await cloudRequest<CloudCampaign>(`${campaignPath}/cells/${cell.cell_index}/start`, {})
        if (Array.isArray(campaign?.cells)) onCampaign(campaign)
      } else if (jobId) {
        await cloudRequest<CloudJob>(`/jobs/${jobId}/${action}`, {})
      }
      onChanged()
    } catch (e) {
      setError(errorText(e))
      onChanged()
    } finally {
      lock.current = false; setBusy('')
    }
  }

  return <article className="cb-card cb-cell" aria-labelledby={`cell-${cell.cell_index}`}>
    <header><h3 id={`cell-${cell.cell_index}`}>Game {number}{board ? <small> · Board {board}</small> : null}</h3><StatusPill label={statusLabel} tone={statusTone} /></header>
    {watchHref ? <a className="cb-job-board" href={watchHref} tabIndex={-1} aria-hidden="true">
      {game?.snapshot ? <div className="cloud-thumbnail"><Board spaces={game.snapshot.board} players={game.snapshot.players} activePlayerId={game.snapshot.active_player_id} /></div>
        : <div className="cloud-placeholder">{waitingText(game?.status ?? cell.job_status)}</div>}
    </a> : <div className="cloud-placeholder" aria-hidden="true">Not started</div>}
    {cell.models_by_seat ? <SeatTokens models={cell.models_by_seat} labelled /> : null}
    {game ? <p className="cb-meta">{[
      turn != null ? `Turn ${turn}` : null,
      game.elapsed_seconds != null ? `${duration(game.elapsed_seconds)} elapsed` : null,
      game.progress_age_seconds != null && game.status === 'running' ? `last move ${duration(game.progress_age_seconds)} ago` : null,
      `recorded cost ${money(game.cost.known_total)}`,
    ].filter(Boolean).join(' · ')}</p> : null}
    {game ? <p className="cb-meta">{settingsLine(game.config)}</p> : null}
    {game?.pause_reason && game.status === 'paused' ? <p className="cb-flag" data-tone="warn">Paused: {game.pause_reason.replace(/_/g, ' ')}</p> : null}
    {cell.rerun_count ? <p className="cb-meta">Technical rerun {cell.rerun_count}×</p> : null}
    {!jobId && cell.not_started_reason && cell.not_started_reason !== 'code_identity_mismatch' ? <p className="cb-meta">{cell.not_started_reason.replace(/_/g, ' ')}</p> : null}
    <div className="cloud-actions">
      {watchHref ? <a className="cb-btn cb-btn-secondary" href={watchHref}>Watch board</a> : null}
      {actions.map(action => {
        const blocked = action === 'start' && !canStart
        return <button key={action} className={`cb-btn ${action === 'cancel' ? 'cb-btn-danger' : action === 'start' ? 'cb-btn-secondary' : 'cb-btn-ghost'}`}
          disabled={Boolean(busy) || campaignBusy || blocked} title={blocked ? 'Games can’t start yet. See the reasons above.' : undefined}
          onClick={() => void act(action)}>{busy === action ? 'Working…' : ACTION_LABELS[action] ?? action}</button>
      })}
    </div>
    {error ? <p className="cb-error" role="alert">{error}</p> : null}
  </article>
}
