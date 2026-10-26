import { useCallback, useEffect, useMemo, useRef, useState } from 'react'
import { CLOUD_API, type CloudJob } from '@/net/jobs'
import { Board } from '@/components/board/Board'
import { Inspector } from '@/components/panels/Inspector'
import { useGameStore } from '@/state/store'
import { StatusPill } from '../CloudShell'
import { useJobAction } from '../useJobAction'
import { ACTION_LABELS, downloadWait, exportFailed, jobHome, jobStatus, jobTitle, playerModels, usePoll, waitingText } from '../cloudUi'
import { ActivityTimeline } from './ActivityTimeline'
import { BoardCenter } from './BoardCenter'
import { PlayerLineup } from './PlayerLineup'
import { ResearchDrawer, type DrawerTab } from './ResearchDrawer'
import { buildSeats, isActiveStatus, reasonLabel, TERMINAL } from './gameModel'
import { MAX_PANEL_EVENTS, useJobLive, type LiveConnection } from './useJobLive'
import '../../cloud.css'
import './game.css'

const CONNECTION_TEXT: Record<LiveConnection, string> = {
  connecting: 'Connecting to live updates…',
  live: 'Live updates on',
  reconnecting: 'Reconnecting to live updates…',
  closed: 'Live updates unavailable',
}

/** Server-listed actions only. Resume is the primary action when offered. */
function GameActions({ job, onChanged, onError }: { job: CloudJob; onChanged: (job: CloudJob) => void; onError: (text: string) => void }) {
  const { act, error, busy } = useJobAction(job, onChanged)
  useEffect(() => { onError(error) }, [error, onError])
  const style = (action: string) => action === 'resume' || action === 'start' ? 'cb-btn-primary' : action === 'cancel' ? 'cb-btn-danger' : action === 'pause' ? 'cb-btn-secondary' : 'cb-btn-ghost'
  return <>{job.allowed_actions.map(action => <button key={action} type="button" className={`cb-btn ${style(action)}`} disabled={Boolean(busy)} onClick={() => void act(action)}>{busy === action ? 'Working…' : ACTION_LABELS[action] ?? action}</button>)}</>
}

