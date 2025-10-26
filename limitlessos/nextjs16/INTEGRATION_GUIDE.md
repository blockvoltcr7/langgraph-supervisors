# Backend Integration Guide - Next.js 16 to Python LangGraph

## Overview

This guide covers how the Next.js 16 frontend integrates with the Python LangGraph backend for the Limitless OS AI Sales Agent.

---

## Architecture Overview

```
Next.js 16 Frontend (Vercel)
    ↓ HTTPS
Python FastAPI Backend (Google Cloud Run)
    ↓
LangGraph Agents
    ↓
Supabase PostgreSQL (State Persistence)
```

---

## API Client Setup

### Base API Client

```typescript
// lib/api/langgraph.ts

interface LangGraphConfig {
  apiUrl: string
  apiKey: string
}

class LangGraphClient {
  private config: LangGraphConfig
  
  constructor(config: LangGraphConfig) {
    this.config = config
  }
  
  private async fetch(endpoint: string, options: RequestInit = {}) {
    const url = `${this.config.apiUrl}${endpoint}`
    
    const response = await fetch(url, {
      ...options,
      headers: {
        'Content-Type': 'application/json',
        'Authorization': `Bearer ${this.config.apiKey}`,
        ...options.headers,
      },
    })
    
    if (!response.ok) {
      throw new Error(`API Error: ${response.statusText}`)
    }
    
    return response
  }
  
  // Chat API
  async sendMessage(params: {
    message: string
    threadId: string | null
    campaignCode: string
    instagramHandle?: string
  }) {
    return this.fetch('/chat', {
      method: 'POST',
      body: JSON.stringify(params),
    })
  }
  
  // Streaming Chat API
  async streamMessage(params: {
    message: string
    threadId: string | null
    campaignCode: string
    instagramHandle?: string
  }) {
    return this.fetch('/chat/stream', {
      method: 'POST',
      body: JSON.stringify(params),
    })
  }
  
  // Get conversation state
  async getState(threadId: string) {
    return this.fetch(`/state/${threadId}`, {
      method: 'GET',
    })
  }
  
  // Get conversation history
  async getHistory(threadId: string) {
    return this.fetch(`/history/${threadId}`, {
      method: 'GET',
    })
  }
}

// Singleton instance
export const langGraphClient = new LangGraphClient({
  apiUrl: process.env.LANGGRAPH_API_URL!,
  apiKey: process.env.LANGGRAPH_API_KEY!,
})
```

---

## API Routes

### 1. Streaming Chat Route

```typescript
// app/api/chat/route.ts

import { langGraphClient } from '@/lib/api/langgraph'
import { createClient } from '@/lib/supabase/server'
import { NextRequest, NextResponse } from 'next/server'

export const runtime = 'nodejs' // Use Node.js runtime (not edge)

export async function POST(request: NextRequest) {
  try {
    const supabase = await createClient()
    
    // Verify user authentication (optional for leads, required for dashboard)
    const { data: { user }, error: authError } = await supabase.auth.getUser()
    
    const body = await request.json()
    const { message, threadId, campaignCode, instagramHandle } = body
    
    // Validate campaign code
    const { data: campaign, error: campaignError } = await supabase
      .from('campaigns')
      .select('*')
      .eq('code', campaignCode)
      .eq('is_active', true)
      .single()
    
    if (campaignError || !campaign) {
      return NextResponse.json(
        { error: 'Invalid campaign code' },
        { status: 400 }
      )
    }
    
    // Call LangGraph backend with streaming
    const response = await langGraphClient.streamMessage({
      message,
      threadId,
      campaignCode,
      instagramHandle,
    })
    
    // Stream the response back to client
    // The response body is a ReadableStream
    return new Response(response.body, {
      headers: {
        'Content-Type': 'text/event-stream',
        'Cache-Control': 'no-cache',
        'Connection': 'keep-alive',
      },
    })
  } catch (error: any) {
    console.error('Chat API Error:', error)
    return NextResponse.json(
      { error: error.message || 'Internal server error' },
      { status: 500 }
    )
  }
}
```

