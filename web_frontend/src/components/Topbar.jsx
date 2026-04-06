export default function Topbar({ stats }) {
  const tokens = stats?.today?.total_tokens || 0
  const req    = stats?.today?.request_count || 0

  return (
    <div className="flex items-center justify-between px-5 h-14 flex-shrink-0"
         style={{
           background: '#0d0d1a',
           borderBottom: '1px solid #1a1a2e'
         }}>
      <div className="flex items-center gap-3">
        <div className="w-2 h-2 rounded-full"
             style={{
               background: '#4ecca3',
               boxShadow: '0 0 8px #4ecca3',
               animation: 'pulse-slow 2s infinite'
             }} />
        <span className="text-sm font-medium" style={{ color: '#8888aa' }}>
          Dev AI
        </span>
      </div>

      <div className="flex items-center gap-4">
        <div className="flex items-center gap-2 px-3 py-1 rounded-lg"
             style={{ background: '#12121a', border: '1px solid #1a1a2e' }}>
          <span className="text-xs" style={{ color: '#555577' }}>⚡</span>
          <span className="text-xs font-medium" style={{ color: '#7c6af7' }}>
            {tokens.toLocaleString()} tokens
          </span>
        </div>
        <div className="flex items-center gap-2 px-3 py-1 rounded-lg"
             style={{ background: '#12121a', border: '1px solid #1a1a2e' }}>
          <span className="text-xs" style={{ color: '#555577' }}>📨</span>
          <span className="text-xs font-medium" style={{ color: '#4ecca3' }}>
            {req} req
          </span>
        </div>
      </div>
    </div>
  )
}