import { useEffect, useId, useMemo, useRef, useState } from 'react'
import {
  Activity, AlertCircle, ArrowDownRight, ArrowUpRight, BarChart3, CalendarDays, ChartNoAxesCombined,
  CheckCircle2, ChevronDown, CircleDollarSign, Database, Layers3, LayoutDashboard, Leaf, LoaderCircle,
  Menu, RefreshCw, ScanLine, Sprout, X,
} from 'lucide-react'
import {
  Area, AreaChart, Bar, BarChart, CartesianGrid, Cell, ResponsiveContainer, Tooltip, XAxis, YAxis,
} from 'recharts'
import projectData from 'virtual:project-data'
import { api } from './api.js'
import { availableValues, changeSelection, observationsInRange, selectionKey } from './series.js'

const pages = [
  ['overview', 'Dashboard Overview', LayoutDashboard],
  ['prediction', 'Price Prediction', ScanLine],
  ['history', 'Historical Analysis', ChartNoAxesCombined],
  ['comparison', 'Model Comparison', BarChart3],
  ['dataset', 'Dataset Overview', Database],
]
const labels = { vegetable: 'Vegetable', market: 'Market', price_type: 'Price type' }
const ranges = [[30, '30 days'], [90, '90 days'], [365, '1 year'], [0, 'All time']]
const displayNumber = new Intl.NumberFormat('en-LK', { maximumFractionDigits: 2 })
const currency = new Intl.NumberFormat('en-LK', { minimumFractionDigits: 2, maximumFractionDigits: 2 })
const dateFormat = new Intl.DateTimeFormat('en-GB', { day: 'numeric', month: 'short', year: 'numeric', timeZone: 'UTC' })
const label = value => value ? value[0].toUpperCase() + value.slice(1) : ''
const dateLabel = value => value ? dateFormat.format(new Date(value + 'T00:00:00Z')) : '—'
const readPage = () => pages.find(([id]) => '#' + id === location.hash)?.[0] || 'overview'
const idle = { value: null, pending: false, error: '' }

function useResource(load, key) {
  const [state, setState] = useState({ ...idle, key: undefined })
  useEffect(() => {
    if (key == null) return
    const controller = new AbortController()
    load(controller.signal).then(
      value => { if (!controller.signal.aborted) setState({ value, pending: false, error: '', key }) },
      error => { if (!controller.signal.aborted) setState({ value: null, pending: false, error: error.message, key }) },
    )
    return () => controller.abort()
  }, [key]) // The key contains every input to the request.
  if (key == null) return idle
  return state.key === key ? state : { ...idle, pending: true }
}

function Notice({ children, error = false, busy = false, retry }) {
  const Icon = error ? AlertCircle : busy ? LoaderCircle : Activity
  return <div className={'notice' + (error ? ' notice-error' : '')} role={error ? 'alert' : 'status'}>
    <Icon size={18} className={busy ? 'animate-spin' : undefined} />
    <span>{children}</span>
    {retry && <button type="button" className="retry" onClick={retry}><RefreshCw size={15} /> Retry</button>}
  </div>
}

function SeriesFields({ series, selection, onChange, disabled }) {
  const labelPrefix = useId()
  return <div className="fields grid gap-3 sm:grid-cols-3">
    {Object.entries(labels).map(([field, fieldLabel]) => (
      <label key={field}>
        <span id={labelPrefix + field}>{fieldLabel}</span>
        <div className="select-wrap">
          <select aria-labelledby={labelPrefix + field} disabled={!selection || disabled} value={selection?.[field] || ''}
            onChange={event => onChange(changeSelection(series, selection, field, event.target.value))}>
            {!selection && <option value="">Unavailable</option>}
            {selection && availableValues(series, selection, field).map(value =>
              <option key={value} value={value}>{label(value)}</option>)}
          </select>
          <ChevronDown size={16} aria-hidden="true" />
        </div>
      </label>
    ))}
  </div>
}

