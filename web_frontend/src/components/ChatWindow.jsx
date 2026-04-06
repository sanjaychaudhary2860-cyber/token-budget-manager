import { useEffect, useRef } from 'react'
import MessageBubble from './MessageBubble'

function TypingIndicator() {
  return (
    <div className="flex gap-3 mb-4">
      <div className="w-7 h-7 rounded-lg flex items-center justify-center
                      text-xs flex-shrink-0"
           style={{ background: 'linear-gradient(135deg,#7c6af7,#4ecca3)' }}>
        ◆
      </div>
      <div className="px-4 py-3 rounded-2xl rounded-tl-sm"
           style={{ background: '#12121a', border: '1px solid #1a1a2e' }}>
        <div className="flex gap-1 items-center h-4">
          {[0,1,2].map(i => (
            <div key={i}
              className="typing-dot w-2 h-2 rounded-full"
              style={{ background: '#7c6af7' }} />
          ))}
        </div>
      </div>
    </div>
  )
}

function WelcomeScreen() {
  const hour = new Date().getHours()
  const greeting = hour < 12 ? 'Good morning!'
                 : hour < 17 ? 'Good afternoon!'
                 : hour < 21 ? 'Good evening!'
                 : 'Good night!'

  const suggestions = [
    'Aaj ka news batao',
    'Python mein code banao',
    '25 * 4 kitna hai?',
    'Machine learning explain karo',
  ]

  return (
    <div className="flex flex-col items-center justify-center h-full pb-20">
      <div className="text-4xl mb-4"
           style={{ filter: 'drop-shadow(0 0 20px rgba(124,106,247,0.5))' }}>
        ◆
      </div>
      <h1 className="text-2xl font-semibold mb-2" style={{ color: '#e8e8f0' }}>
        {greeting}
      </h1>
      <p className="text-sm mb-8" style={{ color: '#555577' }}>
        Dev Token Budget Manager — Powered by Groq & Claude
      </p>
      <div className="grid grid-cols-2 gap-3 max-w-lg w-full px-4">
        {suggestions.map((s, i) => (
          <div key={i}
            className="px-4 py-3 rounded-xl text-sm cursor-pointer
                       transition-all duration-200"
            style={{
              background: '#12121a',
              border: '1px solid #1a1a2e',
              color: '#8888aa'
            }}
            onMouseEnter={e => {
              e.currentTarget.style.borderColor = '#7c6af7'
              e.currentTarget.style.color = '#e8e8f0'
            }}
            onMouseLeave={e => {
              e.currentTarget.style.borderColor = '#1a1a2e'
              e.currentTarget.style.color = '#8888aa'
            }}>
            {s}
          </div>
        ))}
      </div>
    </div>
  )
}

export default function ChatWindow({ messages, isLoading }) {
  const bottomRef = useRef(null)

  useEffect(() => {
    bottomRef.current?.scrollIntoView({ behavior: 'smooth' })
  }, [messages, isLoading])

  return (
    <div className="flex-1 overflow-y-auto px-6 py-4"
         style={{ background: '#0a0a0f' }}>
      {messages.length === 0
        ? <WelcomeScreen />
        : <>
            {messages.map((m, i) => (
              <MessageBubble key={i} message={m} />
            ))}
            {isLoading && <TypingIndicator />}
          </>
      }
      <div ref={bottomRef} />
    </div>
  )
}