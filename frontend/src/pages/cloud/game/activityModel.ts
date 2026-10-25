/*
 * Pure model for the game activity timeline. Everything here is derived from accepted
 * engine events (and, for decision details, the recorded decision bundle); nothing infers
 * Monopoly legality. Type-only imports keep the module runnable under Node type stripping.
 */
import type { Event } from '@/net/contracts'
import type { DecisionAttempt, DecisionBundle } from '@/net/decisions'

/** Names supplied by the page so this module needs no board data at runtime. */
export type ActivityNames = {
  player: (playerId: string) => string
  space: (index: number) => string
  /** Space by engine key, e.g. auction `property_space` or trade property keys. */
  spaceKey: (key: string) => string
  card: (cardId: string) => string
}

export type ActivityFilter = 'all' | 'chat' | 'moves'
export type ActivityTone = 'plain' | 'key' | 'warn'

export type ActivityMessage = { eventId: string; text: string }
export type ActivityResponse = { eventId: string; actionName: string; valid: boolean; error: string | null }

export type ActivityItem =
  /** Dice roll with the move (and pass-GO payment) it caused. */
  | { kind: 'roll'; id: string; playerId: string | null; d1: number; d2: number; double: boolean; text: string; details: string[]; eventIds: string[] }
  /** One model decision: request, response, public message(s) and private thought(s), joined by decision_id. */
  | {
      kind: 'decision'; id: string; decisionId: string; playerId: string | null; decisionType: string | null
      requested: boolean; response: ActivityResponse | null; messages: ActivityMessage[]; thoughts: ActivityMessage[]; eventIds: string[]
    }
  /** Public message with no decision id (older runs). */
  | { kind: 'chat'; id: string; playerId: string; text: string; eventIds: string[] }
  /** A game action in plain words. `details` are folded engine effects (cash, transfers). */
  | { kind: 'action'; id: string; type: string; playerId: string | null; text: string; tone: ActivityTone; spaceIndex: number | null; details: string[]; eventIds: string[] }
  /** Routine engine bookkeeping (cash) collapsed into one line. */
  | { kind: 'group'; id: string; summary: string; lines: string[]; eventIds: string[] }
  /** Small structural line (game start, bids, drops). */
  | { kind: 'note'; id: string; playerId: string | null; text: string; eventIds: string[] }
  /** Event type this UI does not know yet. */
  | { kind: 'unknown'; id: string; type: string; label: string; payload: unknown; eventIds: string[] }

export type ActivityTurn = {
  id: string
  turnIndex: number
  /** Turn player, only when an event names them (dice roller or the first decision). */
  playerId: string | null
  /** TURN_STARTED is in the window. */
  started: boolean
  /** Window starts inside this turn: older events of it were trimmed. */
  continued: boolean
  /** Events before the first turn (GAME_STARTED). */
  setup: boolean
  ended: boolean
  items: ActivityItem[]
}

export type Raw = { type: string; event_id: string; seq: number; run_id: string; turn_index: number; actor?: { player_id?: string | null } | null; payload: Record<string, unknown> }

const str = (v: unknown): string | null => typeof v === 'string' && v ? v : null
const num = (v: unknown): number | null => typeof v === 'number' && Number.isFinite(v) ? v : null

export function humanize(value: string): string {
  const text = value.replace(/_/g, ' ').trim().toLowerCase()
  return text ? text[0].toUpperCase() + text.slice(1) : value
}

export function formatMoney(amount: number, signed = false): string {
  const abs = `$${Math.abs(amount).toLocaleString('en-US')}`
  if (!signed) return amount < 0 ? `-${abs}` : abs
  return amount < 0 ? `−${abs}` : `+${abs}`
}

/**
 * Chronological, de-duplicated events for one run. The cloud store already rejects stale
 * commits; this only guards the projection: same event_id or seq is kept once, foreign runs drop.
 */
