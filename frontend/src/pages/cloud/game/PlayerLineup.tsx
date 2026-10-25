import type { CSSProperties } from 'react'
import type { Space, StateSnapshot } from '@/net/contracts'
import { LabLogo } from '@/components/LabLogo'
import { getGroupColor } from '@/domain/monopoly/colors'
import { GROUP_ORDER, SPECIAL_GROUP_ORDER, GROUP_TILE_INDEXES, getGroupDisplayName, normalizeGroupKey, type GroupKey } from '@/domain/monopoly/constants'
import { useGameStore } from '@/state/store'
import { money, type Seat } from './gameModel'

type Props = {
  seats: Seat[]
  snapshot: StateSnapshot | null
  /** Player whose turn it is, only while the game is live. */
  turnPlayerId: string | null
  /** Flag text for the turn player, e.g. "Turn holder" while paused. */
  turnLabel?: string
  winnerId: string | null
  selected: string | null
  onSelect: (playerId: string | null) => void
}

const GROUPS: GroupKey[] = [...GROUP_ORDER, ...SPECIAL_GROUP_ORDER]

function buildingText(space: Space) {
  if (space.hotel) return 'Hotel'
  if (space.houses > 0) return `${space.houses} house${space.houses === 1 ? '' : 's'}`
  return ''
}

/** Small deed swatch: group color, house pips or hotel, hatched when mortgaged. */
function Deed({ space }: { space: Space }) {
  const color = space.kind === 'PROPERTY' ? getGroupColor(space.group) : space.kind === 'RAILROAD' ? '#1a1a1a' : '#8a96a3'
  return <span className="mbg-deed" data-mortgaged={space.mortgaged || undefined} style={{ '--deed': color } as CSSProperties} title={[space.name, buildingText(space), space.mortgaged ? 'mortgaged' : ''].filter(Boolean).join(', ')}>
    {space.hotel ? <i className="mbg-deed-hotel" /> : space.houses > 0 ? <b>{space.houses}</b> : null}
  </span>
}

function Holdings({ seat, snapshot }: { seat: Seat; snapshot: StateSnapshot | null }) {
  const deedHighlight = useGameStore(s => s.ui.deedHighlight)
  const setDeedHighlight = useGameStore(s => s.setDeedHighlight)
  const player = seat.player
  const derivedWorth = snapshot?.derived?.net_worth_estimate_by_player?.[seat.playerId]
  const byGroup = new Map<GroupKey, Space[]>()
  for (const space of seat.holdings) {
    const key = normalizeGroupKey(space.group) ?? (space.kind === 'RAILROAD' ? 'RAILROAD' : space.kind === 'UTILITY' ? 'UTILITY' : null)
    if (!key) continue
    byGroup.set(key, [...(byGroup.get(key) ?? []), space])
  }
  const bankruptTo = player?.bankrupt_to ? snapshot?.players.find(p => p.player_id === player.bankrupt_to)?.name ?? player.bankrupt_to : null
  return <div className="mbg-holdings">
    <dl className="mbg-facts">
      <div><dt>Cash</dt><dd>{player ? money(player.cash) : '—'}</dd></div>
      <div><dt>Deeds</dt><dd>{seat.holdings.length}</dd></div>
      <div><dt>Mortgaged</dt><dd>{seat.holdings.filter(s => s.mortgaged).length}</dd></div>
      <div><dt>Jail cards</dt><dd>{player?.get_out_of_jail_cards ?? 0}</dd></div>
      {typeof derivedWorth === 'number' ? <div><dt>Net worth (server estimate)</dt><dd>{money(derivedWorth)}</dd></div> : null}
      {player?.in_jail ? <div><dt>In jail</dt><dd>{player.jail_turns} turn{player.jail_turns === 1 ? '' : 's'} served</dd></div> : null}
      {player?.bankrupt ? <div><dt>Bankrupt</dt><dd>{bankruptTo ? `to ${bankruptTo}` : 'to the bank'}</dd></div> : null}
    </dl>
    <p className="mbg-model-id"><code>{seat.model}</code></p>
    {seat.holdings.length === 0 ? <p className="mbg-muted">No deeds.</p> : <ul className="mbg-groups">
      {GROUPS.filter(g => byGroup.has(g)).map(group => {
        const owned = byGroup.get(group) ?? []
        return <li key={group}>
          <span className="mbg-group-head"><i style={{ background: group === 'RAILROAD' ? '#1a1a1a' : group === 'UTILITY' ? '#8a96a3' : getGroupColor(group) }} />{getGroupDisplayName(group)}<small>{owned.length} of {GROUP_TILE_INDEXES[group]?.length ?? owned.length}</small></span>
          <ul>{owned.map(space => <li key={space.index}>
            <button type="button" aria-pressed={deedHighlight === space.index} onClick={() => setDeedHighlight(deedHighlight === space.index ? null : space.index)}>
              <span>{space.name}</span>
              <span className="mbg-deed-state">{[buildingText(space), space.mortgaged ? 'Mortgaged' : ''].filter(Boolean).join(' · ')}</span>
            </button>
          </li>)}</ul>
        </li>
      })}
    </ul>}
  </div>
}

