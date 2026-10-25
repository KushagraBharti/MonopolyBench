import type { CSSProperties, ReactNode } from 'react'
import type { Event, StateSnapshot, TradeState } from '@/net/contracts'
import type { CloudJob } from '@/net/jobs'
import { LabLogo } from '@/components/LabLogo'
import { getGroupColor } from '@/domain/monopoly/colors'
import { BOARD_TILES_BY_INDEX, SPACE_INDEX_BY_KEY, getSpaceName } from '@/domain/monopoly/constants'
import { decisionLabel, lastDice, money, pendingDecision, reasonLabel, type Seat } from './gameModel'

type Props = {
  job: CloudJob
  snapshot: StateSnapshot
  seats: Seat[]
  events: Event[]
  /** False while the snapshot is newer than the streamed events; event-derived lines are then hidden. */
  eventsSynchronized?: boolean
}

function Who({ seat, fallback }: { seat: Seat | undefined; fallback?: string }) {
  if (!seat) return <span className="mbc-who">{fallback ?? 'Unknown player'}</span>
  return <span className="mbc-who" style={{ '--seat': seat.color } as CSSProperties}>
    <span className="mbc-chip"><LabLogo model={seat.model} decorative /></span>{seat.label}
  </span>
}

const PIPS: Record<number, number[]> = { 1: [4], 2: [0, 8], 3: [0, 4, 8], 4: [0, 2, 6, 8], 5: [0, 2, 4, 6, 8], 6: [0, 2, 3, 5, 6, 8] }
function Die({ value }: { value: number }) {
  return <span className="mbc-die" aria-hidden="true">{Array.from({ length: 9 }, (_, i) => <i key={i} data-on={PIPS[value]?.includes(i) || undefined} />)}</span>
}

function spaceFromKey(key: string) {
  const index = SPACE_INDEX_BY_KEY[key.toUpperCase()]
  return index === undefined ? { name: key.replace(/_/g, ' '), color: 'transparent' } : { name: getSpaceName(index), color: getGroupColor(BOARD_TILES_BY_INDEX[index]?.group) }
}

function bundleText(bundle: TradeState['current_offer']['offer']) {
  const parts: string[] = []
  if (bundle.cash > 0) parts.push(money(bundle.cash))
  for (const key of bundle.properties) parts.push(spaceFromKey(key).name)
  if (bundle.get_out_of_jail_cards > 0) parts.push(`${bundle.get_out_of_jail_cards} jail card${bundle.get_out_of_jail_cards === 1 ? '' : 's'}`)
  return parts.length ? parts.join(', ') : 'Nothing'
}

function Card({ title, children, tone }: { title: string; children: ReactNode; tone?: 'auction' | 'trade' | 'end' | 'stop' }) {
  return <section className="mbc-card" data-tone={tone}><h2>{title}</h2>{children}</section>
}

/**
 * Center of the board: only facts from the job, the accepted snapshot and its events.
 * Never shows a thinking state once the job is not running or the engine says game over.
 */
