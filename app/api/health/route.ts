import { NextResponse } from 'next/server'
import fs from 'fs'
import path from 'path'

const DB_PATH = path.join(process.cwd(), 'data', 'chat_stats.json')

interface ChatStats {
  total_chats: number
  total_confidence: number
  start_time: string
  last_updated: string
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

// Detect if we're running on Vercel (cloud) — Ollama won't be available there
const IS_VERCEL = process.env.VERCEL === '1' || !!process.env.VERCEL_URL

async function checkOllamaHealth(): Promise<boolean> {
  // On Vercel, localhost:11434 (Ollama) is never available — skip the check
  if (IS_VERCEL) return false

  try {
    const controller = new AbortController()
    const timeoutId = setTimeout(() => controller.abort(), 3000)

    const response = await fetch('http://localhost:11434/api/tags', {
      signal: controller.signal,
    }).catch(() => null)

    clearTimeout(timeoutId)
    return response?.ok ?? false
  } catch {
    return false
  }
}

export async function GET() {
  const stats = loadStats()
  const ollamaAvailable = await checkOllamaHealth()
  const startTime = new Date(stats.start_time).getTime()
  const uptime = Math.floor((Date.now() - startTime) / 1000)

  return NextResponse.json({
    ollama_available: ollamaAvailable,
    database_ready: true,
    uptime: uptime,
    total_chats: stats.total_chats,
    average_confidence:
      stats.total_chats > 0 ? stats.total_confidence / stats.total_chats : 0,
    is_cloud: IS_VERCEL,
  })
}
