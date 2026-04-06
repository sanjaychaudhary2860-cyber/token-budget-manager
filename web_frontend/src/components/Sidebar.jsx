import { useState, useEffect } from 'react'
import TokenUsageBar from './TokenUsageBar'

const models = [
  { id: 'auto',   name: 'Auto',   desc: 'Smart switching',  color: '#4ecca3' },
  { id: 'groq',   name: 'Fast',   desc: 'Llama 3.1 8B',    color: '#7c6af7' },
  { id: 'claude', name: 'Smart',  desc: 'Claude Sonnet',    color: '#ff9f43' },
]

export default function Sidebar({ onClear, selectedModel, onModelChange }) {
  const [stats,   setStats]   = useState(null)
  const [history, setHistory] = useState([])

  useEffect(() => {
    fetchStats()
    fetchHistory()
    const t = setInterval(fetchStats, 30000)
    return () => clearInterval(t)
  }, [])

  async function fetchStats() {
    try {
      const r = await fetch('/api/stats')
      const d = await r.json()
      setStats(d)
    } catch {}
  }

  async function fetchHistory() {
    try {
      const r = await fetch('/api/history')
      const d = await r.json()
      setHistory(d.history || [])
    } catch {}
  }

  async function handleClear() {
    await fetch('/api/clear', { method: 'POST' })
    onClear()
  }

  return (
    <div className="flex flex-col h-full"
         style={{ width: 260, background: '#0d0d1a',
                  borderRight: '1px solid #1a1a2e' }}>

      {/* Logo */}
      <div className="p-5 pb-3"
           style={{ borderBottom: '1px solid #1a1a2e' }}>
        <div className="flex items-center gap-2 mb-1">
          <div className="w-7 h-7 rounded-lg flex items-center justify-center text-sm"
               style={{ background: 'linear-gradient(135deg,#7c6af7,#4ecca3)' }}>
            ◆
          </div>
          <span className="font-semibold text-sm" style={{ color: '#e8e8f0' }}>
            Dev Token Manager
          </span>
        </div>
        <p className="text-xs" style={{ color: '#555577', paddingLeft: 36 }}>
          AI Budget Assistant
        </p>
      </div>

      {/* New Chat */}
      <div className="p-3">
        <button onClick={handleClear}
          className="w-full py-2 px-3 rounded-xl text-sm font-medium
                     flex items-center gap-2 transition-all duration-200"
          style={{ background: '#1a1a2e', color: '#8888aa',
                   border: '1px solid #2a2a3f' }}
          onMouseEnter={e => {
            e.target.style.borderColor = '#7c6af7'
            e.target.style.color = '#7c6af7'
          }}
          onMouseLeave={e => {
            e.target.style.borderColor = '#2a2a3f'
            e.target.style.color = '#8888aa'
          }}>
          <span>＋</span> New Chat
        </button>
      </div>

      {/* Model Selector */}
      <div className="px-3 pb-3">
        <p className="text-xs mb-2 px-1" style={{ color: '#555577',
           letterSpacing: '0.1em' }}>MODEL</p>
        <div className="flex flex-col gap-1">
          {models.map(m => (
            <button key={m.id}
              onClick={() => onModelChange(m.id)}
              className="flex items-center gap-3 px-3 py-2 rounded-lg
                         text-left transition-all duration-200 text-sm"
              style={{
                background: selectedModel === m.id
                  ? 'rgba(124,106,247,0.1)' : 'transparent',
                border: `1px solid ${selectedModel === m.id
                  ? '#7c6af7' : 'transparent'}`,
                color: selectedModel === m.id ? '#e8e8f0' : '#666688'
              }}>
              <div className="w-2 h-2 rounded-full flex-shrink-0"
                   style={{ background: m.color }} />
              <div>
                <div className="font-medium">{m.name}</div>
                <div className="text-xs" style={{ color: '#555577' }}>
                  {m.desc}
                </div>
              </div>
            </button>
          ))}
        </div>
      </div>

      {/* Stats */}
      {stats && (
        <div className="px-3 pb-3">
          <p className="text-xs mb-2 px-1" style={{ color: '#555577',
             letterSpacing: '0.1em' }}>USAGE</p>
          <div className="rounded-xl p-3"
               style={{ background: '#1a1a2e', border: '1px solid #2a2a3f' }}>
            <TokenUsageBar today={stats.today} />
            <div className="grid grid-cols-2 gap-2 mt-2">
              {[
                { label: 'Saved', value: stats.savings?.tokens_saved || 0 },
                { label: 'Efficiency', value: `${stats.savings?.efficiency_percent || 0}%` }
              ].map(s => (
                <div key={s.label} className="rounded-lg p-2 text-center"
                     style={{ background: '#12121a' }}>
                  <div className="text-xs font-semibold"
                       style={{ color: '#4ecca3' }}>{s.value}</div>
                  <div className="text-xs" style={{ color: '#555577' }}>
                    {s.label}
                  </div>
                </div>
              ))}
            </div>
          </div>
        </div>
      )}

      {/* Recent History */}
      <div className="flex-1 overflow-y-auto px-3 pb-3">
        <p className="text-xs mb-2 px-1" style={{ color: '#555577',
           letterSpacing: '0.1em' }}>RECENT</p>
        <div className="flex flex-col gap-1">
          {history.filter(h => h.role === 'user').slice(-8).reverse().map((h, i) => (
            <div key={i}
              className="px-3 py-2 rounded-lg text-xs truncate cursor-pointer
                         transition-all duration-200"
              style={{ color: '#666688', background: 'transparent' }}
              onMouseEnter={e => {
                e.currentTarget.style.background = '#1a1a2e'
                e.currentTarget.style.color = '#e8e8f0'
              }}
              onMouseLeave={e => {
                e.currentTarget.style.background = 'transparent'
                e.currentTarget.style.color = '#666688'
              }}>
              {h.message.slice(0, 35)}...
            </div>
          ))}
        </div>
      </div>
    </div>
  )
}