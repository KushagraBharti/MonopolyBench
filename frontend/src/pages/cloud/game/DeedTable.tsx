import type { CSSProperties } from 'react'
import type { StateSnapshot } from '@/net/contracts'
import { getGroupColor } from '@/domain/monopoly/colors'
import { useGameStore } from '@/state/store'
import { money, type Seat } from './gameModel'

/** Every ownable square from the accepted snapshot, owned or not. Keyboard equivalent of hovering the board. */
export function DeedTable({ snapshot, seats }: { snapshot: StateSnapshot; seats: Seat[] }) {
  const deedHighlight = useGameStore(s => s.ui.deedHighlight)
  const setDeedHighlight = useGameStore(s => s.setDeedHighlight)
  const seatOf = new Map(seats.map(s => [s.playerId, s]))
  const deeds = snapshot.board.filter(s => s.kind === 'PROPERTY' || s.kind === 'RAILROAD' || s.kind === 'UTILITY')
  return <table className="mbd-deeds">
    <caption className="cb-sr">All deeds at turn {snapshot.turn_index}</caption>
    <thead><tr><th scope="col">Deed</th><th scope="col">Price</th><th scope="col">Owner</th><th scope="col">Buildings</th><th scope="col">Mortgaged</th></tr></thead>
    <tbody>{deeds.map(space => {
      const owner = space.owner_id ? seatOf.get(space.owner_id) : undefined
      const color = space.kind === 'PROPERTY' ? getGroupColor(space.group) : space.kind === 'RAILROAD' ? '#1a1a1a' : '#8a96a3'
      return <tr key={space.index}>
        <th scope="row"><button type="button" aria-pressed={deedHighlight === space.index} onClick={() => setDeedHighlight(deedHighlight === space.index ? null : space.index)} title="Highlight on the board"><i style={{ background: color }} />{space.name}</button></th>
        <td>{space.price !== null ? money(space.price) : '—'}</td>
        <td>{owner ? <span className="mbd-owner" style={{ '--seat': owner.color } as CSSProperties}>{owner.label}</span> : space.owner_id ?? 'Bank'}</td>
        <td>{space.hotel ? 'Hotel' : space.houses > 0 ? `${space.houses} house${space.houses === 1 ? '' : 's'}` : '—'}</td>
        <td>{space.mortgaged ? 'Yes' : 'No'}</td>
      </tr>
    })}</tbody>
  </table>
}