### 2. State Retrieval Route

```typescript
// app/api/state/[thread_id]/route.ts

import { langGraphClient } from '@/lib/api/langgraph'
import { NextRequest, NextResponse } from 'next/server'

interface RouteContext {
  params: Promise<{
    thread_id: string
  }>
}

export async function GET(
  request: NextRequest,
  context: RouteContext
) {
  try {
    const { thread_id } = await context.params
    
    const response = await langGraphClient.getState(thread_id)
    const state = await response.json()
    
    return NextResponse.json(state)
  } catch (error: any) {
    console.error('State API Error:', error)
    return NextResponse.json(
      { error: error.message || 'Failed to fetch state' },
      { status: 500 }
    )
  }
}
```

### 3. History Retrieval Route

```typescript
// app/api/history/[thread_id]/route.ts

import { langGraphClient } from '@/lib/api/langgraph'
import { NextRequest, NextResponse } from 'next/server'

interface RouteContext {
  params: Promise<{
    thread_id: string
  }>
}

export async function GET(
  request: NextRequest,
  context: RouteContext
) {
  try {
    const { thread_id } = await context.params
    
    const response = await langGraphClient.getHistory(thread_id)
    const history = await response.json()
    
    return NextResponse.json(history)
  } catch (error: any) {
    console.error('History API Error:', error)
    return NextResponse.json(
      { error: error.message || 'Failed to fetch history' },
      { status: 500 }
    )
  }
}
```

---

## Frontend Components

### Chat Interface with Streaming

```typescript
// components/chat/chat-interface.tsx

'use client'

import { useChat } from 'ai/react'
import { useEffect, useState } from 'react'
import { MessageList } from './message-list'
import { MessageInput } from './message-input'

interface ChatInterfaceProps {
  campaignCode: string
  initialHandle?: string
}

export function ChatInterface({ campaignCode, initialHandle }: ChatInterfaceProps) {
  const [threadId, setThreadId] = useState<string | null>(null)
  const [instagramHandle, setInstagramHandle] = useState(initialHandle || '')
  const [isStarted, setIsStarted] = useState(false)
  
  const { messages, input, handleInputChange, handleSubmit, isLoading, error } = useChat({
    api: '/api/chat',
    body: {
      threadId,
      campaignCode,
      instagramHandle: isStarted ? instagramHandle : undefined,
    },
    onResponse: (response) => {
      // Extract thread_id from response headers if present
      const newThreadId = response.headers.get('X-Thread-ID')
      if (newThreadId && !threadId) {
        setThreadId(newThreadId)
      }
    },
    onFinish: (message) => {
      console.log('Message finished:', message)
    },
    onError: (error) => {
      console.error('Chat error:', error)
    },
  })
  
  const handleStart = (handle: string) => {
    setInstagramHandle(handle)
    setIsStarted(true)
  }
  
  if (!isStarted) {
    return (
      <InstagramHandlePrompt 
        onSubmit={handleStart}
        campaignCode={campaignCode}
      />
    )
  }
  
  return (
    <div className="flex flex-col h-screen bg-gray-50">
      <ChatHeader 
        campaignCode={campaignCode}
        instagramHandle={instagramHandle}
      />
      
      <MessageList 
        messages={messages}
        isLoading={isLoading}
      />
      
      {error && (
        <div className="bg-red-50 border border-red-200 text-red-800 px-4 py-3 rounded-lg m-4">
          <p className="text-sm">Error: {error.message}</p>
        </div>
      )}
      
      <MessageInput 
        input={input}
        handleInputChange={handleInputChange}
        handleSubmit={handleSubmit}
        isLoading={isLoading}
        disabled={isLoading}
      />
    </div>
  )
}
```

### Instagram Handle Prompt

