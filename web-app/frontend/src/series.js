export const dimensions = ['vegetable', 'market', 'price_type']

export const selectionKey = selection =>
  selection ? JSON.stringify(dimensions.map(field => selection[field])) : ''

export function availableValues(series, selection, field) {
  const dependencies = dimensions.slice(0, dimensions.indexOf(field))
  return [...new Set(series
    .filter(row => dependencies.every(key => row[key] === selection[key]))
    .map(row => row[field]))]
}

export function changeSelection(series, current, field, value) {
  const index = dimensions.indexOf(field)
  const compatible = series.filter(row =>
    row[field] === value && dimensions.slice(0, index).every(key => row[key] === current[key]))
  return compatible.find(row => dimensions.slice(index + 1).every(key => row[key] === current[key]))
    ?? compatible.find(row => row[dimensions[index + 1]] === current[dimensions[index + 1]])
    ?? compatible[0]
    ?? current
}

export function observationsInRange(observations, days) {
  if (!days || !observations.length) return observations
  const latest = new Date(observations.at(-1).date + 'T00:00:00Z')
  latest.setUTCDate(latest.getUTCDate() - days + 1)
  const cutoff = latest.toISOString().slice(0, 10)
  return observations.filter(row => row.date >= cutoff)
}

export function summarizeDataset(rows) {
  const groups = new Map()
  const dates = new Set()
  const markets = new Set()
  const priceTypes = new Set()
  const series = new Set()
  for (const row of rows) {
    dates.add(row.date)
    markets.add(row.market)
    priceTypes.add(row.price_type)
    series.add(selectionKey(row))
    if (!groups.has(row.vegetable)) groups.set(row.vegetable, { observations: 0, markets: new Set(), priceTypes: new Set() })
    const group = groups.get(row.vegetable)
    group.observations += 1
    group.markets.add(row.market)
    group.priceTypes.add(row.price_type)
  }
  const orderedDates = [...dates].sort()
  return {
    observations: rows.length,
    series: series.size,
    firstDate: orderedDates[0],
    lastDate: orderedDates.at(-1),
    markets: [...markets].sort(),
    priceTypes: [...priceTypes].sort(),
    vegetables: [...groups].sort(([first], [second]) => first.localeCompare(second)).map(([name, group]) => ({
      name, observations: group.observations, markets: [...group.markets].sort(), priceTypes: [...group.priceTypes].sort(),
    })),
  }
}
