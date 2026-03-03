import { NextRequest, NextResponse } from 'next/server'
import fs from 'fs'
import path from 'path'
import crypto from 'crypto'

const KB_PATH = path.join(process.cwd(), 'data', 'knowledge_base.json')
const DB_PATH = path.join(process.cwd(), 'data', 'chat_stats.json')
const LOGS_PATH = path.join(process.cwd(), 'data', 'chat_logs.json')

interface KBEntry {
  id: string
  question: string
  answer: string
  keywords: string[]
  category: string
  confidence: number
}

interface ChatStats {
  total_chats: number
  total_confidence: number
  start_time: string
  last_updated: string
}

interface ChatLog {
  timestamp: string
  user_message: string
  response: string
  confidence: number
  source: string
  support_ticket_id?: string
}

const CONFIDENCE_THRESHOLD = 0.7
const INTENT_KEYWORDS = {
  greeting: ['hello', 'hi', 'hey', 'greetings', 'good morning', 'good afternoon', 'good evening'],
  farewell: ['bye', 'goodbye', 'see you', 'farewell'],
  help: ['help', 'support', 'assist', 'help me', 'need help', 'i need', 'can you help'],
  pricing: ['price', 'cost', 'pricing', 'how much', 'fee', 'subscription'],
  features: ['features', 'capabilities', 'what can', 'feature'],
  account: ['account', 'login', 'signup', 'register', 'password', 'reset'],
  technical: ['error', 'bug', 'problem', 'issue', 'broken', 'not working'],
  feedback: ['feedback', 'suggest', 'improve', 'feature request'],
  general: ['what', 'how', 'why', 'when', 'where', 'who', 'tell me'],
  contact: ['contact', 'reach', 'phone', 'email', 'call'],
}

function loadKnowledgeBase(): KBEntry[] {
  try {
    if (fs.existsSync(KB_PATH)) {
      const data = fs.readFileSync(KB_PATH, 'utf-8')
      return JSON.parse(data).entries || []
    }
  } catch (error) {
    console.error('Error loading knowledge base:', error)
  }
  return []
}

function loadStats(): ChatStats {
  try {
    if (fs.existsSync(DB_PATH)) {
      const data = fs.readFileSync(DB_PATH, 'utf-8')
      return JSON.parse(data)
    }
  } catch (error) {
    console.error('Error loading stats:', error)
  }
  return {
    total_chats: 0,
    total_confidence: 0,
    start_time: new Date().toISOString(),
    last_updated: new Date().toISOString(),
  }
}

function saveStats(stats: ChatStats) {
  try {
    const dir = path.dirname(DB_PATH)
    if (!fs.existsSync(dir)) {
      fs.mkdirSync(dir, { recursive: true })
    }
    fs.writeFileSync(DB_PATH, JSON.stringify(stats, null, 2))
  } catch (error) {
    console.error('Error saving stats:', error)
  }
}

function saveChatLog(entry: ChatLog) {
  try {
    const dir = path.dirname(LOGS_PATH)
    if (!fs.existsSync(dir)) {
      fs.mkdirSync(dir, { recursive: true })
    }

    let logs: ChatLog[] = []
    if (fs.existsSync(LOGS_PATH)) {
      const data = fs.readFileSync(LOGS_PATH, 'utf-8')
      logs = JSON.parse(data)
    }
    logs.push(entry)
    fs.writeFileSync(LOGS_PATH, JSON.stringify(logs, null, 2))
  } catch (error) {
    console.error('Error saving chat log:', error)
  }
}

function detectIntent(message: string): { intent: string; confidence: number } {
  const lower = message.toLowerCase()
  let bestIntent = 'general'
  let bestScore = 0

  for (const [intent, keywords] of Object.entries(INTENT_KEYWORDS)) {
    const matches = keywords.filter(kw => lower.includes(kw)).length
    const score = matches / keywords.length
    if (score > bestScore) {
      bestScore = score
      bestIntent = intent
    }
  }

  return { intent: bestIntent, confidence: Math.max(bestScore, 0.3) }
}

