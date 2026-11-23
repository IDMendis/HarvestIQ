import { readFileSync } from 'node:fs'
import { fileURLToPath } from 'node:url'
import { defineConfig } from 'vite'
import react from '@vitejs/plugin-react'
import tailwindcss from '@tailwindcss/vite'
import { parse } from 'csv-parse/sync'
import { summarizeDataset } from './src/series.js'

const snapshot = fileURLToPath(new URL('../../dashboard/dashboard_data.csv', import.meta.url))
const evaluations = fileURLToPath(new URL('../../models/final_model_results.csv', import.meta.url))

function readCsv(path) {
  return parse(readFileSync(path, 'utf8'), { columns: true, bom: true, skip_empty_lines: true })
}

function projectData() {
  const id = 'virtual:project-data'
  return {
    name: 'project-data',
    resolveId(source) {
      if (source === id) return '\0' + id
    },
    load(source) {
      if (source !== '\0' + id) return
      this.addWatchFile(snapshot)
      this.addWatchFile(evaluations)
      return 'export default ' + JSON.stringify({
        snapshot: summarizeDataset(readCsv(snapshot)),
        evaluations: readCsv(evaluations),
      })
    },
  }
}

export default defineConfig({
  plugins: [react(), tailwindcss(), projectData()],
  build: {
    rollupOptions: {
      output: { manualChunks: { 'react-vendor': ['react', 'react-dom/client'], charts: ['recharts'] } },
    },
  },
  server: { host: 'localhost', port: 5173, strictPort: true },
})