export function orderEvents(events: readonly Event[], runId?: string | null): Event[] {
  const byId = new Set<string>()
  const bySeq = new Set<number>()
  const out: Event[] = []
  for (const event of events) {
    if (runId && event.run_id !== runId) continue
    if (byId.has(event.event_id) || bySeq.has(event.seq)) continue
    byId.add(event.event_id)
    bySeq.add(event.seq)
    out.push(event)
  }
  return out.sort((a, b) => a.seq - b.seq)
}

/** Seq of the newest accepted event, for follow-latest scrolling. */
export function latestSeq(events: readonly Event[]): number {
  let max = -1
  for (const e of events) if (e.seq > max) max = e.seq
  return max
}

const tradeBundle = (bundle: unknown, names: ActivityNames): string => {
  const b = (bundle ?? {}) as { cash?: unknown; properties?: unknown; get_out_of_jail_cards?: unknown }
  const parts: string[] = []
  const cash = num(b.cash)
  if (cash) parts.push(formatMoney(cash))
  if (Array.isArray(b.properties)) for (const p of b.properties) if (typeof p === 'string') parts.push(names.spaceKey(p))
  const cards = num(b.get_out_of_jail_cards)
  if (cards) parts.push(`${cards} Get Out of Jail Free card${cards === 1 ? '' : 's'}`)
  return parts.length ? parts.join(', ') : 'nothing'
}

/** Cash reasons that belong to the action next to them, so they are not repeated as cash noise. */
const CASH_FOR: Record<string, string[]> = {
  PROPERTY_PURCHASED: ['buy_property'],
  AUCTION_ENDED: ['auction_bid'],
  RENT_PAID: ['rent'],
  PROPERTY_MORTGAGED: ['mortgage', 'property_mortgaged'],
  PROPERTY_UNMORTGAGED: ['unmortgage', 'property_unmortgaged', 'mortgage_interest'],
  HOUSE_BUILT: ['build', 'house'],
  HOTEL_BUILT: ['build', 'house'],
  HOUSE_SOLD: ['sell_building', 'house'],
  HOTEL_SOLD: ['sell_building', 'house'],
  TRADE_ACCEPTED: ['trade_cash'],
  DICE_ROLLED: ['pass_go'],
  CARD_DRAWN: ['card', 'pass_go'],
}
/** Actions whose effects (moves, pass-GO cash) follow them, possibly after a move. */
const LOOKS_AHEAD_ONLY = new Set(['DICE_ROLLED', 'CARD_DRAWN'])

function involved(e: Raw): Set<string> {
  const p = e.payload
  const ids = [p.player_id, p.from_player_id, p.to_player_id, p.winner_player_id, p.initiator_player_id, p.counterparty_player_id, e.actor?.player_id]
  return new Set(ids.filter((v): v is string => typeof v === 'string'))
}

/** Cash events folded into a neighbouring action of the same turn: cash index -> action index. */
export function foldCash(list: readonly Raw[]): Map<number, number> {
  const folded = new Map<number, number>()
  list.forEach((e, i) => {
    const reasons = CASH_FOR[e.type]
    if (!reasons) return
    const who = involved(e)
    const take = (j: number) => {
      const c = list[j]
      if (c.type !== 'CASH_CHANGED' || folded.has(j) || c.turn_index !== e.turn_index) return
      const reason = String(c.payload.reason ?? '').toLowerCase()
      if (reasons.includes(reason) && who.has(String(c.payload.player_id))) folded.set(j, i)
    }
    const ahead = LOOKS_AHEAD_ONLY.has(e.type)
    for (let j = i + 1; j < list.length && (list[j].type === 'CASH_CHANGED' || (ahead && list[j].type === 'PLAYER_MOVED')); j++) take(j)
    if (!ahead) for (let j = i - 1; j >= 0 && list[j].type === 'CASH_CHANGED'; j--) take(j)
  })
  return folded
}

