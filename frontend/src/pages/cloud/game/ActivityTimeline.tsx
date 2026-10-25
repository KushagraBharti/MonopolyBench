import { useCallback, useEffect, useLayoutEffect, useMemo, useRef, useState, type CSSProperties, type ReactNode } from 'react'
import type { Event } from '@/net/contracts'
import { fetchDecisionBundle, type DecisionAttempt, type DecisionBundle } from '@/net/decisions'
import { LabLogo } from '@/components/LabLogo'
import { getGroupColor } from '@/domain/monopoly/colors'
import { BOARD_TILES_BY_INDEX, SPACE_INDEX_BY_KEY, getSpaceName } from '@/domain/monopoly/constants'
import { formatCardTitle } from '@/domain/monopoly/formatters'
import type { Seat } from './gameModel'
import {
  buildActivity, describeDecision, filterActivity, humanize, latestSeq, waitingDecisionId,
  type ActivityFilter, type ActivityItem, type ActivityNames, type ActivityTurn, type AttemptView,
} from './activityModel'
import './activity.css'

type Props = {
  events: Event[]
  seats: Seat[]
  jobId: string
  runId: string
  /** The job is running, so the newest unanswered decision is genuinely in progress. */
  live: boolean
  onOpenDecisions: () => void
}

type DecisionItem = Extract<ActivityItem, { kind: 'decision' }>

const FILTERS: { value: ActivityFilter; label: string }[] = [
  { value: 'all', label: 'Everything' },
  { value: 'chat', label: 'Chat' },
  { value: 'moves', label: 'Moves' },
]
const NEAR_BOTTOM_PX = 48

// A decision bundle is immutable only once the canonical record says it resolved with a
// final action. Only those are cached (per job and decision, least recently used first out);
// provisional, incomplete or failed loads always refetch.
const BUNDLE_CACHE_LIMIT = 128
const resolvedBundles = new Map<string, DecisionBundle>()
const isResolved = (bundle: DecisionBundle) =>
  bundle.summary?.phase === 'decision_resolved' && bundle.final_action !== null && bundle.final_action !== undefined
async function loadBundle(runId: string, jobId: string, decisionId: string): Promise<DecisionBundle> {
  const key = `${jobId}/${decisionId}`
  const cached = resolvedBundles.get(key)
  if (cached) {
    resolvedBundles.delete(key)
    resolvedBundles.set(key, cached)
    return cached
  }
  const bundle = await fetchDecisionBundle(runId, decisionId, jobId)
  if (isResolved(bundle)) {
    resolvedBundles.set(key, bundle)
    if (resolvedBundles.size > BUNDLE_CACHE_LIMIT) resolvedBundles.delete(resolvedBundles.keys().next().value!)
  }
  return bundle
}

const spaceColor = (index: number | null) => {
  if (index === null) return null
  const tile = BOARD_TILES_BY_INDEX[index]
  if (!tile) return null
  if (tile.group) return getGroupColor(tile.group)
  return tile.kind === 'RAILROAD' ? '#1a1a1a' : tile.kind === 'UTILITY' ? '#8a96a3' : null
}

function Avatar({ seat, small }: { seat: Seat | undefined; small?: boolean }) {
  return <span className="mba-avatar" data-small={small || undefined} style={{ '--seat': seat?.color ?? '#9aa39b' } as CSSProperties} aria-hidden="true">
    {seat ? <LabLogo model={seat.model} decorative /> : null}
  </span>
}

function Author({ seat, playerId }: { seat: Seat | undefined; playerId: string | null }) {
  if (!seat) return <span className="mba-author"><strong>{playerId ?? 'Unknown player'}</strong></span>
  return <span className="mba-author" title={`Seat ${seat.seat}, configured participant ${seat.modelName}. Decision details shows which model answered.`}>
    <strong>Seat {seat.seat}</strong><span>{seat.modelName}</span>
  </span>
}

