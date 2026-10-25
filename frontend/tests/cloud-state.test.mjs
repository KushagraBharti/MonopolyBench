import assert from 'node:assert/strict'
import { test } from 'node:test'
import { mergeCloudView, useCloudStore } from '../src/state/cloud.ts'

const event = (seq, run_id = 'run-a') => ({ seq, run_id, type: 'TURN_STARTED', payload: {} })
const message = (overrides = {}) => ({ job_id: 'job-a', run_id: 'run-a', commit_seq: 5, recovery_generation: 0, reset: false, snapshot: { run_id: 'run-a', turn_index: 2 }, events: [event(1)], ...overrides })

test('duplicate commits, lower commits and older recovery generations cannot roll back the view', () => {
  const current = mergeCloudView(undefined, message({ recovery_generation: 2 }))
  for (const envelope of [message({ recovery_generation: 2 }), message({ commit_seq: 4, recovery_generation: 2 }), message({ commit_seq: 999, recovery_generation: 1, reset: true })]) {
    assert.equal(mergeCloudView(current, envelope), current)
  }
})

test('a recovery generation boundary preserves append-only history and snapshot', () => {
  const old = mergeCloudView(undefined, message())
  const recovered = mergeCloudView(old, message({ commit_seq: 6, recovery_generation: 1, reset: true, snapshot: null, events: [event(3)] }))
  assert.equal(recovered.commit, 6)
  assert.equal(recovered.generation, 1)
  assert.deepEqual(recovered.events.map(e => e.seq), [1, 3])
  assert.equal(recovered.snapshot, old.snapshot)
  assert.equal(mergeCloudView(recovered, message({ commit_seq: 2, recovery_generation: 2 })), recovered)
})

test('null incremental snapshots retain the last committed board, events are ordered and deduplicated', () => {
  const old = mergeCloudView(undefined, message({ events: [event(1), event(2)] }))
  const next = mergeCloudView(old, message({ commit_seq: 6, snapshot: null, events: [event(3), event(2)] }))
  assert.equal(next.snapshot, old.snapshot)
  assert.deepEqual(next.events.map(e => e.seq), [1, 2, 3])
})

test('foreign run snapshots, events and run reassignment are rejected', () => {
  const old = mergeCloudView(undefined, message())
  for (const change of [{ snapshot: { run_id: 'run-b' } }, { events: [event(2, 'run-b')] }, { run_id: 'run-b', snapshot: null, events: [] }]) {
    assert.equal(mergeCloudView(old, message({ commit_seq: 6, ...change })), old)
  }
})

test('accepted-envelope signal and separate job caches prevent cross-panel stale updates', () => {
  useCloudStore.setState({ views: {} })
  assert.equal(useCloudStore.getState().receive(message()), true)
  assert.equal(useCloudStore.getState().receive(message()), false)
  assert.equal(useCloudStore.getState().receive(message({ job_id: 'job-b', run_id: 'run-b', snapshot: { run_id: 'run-b' }, events: [] })), true)
  assert.equal(useCloudStore.getState().views['job-a'].runId, 'run-a')
  assert.equal(useCloudStore.getState().views['job-b'].runId, 'run-b')
})

test('event window stays bounded without using arrival time for ordering', () => {
  const view = mergeCloudView(undefined, message({ events: Array.from({ length: 600 }, (_, i) => event(599 - i)) }))
  assert.equal(view.events.length, 500)
  assert.equal(view.events[0].seq, 100)
  assert.equal(view.events.at(-1).seq, 599)
})
