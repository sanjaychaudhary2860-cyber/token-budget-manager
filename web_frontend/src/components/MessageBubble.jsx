export default function MessageBubble({ message }) {
  const isUser = message.role === 'user'
  const model = message.model || ''
  const sources = message.sources || []

  const modelColor = model.includes('claude')
    ? '#ff9f43'
    : model.includes('70b')
    ? '#a29bfe'
    : '#4ecca3'

  const modelLabel = model.includes('claude')
    ? '🧠 Claude'
    : model.includes('70b')
    ? '🧠 Smart'
    : '⚡ Fast'

  // ================= USER MESSAGE =================
  if (isUser) {
    return (
      <div style={{ display: 'flex', justifyContent: 'flex-end', marginBottom: 16 }}>
        <div style={{ maxWidth: 480 }}>
          <div
            style={{
              padding: '12px 16px',
              borderRadius: 18,
              borderTopRightRadius: 4,
              background: 'linear-gradient(135deg,#7c6af7,#5544dd)',
              color: '#fff',
              fontSize: 14,
              lineHeight: 1.6
            }}
          >
            {message.content}
          </div>

          <div
            style={{
              textAlign: 'right',
              marginTop: 4,
              fontSize: 11,
              color: '#555577'
            }}
          >
            {message.time}
          </div>
        </div>
      </div>
    )
  }

  // ================= AI MESSAGE =================
  return (
    <div style={{ display: 'flex', gap: 12, marginBottom: 16 }}>
      {/* Avatar */}
      <div
        style={{
          width: 28,
          height: 28,
          borderRadius: 8,
          background: 'linear-gradient(135deg,#7c6af7,#4ecca3)',
          display: 'flex',
          alignItems: 'center',
          justifyContent: 'center',
          fontSize: 12,
          flexShrink: 0,
          marginTop: 4
        }}
      >
        ◆
      </div>

      <div style={{ flex: 1, maxWidth: 640 }}>
        
        {/* Model info */}
        <div style={{ display: 'flex', alignItems: 'center', gap: 8, marginBottom: 4 }}>
          <span style={{ fontSize: 12, fontWeight: 500, color: modelColor }}>
            {modelLabel}
          </span>

          {message.tokens > 0 && (
            <span style={{ fontSize: 11, color: '#444466' }}>
              {message.tokens} tokens
            </span>
          )}
        </div>

        {/* Message content */}
        <div
          style={{
            padding: '12px 16px',
            borderRadius: 18,
            borderTopLeftRadius: 4,
            background: '#12121a',
            border: '1px solid #1a1a2e',
            color: '#d0d0e0',
            fontSize: 14,
            lineHeight: 1.6,
            whiteSpace: 'pre-wrap'
          }}
        >
          {message.content}
        </div>

        {/* Sources */}
        {sources.length > 0 && (
          <div style={{ marginTop: 8 }}>
            <p style={{ fontSize: 11, color: '#444466', marginBottom: 6 }}>
              🔗 Sources
            </p>

            <div style={{ display: 'flex', flexWrap: 'wrap', gap: 8 }}>
              {sources.map((src, i) => (
                <a
                  key={i}
                  href={src.url}
                  target="_blank"
                  rel="noreferrer"
                  style={{
                    display: 'flex',
                    alignItems: 'center',
                    gap: 4,
                    padding: '4px 10px',
                    borderRadius: 8,
                    fontSize: 12,
                    background: '#1a1a2e',
                    border: '1px solid #2a2a3f',
                    color: '#7c6af7',
                    textDecoration: 'none'
                  }}
                >
                  🌐 {src.site || 'Link'} ↗
                </a>
              ))}
            </div>
          </div>
        )}

        {/* Time */}
        <div style={{ marginTop: 4, fontSize: 11, color: '#444466' }}>
          {message.time}
        </div>
      </div>
    </div>
  )
}