/** Full-screen game table: board in the middle, seats and feeds beside it, research in a drawer. */
export function GamePage() {
  const id = window.location.pathname.split('/')[2]
  const { data, error, replace } = usePoll<CloudJob>(`/jobs/${id}`)
  // usePoll can briefly hold another job's data; never render it under this id.
  const job = data?.job_id === id ? data : null
  const { connection, error: liveError, historyLimited, eventsSynchronized } = useJobLive(id, job)
  const stored = useGameStore(s => s.snapshot)
  const events = useGameStore(s => s.events)
  const deedHighlight = useGameStore(s => s.ui.deedHighlight)
  const inspectorOpen = useGameStore(s => s.inspectorOpen)
  const snapshot = job && stored?.run_id === job.run_id ? stored : null
  const [drawerOpen, setDrawerOpen] = useState(false)
  const [drawerTab, setDrawerTab] = useState<DrawerTab>('Deeds')
  const [actionError, setActionError] = useState('')
  const drawerTrigger = useRef<HTMLButtonElement>(null)
  // Focus returns to whatever opened the drawer (header button or a timeline link).
  const drawerOpener = useRef<HTMLElement | null>(null)
  const closeDrawer = useCallback(() => {
    setDrawerOpen(false)
    const opener = drawerOpener.current
    drawerOpener.current = null
    requestAnimationFrame(() => (opener?.isConnected ? opener : drawerTrigger.current)?.focus())
  }, [])

  const seats = useMemo(() => job ? buildSeats(job, snapshot) : [], [job, snapshot])
  const models = useMemo(() => job ? playerModels(job.config) : {}, [job])
  const labels = useMemo(() => Object.fromEntries(seats.map(s => [s.playerId, s.label])), [seats])
  const openDrawer = useCallback((tab: DrawerTab) => {
    const active = document.activeElement
    drawerOpener.current = active instanceof HTMLElement && active !== document.body ? active : null
    setDrawerTab(tab)
    setDrawerOpen(true)
  }, [])
  const openDecisions = useCallback(() => openDrawer('Decisions'), [openDrawer])

  useEffect(() => {
    if (!job) return
    useGameStore.getState().setRunStatus({
      runId: job.run_id,
      running: job.status === 'running',
      paused: job.status === 'paused',
      // The inspector labels players by model; configured fallbacks are shown in the drawer, not here.
      players: job.config.players.map(p => ({ ...p, name: labels[p.player_id] ?? p.name, model_display_name: p.openrouter_model_id })),
    })
  }, [job, labels])

  const title = job ? jobTitle(job) : 'Loading game…'
  useEffect(() => {
    document.title = snapshot ? `${title}, turn ${snapshot.turn_index} | MonopolyBench` : `${title} | MonopolyBench`
  }, [title, snapshot])

  const [statusLabel, statusTone] = jobStatus(job?.status)
  const home = job ? jobHome(job) : { href: '/games', label: 'Games' }
  const gameOver = snapshot?.phase === 'GAME_OVER'
  // Queued games show a preview board with no turn in progress.
  const turnHolder = job && snapshot && isActiveStatus(job.status) && job.status !== 'queued' && !gameOver ? snapshot.active_player_id : null
  const winnerId = job && (job.status === 'completed' || job.status === 'finalizing') ? job.outcome?.winner_player_id ?? null : null
  const terminal = job ? TERMINAL.has(job.status) : false

  const notices: { text: string; tone: 'warn' | 'idle' | 'bad' }[] = []
  if (error) notices.push({ text: error, tone: 'bad' })
  if (liveError) notices.push({ text: liveError, tone: 'bad' })
  if (actionError) notices.push({ text: actionError, tone: 'bad' })
  if (job?.status === 'paused' && job.pause_reason) notices.push({ text: `Paused: ${reasonLabel(job.pause_reason)}.`, tone: 'warn' })
  if (job?.slow && job.status === 'running') notices.push({ text: 'Slow: no move in over 5 minutes.', tone: 'warn' })
  if (job?.snapshot_kind === 'initial_preview' && !events.length) notices.push({ text: 'Starting board. The first saved move appears when the game begins.', tone: 'idle' })
  if (job && terminal && job.export_status !== 'ready') notices.push({ text: downloadWait(job) ?? '', tone: exportFailed(job) ? 'bad' : 'idle' })

  // Everything behind an open drawer or inspector is inert so focus and screen readers stay in the modal.
  const backdropInert = drawerOpen || inspectorOpen || undefined

  return <div className="mbg">
    <a className="cb-skip" href="#mbg-board" inert={backdropInert}>Skip to board</a>
    <header className="mbg-bar" inert={backdropInert}>
      <div className="mbg-bar-id">
        <a className="mbg-brand" href="/" aria-label="MonopolyBench dashboard"><span className="cb-brand-mark" aria-hidden="true" /></a>
        <a className="mbg-back" href={home.href}>{home.label}</a>
        <h1>{title}</h1>
        {job ? <StatusPill label={statusLabel} tone={statusTone} /> : null}
        {snapshot ? <span className="mbg-turn">Turn {snapshot.turn_index}</span> : null}
        <span className="mbg-conn" data-state={connection} role="status">{CONNECTION_TEXT[connection]}</span>
      </div>
      <div className="mbg-bar-actions">
        {job?.export_status === 'ready' ? <a className="cb-btn cb-btn-secondary" href={`${CLOUD_API}/jobs/${job.job_id}/export`}>Download game</a> : null}
        {job ? <GameActions job={job} onChanged={replace} onError={setActionError} /> : null}
        <button ref={drawerTrigger} type="button" className="cb-btn cb-btn-secondary" aria-haspopup="dialog" aria-expanded={drawerOpen} disabled={!job} onClick={() => openDrawer(drawerTab)}>Details and research</button>
      </div>
    </header>
    {notices.length ? <div className="mbg-notices" inert={backdropInert}>{notices.map((n, i) => <p key={i} data-tone={n.tone} role={n.tone === 'bad' ? 'alert' : undefined}>{n.text}</p>)}</div> : <div />}

    <main className="mbg-main" inert={backdropInert} data-stopped={job?.status === 'cancelled' || job?.status === 'failed' || undefined}>
      <section className="mbg-players" aria-labelledby="mbg-players-title">
        <h2 id="mbg-players-title" className="mbg-h">Players</h2>
        <PlayerLineup seats={seats} snapshot={snapshot} turnPlayerId={turnHolder} turnLabel={job?.status === 'running' ? 'Turn' : 'Turn holder'} winnerId={winnerId} />
      </section>

      <section className="mbg-board-area" id="mbg-board" aria-label="Board">
        {job && snapshot ? <Board
          className="mbg-board p-0"
          label={`Monopoly board at turn ${snapshot.turn_index}`}
          spaces={snapshot.board}
          players={snapshot.players}
          activePlayerId={turnHolder}
          phase={snapshot.phase}
          playerModels={models}
          playerLabels={labels}
          highlightState={{ deedHighlight, eventHighlight: null, decisionHighlight: null }}
          centerContent={<BoardCenter job={job} snapshot={snapshot} seats={seats} events={events} eventsSynchronized={eventsSynchronized} />}
        /> : <div className="mbg-placeholder">{job ? waitingText(job.status) : error ? 'Couldn’t load this game.' : 'Loading…'}</div>}
      </section>

      <section className="mbg-feeds" aria-labelledby="mba-title">
        {historyLimited ? <p className="mbg-history-note">Latest {MAX_PANEL_EVENTS} events shown. Earlier messages are in <button type="button" onClick={openDecisions}>Decisions</button> and <button type="button" onClick={() => openDrawer('Artifacts')}>artifacts</button>.</p> : null}
        {job ? <ActivityTimeline
          events={events}
          seats={seats}
          jobId={job.job_id}
          runId={job.run_id}
          live={job.status === 'running' && !gameOver}
          onOpenDecisions={openDecisions}
        /> : null}
      </section>
    </main>

    {job ? <ResearchDrawer job={job} snapshot={snapshot} seats={seats} open={drawerOpen} tab={drawerTab} onTab={setDrawerTab} onClose={closeDrawer} /> : null}
    <Inspector showLauncher={false} jobId={job?.job_id} />
  </div>
}
