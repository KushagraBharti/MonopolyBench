import type { Player, Space } from '@/net/contracts'
import board from '../../../../contracts/data/board.json' with { type: 'json' }

const HOUSE_COSTS: Record<string, number> = board.house_cost_by_group
const OWNABLE = new Set<Space['kind']>(['PROPERTY', 'RAILROAD', 'UTILITY'])

/** Display accounting only. Never determines an outcome, legal action or available cash. */
export function portfolioMetrics(player: Player | null, spaces: Space[], serverEstimate?: number) {
  const owned = player ? spaces.filter(space => space.owner_id === player.player_id && OWNABLE.has(space.kind)) : []
  let deedsValue = 0
  let buildingValue = 0
  let mortgageDebt = 0
  let complete = Boolean(player)
  for (const space of owned) {
    if (space.price === null || !Number.isFinite(space.price)) complete = false
    const price = space.price ?? 0
    deedsValue += price
    if (space.mortgaged) mortgageDebt += Math.floor(price / 2)
    const cost = space.group ? HOUSE_COSTS[space.group] : undefined
    if ((space.houses || space.hotel) && cost === undefined) complete = false
    // A hotel includes the four houses exchanged for it plus the hotel purchase.
    buildingValue += (space.houses + (space.hotel ? 5 : 0)) * (cost ?? 0)
  }
  const serverProvided = typeof serverEstimate === 'number' && Number.isFinite(serverEstimate)
  return {
    deeds: owned.length,
    houses: owned.reduce((count, space) => count + space.houses, 0),
    hotels: owned.filter(space => space.hotel).length,
    mortgaged: owned.filter(space => space.mortgaged).length,
    deedsValue, buildingValue, mortgageDebt,
    netWorth: serverProvided ? serverEstimate : complete && player ? player.cash + deedsValue + buildingValue - mortgageDebt : null,
    worthSource: serverProvided ? 'server' as const : 'book' as const,
  }
}