function cashLine(e: Raw, names: ActivityNames) {
  const delta = num(e.payload.delta) ?? 0
  const reason = str(e.payload.reason)
  return `${names.player(String(e.payload.player_id))} ${formatMoney(delta, true)}${reason ? ` (${humanize(reason).toLowerCase()})` : ''}`
}

type ActionItem = Extract<ActivityItem, { kind: 'action' }>
type RollItem = Extract<ActivityItem, { kind: 'roll' }>
type GroupItem = Extract<ActivityItem, { kind: 'group' }>
type DecisionItem = Extract<ActivityItem, { kind: 'decision' }>

/**
 * Turns, oldest first, each with readable items. `events` may be in any order (the store
 * keeps newest first). Every event lands in exactly one item; decision events join only by
 * exact decision_id, so identical public messages on different decisions stay separate.
 */
export function buildActivity(events: readonly Event[], names: ActivityNames, runId?: string | null): ActivityTurn[] {
  const list = orderEvents(events, runId) as unknown as Raw[]
  const folded = foldCash(list)
  const turns: ActivityTurn[] = []
  const decisions = new Map<string, DecisionItem>()
  const owners = new Map<number, ActionItem | RollItem>()
  let turn: ActivityTurn | null = null
  // The open cash group, and the action that absorbs the engine effects right after it.
  let cash: GroupItem | null = null
  let absorber: { item: ActionItem; kind: 'card' | 'trade' | 'bankrupt' } | null = null

  const open = (e: Raw, started: boolean): ActivityTurn => {
    const setup = !started && e.type === 'GAME_STARTED'
    const next: ActivityTurn = { id: `turn-${e.event_id}`, turnIndex: e.turn_index, playerId: null, started, continued: !started && !setup && turns.length === 0, setup, ended: false, items: [] }
    turns.push(next)
    cash = null
    absorber = null
    return next
  }
  const absorb = (item: ActionItem | RollItem, e: Raw, line?: string) => {
    if (line) item.details.push(line)
    item.eventIds.push(e.event_id)
  }

  list.forEach((e, index) => {
    const prev: ActivityTurn | null = turn
    const current: ActivityTurn = e.type === 'TURN_STARTED' ? open(e, true)
      : !prev || prev.turnIndex !== e.turn_index || (prev.setup && e.type !== 'GAME_STARTED') ? open(e, false) : prev
    turn = current
    const p = e.payload
    const actor = str(e.actor?.player_id)
    const id = e.event_id
    const push = (item: ActivityItem) => {
      current.items.push(item)
      if (item.kind !== 'group') cash = null
      absorber = null
    }
    const action = (text: string, tone: ActivityTone, playerId: string | null, spaceIndex: number | null = null): ActionItem => {
      const item: ActionItem = { kind: 'action', id, type: e.type, playerId, text, tone, spaceIndex, details: [], eventIds: [id] }
      push(item)
      owners.set(index, item)
      return item
    }
    const claimTurnPlayer = (playerId: string | null, strong: boolean) => {
      // Without TURN_STARTED a decision could be an auction bidder's, so only a roll names the turn.
      if (!current.playerId && playerId && (strong || current.started)) current.playerId = playerId
    }

    const owner = folded.get(index)
    if (owner !== undefined && owner < index) {
      const item = owners.get(owner)
      if (item) { absorb(item, e, cashLine(e, names)); return }
    }
    if (owner !== undefined && owner > index) return // Attached when its action is built (see below).

    switch (e.type) {
      case 'TURN_STARTED':
        return
      case 'TURN_ENDED':
        current.ended = true
        return
      case 'GAME_STARTED':
        push({ kind: 'note', id, playerId: null, text: 'Game started', eventIds: [id] })
        return
      case 'DICE_ROLLED': {
        claimTurnPlayer(actor, true)
        const d1 = num(p.d1) ?? 0, d2 = num(p.d2) ?? 0
        const item: RollItem = { kind: 'roll', id, playerId: actor, d1, d2, double: p.is_double === true, text: '', details: [], eventIds: [id] }
        const next = list[index + 1]
        let where = ''
        if (next?.type === 'PLAYER_MOVED' && next.turn_index === e.turn_index) {
          const to = num(next.payload.to)
          if (to !== null) where = ` and moved to ${names.space(to)}`
          if (next.payload.passed_go === true) where += ', passing GO'
        }
        item.text = `${names.player(actor ?? '')} rolled ${d1 + d2}${item.double ? ' (doubles)' : ''}${where}`
        push(item)
        owners.set(index, item)
        return
      }
      case 'PLAYER_MOVED': {
        const rolled = list[index - 1]?.type === 'DICE_ROLLED' ? owners.get(index - 1) : undefined
        if (rolled && rolled.kind === 'roll') { absorb(rolled, e); return }
        const to = num(p.to)
        const text = `Moved to ${to === null ? 'another space' : names.space(to)}${p.passed_go === true ? ', passing GO' : ''}`
        const held = absorber as { item: ActionItem; kind: string } | null
        if (held?.kind === 'card') { absorb(held.item, e, text); owners.set(index, held.item); return }
        push({ kind: 'note', id, playerId: actor, text: `${names.player(actor ?? '')} moved to ${to === null ? 'another space' : names.space(to)}`, eventIds: [id] })
        return
      }
      case 'CARD_DRAWN': {
        const deck = p.deck_type === 'CHANCE' ? 'Chance' : 'Community Chest'
        absorber = { item: action(`${names.player(actor ?? '')} drew ${deck}: ${names.card(String(p.card_id ?? ''))}`, 'plain', actor), kind: 'card' }
        return
      }
      case 'SENT_TO_JAIL': {
        const who = String(p.player_id ?? actor ?? '')
        const held = absorber as { item: ActionItem; kind: string } | null
        if (held?.kind === 'card') { absorb(held.item, e, 'Sent to jail'); return }
        action(`${names.player(who)} went to jail${p.reason ? ` (${humanize(String(p.reason)).toLowerCase()})` : ''}`, 'warn', who)
        return
      }
      case 'PROPERTY_PURCHASED': {
        const who = String(p.player_id ?? '')
        const space = num(p.space_index)
        const price = num(p.price) ?? 0
        const place = space === null ? 'a property' : names.space(space)
        const held = absorber as { item: ActionItem; kind: string } | null
        if (price === 0 && held?.kind === 'bankrupt') { absorb(held.item, e, `${names.player(who)} received ${place}`); return }
        action(price > 0 ? `${names.player(who)} bought ${place} for ${formatMoney(price)}` : `${names.player(who)} received ${place}`, 'key', who, space)
        return
      }
      case 'PROPERTY_TRANSFERRED': {
        const space = num(p.space_index)
        const from = str(p.from_player_id), to = str(p.to_player_id)
        const text = `${space === null ? 'A property' : names.space(space)} went from ${from ? names.player(from) : 'the bank'} to ${to ? names.player(to) : 'the bank'}${p.mortgaged === true ? ' (mortgaged)' : ''}`
        const held = absorber as { item: ActionItem; kind: string } | null
        if (held && held.kind !== 'card') { absorb(held.item, e, text); return }
        action(text, 'plain', to, space)
        return
      }
      case 'RENT_PAID': {
        const from = String(p.from_player_id ?? ''), to = String(p.to_player_id ?? '')
        const space = num(p.space_index)
        action(`${names.player(from)} paid ${names.player(to)} ${formatMoney(num(p.amount) ?? 0)} rent${space === null ? '' : ` for ${names.space(space)}`}`, 'plain', from, space)
        return
      }
      case 'AUCTION_STARTED': {
        const who = str(p.initiator_player_id)
        action(`Auction opened for ${names.spaceKey(String(p.property_space ?? ''))}`, 'plain', who)
        return
      }
      case 'AUCTION_BID_PLACED': {
        const who = String(p.bidder_player_id ?? '')
        push({ kind: 'note', id, playerId: who, text: `${names.player(who)} bid ${formatMoney(num(p.bid_amount) ?? 0)}`, eventIds: [id] })
        return
      }
      case 'AUCTION_PLAYER_DROPPED': {
        const who = String(p.player_id ?? '')
        push({ kind: 'note', id, playerId: who, text: `${names.player(who)} dropped out of the auction`, eventIds: [id] })
        return
      }
      case 'AUCTION_ENDED': {
        const place = names.spaceKey(String(p.property_space ?? ''))
        const winner = str(p.winner_player_id)
        const bid = num(p.winning_bid)
        if (winner && bid !== null) {
          const row = action(`${names.player(winner)} won the auction for ${place} at ${formatMoney(bid)}`, 'key', winner)
          if (p.reason && p.reason !== 'SOLD') row.details.push(`Auction ended: ${humanize(String(p.reason))}`)
        }
        else action(`Auction for ${place} ended with no sale${p.reason === 'NO_BIDS' ? ' (no bids)' : p.reason ? ` (${humanize(String(p.reason)).toLowerCase()})` : ''}`, 'plain', null)
        return
      }
      case 'TRADE_PROPOSED':
      case 'TRADE_COUNTERED':
      case 'TRADE_ACCEPTED':
      case 'TRADE_REJECTED': {
        // The payload carries the current offer without its author. The actor is the
        // offerer for proposals and counters, and the receiver for accept and reject.
        const initiator = String(p.initiator_player_id ?? ''), counterparty = String(p.counterparty_player_id ?? '')
        const who = actor === initiator || actor === counterparty ? actor : null
        const other = who === null ? null : who === initiator ? counterparty : initiator
        const offerer = e.type === 'TRADE_PROPOSED' || e.type === 'TRADE_COUNTERED' ? who : other
        const receiver = offerer === null ? null : offerer === initiator ? counterparty : initiator
        const pair = `${names.player(initiator)} and ${names.player(counterparty)}`
        const verb = { TRADE_PROPOSED: 'proposed', TRADE_COUNTERED: 'countered', TRADE_ACCEPTED: 'accepted', TRADE_REJECTED: 'rejected' }[e.type]
        const text = who === null || other === null ? `Trade ${verb} between ${pair}`
          : e.type === 'TRADE_PROPOSED' ? `${names.player(who)} offered ${names.player(other)} a trade`
          : e.type === 'TRADE_COUNTERED' ? `${names.player(who)} countered with a new offer to ${names.player(other)}`
          : `${names.player(who)} ${verb} ${names.player(other)}’s offer`
        const item = action(text, e.type === 'TRADE_ACCEPTED' ? 'key' : 'plain', who)
        if (offerer !== null && receiver !== null) item.details.push(`${names.player(offerer)} gives: ${tradeBundle(p.offer, names)}`, `${names.player(receiver)} gives: ${tradeBundle(p.request, names)}`)
        else item.details.push(`Offer: ${tradeBundle(p.offer, names)}`, `Request: ${tradeBundle(p.request, names)}`)
        if (e.type === 'TRADE_ACCEPTED') absorber = { item, kind: 'trade' }
        return
      }
      case 'TRADE_EXPIRED':
        action(`Trade between ${names.player(String(p.initiator_player_id ?? ''))} and ${names.player(String(p.counterparty_player_id ?? ''))} expired`, 'plain', null)
        return
      case 'HOUSE_BUILT':
      case 'HOTEL_BUILT':
      case 'HOUSE_SOLD':
      case 'HOTEL_SOLD': {
        const who = String(p.player_id ?? ''), space = num(p.space_index), count = num(p.count) ?? 1
        const thing = e.type.startsWith('HOTEL') ? (count === 1 ? 'a hotel' : `${count} hotels`) : (count === 1 ? 'a house' : `${count} houses`)
        const built = e.type.endsWith('BUILT')
        action(`${names.player(who)} ${built ? 'built' : 'sold'} ${thing} on ${space === null ? 'a property' : names.space(space)}`, built ? 'key' : 'plain', who, space)
        return
      }
      case 'PROPERTY_MORTGAGED':
      case 'PROPERTY_UNMORTGAGED': {
        const who = String(p.player_id ?? ''), space = num(p.space_index)
        const place = space === null ? 'a property' : names.space(space)
        const amount = formatMoney(num(p.amount) ?? 0)
        action(e.type === 'PROPERTY_MORTGAGED' ? `${names.player(who)} mortgaged ${place} for ${amount}` : `${names.player(who)} paid off the mortgage on ${place} (${amount})`, 'plain', who, space)
        return
      }
      case 'CASH_CHANGED': {
        const reason = String(p.reason ?? '')
        const who = String(p.player_id ?? '')
        if (reason === 'BANKRUPTCY') { absorber = { item: action(`${names.player(who)} went bankrupt`, 'key', who), kind: 'bankrupt' }; return }
        const held = absorber as { item: ActionItem; kind: string } | null
        if (reason === 'BANKRUPTCY_ASSETS_TO_BANK' && held?.kind === 'bankrupt') { absorb(held.item, e, 'Remaining deeds returned to the bank'); return }
        const line = cashLine(e, names)
        const group = cash as GroupItem | null
        if (group) { group.lines.push(line); group.eventIds.push(id); group.summary = `${group.lines.length} cash changes`; return }
        const fresh: GroupItem = { kind: 'group', id, summary: line, lines: [line], eventIds: [id] }
        push(fresh)
        cash = fresh
        return
      }
      case 'GAME_ENDED': {
        const winner = str(p.winner_player_id)
        action(winner ? `${names.player(winner)} won the game${p.reason ? ` (${humanize(String(p.reason)).toLowerCase()})` : ''}` : 'Game over', 'key', winner)
        return
      }
      case 'LLM_DECISION_REQUESTED':
      case 'LLM_DECISION_RESPONSE':
      case 'LLM_PUBLIC_MESSAGE':
      case 'LLM_PRIVATE_THOUGHT': {
        const decisionId = str(p.decision_id)
        const playerId = str(p.player_id) ?? actor
        if (!decisionId) {
          // Public text with no decision stays public; private text with no decision is never shown as public.
          if (e.type === 'LLM_PUBLIC_MESSAGE') push({ kind: 'chat', id, playerId: playerId ?? '', text: String(p.message ?? ''), eventIds: [id] })
          else if (e.type === 'LLM_PRIVATE_THOUGHT') push({ kind: 'decision', id: `thought-${id}`, decisionId: '', playerId, decisionType: null, requested: false, response: null, messages: [], thoughts: [{ eventId: id, text: String(p.thought ?? '') }], eventIds: [id] })
          else push({ kind: 'unknown', id, type: e.type, label: humanize(e.type), payload: p, eventIds: [id] })
          return
        }
        let item = decisions.get(decisionId)
        if (!item) {
          item = { kind: 'decision', id: `decision-${decisionId}`, decisionId, playerId, decisionType: null, requested: false, response: null, messages: [], thoughts: [], eventIds: [] }
          decisions.set(decisionId, item)
          push(item)
        }
        item.eventIds.push(id)
        if (!item.playerId) item.playerId = playerId
        if (e.type === 'LLM_DECISION_REQUESTED') { item.requested = true; item.decisionType = str(p.decision_type); claimTurnPlayer(playerId, false) }
        else if (e.type === 'LLM_DECISION_RESPONSE') item.response = { eventId: id, actionName: String(p.action_name ?? ''), valid: p.valid === true, error: str(p.error) }
        else if (e.type === 'LLM_PUBLIC_MESSAGE') item.messages.push({ eventId: id, text: String(p.message ?? '') })
        else item.thoughts.push({ eventId: id, text: String(p.thought ?? '') })
        return
      }
      default:
        push({ kind: 'unknown', id, type: e.type, label: humanize(String(e.type)), payload: e.payload, eventIds: [id] })
    }
  })

  // Cash emitted before its action is attached now that every action exists.
  for (const [cashIndex, ownerIndex] of folded) {
    if (ownerIndex < cashIndex) continue
    const item = owners.get(ownerIndex)
    const e = list[cashIndex]
    if (item) {
      item.details.unshift(cashLine(e, names))
      item.eventIds.push(e.event_id)
    } else {
      // Defensive: the owner never became an item, so keep the cash visible on its own.
      const t = turns.find(x => x.turnIndex === e.turn_index) ?? turns[turns.length - 1]
      t?.items.push({ kind: 'group', id: e.event_id, summary: cashLine(e, names), lines: [cashLine(e, names)], eventIds: [e.event_id] })
    }
  }
  return turns.filter(t => t.started || t.items.length > 0)
}