function Reasoning({ attempt, onToggle }: { attempt: AttemptView; onToggle: () => void }) {
  const r = attempt.reasoning
  if (r.kind === 'text') return <details className="mba-reasoning" onToggle={onToggle}><summary>Provider reasoning</summary><p>{r.text}</p></details>
  if (r.kind === 'unreadable') return <p className="mba-quiet">The provider returned reasoning with no readable text (for example, encrypted).</p>
  return <p className="mba-quiet">The provider returned no reasoning text for this attempt.{attempt.withoutPrivateThought ? ' This was a recovery request, which asks for an action without a private thought.' : ''}</p>
}

const json = (value: unknown) => typeof value === 'string' ? value : JSON.stringify(value, null, 2)

/** The recorded request and response for one attempt, from the bundle already loaded. Rendered only when opened. */
function AttemptRecord({ attempt, onToggle }: { attempt: DecisionAttempt; onToggle: () => void }) {
  const [open, setOpen] = useState(false)
  const parts: [string, unknown][] = [
    ['System prompt', attempt.system_prompt],
    ['User payload', attempt.user_payload],
    ['Tools offered', attempt.tools],
    ['Raw provider response', attempt.response],
    ['Parsed tool call', attempt.parsed_tool_calls ?? attempt.parsed_tool_call],
  ]
  return <details className="mba-record" onToggle={e => { setOpen(e.currentTarget.open); onToggle() }}>
    <summary>Full request and response record</summary>
    {open ? parts.map(([label, value]) => <div key={label}>
      <h5>{label}</h5>
      {value === null || value === undefined ? <p className="mba-quiet">Not recorded.</p> : <pre className="mba-raw">{json(value)}</pre>}
    </div>) : null}
  </details>
}

/**
 * Recorded decision, loaded only when opened. `revision` changes when this decision's own
 * events change (for example its response arrives), which refetches an unresolved record.
 */
function DecisionDetails({ runId, jobId, decisionId, revision, seat, onOpenDecisions, relayout }: { runId: string; jobId: string; decisionId: string; revision: string; seat: Seat | undefined; onOpenDecisions: () => void; relayout: () => void }) {
  const key = `${jobId}/${decisionId}/${revision}`
  const [nonce, setNonce] = useState(0)
  const [result, setResult] = useState<{ key: string; nonce: number; bundle?: DecisionBundle; error?: string } | null>(null)
  useEffect(() => {
    let active = true
    loadBundle(runId, jobId, decisionId).then(
      bundle => { if (active) setResult({ key, nonce, bundle }) },
      error => { if (active) setResult({ key, nonce, error: error instanceof Error ? error.message : 'Could not load this decision.' }) },
    )
    return () => { active = false }
  }, [runId, jobId, decisionId, key, nonce])
  const current = result && result.key === key && result.nonce === nonce ? result : null
  // While a newer revision loads, keep showing the previous record for this decision so the row does not collapse.
  const shown = current ?? (result?.bundle && result.key.startsWith(`${jobId}/${decisionId}/`) ? result : null)
  if (!shown) return <div className="mba-details" role="status">Loading decision…</div>
  if (shown.error || !shown.bundle) return <div className="mba-details">
    <p className="mba-error" role="alert">{shown.error ?? 'Could not load this decision.'}</p>
    <button type="button" className="mba-link" onClick={() => setNonce(n => n + 1)}>Try again</button>
  </div>
  const bundle = shown.bundle
  const view = describeDecision(bundle, seat?.model ?? null)
  const records = new Map(bundle.attempts.map(a => [a.attempt_index, a]))
  return <div className="mba-details">
    <p className="mba-outcome" data-tone={view.defaultActionApplied ? 'warn' : undefined}>{view.outcome}</p>
    {view.finalAction ? <p>Applied action: <strong>{humanize(view.finalAction)}</strong>{view.defaultActionApplied ? ' (engine default)' : ''}</p> : null}
    {!current ? <p className="mba-quiet" role="status">Updating…</p>
      : !isResolved(bundle) ? <p className="mba-quiet">This record is not final yet. <button type="button" className="mba-link" onClick={() => setNonce(n => n + 1)}>Refresh</button></p> : null}
    <ol className="mba-attempts">{view.attempts.map(a => {
      const record = records.get(a.index)
      return <li key={a.index}>
        <h4>{a.label}</h4>
        <dl>
          <dt>Requested</dt><dd><code>{a.requestedModel ?? 'Not recorded'}</code></dd>
          <dt>Returned</dt><dd><code>{a.returnedModel ?? 'Not reported by the provider'}</code></dd>
          <dt>Request</dt><dd>{a.condition}</dd>
        </dl>
        {a.usedFallbackModel && seat ? <p className="mba-quiet">This request went to a configured fallback model, not the seat’s participant ({seat.modelName}).</p> : null}
        {a.errors.length ? <ul className="mba-errors">{a.errors.map((err, i) => <li key={i}>{err}</li>)}</ul> : null}
        <Reasoning attempt={a} onToggle={relayout} />
        {record ? <AttemptRecord attempt={record} onToggle={relayout} /> : null}
      </li>
    })}</ol>
    <p className="mba-quiet">The seat label names the configured participant. The requested and returned models show which model answered.</p>
    <button type="button" className="mba-link" onClick={onOpenDecisions}>Browse all decisions</button>
  </div>
}