function ForecastCards({ forecast }) {
  const change = forecast?.predicted_change
  const cards = [
    ['Observed price', forecast ? currency.format(forecast.observed_price) : '—', forecast ? 'As of ' + dateLabel(forecast.observation_date) : 'Source observation', 'emerald', CircleDollarSign, 'LKR/kg'],
    ['Predicted price', forecast ? currency.format(forecast.forecast_price) : '—', 'Stacking ensemble estimate', 'teal', ChartNoAxesCombined, 'LKR/kg'],
    ['Predicted change', forecast ? (change > 0 ? '+' : '') + currency.format(change) : '—', 'From observed price', 'blue', change < 0 ? ArrowDownRight : ArrowUpRight, 'LKR/kg'],
    ['Forecast date', dateLabel(forecast?.forecast_date), '7 calendar days ahead', 'purple', CalendarDays, ''],
  ]
  return <div className="summary grid gap-4 sm:grid-cols-2 xl:grid-cols-4">
    {cards.map(([title, value, detail, color, Icon, unit]) => (
      <article className={'summary-card ' + color} key={title}>
        <div className="stat-top"><span>{title}</span><span className="stat-icon"><Icon size={19} /></span></div>
        <div className="stat-value">{value}{unit && forecast && <small>{unit}</small>}</div>
        <p>{detail}</p>
      </article>
    ))}
  </div>
}

function HistoryChart({ history, selection, onRetry }) {
  const [days, setDays] = useState(90)
  const gradient = useId()
  const observations = history.value?.observations
  const chart = useMemo(() => observationsInRange(observations || [], days).map(point => ({
    ...point, time: Date.parse(point.date + 'T00:00:00Z'),
  })), [observations, days])
  return <section className="panel chart-panel" aria-labelledby="historical-title">
    <div className="panel-heading chart-heading">
      <div><h2 id="historical-title">Historical price trend</h2>
        <p>{selection ? [selection.vegetable, label(selection.market), label(selection.price_type)].join(' · ') : 'Observed market prices'} · LKR/kg</p></div>
      <div className="segments" aria-label="History window">
        {ranges.map(([range, text]) => <button type="button" key={range} aria-pressed={range === days} onClick={() => setDays(range)}>{text}</button>)}
      </div>
    </div>
    {history.pending ? <Notice busy>Loading observed prices…</Notice> : history.error ? <Notice error retry={onRetry}>{history.error}</Notice> :
      chart.length ? <>
        <div className="chart" aria-label="Chart of historical observed prices">
          <ResponsiveContainer width="100%" height="100%" minWidth={0}>
            <AreaChart data={chart} margin={{ top: 14, right: 12, bottom: 4, left: 0 }}>
              <defs><linearGradient id={gradient} x1="0" x2="0" y1="0" y2="1">
                <stop offset="0%" stopColor="#14b88c" stopOpacity={0.26} /><stop offset="100%" stopColor="#14b88c" stopOpacity={0.02} />
              </linearGradient></defs>
              <CartesianGrid vertical={false} stroke="#e4eeea" strokeDasharray="4 5" />
              <XAxis type="number" dataKey="time" domain={['dataMin', 'dataMax']} scale="time" tickCount={5}
                tickFormatter={value => dateLabel(new Date(value).toISOString().slice(0, 10))}
                tick={{ fontSize: 11, fill: '#526960' }} minTickGap={22} axisLine={false} tickLine={false} />
              <YAxis width={50} axisLine={false} tickLine={false} tick={{ fontSize: 11, fill: '#526960' }} />
              <Tooltip labelFormatter={(_, payload) => dateLabel(payload[0]?.payload.date)}
                formatter={value => [currency.format(value) + ' LKR/kg', 'Observed price']}
                contentStyle={{ borderRadius: 12, borderColor: '#d8ebe2' }} />
              <Area dataKey="price" type="linear" stroke="#07966f" strokeWidth={2.6} fill={'url(#' + gradient + ')'}
                dot={chart.length === 1} activeDot={{ r: 5 }} isAnimationActive={false} />
            </AreaChart>
          </ResponsiveContainer>
        </div>
        <div className="chart-footer"><span><i /> Observed price</span><span>{displayNumber.format(chart.length)} observations · {dateLabel(chart[0].date)} – {dateLabel(chart.at(-1).date)}</span></div>
      </> : <Notice>{selection ? 'No observations in this date range.' : 'Choose an available series to view its history.'}</Notice>}
  </section>
}

