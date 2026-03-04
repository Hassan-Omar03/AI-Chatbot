'use client'

import { useState, useRef, useEffect } from 'react'
import { Button } from '@/components/ui/button'
import { Card } from '@/components/ui/card'
import { Input } from '@/components/ui/input'
import { ScrollArea } from '@/components/ui/scroll-area'
import { Badge } from '@/components/ui/badge'
import { AlertCircle, Send, CheckCircle, AlertTriangle, Loader } from 'lucide-react'
import { Alert, AlertDescription } from '@/components/ui/alert'

interface Message {
  id: string
  role: 'user' | 'assistant'
  content: string
  timestamp: Date
  confidence?: number
  source?: 'knowledge_base' | 'ai' | 'support'
  supportTicketId?: string
}

interface SystemStatus {
  ollama_available: boolean
  database_ready: boolean
  uptime: number
  total_chats: number
  average_confidence: number
  is_cloud?: boolean
}

export default function Home() {
  const [messages, setMessages] = useState<Message[]>([])
  const [inputValue, setInputValue] = useState('')
  const [isLoading, setIsLoading] = useState(false)
  const [systemStatus, setSystemStatus] = useState<SystemStatus | null>(null)
  const [error, setError] = useState<string | null>(null)
  const scrollRef = useRef<HTMLDivElement>(null)

  // Check system health on mount
  useEffect(() => {
    checkHealth()
    const interval = setInterval(checkHealth, 5000)
    return () => clearInterval(interval)
  }, [])

  // Auto-scroll to bottom
  useEffect(() => {
    if (scrollRef.current) {
      scrollRef.current.scrollIntoView({ behavior: 'smooth' })
    }
  }, [messages])

  async function checkHealth() {
    try {
      const response = await fetch('/api/health')
      if (response.ok) {
        const data = await response.json()
        setSystemStatus(data)
        setError(null)
      }
    } catch (err) {
      setError('Cannot connect to backend. Make sure the server is running.')
      console.error('Health check failed:', err)
    }
  }

  async function handleSendMessage(e: React.FormEvent) {
    e.preventDefault()
    if (!inputValue.trim() || isLoading) return

    // Add user message
    const userMessage: Message = {
      id: Date.now().toString(),
      role: 'user',
      content: inputValue,
      timestamp: new Date(),
      source: 'user' as any,
    }
    setMessages(prev => [...prev, userMessage])
    setInputValue('')
    setIsLoading(true)

    try {
      const response = await fetch('/api/chat', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ message: inputValue }),
      })

      if (!response.ok) {
        throw new Error(`API error: ${response.status}`)
      }

      const data = await response.json()

      const assistantMessage: Message = {
        id: (Date.now() + 1).toString(),
        role: 'assistant',
        content: data.response,
        timestamp: new Date(),
        confidence: data.confidence,
        source: data.source,
        supportTicketId: data.support_ticket_id,
      }

      setMessages(prev => [...prev, assistantMessage])
      setError(null)
    } catch (err) {
      const errorMessage = err instanceof Error ? err.message : 'Failed to send message'
      setError(errorMessage)
      console.error('Chat error:', err)
    } finally {
      setIsLoading(false)
    }
  }

  return (
    <div className="min-h-screen bg-gradient-to-b from-slate-900 to-slate-800 p-4">
      <div className="max-w-4xl mx-auto">
        {/* Header */}
        <div className="mb-6">
          <h1 className="text-3xl font-bold text-white mb-2">Local AI Assistant</h1>
          <p className="text-slate-400">Powered by Llama 3 running locally</p>
        </div>

        {/* System Status */}
        {systemStatus && (
          <Card className="mb-6 bg-slate-800 border-slate-700 p-4">
            <div className="grid grid-cols-2 md:grid-cols-5 gap-4 text-sm">
              <div>
                <div className="text-slate-400 text-xs">Status</div>
                <div className="flex items-center gap-2 mt-1">
                  {systemStatus.ollama_available ? (
                    <>
                      <CheckCircle className="w-4 h-4 text-green-500" />
                      <span className="text-green-400">Online</span>
                    </>
                  ) : systemStatus.is_cloud ? (
                    <>
                      <CheckCircle className="w-4 h-4 text-blue-400" />
                      <span className="text-blue-400">Cloud Mode</span>
                    </>
                  ) : (
                    <>
                      <AlertCircle className="w-4 h-4 text-red-500" />
                      <span className="text-red-400">Offline</span>
                    </>
                  )}
                </div>
              </div>
              <div>
                <div className="text-slate-400 text-xs">Chats</div>
                <div className="text-white mt-1 font-semibold">{systemStatus.total_chats}</div>
              </div>
              <div>
                <div className="text-slate-400 text-xs">Avg Confidence</div>
                <div className="text-white mt-1 font-semibold">
                  {(systemStatus.average_confidence * 100).toFixed(0)}%
                </div>
              </div>
              <div>
                <div className="text-slate-400 text-xs">Database</div>
                <div className="text-green-400 mt-1 font-semibold">
                  {systemStatus.database_ready ? 'Ready' : 'Error'}
                </div>
              </div>
              <div>
                <div className="text-slate-400 text-xs">Uptime</div>
                <div className="text-white mt-1 font-semibold">
                  {Math.floor(systemStatus.uptime / 60)}m
                </div>
              </div>
            </div>
          </Card>
        )}

        {/* Error Alert */}
        {error && (
          <Alert className="mb-6 bg-red-950 border-red-700">
            <AlertTriangle className="h-4 w-4 text-red-500" />
            <AlertDescription className="text-red-200">{error}</AlertDescription>
          </Alert>
        )}

        {/* Chat Messages */}
        <Card className="mb-6 bg-slate-800 border-slate-700 h-96 flex flex-col">
          <ScrollArea className="flex-1 p-4">
            <div className="space-y-4">
              {messages.length === 0 ? (
                <div className="h-full flex items-center justify-center text-slate-400 text-center">
                  <div>
                    <p className="mb-2">No messages yet</p>
                    <p className="text-sm">Type a message below to start chatting</p>
                  </div>
                </div>
              ) : (
                messages.map(msg => (
                  <div key={msg.id} className={`flex ${msg.role === 'user' ? 'justify-end' : 'justify-start'}`}>
                    <div
                      className={`max-w-xs lg:max-w-md px-4 py-2 rounded-lg ${msg.role === 'user'
                          ? 'bg-blue-600 text-white'
                          : 'bg-slate-700 text-slate-100'
                        }`}
                    >
                      <p className="text-sm">{msg.content}</p>
                      {msg.role === 'assistant' && (
                        <div className="mt-2 pt-2 border-t border-slate-600 text-xs space-y-1">
                          {msg.confidence !== undefined && (
                            <div className="flex items-center justify-between">
                              <span className="text-slate-400">Confidence:</span>
                              <span className={msg.confidence >= 0.7 ? 'text-green-400' : 'text-yellow-400'}>
                                {(msg.confidence * 100).toFixed(0)}%
                              </span>
                            </div>
                          )}
                          <div className="flex items-center justify-between">
                            <span className="text-slate-400">Source:</span>
                            <Badge variant="secondary" className="text-xs">
                              {msg.source === 'knowledge_base' ? 'KB' : msg.source === 'ai' ? 'AI' : 'Support'}
                            </Badge>
                          </div>
                          {msg.supportTicketId && (
                            <div className="text-slate-400">
                              Ticket: <span className="text-amber-400">{msg.supportTicketId}</span>
                            </div>
                          )}
                        </div>
                      )}
                    </div>
                  </div>
                ))
              )}
              {isLoading && (
                <div className="flex justify-start">
                  <div className="bg-slate-700 text-slate-100 px-4 py-2 rounded-lg flex items-center gap-2">
                    <Loader className="w-4 h-4 animate-spin" />
                    <span className="text-sm">Thinking...</span>
                  </div>
                </div>
              )}
              <div ref={scrollRef} />
            </div>
          </ScrollArea>
        </Card>

        {/* Input Form */}
        <form onSubmit={handleSendMessage} className="flex gap-2">
          <Input
            value={inputValue}
            onChange={e => setInputValue(e.target.value)}
            placeholder="Type your message..."
            disabled={isLoading}
            className="flex-1 bg-slate-700 border-slate-600 text-white placeholder-slate-400"
          />
          <Button
            type="submit"
            disabled={isLoading || !inputValue.trim()}
            className="bg-blue-600 hover:bg-blue-700"
          >
            <Send className="w-4 h-4" />
          </Button>
        </form>

        {/* Footer */}
        <div className="mt-6 text-center text-sm text-slate-400">
          <p>
            {systemStatus?.is_cloud
              ? 'Running in cloud mode · Powered by knowledge base'
              : 'This AI runs entirely on your local machine. No data is sent to external servers.'}
          </p>
        </div>
      </div>
    </div>
  )
}