function Toggle({ open, onToggle, children }: { open: boolean; onToggle: () => void; children: ReactNode }) {
  return <button type="button" className="mba-toggle" aria-expanded={open} onClick={onToggle}>{children}</button>
}

function DecisionBlock({ item, seat, filter, waiting, ctx }: { item: DecisionItem; seat: Seat | undefined; filter: ActivityFilter; waiting: boolean; ctx: Ctx }) {
  const messages = item.messages.filter(message => message.text.trim())
  const [thoughtOpen, setThoughtOpen] = useState(false)
  const [detailsOpen, setDetailsOpen] = useState(false)
  const showThoughts = filter !== 'chat' && item.thoughts.length > 0
  const type = item.decisionType ? humanize(item.decisionType).toLowerCase().replace(/ decision$/, '') : 'a'
  const who = seat ? `Seat ${seat.seat}` : item.playerId ?? 'A player'
  const toggle = (set: (fn: (v: boolean) => boolean) => void) => () => { set(v => !v); ctx.relayout() }

  let status: ReactNode = null
  if (item.response) status = item.response.valid
    ? <span>Chose <strong>{humanize(item.response.actionName).toLowerCase()}</strong></span>
    : <span className="mba-warn">Answer not accepted{item.response.error ? `: ${item.response.error}` : ''}</span>
  else if (waiting) status = <span>Waiting for {who}’s {type} decision</span>
  else if (item.requested) status = <span className="mba-quiet">No answer is in the visible events</span>

  return <li className="mba-decision" data-chat={messages.length > 0 || undefined}>
    {messages.length > 0 ? <div className="mba-speaker">
      <Avatar seat={seat} />
      <div className="mba-said">
        <Author seat={seat} playerId={item.playerId} />
        {messages.map(m => <p key={m.eventId} className="mba-bubble" style={{ '--seat': seat?.color ?? '#9aa39b' } as CSSProperties}>{m.text}</p>)}
      </div>
    </div> : <div className="mba-row mba-row-quiet"><Avatar seat={seat} small /><span>{who}{item.decisionId ? '' : ': private thought from an older run'}</span></div>}
    {filter === 'chat' ? null : <div className="mba-meta">
      {status}
      {showThoughts ? <Toggle open={thoughtOpen} onToggle={toggle(setThoughtOpen)}>Private thought</Toggle> : null}
      {item.decisionId && (item.response || !waiting) ? <Toggle open={detailsOpen} onToggle={toggle(setDetailsOpen)}>Decision details</Toggle> : null}
    </div>}
    {showThoughts && thoughtOpen ? <div className="mba-thought">
      <p className="mba-thought-label">Private thought, not shown to other players</p>
      {item.thoughts.map(t => <p key={t.eventId}>{t.text}</p>)}
    </div> : null}
    {item.decisionId && detailsOpen && filter !== 'chat' ? <div>
      <DecisionDetails runId={ctx.runId} jobId={ctx.jobId} decisionId={item.decisionId} revision={`${item.eventIds.length}:${item.response?.eventId ?? ''}`} seat={seat} onOpenDecisions={ctx.onOpenDecisions} relayout={ctx.relayout} />
    </div> : null}
  </li>
}

type Ctx = { runId: string; jobId: string; onOpenDecisions: () => void; relayout: () => void; seatOf: (id: string | null) => Seat | undefined }