/** True when an item has something for the given filter. Private thoughts never count as chat. */
export function itemMatches(item: ActivityItem, filter: ActivityFilter): boolean {
  if (filter === 'all') return true
  const chat = item.kind === 'chat' ? Boolean(item.text.trim()) : item.kind === 'decision' && item.messages.some(message => message.text.trim())
  if (filter === 'chat') return chat
  return item.kind !== 'chat' && item.kind !== 'decision'
}

export function filterActivity(turns: readonly ActivityTurn[], filter: ActivityFilter): ActivityTurn[] {
  if (filter === 'all') return turns as ActivityTurn[]
  return turns.map(t => ({ ...t, items: t.items.filter(i => itemMatches(i, filter)) })).filter(t => t.items.length > 0)
}

/**
 * The newest decision still waiting for an answer in the visible window, if any. Nothing
 * waits once the game has ended; the page also gates this on the job actually running.
 */
export function waitingDecisionId(turns: readonly ActivityTurn[]): string | null {
  for (let t = turns.length - 1; t >= 0; t--) {
    const items = turns[t].items
    for (let i = items.length - 1; i >= 0; i--) {
      const item = items[i]
      if (item.kind === 'action' && item.type === 'GAME_ENDED') return null
      if (item.kind !== 'decision' || !item.decisionId) continue
      return item.requested && !item.response ? item.decisionId : null
    }
  }
  return null
}

