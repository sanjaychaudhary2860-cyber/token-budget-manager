import { useState, useEffect } from 'react'
import Sidebar    from './components/Sidebar'
import Topbar     from './components/Topbar'
import ChatWindow from './components/ChatWindow'
import InputBox   from './components/InputBox'

function getTime() {
  return new Date().toLocaleTimeString('en-US', {
    hour: '2-digit', minute: '2-digit'
  })
}

export default function App() {
  const [messages,      setMessages]      = useState([])
  const [isLoading,     setIsLoading]     = useState(false)
  const [stats,         setStats]         = useState(null)
  const [selectedModel, setSelectedModel] = useState('auto')

  useEffect(() => {
    fetchStats()
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

  async function sendMessage(text) {
    const userMsg = {
      role: 'user', content: text, time: getTime()
    }
    setMessages(prev => [...prev, userMsg])
    setIsLoading(true)

    try {
      const r = await fetch('/api/chat', {
        method:  'POST',
        headers: { 'Content-Type': 'application/json' },
        body:    JSON.stringify({ message: text })
      })
      const d = await r.json()

      const aiMsg = {
        role:    'assistant',
        content: d.response            || '❌ Koi jawab nahi aaya.',
        model:   d.model               || 'unknown',
        tokens:  d.stats?.total_tokens || 0,
        sources: d.sources             || [],
        time:    getTime()
      }
      setMessages(prev => [...prev, aiMsg])
      fetchStats()

    } catch {
      setMessages(prev => [...prev, {
        role:    'assistant',
        content: '❌ Server se connect nahi ho pa raha.',
        model:   'error',
        tokens:  0,
        sources: [],
        time:    getTime()
      }])
    } finally {
      setIsLoading(false)
    }
  }

  function clearChat() {
    setMessages([])
  }

  return (
    <div className="flex h-screen w-screen overflow-hidden"
         style={{ background: '#0a0a0f' }}>
      <Sidebar
        onClear={clearChat}
        selectedModel={selectedModel}
        onModelChange={setSelectedModel}
      />
      <div className="flex flex-col flex-1 overflow-hidden">
        <Topbar stats={stats} />
        <ChatWindow messages={messages} isLoading={isLoading} />
        <InputBox onSend={sendMessage} isLoading={isLoading} />
      </div>
    </div>
  )
}