function Disclosure({ summary, children, className, ctx }: { summary: ReactNode; children: ReactNode; className?: string; ctx: Ctx }) {
  return <details className={className} onToggle={ctx.relayout}><summary>{summary}</summary><div className="mba-more">{children}</div></details>
}

function Item({ item, filter, waiting, ctx }: { item: ActivityItem; filter: ActivityFilter; waiting: string | null; ctx: Ctx }) {
  switch (item.kind) {
    case 'decision':
      return <DecisionBlock item={item} seat={ctx.seatOf(item.playerId)} filter={filter} waiting={waiting === item.decisionId} ctx={ctx} />
    case 'chat': {
      if (!item.text.trim()) return null
      const seat = ctx.seatOf(item.playerId)
      return <li className="mba-decision" data-chat><div className="mba-speaker"><Avatar seat={seat} /><div className="mba-said">
        <Author seat={seat} playerId={item.playerId} />
        <p className="mba-bubble" style={{ '--seat': seat?.color ?? '#9aa39b' } as CSSProperties}>{item.text}</p>
      </div></div></li>
    }
    case 'roll':
      return <li className="mba-row mba-row-quiet mba-roll">
        <span className="mba-dice" aria-hidden="true"><i>{item.d1}</i><i>{item.d2}</i></span>
        <span>{item.text}{item.details.length ? <span className="mba-quiet">. {item.details.join('; ')}</span> : null}</span>
      </li>
    case 'note':
      return <li className="mba-row mba-row-quiet mba-note">{item.text}</li>
    case 'group':
      if (item.lines.length === 1) return <li className="mba-row mba-row-quiet mba-cash">{item.summary}</li>
      return <li className="mba-row mba-row-quiet mba-cash"><Disclosure ctx={ctx} summary={item.summary}><ul>{item.lines.map((l, i) => <li key={i}>{l}</li>)}</ul></Disclosure></li>
    case 'action': {
      const seat = ctx.seatOf(item.playerId)
      const swatch = spaceColor(item.spaceIndex)
      const text = <>{swatch ? <i className="mba-swatch" style={{ background: swatch }} aria-hidden="true" /> : null}{item.text}</>
      return <li className="mba-row mba-action" data-tone={item.tone} style={{ '--seat': seat?.color ?? '#9aa39b' } as CSSProperties}>
        {item.details.length ? <Disclosure ctx={ctx} summary={text}><ul>{item.details.map((l, i) => <li key={i}>{l}</li>)}</ul></Disclosure> : <span>{text}</span>}
      </li>
    }
    case 'unknown':
      return <li className="mba-row mba-row-quiet"><Disclosure ctx={ctx} summary={<>{item.label}<span className="mba-quiet"> (event this view does not describe yet)</span></>}>
        <pre className="mba-raw">{JSON.stringify(item.payload, null, 2)}</pre>
      </Disclosure></li>
  }
}

function turnTitle(turn: ActivityTurn) {
  if (turn.setup) return 'Game setup'
  return turn.continued ? `Turn ${turn.turnIndex}, continued` : `Turn ${turn.turnIndex}`
}

/**
 * One chronological activity panel: public messages, decisions and engine actions grouped
 * by turn. Follows new activity only while the reader is at the bottom.
 */
