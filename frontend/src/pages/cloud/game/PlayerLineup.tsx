import type { CSSProperties } from 'react'
import type { Space, StateSnapshot } from '@/net/contracts'
import { LabLogo } from '@/components/LabLogo'
import { getGroupColor } from '@/domain/monopoly/colors'
import { portfolioMetrics } from '@/domain/monopoly/portfolio'
import { useGameStore } from '@/state/store'
import { money, type Seat } from './gameModel'

type Props = {
  seats: Seat[]
  snapshot: StateSnapshot | null
  turnPlayerId: string | null
  turnLabel?: string
  winnerId: string | null
}

function buildingText(space: Space) {
  if (space.hotel) return 'Hotel'
  if (space.houses > 0) return `${space.houses} house${space.houses === 1 ? '' : 's'}`
  return ''
}

/** Visible deed name and state; clicking only highlights the authoritative board square. */
function PropertyChip({ space, selected, onSelect }: { space: Space; selected: boolean; onSelect: () => void }) {
  const color = space.kind === 'PROPERTY' ? getGroupColor(space.group) : space.kind === 'RAILROAD' ? '#1a1a1a' : '#8a96a3'
  const state = [buildingText(space), space.mortgaged ? 'Mortgaged' : ''].filter(Boolean).join(', ')
  return <li>
    <button type="button" className="mbg-property-chip" aria-pressed={selected}
      aria-label={`${space.name}${state ? `, ${state}` : ''}. Highlight on board`}
      data-mortgaged={space.mortgaged || undefined} style={{ '--deed': color } as CSSProperties} onClick={onSelect}>
      <span className="mbg-property-name">{space.name}</span>
      {state ? <span className="mbg-property-state">{state}</span> : null}
    </button>
  </li>
}

/** Every player's finances and possessions are visible without opening a card. */
export function PlayerLineup({ seats, snapshot, turnPlayerId, turnLabel = 'Turn', winnerId }: Props) {
  const deedHighlight = useGameStore(state => state.ui.deedHighlight)
  const setDeedHighlight = useGameStore(state => state.setDeedHighlight)
  if (seats.length === 0) return <p className="mbg-muted">Waiting for players…</p>
  const rows = seats.map(seat => seat.player?.bankrupt && !seat.holdings.length ? 'auto' : 'minmax(0, max-content)').join(' ')
  return <div className="mbg-roster">
    <ol className="mbg-lineup" aria-label="Players in seat order" style={{ '--seat-rows': rows } as CSSProperties}>
      {seats.map(seat => {
        const player = seat.player
        const metrics = portfolioMetrics(player, seat.holdings, snapshot?.derived?.net_worth_estimate_by_player?.[seat.playerId])
        const creditor = player?.bankrupt_to ? seats.find(other => other.playerId === player.bankrupt_to)?.label ?? player.bankrupt_to : 'the bank'
        return <li key={seat.playerId} className="mbg-seat" data-turn={turnPlayerId === seat.playerId || undefined}
          data-bankrupt={player?.bankrupt || undefined} style={{ '--seat': seat.color } as CSSProperties}>
          <header className="mbg-seat-header">
            <span className="mbg-seat-token"><LabLogo model={seat.model} decorative /></span>
            <div className="mbg-seat-main"><h3 className="mbg-seat-name">{seat.modelName}</h3><span className="mbg-seat-sub">Seat {seat.seat}</span></div>
            <div className="mbg-seat-flags">
              {turnPlayerId === seat.playerId ? <span className="mbg-flag" data-kind="turn">{turnLabel}</span> : null}
              {winnerId === seat.playerId ? <span className="mbg-flag" data-kind="winner">Winner</span> : null}
              {player?.in_jail ? <span className="mbg-flag" data-kind="jail">In jail</span> : null}
              {player?.bankrupt ? <span className="mbg-flag" data-kind="out">Bankrupt</span> : null}
            </div>
          </header>
          <dl className="mbg-seat-finances">
            <div><dt>Cash</dt><dd>{player ? money(player.cash) : '—'}</dd></div>
            <div><dt>Net worth <span>{metrics.worthSource === 'server' ? 'server estimate' : 'book value'}</span></dt><dd>{metrics.netWorth === null ? '—' : money(metrics.netWorth)}</dd></div>
          </dl>
          <p className="mbg-portfolio-summary">
            <span>{metrics.deeds} {metrics.deeds === 1 ? 'deed' : 'deeds'}</span>
            {metrics.houses ? <span>{metrics.houses} {metrics.houses === 1 ? 'house' : 'houses'}</span> : null}
            {metrics.hotels ? <span>{metrics.hotels} {metrics.hotels === 1 ? 'hotel' : 'hotels'}</span> : null}
            {metrics.mortgaged ? <span>{metrics.mortgaged} mortgaged</span> : null}
            {player?.get_out_of_jail_cards ? <span>{player.get_out_of_jail_cards} jail {player.get_out_of_jail_cards === 1 ? 'card' : 'cards'}</span> : null}
          </p>
          {seat.holdings.length ? <div className="mbg-property-scroll" tabIndex={0} role="region" aria-label={`${seat.label}, seat ${seat.seat} properties`}>
            <ul className="mbg-seat-properties">{seat.holdings.map(space => <PropertyChip key={space.index} space={space} selected={deedHighlight === space.index} onSelect={() => setDeedHighlight(deedHighlight === space.index ? null : space.index)} />)}</ul>
          </div> : <p className="mbg-empty-portfolio">{player?.bankrupt ? `Assets passed to ${creditor}.` : player ? 'No properties yet.' : 'Waiting for the first snapshot.'}</p>}
        </li>
      })}
    </ol>
    <p className="mbg-worth-note">Book value includes deeds and building purchase values, less mortgage principal. It isn’t cash available to spend.</p>
  </div>
}