function findKBMatch(message: string, intent: string): KBEntry | null {
  const kb = loadKnowledgeBase()
  const lower = message.toLowerCase()

  // Filter by intent first
  const filtered = kb.filter(entry => entry.category === intent || intent === 'general')

  // Score matches
  let bestMatch: KBEntry | null = null
  let bestScore = 0

  for (const entry of filtered) {
    let score = 0

    // Keyword matching
    for (const keyword of entry.keywords) {
      if (lower.includes(keyword.toLowerCase())) {
        score += 0.3
      }
    }

    // Question similarity (simple word overlap)
    const qWords = entry.question.toLowerCase().split(' ')
    const mWords = lower.split(' ')
    const overlap = qWords.filter(w => mWords.includes(w)).length
    score += (overlap / qWords.length) * 0.7

    if (score > bestScore) {
      bestScore = score
      bestMatch = entry
    }
  }

  return bestScore > 0.3 ? bestMatch : null
}

async function queryOllama(message: string): Promise<{ response: string; confidence: number }> {
  try {
    const controller = new AbortController()
    const timeoutId = setTimeout(() => controller.abort(), 30000)

    const response = await fetch('http://localhost:11434/api/generate', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        model: 'llama2',
        prompt: `Answer this question concisely in 1-2 sentences: ${message}`,
        stream: false,
        temperature: 0.7,
      }),
      signal: controller.signal,
    })

    clearTimeout(timeoutId)

    if (!response.ok) {
      throw new Error(`Ollama error: ${response.status}`)
    }

    const data = await response.json()
    return {
      response: data.response || 'No response generated',
      confidence: 0.6, // Default moderate confidence for AI responses
    }
  } catch (error) {
    console.error('Ollama error:', error)
    throw new Error('Failed to query Ollama. Make sure it is running on http://localhost:11434')
  }
}

function generateSupportTicket(): string {
  return 'TKT-' + crypto.randomBytes(6).toString('hex').toUpperCase()
}

export async function POST(request: NextRequest) {
  try {
    const { message } = await request.json()

    if (!message || typeof message !== 'string') {
      return NextResponse.json({ error: 'Invalid message' }, { status: 400 })
    }

    // 1. Detect intent
    const { intent, confidence: intentConfidence } = detectIntent(message)

    // 2. Check knowledge base FIRST
    const kbMatch = findKBMatch(message, intent)

    let response: string
    let source: string
    let confidence: number
    let supportTicketId: string | undefined

    if (kbMatch) {
      // Found in knowledge base - USE THIS
      response = kbMatch.answer
      source = 'knowledge_base'
      confidence = kbMatch.confidence
    } else {
      // Only try Ollama if KB didn't have answer
      let ollamaAvailable = false
      try {
        const { response: aiResponse, confidence: aiConfidence } = await queryOllama(message)
        response = aiResponse
        confidence = aiConfidence
        source = 'ai'
        ollamaAvailable = true

        // Check confidence threshold for AI responses
        if (confidence < CONFIDENCE_THRESHOLD) {
          supportTicketId = generateSupportTicket()
          response = `I'm not entirely confident in my answer. Here's what I found: "${response}"\n\nA support agent will verify this. Support ticket: ${supportTicketId}`
          source = 'support'
        }
      } catch (error) {
        // Ollama failed or unavailable
        supportTicketId = generateSupportTicket()
        response = `I couldn't find an answer in our knowledge base, and my AI service is currently unavailable. A support agent will help you shortly.\n\nSupport ticket: ${supportTicketId}`
        source = 'support'
        confidence = 0
      }
    }

    // Update stats
    const stats = loadStats()
    stats.total_chats += 1
    stats.total_confidence += confidence
    stats.last_updated = new Date().toISOString()
    saveStats(stats)

    // Save chat log
    saveChatLog({
      timestamp: new Date().toISOString(),
      user_message: message,
      response: response,
      confidence: confidence,
      source: source,
      support_ticket_id: supportTicketId,
    })

    return NextResponse.json({
      response: response,
      confidence: confidence,
      source: source,
      support_ticket_id: supportTicketId,
      intent: intent,
    })
  } catch (error) {
    const errorMessage = error instanceof Error ? error.message : 'Unknown error'
    console.error('Chat error:', error)
    return NextResponse.json(
      { error: errorMessage },
      { status: 500 }
    )
  }
}
