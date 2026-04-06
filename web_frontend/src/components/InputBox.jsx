import { useState, useRef, useEffect } from 'react'

export default function InputBox({ onSend, isLoading }) {
  const [value, setValue] = useState('')
  const textareaRef = useRef(null)

  useEffect(() => {
    if (textareaRef.current) {
      textareaRef.current.style.height = 'auto'
      textareaRef.current.style.height =
        Math.min(textareaRef.current.scrollHeight, 200) + 'px'
    }
  }, [value])

  function handleKey(e) {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault()
      handleSend()
    }
  }

  function handleSend() {
    const msg = value.trim()
    if (!msg || isLoading) return
    onSend(msg)
    setValue('')
  }

  return (
    <div className="px-6 pb-6 pt-3"
         style={{ background: '#0a0a0f' }}>
      <div className="max-w-3xl mx-auto">
        <div className="relative rounded-2xl transition-all duration-200"
             style={{
               background: '#12121a',
               border: '1px solid #2a2a3f',
             }}>
          <textarea
            ref={textareaRef}
            value={value}
            onChange={e => setValue(e.target.value)}
            onKeyDown={handleKey}
            placeholder="Kuch bhi poocho..."
            rows={1}
            className="w-full bg-transparent resize-none outline-none
                       text-sm leading-relaxed"
            style={{
              color: '#e8e8f0',
              padding: '14px 52px 14px 18px',
              maxHeight: 200,
              fontFamily: 'Inter, sans-serif',
            }}
          />
          <button
            onClick={handleSend}
            disabled={!value.trim() || isLoading}
            className="absolute right-3 bottom-3 w-8 h-8 rounded-xl
                       flex items-center justify-center text-sm
                       transition-all duration-200"
            style={{
              background: value.trim() && !isLoading
                ? 'linear-gradient(135deg,#7c6af7,#5544dd)'
                : '#1a1a2e',
              color: value.trim() && !isLoading ? '#fff' : '#444466',
              cursor: value.trim() && !isLoading ? 'pointer' : 'not-allowed'
            }}>
            ➤
          </button>
        </div>
        <p className="text-center text-xs mt-2" style={{ color: '#333355' }}>
          Enter to send • Shift+Enter for new line
        </p>
      </div>
    </div>
  )
}