function deedSummary(seat: Seat) {
  const mortgaged = seat.holdings.filter(s => s.mortgaged).length
  const deeds = `${seat.holdings.length} deed${seat.holdings.length === 1 ? '' : 's'}`
  return mortgaged ? `${deeds}, ${mortgaged} mortgaged` : deeds
}

/**
 * All four seats stay visible as compact rows. The selected seat's holdings open in a
 * separate section below the roster that scrolls on its own, so no row is pushed away.
 */
export function PlayerLineup({ seats, snapshot, turnPlayerId, turnLabel = 'Turn', winnerId, selected, onSelect }: Props) {
  if (seats.length === 0) return <p className="mbg-muted">Waiting for players…</p>
  const open = seats.find(s => s.playerId === selected) ?? null
  return <div className="mbg-roster" data-detail={open ? true : undefined}>
    <ol className="mbg-lineup" aria-label="Players in seat order">
      {seats.map(seat => {
        const p = seat.player
        const isOpen = open?.playerId === seat.playerId
        const isTurn = turnPlayerId === seat.playerId
        return <li key={seat.playerId} className="mbg-seat" data-turn={isTurn || undefined} data-bankrupt={p?.bankrupt || undefined} data-open={isOpen || undefined} style={{ '--seat': seat.color } as CSSProperties}>
          <button type="button" className="mbg-seat-row" aria-expanded={isOpen} aria-controls={isOpen ? 'mbg-holdings' : undefined} onClick={() => onSelect(isOpen ? null : seat.playerId)}>
            <span className="mbg-seat-token"><LabLogo model={seat.model} decorative /></span>
            <span className="mbg-seat-main">
              <span className="mbg-seat-name">{seat.modelName}</span>
              <span className="mbg-seat-sub">Seat {seat.seat}{p?.name && p.name !== `Player ${seat.seat}` ? ` · ${p.name}` : ''}</span>
            </span>
            <span className="mbg-seat-cash">{p ? money(p.cash) : '—'}</span>
            <span className="mbg-seat-flags">
              {isTurn ? <span className="mbg-flag" data-kind="turn">{turnLabel}</span> : null}
              {winnerId === seat.playerId ? <span className="mbg-flag" data-kind="winner">Winner</span> : null}
              {p?.in_jail ? <span className="mbg-flag" data-kind="jail">In jail</span> : null}
              {p && p.get_out_of_jail_cards > 0 ? <span className="mbg-flag" title="Get out of jail free cards">Jail card ×{p.get_out_of_jail_cards}</span> : null}
              {p?.bankrupt ? <span className="mbg-flag" data-kind="out">Bankrupt</span> : null}
            </span>
            {/* Swatches are visual only; the summary carries the same facts for assistive tech. */}
            <span className="mbg-seat-summary">{seat.holdings.length ? deedSummary(seat) : 'No deeds'}</span>
            <span className="mbg-seat-deeds" aria-hidden="true">
              {seat.holdings.length ? seat.holdings.map(space => <Deed key={space.index} space={space} />) : <span className="mbg-muted">No deeds</span>}
            </span>
          </button>
        </li>
      })}
    </ol>
    {open ? <section id="mbg-holdings" className="mbg-detail" aria-label={`Seat ${open.seat} holdings`} style={{ '--seat': open.color } as CSSProperties}>
      <header className="mbg-detail-head">
        <h3>Seat {open.seat} · {open.modelName}</h3>
        <button type="button" className="mbg-detail-close" onClick={() => onSelect(null)}>Close</button>
      </header>
      <Holdings seat={open} snapshot={snapshot} />
    </section> : null}
  </div>
}
