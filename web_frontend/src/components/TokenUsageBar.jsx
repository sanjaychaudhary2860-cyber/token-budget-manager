export default function TokenUsageBar({ today }) {
  const used    = today?.request_count || 0
  const limit   = 1500
  const percent = Math.min(100, Math.round((used / limit) * 100))
  const color   = percent < 50 ? '#4ecca3'
                : percent < 80 ? '#ffd93d'
                : '#ff6b6b'

  return (
    <div className="px-4 py-2">
      <div className="flex justify-between text-xs mb-1"
           style={{ color: '#8888aa' }}>
        <span>Daily Usage</span>
        <span style={{ color }}>{percent}%</span>
      </div>
      <div className="w-full h-1 rounded-full"
           style={{ background: '#1a1a26' }}>
        <div className="h-1 rounded-full transition-all duration-500"
             style={{ width: `${percent}%`, background: color }} />
      </div>
      <div className="flex justify-between text-xs mt-1"
           style={{ color: '#555577' }}>
        <span>{today?.total_tokens || 0} tokens</span>
        <span>{used}/{limit} req</span>
      </div>
    </div>
  )
}