```typescript
// components/chat/instagram-handle-prompt.tsx

'use client'

import { useState } from 'react'
import { Button } from '@/components/ui/button'
import { Input } from '@/components/ui/input'

interface InstagramHandlePromptProps {
  onSubmit: (handle: string) => void
  campaignCode: string
}

export function InstagramHandlePrompt({ onSubmit, campaignCode }: InstagramHandlePromptProps) {
  const [handle, setHandle] = useState('')
  
  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault()
    if (handle.trim()) {
      onSubmit(handle.trim())
    }
  }
  
  return (
    <div className="flex flex-col items-center justify-center min-h-screen bg-gradient-to-br from-purple-50 to-blue-50 p-4">
      <div className="max-w-md w-full bg-white rounded-xl shadow-lg p-8">
        <div className="text-center mb-8">
          <h1 className="text-3xl font-bold text-gray-900 mb-2">
            Welcome to Limitless OS
          </h1>
          <p className="text-gray-600">
            Enter your Instagram handle to get started
          </p>
        </div>
        
        <form onSubmit={handleSubmit} className="space-y-4">
          <div>
            <label htmlFor="instagram" className="block text-sm font-medium text-gray-700 mb-2">
              Instagram Handle
            </label>
            <div className="relative">
              <span className="absolute inset-y-0 left-0 flex items-center pl-3 text-gray-500">
                @
              </span>
              <Input
                id="instagram"
                type="text"
                value={handle}
                onChange={(e) => setHandle(e.target.value)}
                placeholder="yourhandle"
                className="pl-8"
                required
              />
            </div>
          </div>
          
          <Button type="submit" className="w-full" disabled={!handle.trim()}>
            Start Chat
          </Button>
        </form>
        
        <div className="mt-6 text-center">
          <p className="text-xs text-gray-500">
            Campaign Code: <span className="font-mono">{campaignCode}</span>
          </p>
        </div>
      </div>
    </div>
  )
}
```

### Message List

```typescript
// components/chat/message-list.tsx

'use client'

import { useEffect, useRef } from 'react'
import { Message } from 'ai'
import { Avatar } from '@/components/ui/avatar'
import { cn } from '@/lib/utils'

interface MessageListProps {
  messages: Message[]
  isLoading: boolean
}

export function MessageList({ messages, isLoading }: MessageListProps) {
  const bottomRef = useRef<HTMLDivElement>(null)
  
  useEffect(() => {
    bottomRef.current?.scrollIntoView({ behavior: 'smooth' })
  }, [messages])
  
  return (
    <div className="flex-1 overflow-y-auto p-4 space-y-4">
      {messages.length === 0 && (
        <div className="flex items-center justify-center h-full">
          <p className="text-gray-500">
            Send a message to start the conversation
          </p>
        </div>
      )}
      
      {messages.map((message) => (
        <div
          key={message.id}
          className={cn(
            'flex gap-3',
            message.role === 'user' ? 'justify-end' : 'justify-start'
          )}
        >
          {message.role === 'assistant' && (
            <Avatar className="h-8 w-8">
              <div className="bg-purple-500 h-full w-full flex items-center justify-center text-white text-sm">
                AI
              </div>
            </Avatar>
          )}
          
          <div
            className={cn(
              'max-w-[70%] rounded-lg px-4 py-2',
              message.role === 'user'
                ? 'bg-purple-500 text-white'
                : 'bg-gray-100 text-gray-900'
            )}
          >
            <p className="text-sm whitespace-pre-wrap">{message.content}</p>
          </div>
          
          {message.role === 'user' && (
            <Avatar className="h-8 w-8">
              <div className="bg-gray-300 h-full w-full flex items-center justify-center text-gray-700 text-sm">
                U
              </div>
            </Avatar>
          )}
        </div>
      ))}
      
      {isLoading && (
        <div className="flex gap-3 justify-start">
          <Avatar className="h-8 w-8">
            <div className="bg-purple-500 h-full w-full flex items-center justify-center text-white text-sm">
              AI
            </div>
          </Avatar>
          <div className="bg-gray-100 rounded-lg px-4 py-2">
            <div className="flex gap-1">
              <div className="w-2 h-2 bg-gray-400 rounded-full animate-bounce" />
              <div className="w-2 h-2 bg-gray-400 rounded-full animate-bounce [animation-delay:0.2s]" />
              <div className="w-2 h-2 bg-gray-400 rounded-full animate-bounce [animation-delay:0.4s]" />
            </div>
          </div>
        </div>
      )}
      
      <div ref={bottomRef} />
    </div>
  )
}
```