// Decision bundle helpers. Provider reasoning is the provider's own reasoning text from the
// raw response; it is separate from the LLM_PRIVATE_THOUGHT event and from tool arguments.

export type ProviderReasoning =
  | { kind: 'text'; text: string }
  /** The provider sent reasoning in a form with no readable text (encrypted or summary-less). */
  | { kind: 'unreadable' }
  | { kind: 'none' }

export function providerReasoning(response: unknown): ProviderReasoning {
  const choices = (response as { choices?: unknown } | null)?.choices
  const message = Array.isArray(choices) ? (choices[0] as { message?: Record<string, unknown> } | undefined)?.message : undefined
  if (!message) return { kind: 'none' }
  const direct = str(message.reasoning)
  if (direct && direct.trim()) return { kind: 'text', text: direct }
  const details = message.reasoning_details
  if (Array.isArray(details) && details.length) {
    const parts: string[] = []
    for (const d of details as Record<string, unknown>[]) {
      const text = str(d?.text) ?? str(d?.summary)
      if (text && text.trim()) parts.push(text)
    }
    return parts.length ? { kind: 'text', text: parts.join('\n\n') } : { kind: 'unreadable' }
  }
  return { kind: 'none' }
}

/** Per-attempt response identity. Sequence metadata describes the whole resolver outcome. */
export function returnedModel(attempt: DecisionAttempt | undefined): string | null {
  return str((attempt?.response as Record<string, unknown> | null | undefined)?.model)
}