function ModelSummary({ model, navigate }) {
  return <section className="panel model-summary">
    <span className="tile-icon"><Layers3 size={23} /></span>
    <h2>Stacking ensemble</h2>
    <p>{model.value?.model_name || 'Three base regressors feed a Ridge meta-model to estimate the seven-day price change.'}</p>
    {model.value && <ul>{model.value.base_order.map(name => <li key={name}>{name}</li>)}</ul>}
    {model.value && <p className="muted">{model.value.features.length} input features · {model.value.forecast_horizon_days}-day horizon</p>}
    {model.error && <p role="status">Live model details unavailable.</p>}
    <button type="button" className="button secondary" onClick={() => navigate('comparison')}>Compare models</button>
  </section>
}

const modelStyles = {
  'Stacking (Change)': ['Stacking', 'Stacking ensemble', '#07966f'],
  'Naive Baseline': ['Baseline', 'Naive baseline', '#94a3b8'],
  'Gradient Boosting (Change)': ['Boosting', 'Gradient Boosting', '#3278dd'],
  'XGBoost (Change)': ['Boosting', 'XGBoost', '#7258d6'],
  'Random Forest (Change)': ['Bagging', 'Random Forest', '#0e9bad'],
}
const metricLabels = { MAE: 'MAE', RMSE: 'RMSE', R2: 'R²' }

function Comparison() {
  const [metric, setMetric] = useState('MAE')
  const rows = projectData.evaluations.map(row => {
    const [family, name, color] = modelStyles[row.Model] || ['Model', row.Model, '#07966f']
    return { family, name, color, ...Object.fromEntries(Object.keys(metricLabels).map(key => [
      key, row[key]?.trim() && Number.isFinite(Number(row[key])) ? Number(row[key]) : null,
    ])) }
  })
  const metricValue = value => value == null ? 'Unavailable' : metric === 'R2' ? value.toFixed(3) : currency.format(value)
  return <>
    <section className="panel">
      <div className="panel-heading chart-heading"><div><h2>Evaluation results</h2>
        <p>{metric === 'R2' ? 'Higher R² is better.' : 'Lower error is better · LKR/kg'}</p></div>
        <div className="segments" aria-label="Evaluation metric">
          {Object.entries(metricLabels).map(([key, title]) => <button type="button" key={key} aria-pressed={metric === key} onClick={() => setMetric(key)}>{title}</button>)}
        </div>
      </div>
      {rows.some(row => row[metric] != null) ? <div className="chart">
        <ResponsiveContainer width="100%" height="100%" minWidth={0}>
          <BarChart data={rows.filter(row => row[metric] != null)} margin={{ top: 14, right: 8, bottom: 12, left: 0 }}>
            <CartesianGrid vertical={false} stroke="#e4eeea" strokeDasharray="4 5" />
            <XAxis dataKey="name" interval={0} tick={{ fontSize: 10, fill: '#526960' }} axisLine={false} tickLine={false} />
            <YAxis width={50} tick={{ fontSize: 11, fill: '#526960' }} axisLine={false} tickLine={false} />
            <Tooltip formatter={value => [metricValue(value) + (metric === 'R2' ? '' : ' LKR/kg'), metricLabels[metric]]} />
            <Bar dataKey={metric} radius={[7, 7, 0, 0]} maxBarSize={80} isAnimationActive={false}>
              {rows.filter(row => row[metric] != null).map(row => <Cell key={row.name} fill={row.color} />)}
            </Bar>
          </BarChart>
        </ResponsiveContainer>
      </div> : <Notice>No values available for this metric.</Notice>}
    </section>
    <section className="panel">
      <div className="panel-heading"><h2>Metrics by model</h2><p>Source: models/final_model_results.csv</p></div>
      <div className="table-scroll"><table><thead><tr><th>Model</th><th>Family</th><th>MAE (LKR/kg)</th><th>RMSE (LKR/kg)</th><th>R²</th></tr></thead><tbody>
        {rows.map(row => <tr key={row.name}><th scope="row">{row.name}</th><td>{row.family}</td>
          <td>{row.MAE?.toFixed(2) ?? '—'}</td><td>{row.RMSE?.toFixed(2) ?? '—'}</td><td>{row.R2?.toFixed(3) ?? '—'}</td></tr>)}
      </tbody></table></div>
    </section>
  </>
}

