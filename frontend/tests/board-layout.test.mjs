import assert from 'node:assert/strict'
import { test } from 'node:test'
import { getGridPosition, getCSSPosition, getBoardSide, getTokenAnchor, getTokenPlacement, getTokenZone, CORNER_PERCENT } from '../src/components/board/utils.ts'

test('all forty spaces occupy unique perimeter cells in authoritative index order', () => {
  const positions = Array.from({ length: 40 }, (_, i) => getGridPosition(i))
  assert.equal(new Set(positions.map(p => `${p.row},${p.col}`)).size, 40)
  assert.deepEqual([0, 10, 20, 30].map(getGridPosition), [{ row: 11, col: 11 }, { row: 11, col: 1 }, { row: 1, col: 1 }, { row: 1, col: 11 }])
  for (const p of positions) assert.ok(p.row === 1 || p.row === 11 || p.col === 1 || p.col === 11)
})

test('token positions use the same wider corner grid as the board', () => {
  for (let index = 0; index < 40; index++) {
    const p = getCSSPosition(index)
    assert.ok(p.x > 0 && p.x < 100 && p.y > 0 && p.y < 100)
  }
  assert.equal(getCSSPosition(20).x, CORNER_PERCENT / 2)
  assert.equal(getCSSPosition(20).y, CORNER_PERCENT / 2)
  assert.ok(getCSSPosition(1).x < getCSSPosition(0).x)
  assert.deepEqual([1, 11, 21, 31].map(getBoardSide), ['bottom', 'left', 'top', 'right'])
})

test('jail and visiting occupy different zones based only on snapshot jail status', () => {
  const jailed = getTokenAnchor(10, true)
  const visiting = getTokenAnchor(10, false)
  assert.notDeepEqual(jailed, visiting)
  for (const p of [jailed, visiting]) assert.ok(p.x > 0 && p.x < CORNER_PERCENT && p.y > 100 - CORNER_PERCENT && p.y < 100)
  assert.deepEqual(getTokenAnchor(5, true), getTokenAnchor(5, false))
})

test('one through four tokens at GO and jail leave room for active discs, rings and shadows', () => {
  for (const position of [0, 10]) for (const inJail of [false, true]) {
    for (let count = 1; count <= 4; count++) for (let index = 0; index < count; index++) {
      const p = getTokenPlacement(position, inJail, count, index)
      const visiting = position === 10 && !inJail
      const radius = ((visiting ? 3 : 3.6) / 2 + 0.6 + 0.5) * 1.1
      const x = p.x + p.dx, y = p.y + p.dy
      assert.ok(x - radius >= 0 && x + radius <= 100, `horizontal clipping: ${position}/${inJail}/${count}/${index}`)
      assert.ok(y - radius >= 0 && y + radius <= 100, `vertical clipping: ${position}/${inJail}/${count}/${index}`)
    }
  }
  assert.notEqual(getTokenZone(10, true), getTokenZone(10, false))
  assert.equal(getTokenZone(0, true), getTokenZone(0, false))
})
