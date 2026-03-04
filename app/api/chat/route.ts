import { NextRequest, NextResponse } from 'next/server'
import fs from 'fs'
import path from 'path'
import crypto from 'crypto'

const KB_PATH = path.join(process.cwd(), 'data', 'knowledge_base.json')
const DB_PATH = path.join(process.cwd(), 'data', 'chat_stats.json')
const LOGS_PATH = path.join(process.cwd(), 'data', 'chat_logs.json')

// Detect Vercel cloud environment — Ollama won't be available there
const IS_VERCEL = process.env.VERCEL === '1' || !!process.env.VERCEL_URL

interface KBEntry {
  id: number
  intent: string
  question?: string
  answer: string
  keywords: string[]
  category: string
  confidence?: number
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

// ── Knowledge Base ────────────────────────────────────────────────────────────

function loadKnowledgeBase(): KBEntry[] {
  try {
    if (fs.existsSync(KB_PATH)) {
      const data = fs.readFileSync(KB_PATH, 'utf-8')
      const parsed = JSON.parse(data)
      // Support both { answers: [] } and { entries: [] } formats
      return parsed.answers || parsed.entries || []
    }
  } catch (error) {
    console.error('Error loading knowledge base:', error)
  }
  return []
}

function findKBMatch(message: string): { entry: KBEntry; score: number } | null {
  const kb = loadKnowledgeBase()
  const lower = message.toLowerCase().trim()

  let bestMatch: KBEntry | null = null
  let bestScore = 0

  for (const entry of kb) {
    let score = 0

    // Keyword matching — each keyword hit counts
    for (const keyword of entry.keywords) {
      if (lower.includes(keyword.toLowerCase())) {
        // Longer keyword matches are more specific — reward them more
        score += 0.2 + keyword.length * 0.01
      }
    }

    // Question word overlap (if entry has a question field)
    if (entry.question) {
      const qWords = entry.question.toLowerCase().split(/\s+/)
      const mWords = lower.split(/\s+/)
      const overlap = qWords.filter(w => w.length > 2 && mWords.includes(w)).length
      score += (overlap / Math.max(qWords.length, 1)) * 0.5
    }

    if (score > bestScore) {
      bestScore = score
      bestMatch = entry
    }
  }

  return bestScore > 0.15 ? { entry: bestMatch!, score: bestScore } : null
}

// ── Stats / Logs ──────────────────────────────────────────────────────────────

function loadStats(): ChatStats {
  try {
    if (fs.existsSync(DB_PATH)) {
      const data = fs.readFileSync(DB_PATH, 'utf-8')
      return JSON.parse(data)
    }
  } catch { }
  return {
    total_chats: 0,
    total_confidence: 0,
    start_time: new Date().toISOString(),
    last_updated: new Date().toISOString(),
  }
}

function saveStats(stats: ChatStats) {
  // Vercel has a read-only filesystem — skip writes silently
  if (IS_VERCEL) return
  try {
    const dir = path.dirname(DB_PATH)
    if (!fs.existsSync(dir)) fs.mkdirSync(dir, { recursive: true })
    fs.writeFileSync(DB_PATH, JSON.stringify(stats, null, 2))
  } catch (error) {
    console.error('Error saving stats:', error)
  }
}

function saveChatLog(entry: ChatLog) {
  // Vercel has a read-only filesystem — skip writes silently
  if (IS_VERCEL) return
  try {
    const dir = path.dirname(LOGS_PATH)
    if (!fs.existsSync(dir)) fs.mkdirSync(dir, { recursive: true })
    let logs: ChatLog[] = []
    if (fs.existsSync(LOGS_PATH)) {
      logs = JSON.parse(fs.readFileSync(LOGS_PATH, 'utf-8'))
    }
    logs.push(entry)
    fs.writeFileSync(LOGS_PATH, JSON.stringify(logs, null, 2))
  } catch (error) {
    console.error('Error saving chat log:', error)
  }
}

// ── Ollama ────────────────────────────────────────────────────────────────────

async function queryOllama(message: string): Promise<{ response: string; confidence: number }> {
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

  if (!response.ok) throw new Error(`Ollama error: ${response.status}`)

  const data = await response.json()
  return {
    response: data.response || 'No response generated',
    confidence: 0.6,
  }
}

// ── Fallback response when neither KB nor Ollama can answer ───────────────────

function generateFallbackResponse(message: string): string {
  const lower = message.toLowerCase()

  if (/\b(hi|hello|hey|hii|helo|howdy|sup)\b/.test(lower)) {
    return "Hello! 👋 Welcome! I'm your AI assistant. How can I help you today? Feel free to ask me about pricing, accounts, features, or support!"
  }
  if (/\b(bye|goodbye|see you|farewell|later|cya)\b/.test(lower)) {
    return "Goodbye! 👋 It was great chatting with you. Feel free to come back anytime. Have a wonderful day!"
  }
  if (/\b(thanks|thank you|thx|ty|appreciate)\b/.test(lower)) {
    return "You're very welcome! 😊 Is there anything else I can help you with?"
  }
  if (/\b(how are you|how r u|you ok|how's it going)\b/.test(lower)) {
    return "I'm doing great, thank you for asking! 😊 Ready to help you with any questions you have."
  }
  if (/\b(price|cost|pricing|plan|how much|fee|subscription)\b/.test(lower)) {
    return "Our pricing starts at $29/month for Basic, $99/month for Professional, and $299/month for Enterprise. All plans include a 14-day free trial. Would you like more details?"
  }
  if (/\b(account|signup|register|sign up|create account|login)\b/.test(lower)) {
    return "You can create an account by visiting our website and clicking 'Sign Up'. It only takes a minute and includes a free trial — no credit card required!"
  }
  if (/\b(feature|capabilities|what can|what do you offer|services)\b/.test(lower)) {
    return "We offer AI-powered automation, analytics dashboards, API access, integrations, priority support, and more — depending on your plan. Would you like a full breakdown?"
  }
  if (/\b(help|support|contact|assist|problem|issue)\b/.test(lower)) {
    return "I'm here to help! 🙂 You can reach our support team at support@company.com or via live chat 24/7. What can I assist you with?"
  }
  if (/\b(security|data|privacy|safe|secure|encrypted)\b/.test(lower)) {
    return "We take security seriously. All data is encrypted with AES-256 at rest and TLS 1.3 in transit. We are SOC 2 Type II certified and GDPR compliant."
  }

  return "That's a great question! 🤔 I'm currently operating in knowledge-base mode. For complex queries, please contact our support team at support@company.com or try rephrasing your question — I may have a better answer for you!"
}

function generateSupportTicket(): string {
  return 'TKT-' + crypto.randomBytes(6).toString('hex').toUpperCase()
}

// ── Main Handler ──────────────────────────────────────────────────────────────

export async function POST(request: NextRequest) {
  try {
    const { message } = await request.json()

    if (!message || typeof message !== 'string') {
      return NextResponse.json({ error: 'Invalid message' }, { status: 400 })
    }

    let response: string
    let source: string
    let confidence: number
    let supportTicketId: string | undefined

    // 1. Try knowledge base first
    const kbResult = findKBMatch(message)

    if (kbResult) {
      response = kbResult.entry.answer
      source = 'knowledge_base'
      confidence = kbResult.entry.confidence ?? Math.min(0.5 + kbResult.score, 0.99)
    } else if (IS_VERCEL) {
      // 2a. On Vercel: use built-in fallback responses (no Ollama available)
      response = generateFallbackResponse(message)
      source = 'knowledge_base'
      confidence = 0.65
    } else {
      // 2b. Local: try Ollama
      try {
        const { response: aiResponse, confidence: aiConfidence } = await queryOllama(message)
        response = aiResponse
        confidence = aiConfidence
        source = 'ai'

        if (confidence < CONFIDENCE_THRESHOLD) {
          supportTicketId = generateSupportTicket()
          response = `Here's what I found: "${response}"\n\nA support agent will verify this. Support ticket: ${supportTicketId}`
          source = 'support'
        }
      } catch {
        // Ollama unavailable locally too — use fallback
        response = generateFallbackResponse(message)
        source = 'knowledge_base'
        confidence = 0.5
      }
    }

    // Update stats (no-op on Vercel)
    const stats = loadStats()
    stats.total_chats += 1
    stats.total_confidence += confidence
    stats.last_updated = new Date().toISOString()
    saveStats(stats)

    // Save chat log (no-op on Vercel)
    saveChatLog({
      timestamp: new Date().toISOString(),
      user_message: message,
      response,
      confidence,
      source,
      support_ticket_id: supportTicketId,
    })

    return NextResponse.json({
      response,
      confidence,
      source,
      support_ticket_id: supportTicketId,
    })
  } catch (error) {
    const errorMessage = error instanceof Error ? error.message : 'Unknown error'
    console.error('Chat error:', error)
    return NextResponse.json({ error: errorMessage }, { status: 500 })
  }
}