export const CONDITION_TEXT: Record<string, string> = {
  standard: 'Standard request',
  same_model_without_private_thought: 'Recovery request to the same model, without asking for a private thought',
  fallback_without_private_thought: 'Recovery request to the configured fallback model, without asking for a private thought',
}

export function conditionText(condition: string | null | undefined): string {
  if (!condition) return 'Request type not recorded'
  return CONDITION_TEXT[condition] ?? humanize(condition)
}

export function attemptLabel(index: number): string {
  return index <= 0 ? 'First attempt' : `Retry ${index}`
}

export type AttemptView = {
  index: number
  label: string
  requestedModel: string | null
  returnedModel: string | null
  condition: string
  /** The request asked the model to skip the private thought, so none is expected. */
  withoutPrivateThought: boolean
  /** A different model than the seat's configured participant was requested. */
  usedFallbackModel: boolean
  errors: string[]
  reasoning: ProviderReasoning
}

export type DecisionView = {
  outcome: string
  /** A final action is recorded and it came from a model answer. */
  accepted: boolean
  /** The engine applied its deterministic default action; no model choice was used. */
  defaultActionApplied: boolean
  retried: boolean
  finalAction: string | null
  attempts: AttemptView[]
}

function actionName(value: unknown): string | null {
  if (!value || typeof value !== 'object') return str(value)
  const v = value as Record<string, unknown>
  return str(v.action) ?? str(v.name) ?? str(v.action_name)
}