### Message Input

```typescript
// components/chat/message-input.tsx

'use client'

import { FormEvent } from 'react'
import { Button } from '@/components/ui/button'
import { Textarea } from '@/components/ui/textarea'
import { Send } from 'lucide-react'

interface MessageInputProps {
  input: string
  handleInputChange: (e: React.ChangeEvent<HTMLTextAreaElement>) => void
  handleSubmit: (e: FormEvent<HTMLFormElement>) => void
  isLoading: boolean
  disabled?: boolean
}

export function MessageInput({
  input,
  handleInputChange,
  handleSubmit,
  isLoading,
  disabled,
}: MessageInputProps) {
  const onSubmit = (e: FormEvent<HTMLFormElement>) => {
    e.preventDefault()
    if (input.trim() && !disabled) {
      handleSubmit(e)
    }
  }
  
  return (
    <div className="border-t bg-white p-4">
      <form onSubmit={onSubmit} className="flex gap-2">
        <Textarea
          value={input}
          onChange={handleInputChange}
          placeholder="Type your message..."
          className="flex-1 min-h-[60px] max-h-[120px]"
          disabled={disabled || isLoading}
          onKeyDown={(e) => {
            if (e.key === 'Enter' && !e.shiftKey) {
              e.preventDefault()
              onSubmit(e as any)
            }
          }}
        />
        
        <Button 
          type="submit" 
          disabled={!input.trim() || disabled || isLoading}
          className="self-end"
        >
          <Send className="h-4 w-4" />
        </Button>
      </form>
      
      <p className="text-xs text-gray-500 mt-2">
        Press Enter to send, Shift + Enter for new line
      </p>
    </div>
  )
}
```

---

## Python Backend API Contract

### Expected Request Format

```typescript
interface ChatRequest {
  message: string
  thread_id: string | null
  campaign_code: string
  instagram_handle?: string
}
```

### Expected Response Format (Streaming)

```typescript
// Server-Sent Events (SSE) format
// Each event:

data: {"type": "message_start", "thread_id": "lead-handle-abc123"}

data: {"type": "content_delta", "content": "Hey"}

data: {"type": "content_delta", "content": ", thanks"}

data: {"type": "content_delta", "content": " for reaching out!"}

data: {"type": "message_end", "metadata": {"stage": "greeting", "agent": "greeter"}}

data: [DONE]
```

### Expected Response Format (Non-Streaming)

```typescript
interface ChatResponse {
  thread_id: string
  message: string
  metadata: {
    stage: string
    agent: string
    qualified?: boolean
    qualification_score?: number
  }
}
```

### State Response Format

```typescript
interface StateResponse {
  thread_id: string
  instagram_handle: string
  campaign_code: string
  campaign_id: string
  current_stage: string
  messages: Array<{
    role: 'human' | 'ai'
    content: string
    timestamp: string
  }>
  qualification_score: number
  qualified: boolean
  objections_raised: string[]
  payment_link_sent: boolean
  created_at: string
  updated_at: string
}
```

---

## Error Handling

### Frontend Error Handling

```typescript
// lib/api/error-handler.ts

export class APIError extends Error {
  constructor(
    message: string,
    public statusCode: number,
    public code?: string
  ) {
    super(message)
    this.name = 'APIError'
  }
}

export async function handleAPIError(response: Response) {
  const data = await response.json().catch(() => ({}))
  
  throw new APIError(
    data.error || data.message || 'An error occurred',
    response.status,
    data.code
  )
}

// Usage in components
try {
  const response = await fetch('/api/chat', options)
  if (!response.ok) {
    await handleAPIError(response)
  }
  return response
} catch (error) {
  if (error instanceof APIError) {
    // Handle specific error codes
    if (error.code === 'INVALID_CAMPAIGN') {
      // Show campaign error
    }
  }
  throw error
}
```