export function BoardCenter({ job, snapshot, seats, events, eventsSynchronized = true }: Props) {
  const seat = (id: string | null | undefined) => seats.find(s => s.playerId === id)
  const status = job.status
  const live = status === 'running'
  const gameOver = snapshot.phase === 'GAME_OVER'
  const active = seat(snapshot.active_player_id)
  const winner = job.outcome?.winner_player_id ? seat(job.outcome.winner_player_id) : undefined
  const pending = live && !gameOver && eventsSynchronized ? pendingDecision(events) : null
  const dice = eventsSynchronized ? lastDice(events, snapshot.turn_index) : null
  const showLiveContext = (status === 'running' || status === 'paused' || status === 'recovering') && !gameOver
  const auction = showLiveContext ? snapshot.auction ?? null : null
  const trade = showLiveContext ? snapshot.trade ?? null : null

  let main: ReactNode
  if (status === 'completed' || (status === 'finalizing' && job.outcome)) {
    main = <Card title={status === 'finalizing' ? 'Game over, saving results' : 'Game over'} tone="end">
      {winner ? <p className="mbc-big"><Who seat={winner} /> wins</p> : <p className="mbc-big">No winner</p>}
      {job.outcome?.reason ? <p className="mbc-sub">Ended by {reasonLabel(job.outcome.reason)} after turn {snapshot.turn_index}.</p> : <p className="mbc-sub">Ended after turn {snapshot.turn_index}.</p>}
    </Card>
  } else if (status === 'cancelled' || status === 'failed') {
    main = <Card title={status === 'cancelled' ? 'Game cancelled' : 'Game stopped by an error'} tone="stop">
      <p className="mbc-sub">Stopped at turn {snapshot.turn_index}. The board shows the last saved position.</p>
    </Card>
  } else if (status === 'finalizing' || gameOver) {
    main = <Card title="Game over" tone="end"><p className="mbc-sub">Recording the result.</p></Card>
  } else if (status === 'queued') {
    main = <Card title="Waiting for a slot"><p className="mbc-sub">The game starts when a worker is free.</p></Card>
  } else {
    const heading = status === 'paused' ? 'Paused' : status === 'recovering' ? 'Recovering' : `Turn ${snapshot.turn_index}`
    const pendingSeat = pending ? seat(pending.playerId) : undefined
    main = <Card title={heading}>
      {status === 'paused' && job.pause_reason ? <p className="mbc-sub">{reasonLabel(job.pause_reason)}</p> : null}
      <p className="mbc-line"><span className="mbc-label">{status === 'running' ? 'To move' : 'Turn holder'}</span><Who seat={active} fallback={snapshot.active_player_id} /></p>
      {pending ? <p className="mbc-line"><span className="mbc-label">Deciding</span><span>{pendingSeat && pendingSeat !== active ? <><Who seat={pendingSeat} /> · </> : null}{decisionLabel(pending.type)}</span></p> : null}
      {dice ? <p className="mbc-line"><span className="mbc-label">Rolled</span><span className="mbc-dice" aria-label={`Rolled ${dice.d1} and ${dice.d2}${dice.is_double ? ', doubles' : ''}`}><Die value={dice.d1} /><Die value={dice.d2} /><b>{dice.d1 + dice.d2}</b>{dice.is_double ? <small>Doubles</small> : null}</span></p> : null}
    </Card>
  }

  return <div className="mbc" tabIndex={0} role="region" aria-label="Game status, auction and trade">
    <p className="mbc-turn">Turn {snapshot.turn_index}</p>
    {main}
    {auction ? (() => {
      const space = spaceFromKey(auction.property_space_key)
      return <Card title="Auction" tone="auction">
        <p className="mbc-prop"><i style={{ background: space.color }} />{space.name}</p>
        <p className="mbc-line"><span className="mbc-label">High bid</span><span>{auction.current_high_bid > 0 ? money(auction.current_high_bid) : 'No bids'}{auction.current_leader_player_id ? <> by <Who seat={seat(auction.current_leader_player_id)} fallback={auction.current_leader_player_id} /></> : null}</span></p>
        {auction.current_bidder_player_id ? <p className="mbc-line"><span className="mbc-label">Now bidding</span><Who seat={seat(auction.current_bidder_player_id)} fallback={auction.current_bidder_player_id} /></p> : null}
        <p className="mbc-line"><span className="mbc-label">Still in</span><span className="mbc-chips" role="list" aria-label={`Still bidding: ${auction.active_bidders_player_ids.map(id => seat(id)?.label ?? id).join(', ') || 'nobody'}`}>{auction.active_bidders_player_ids.map(id => { const s = seat(id); return <span key={id} role="listitem" className="mbc-chip" title={s?.label ?? id} style={{ '--seat': s?.color } as CSSProperties}>{s ? <LabLogo model={s.model} decorative /> : null}<span className="cb-sr">{s?.label ?? id}</span></span> })}</span></p>
      </Card>
    })() : null}
    {trade ? (() => {
      const author = trade.current_offer.from_player_id ?? trade.initiator_player_id
      const other = author === trade.initiator_player_id ? trade.counterparty_player_id : trade.initiator_player_id
      return <Card title={`Trade · exchange ${trade.exchange_index + 1} of ${trade.max_exchanges}`} tone="trade">
        <p className="mbc-line"><span className="mbc-label">Offer from</span><Who seat={seat(author)} fallback={author} /></p>
        <p className="mbc-line"><span className="mbc-label">Gives</span><span>{bundleText(trade.current_offer.offer)}</span></p>
        <p className="mbc-line"><span className="mbc-label">Asks</span><span>{bundleText(trade.current_offer.request)}</span></p>
        <p className="mbc-line"><span className="mbc-label">To</span><Who seat={seat(other)} fallback={other} /></p>
      </Card>
    })() : null}
    <p className="mbc-bank">Bank: {snapshot.bank.houses_remaining} houses, {snapshot.bank.hotels_remaining} hotels left</p>
  </div>
}
