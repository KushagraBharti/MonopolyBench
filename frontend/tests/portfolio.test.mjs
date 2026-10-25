import assert from 'node:assert/strict'
import { test } from 'node:test'
import { portfolioMetrics } from '../src/domain/monopoly/portfolio.ts'

const player = { player_id: 'p1', cash: 100 }
const deed = (overrides = {}) => ({ index: 6, kind: 'PROPERTY', name: 'Oriental Avenue', group: 'LIGHT_BLUE', price: 100, owner_id: 'p1', mortgaged: false, houses: 0, hotel: false, ...overrides })

test('book net worth includes building purchases and mortgage principal across all ownable kinds', () => {
  const result = portfolioMetrics(player, [
    deed({ houses: 2 }),
    deed({ index: 39, group: 'DARK_BLUE', price: 400, hotel: true }),
    deed({ index: 5, kind: 'RAILROAD', group: 'RAILROAD', price: 200, mortgaged: true }),
    deed({ index: 12, kind: 'UTILITY', group: 'UTILITY', price: 150, mortgaged: true }),
  ])
  assert.equal(result.deedsValue, 850)
  assert.equal(result.buildingValue, 1100)
  assert.equal(result.mortgageDebt, 175)
  assert.equal(result.netWorth, 1875)
  assert.deepEqual([result.deeds, result.houses, result.hotels, result.mortgaged], [4, 2, 1, 2])
})

test('ownership changes, bank transfers and non-deed spaces cannot leak into a portfolio', () => {
  const spaces = [deed(), deed({ owner_id: 'p2' }), deed({ owner_id: null }), deed({ kind: 'TAX', price: 500 })]
  assert.equal(portfolioMetrics(player, spaces).netWorth, 200)
  assert.equal(portfolioMetrics({ ...player, player_id: 'p2' }, spaces).deeds, 1)
})

test('zero and negative cash remain meaningful and an absent snapshot is unavailable', () => {
  assert.equal(portfolioMetrics({ ...player, cash: 0 }, []).netWorth, 0)
  assert.equal(portfolioMetrics({ ...player, cash: -20 }, []).netWorth, -20)
  assert.equal(portfolioMetrics(null, []).netWorth, null)
})

test('server estimates take priority including zero; invalid estimates fall back to labelled book value', () => {
  assert.equal(portfolioMetrics(player, [deed()], 0).netWorth, 0)
  assert.equal(portfolioMetrics(player, [deed()], 0).worthSource, 'server')
  assert.equal(portfolioMetrics(player, [deed()], NaN).netWorth, 200)
  assert.equal(portfolioMetrics(player, [deed()], NaN).worthSource, 'book')
})

test('missing prices or unknown building prices produce an unavailable estimate instead of an invented zero', () => {
  assert.equal(portfolioMetrics(player, [deed({ price: null })]).netWorth, null)
  assert.equal(portfolioMetrics(player, [deed({ houses: 1, group: 'FUTURE_GROUP' })]).netWorth, null)
})