export function ActivityTimeline({ events, seats, jobId, runId, live, onOpenDecisions }: Props) {
  const [filter, setFilter] = useState<ActivityFilter>('all')
  const scrollRef = useRef<HTMLDivElement>(null)
  const contentRef = useRef<HTMLDivElement>(null)
  const pinned = useRef(true)
  const [following, setFollowing] = useState(true)
  const latest = latestSeq(events)
  const [seenSeq, setSeenSeq] = useState(latest)

  const bySeat = useMemo(() => new Map(seats.map(s => [s.playerId, s])), [seats])
  const names = useMemo<ActivityNames>(() => ({
    player: id => bySeat.get(id)?.label ?? (id || 'Unknown player'),
    space: index => getSpaceName(index),
    spaceKey: key => { const index = SPACE_INDEX_BY_KEY[key.toUpperCase()]; return index === undefined ? humanize(key) : getSpaceName(index) },
    card: id => formatCardTitle(id),
  }), [bySeat])
  const turns = useMemo(() => buildActivity(events, names, runId), [events, names, runId])
  const shown = useMemo(() => filterActivity(turns, filter), [turns, filter])
  const waiting = live ? waitingDecisionId(turns) : null

  const latestRef = useRef(latest)
  useLayoutEffect(() => { latestRef.current = latest }, [latest])
  // Re-reads where the reader is. Never scrolls; only decides whether new events should follow.
  const measure = useCallback(() => {
    const el = scrollRef.current
    if (!el) return
    const near = el.scrollHeight - el.scrollTop - el.clientHeight < NEAR_BOTTOM_PX
    pinned.current = near
    setFollowing(near)
    if (near) setSeenSeq(latestRef.current)
  }, [])
  const relayout = useCallback(() => { requestAnimationFrame(measure) }, [measure])
  useEffect(() => { relayout() }, [filter, relayout])

  // The only automatic scroll: new events while the reader is at the bottom. It runs in a
  // layout effect, before the resize observer below sees the new content.
  useLayoutEffect(() => {
    const el = scrollRef.current
    if (el && pinned.current) el.scrollTop = el.scrollHeight
  }, [latest])

  // Content that grows or shrinks without a new event (a decision record arriving, reasoning
  // opened, fonts loading) is the reader's doing: re-measure so a later event does not yank
  // them away from what they expanded. A panel resize keeps a pinned reader at the bottom.
  useEffect(() => {
    const el = scrollRef.current
    const content = contentRef.current
    if (!el || !content || typeof ResizeObserver === 'undefined') return
    const observer = new ResizeObserver(entries => {
      if (pinned.current && entries.some(e => e.target === el) && !entries.some(e => e.target === content)) el.scrollTop = el.scrollHeight
      measure()
    })
    observer.observe(el)
    observer.observe(content)
    document.fonts?.ready.then(() => relayout(), () => {})
    return () => observer.disconnect()
  }, [measure, relayout])

  const jump = () => {
    const el = scrollRef.current
    if (!el) return
    el.scrollTop = el.scrollHeight
    pinned.current = true
    setFollowing(true)
    setSeenSeq(latest)
  }

  const ctx = useMemo<Ctx>(() => ({ runId, jobId, onOpenDecisions, relayout, seatOf: id => id ? bySeat.get(id) : undefined }), [runId, jobId, onOpenDecisions, relayout, bySeat])
  const unseen = !following && latest > seenSeq

  return <div className="mba">
    <header className="mba-head">
      <h2 id="mba-title">Game activity</h2>
      <div className="mba-filter" role="group" aria-label="Show">
        {FILTERS.map(f => <button key={f.value} type="button" aria-pressed={filter === f.value} onClick={() => setFilter(f.value)}>{f.label}</button>)}
      </div>
    </header>
    <div ref={scrollRef} className="mba-scroll" onScroll={measure} tabIndex={0} role="log" aria-labelledby="mba-title" aria-live="off">
      <div ref={contentRef}>
      {turns.length === 0 ? <p className="mba-empty">No moves yet. Messages and moves appear here as the game plays.</p>
        : shown.length === 0 ? <p className="mba-empty">{filter === 'chat' ? 'No public messages in the events shown.' : 'No moves in the events shown.'}</p>
        : shown.map(turn => {
          const seat = turn.playerId ? bySeat.get(turn.playerId) : undefined
          return <section key={turn.id} className="mba-turn" aria-label={turnTitle(turn)}>
            <h3 className="mba-turn-head">
              <span>{turnTitle(turn)}</span>
              {seat ? <span className="mba-turn-who"><Avatar seat={seat} small />{seat.label}</span> : null}
            </h3>
            <ol className="mba-items">{turn.items.map(item => <Item key={item.id} item={item} filter={filter} waiting={waiting} ctx={ctx} />)}</ol>
          </section>
        })}
      </div>
    </div>
    {following ? null : <div className="mba-foot">
      <span aria-live="polite">{unseen ? 'New activity below' : 'Viewing earlier activity'}</span>
      <button type="button" className="mba-jump" onClick={jump}>Jump to latest</button>
    </div>}
  </div>
}