/** Plain-language summary of a recorded decision bundle. `participantModel` is the seat's configured model. */
export function describeDecision(bundle: DecisionBundle, participantModel: string | null): DecisionView {
  const attempts = [...(bundle.attempts ?? [])].sort((a, b) => a.attempt_index - b.attempt_index).map((a): AttemptView => ({
    index: a.attempt_index,
    label: attemptLabel(a.attempt_index),
    requestedModel: str(a.requested_model),
    returnedModel: returnedModel(a),
    condition: conditionText(a.response_condition),
    withoutPrivateThought: Boolean(a.response_condition?.includes('without_private_thought')),
    usedFallbackModel: Boolean(participantModel && a.requested_model && a.requested_model !== participantModel),
    errors: [...(a.validation_errors ?? []), ...(a.error_reason && !(a.validation_errors ?? []).length ? [humanize(a.error_reason)] : [])],
    reasoning: providerReasoning(a.response),
  }))
  // Provisional response artifacts can exist before an infrastructure failure. Only
  // the canonical resolved decision record establishes that an action was applied.
  const applied = bundle.summary?.phase === 'decision_resolved' && bundle.final_action !== null && bundle.final_action !== undefined
  const defaultActionApplied = applied && bundle.fallback_used === true
  const retried = bundle.retry_used === true || attempts.length > 1
  const finalAction = applied ? actionName(bundle.final_action) : null
  const last = attempts[attempts.length - 1]
  const accepted = applied && !defaultActionApplied
  let outcome: string
  if (defaultActionApplied) outcome = `No valid model answer was accepted, so the engine applied its default action${bundle.fallback_reason ? ` (${humanize(bundle.fallback_reason).toLowerCase()})` : ''}. This is not a fallback model.`
  else if (!accepted) outcome = attempts.length ? `No accepted answer is recorded for this decision yet (${attempts.length} attempt${attempts.length === 1 ? '' : 's'} recorded).` : 'No attempts are recorded for this decision yet.'
  else if (!last) outcome = 'Accepted. The attempt records are not available.'
  else if (last.usedFallbackModel) outcome = `Accepted from the configured fallback model on ${last.label.toLowerCase()}.`
  else outcome = retried ? `Accepted on ${last.label.toLowerCase()}.` : 'Accepted on the first attempt.'
  return { outcome, accepted, defaultActionApplied, retried, finalAction, attempts }
}