function Dataset() {
  const data = projectData.snapshot
  return <>
    <div className="summary grid gap-4 sm:grid-cols-2 xl:grid-cols-4">
      {[
        ['Observations', data.observations, Database, 'emerald'], ['Vegetables', data.vegetables.length, Sprout, 'teal'],
        ['Markets', data.markets.length, Layers3, 'blue'], ['Unique series', data.series, Activity, 'purple'],
      ].map(([title, value, Icon, color]) => <article className={'summary-card ' + color} key={title}>
        <div className="stat-top"><span>{title}</span><span className="stat-icon"><Icon size={19} /></span></div>
        <div className="stat-value">{displayNumber.format(value)}</div>
      </article>)}
    </div>
    <section className="panel">
      <div className="panel-heading"><h2>Snapshot coverage</h2><p>Source: dashboard/dashboard_data.csv</p></div>
      <div className="coverage grid gap-3 md:grid-cols-3">
        <div><strong>Observation dates</strong><span>{dateLabel(data.firstDate)} – {dateLabel(data.lastDate)}</span></div>
        <div><strong>Markets</strong><span>{data.markets.map(label).join(', ')}</span></div>
        <div><strong>Price types</strong><span>{data.priceTypes.map(label).join(', ')}</span></div>
      </div>
      <div className="table-scroll"><table><thead><tr><th>Vegetable</th><th>Observations</th><th>Markets</th><th>Price types</th></tr></thead><tbody>
        {data.vegetables.map(row => <tr key={row.name}><th scope="row">{row.name}</th><td>{displayNumber.format(row.observations)}</td><td>{row.markets.map(label).join(', ')}</td><td>{row.priceTypes.map(label).join(', ')}</td></tr>)}
      </tbody></table></div>
    </section>
  </>
}