---

## Rate Limiting

### Vercel Edge Config (Recommended)

```typescript
// middleware.ts

import { Ratelimit } from '@upstash/ratelimit'
import { Redis } from '@upstash/redis'
import { NextResponse } from 'next/server'
import type { NextRequest } from 'next/server'

const ratelimit = new Ratelimit({
  redis: Redis.fromEnv(),
  limiter: Ratelimit.slidingWindow(10, '10 s'), // 10 requests per 10 seconds
})

export async function middleware(request: NextRequest) {
  if (request.nextUrl.pathname.startsWith('/api/chat')) {
    const ip = request.ip ?? '127.0.0.1'
    const { success } = await ratelimit.limit(ip)
    
    if (!success) {
      return NextResponse.json(
        { error: 'Too many requests' },
        { status: 429 }
      )
    }
  }
  
  return NextResponse.next()
}

export const config = {
  matcher: '/api/:path*',
}
```

---

## WebSocket Alternative (Optional)

For real-time bidirectional communication:

```typescript
// lib/api/websocket.ts

export class WebSocketClient {
  private ws: WebSocket | null = null
  
  connect(threadId: string) {
    const wsUrl = process.env.NEXT_PUBLIC_WS_URL!
    this.ws = new WebSocket(`${wsUrl}/${threadId}`)
    
    this.ws.onopen = () => {
      console.log('WebSocket connected')
    }
    
    this.ws.onmessage = (event) => {
      const data = JSON.parse(event.data)
      // Handle incoming messages
    }
    
    this.ws.onerror = (error) => {
      console.error('WebSocket error:', error)
    }
    
    this.ws.onclose = () => {
      console.log('WebSocket disconnected')
    }
  }
  
  send(message: string) {
    if (this.ws?.readyState === WebSocket.OPEN) {
      this.ws.send(JSON.stringify({ message }))
    }
  }
  
  disconnect() {
    this.ws?.close()
  }
}
```

---

## Testing Integration

### API Route Tests

```typescript
// __tests__/api/chat.test.ts

import { POST } from '@/app/api/chat/route'
import { NextRequest } from 'next/server'

describe('POST /api/chat', () => {
  it('should return 400 for invalid campaign code', async () => {
    const request = new NextRequest('http://localhost:3000/api/chat', {
      method: 'POST',
      body: JSON.stringify({
        message: 'Hello',
        threadId: null,
        campaignCode: 'INVALID',
      }),
    })
    
    const response = await POST(request)
    expect(response.status).toBe(400)
  })
  
  it('should stream response for valid request', async () => {
    const request = new NextRequest('http://localhost:3000/api/chat', {
      method: 'POST',
      body: JSON.stringify({
        message: 'Hello',
        threadId: null,
        campaignCode: 'VALID123',
        instagramHandle: 'testuser',
      }),
    })
    
    const response = await POST(request)
    expect(response.headers.get('content-type')).toBe('text/event-stream')
  })
})
```

---

## Monitoring & Logging

### Vercel Analytics

```typescript
// app/layout.tsx

import { Analytics } from '@vercel/analytics/react'

export default function RootLayout({ children }) {
  return (
    <html>
      <body>
        {children}
        <Analytics />
      </body>
    </html>
  )
}
```

### Custom Logging

```typescript
// lib/logger.ts

export const logger = {
  info: (message: string, data?: any) => {
    console.log(`[INFO] ${message}`, data)
  },
  error: (message: string, error?: any) => {
    console.error(`[ERROR] ${message}`, error)
    // Send to error tracking service (Sentry, etc.)
  },
  warn: (message: string, data?: any) => {
    console.warn(`[WARN] ${message}`, data)
  },
}
```

---

## Next Steps

- Review [API_ROUTES.md](./API_ROUTES.md) for complete API documentation
- See [COMPONENT_LIBRARY.md](./COMPONENT_LIBRARY.md) for more UI components
- Check [DEPLOYMENT.md](./DEPLOYMENT.md) for production deployment guide
