import assert from 'node:assert/strict'
import test from 'node:test'
import { availableValues, changeSelection, observationsInRange, summarizeDataset } from '../src/series.js'

const pettah = { vegetable: 'Beans', market: 'pettah', price_type: 'wholesale' }
const narahenpita = { vegetable: 'Beans', market: 'narahenpita', price_type: 'retail' }
const tomato = { vegetable: 'Tomato', market: 'pettah', price_type: 'wholesale' }
const series = [pettah, narahenpita, tomato]

test('dependent selectors preserve exact API labels and valid combinations', () => {
  assert.deepEqual(availableValues(series, pettah, 'market'), ['pettah', 'narahenpita'])
  assert.deepEqual(availableValues(series, narahenpita, 'price_type'), ['retail'])
  assert.equal(changeSelection(series, pettah, 'market', 'narahenpita'), narahenpita)
  assert.equal(changeSelection(series, pettah, 'vegetable', 'Tomato'), tomato)
})

test('historical ranges use calendar days relative to the selected series', () => {
  const rows = [{ date: '2026-11-17' }, { date: '2026-11-19' }, { date: '2026-11-20' }]
  assert.deepEqual(observationsInRange(rows, 2), rows.slice(1))
  assert.deepEqual(observationsInRange(rows, 0), rows)
  assert.deepEqual(observationsInRange([], 7), [])
})

test('dataset counts are derived from observations and exact series keys', () => {
  const stats = summarizeDataset([
    { ...pettah, date: '2026-11-20' }, { ...pettah, date: '2026-11-18' },
    { ...narahenpita, date: '2026-11-20' },
  ])
  assert.equal(stats.observations, 3)
  assert.equal(stats.series, 2)
  assert.equal(stats.firstDate, '2026-11-18')
  assert.deepEqual(stats.vegetables[0].markets, ['narahenpita', 'pettah'])
})