export default function App() {
  const [page, setPage] = useState(readPage)
  const [mobileOpen, setMobileOpen] = useState(false)
  const [chosen, setChosen] = useState(null)
  const [refresh, setRefresh] = useState(0)
  const [historyRefresh, setHistoryRefresh] = useState(0)
  const [submission, setSubmission] = useState(null)
  const attempt = useRef(0)
  useEffect(() => {
    const onHash = () => { setPage(readPage()); setMobileOpen(false) }
    window.addEventListener('hashchange', onHash)
    return () => window.removeEventListener('hashchange', onHash)
  }, [])

  const options = useResource(api.options, refresh)
  const model = useResource(api.model, refresh)
  const series = options.value?.series || []
  const selection = series.find(row => selectionKey(row) === selectionKey(chosen))
    || series.find(row => row.vegetable === 'Beans' && row.market === 'pettah' && row.price_type === 'retail') || series[0]
  const key = selectionKey(selection)
  const shouldLoadHistory = page === 'overview' || page === 'history'
  const history = useResource(signal => api.history(selection, signal), key && shouldLoadHistory ? key + '|' + historyRefresh : null)
  const prediction = useResource(signal => api.predict(selection, signal),
    key && submission?.key === key ? key + '|' + submission.attempt : null)
  const forecast = prediction.value
  const navTitle = pages.find(([id]) => id === page)[1]

  function navigate(nextPage) {
    location.hash = nextPage
    setPage(nextPage)
    setMobileOpen(false)
    window.scrollTo({ top: 0, behavior: 'instant' })
  }

  function updateSelection(next) {
    setChosen(next)
    setSubmission(null)
  }

  function submit(event) {
    event.preventDefault()
    if (key) setSubmission({ key, attempt: ++attempt.current })
  }

  const controls = <SeriesFields series={series} selection={selection} onChange={updateSelection} />
  const retry = () => setRefresh(value => value + 1)
  const retryHistory = () => setHistoryRefresh(value => value + 1)
  const optionsStatus = options.pending ? <Notice busy>Loading available market series…</Notice> :
    options.error ? <Notice error retry={retry}>{options.error}</Notice> :
      !series.length ? <Notice>No series have complete forecast inputs.</Notice> : null
  const forecastStatus = prediction.pending ? <Notice busy>Running the stacking ensemble…</Notice> :
    prediction.error ? <Notice error>{prediction.error}</Notice> : forecast ?
      <div className="success" role="status"><CheckCircle2 size={17} /> Forecast generated for {forecast.vegetable} · {label(forecast.market)} · {label(forecast.price_type)}</div> : null

  return <div className="shell">
    {mobileOpen && <button className="sidebar-overlay" type="button" aria-label="Close navigation" onClick={() => setMobileOpen(false)} />}
    <aside id="primary-navigation" className={'sidebar' + (mobileOpen ? ' open' : '')}>
      <div className="brand"><div className="brand-icon"><Sprout size={24} /></div><div><strong>Harvest<span>IQ</span></strong><small>Sri Lanka Market Intelligence</small></div>
        <button className="mobile-close" type="button" aria-label="Close navigation" onClick={() => setMobileOpen(false)}><X size={21} /></button>
      </div>
      <nav aria-label="Dashboard sections">
        {pages.map(([id, title, Icon]) => <a href={'#' + id} key={id} aria-current={page === id ? 'page' : undefined}
          onClick={event => { event.preventDefault(); navigate(id) }}><Icon size={19} />{title}</a>)}
      </nav>
      <div className="sidebar-footer"><Leaf size={19} /><div><strong>Market price forecasting</strong></div></div>
    </aside>
    <main className="main">
      <header className="topbar"><div className="topbar-title">
        <button type="button" className="menu-button" aria-label="Open navigation" aria-expanded={mobileOpen} aria-controls="primary-navigation" onClick={() => setMobileOpen(true)}><Menu size={22} /></button>
        <span>{navTitle}</span></div>
        <div className={'connection' + (options.error ? ' offline' : options.pending ? ' connecting' : '')}><i />
          {options.error ? 'API unavailable' : options.pending ? 'Connecting to API' : 'API connected'}</div>
      </header>
      <div className="content">
        {page === 'overview' ? <>
          <section className="hero">
            <div className="hero-copy">
              <span className="hero-label"><Sprout size={17} /> SRI LANKAN MARKET ANALYTICS</span>
              <h1>Vegetable price intelligence</h1>
              <p>Explore market price trends and forecast vegetable prices</p>
            </div>
            <div className="hero-date"><CalendarDays size={19} /><div><small>Latest snapshot observation</small><strong>{dateLabel(model.value?.latest_snapshot_observation_date || projectData.snapshot.lastDate)}</strong></div></div>
          </section>
          {optionsStatus}
          <section className="panel selection-panel" aria-labelledby="selected-series">
            <form onSubmit={submit}>
              <div className="panel-heading"><h2 id="selected-series">Market selection</h2><p>Choose a series to view its history and generate a forecast.</p></div>
              <div className="selection-row">{controls}<button className="button primary" disabled={!selection || prediction.pending}><ScanLine size={18} /> Predict price</button></div>
            </form>
          </section>
          {forecastStatus}
          <ForecastCards forecast={forecast} />
          <div className="overview-bottom"><HistoryChart history={history} selection={selection} onRetry={retryHistory} /><ModelSummary model={model} navigate={navigate} /></div>
        </> : <>
          <div className="page-title"><h1>{navTitle}</h1><p>{{
            prediction: 'Generate one forecast seven calendar days after the latest complete observation.',
            history: 'Explore observed prices by vegetable, market, and price type.',
            comparison: 'Compare measured performance across the fitted models and the baseline.',
            dataset: 'Explore the snapshot behind the forecasting dashboard.',
          }[page]}</p></div>
          {page === 'prediction' && <>
            {optionsStatus}
            <section className="panel selection-panel"><form onSubmit={submit}>
              <div className="panel-heading"><h2>Choose a market series</h2><p>Select a vegetable, market, and price type to run the fitted ensemble.</p></div>
              <div className="selection-row">{controls}<button className="button primary" disabled={!selection || prediction.pending}><ScanLine size={18} /> Predict price</button></div>
            </form></section>
            {forecastStatus}
            <ForecastCards forecast={forecast} />
            <ModelSummary model={model} navigate={navigate} />
          </>}
          {page === 'history' && <>{optionsStatus}
            <section className="panel selection-panel"><div className="panel-heading"><h2>Filter observations</h2></div>{controls}</section>
            <HistoryChart history={history} selection={selection} onRetry={retryHistory} />
          </>}
          {page === 'comparison' && <Comparison />}
          {page === 'dataset' && <Dataset />}
        </>}
      </div>
    </main>
  </div>
}
