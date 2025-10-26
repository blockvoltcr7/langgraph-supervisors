# Next.js 16 Setup Guide for Limitless OS

## Overview

Limitless OS uses **Next.js 16** with the App Router for the frontend chat interface. This guide covers setup, configuration, and key implementation details specific to our AI sales agent application.

---

## Prerequisites

### Required Versions
- **Node.js:** 20.9.0+ (LTS) - **REQUIRED**
- **TypeScript:** 5.1.0+
- **React:** 19.2+ (included with Next.js 16)
- **Next.js:** 16.x

### Browser Support
- Chrome 111+
- Edge 111+
- Firefox 111+
- Safari 16.4+

---

## Installation

### 1. Create Next.js 16 Project

```bash
npx create-next-app@latest limitless-os-frontend --typescript --tailwind --app
cd limitless-os-frontend
```

### 2. Install Core Dependencies

```bash
# Next.js and React (already installed via create-next-app)
npm install next@latest react@latest react-dom@latest

# Supabase Client
npm install @supabase/supabase-js

# Vercel AI SDK for streaming responses
npm install ai

# UI Framework (shadcn/ui)
npx shadcn@latest init

# Icons
npm install lucide-react

# Date utilities
npm install date-fns
```

### 3. Install Development Dependencies

```bash
npm install -D @types/react @types/react-dom @types/node
npm install -D eslint eslint-config-next
npm install -D prettier prettier-plugin-tailwindcss
```

---

## Project Structure

```
limitless-os-frontend/
├── app/
│   ├── (auth)/
│   │   ├── login/
│   │   └── signup/
│   ├── (dashboard)/
│   │   ├── campaigns/
│   │   ├── analytics/
│   │   └── documents/
│   ├── chat/
│   │   └── [campaign_code]/
│   │       └── page.tsx        # Main chat interface
│   ├── api/
│   │   ├── chat/
│   │   │   └── route.ts        # Streaming chat API
│   │   ├── campaigns/
│   │   │   └── route.ts        # Campaign management
│   │   └── webhooks/
│   │       └── stripe/
│   │           └── route.ts    # Stripe webhook handler
│   ├── layout.tsx              # Root layout
│   └── page.tsx                # Landing page
├── components/
│   ├── ui/                     # shadcn/ui components
│   ├── chat/
│   │   ├── chat-interface.tsx
│   │   ├── message-list.tsx
│   │   └── message-input.tsx
│   └── dashboard/
├── lib/
│   ├── supabase/
│   │   ├── client.ts           # Client-side Supabase
│   │   └── server.ts           # Server-side Supabase
│   ├── api/
│   │   └── langgraph.ts        # Python backend API client
│   └── utils.ts
├── types/
│   └── conversation.ts
├── public/
├── next.config.ts
├── tailwind.config.ts
├── tsconfig.json
└── package.json
```

---

## Next.js 16 Configuration

### `next.config.ts`

```typescript
import type { NextConfig } from 'next'

const nextConfig: NextConfig = {
  // Turbopack is now default (no flag needed)
  // For development and production builds
  
  // React Compiler (optional but recommended)
  reactCompiler: true,
  
  // Image optimization
  images: {
    remotePatterns: [
      {
        protocol: 'https',
        hostname: 'storage.googleapis.com',
        pathname: '/limitless-os-uploads/**',
      },
    ],
    minimumCacheTTL: 14400, // 4 hours (new default)
    imageSizes: [32, 48, 64, 96, 128, 256, 384], // 16 removed in v16
    qualities: [75], // New default in v16
  },
  
  // Environment variables available to client
  env: {
    NEXT_PUBLIC_SUPABASE_URL: process.env.NEXT_PUBLIC_SUPABASE_URL,
    NEXT_PUBLIC_SUPABASE_ANON_KEY: process.env.NEXT_PUBLIC_SUPABASE_ANON_KEY,
    NEXT_PUBLIC_STRIPE_PUBLISHABLE_KEY: process.env.NEXT_PUBLIC_STRIPE_PUBLISHABLE_KEY,
  },
  
  // TypeScript strict mode
  typescript: {
    ignoreBuildErrors: false,
  },
  
  // ESLint during builds (removed next lint integration)
  eslint: undefined, // No longer supported in v16
}

export default nextConfig
```

---

## Key Next.js 16 Features for Limitless OS

### 1. Async Request APIs

All dynamic APIs are now **fully async** in Next.js 16:

#### Campaign Chat Page

```typescript
// app/chat/[campaign_code]/page.tsx

import { cookies, headers } from 'next/headers'

interface PageProps {
  params: Promise<{ campaign_code: string }>
  searchParams: Promise<{ instagram?: string }>
}

export default async function ChatPage(props: PageProps) {
  // REQUIRED: Await params and searchParams
  const params = await props.params
  const searchParams = await props.searchParams
  
  const { campaign_code } = params
  const instagramHandle = searchParams.instagram
  
  // Await cookies and headers
  const cookieStore = await cookies()
  const headersList = await headers()
  
  // Validate campaign code
  const campaign = await validateCampaign(campaign_code)
  
  if (!campaign) {
    notFound()
  }
  
  return (
    <ChatInterface 
      campaignCode={campaign_code}
      initialHandle={instagramHandle}
    />
  )
}
```

#### API Routes

```typescript
// app/api/chat/route.ts

import { cookies } from 'next/headers'
import { NextRequest } from 'next/server'

export async function POST(request: NextRequest) {
  const cookieStore = await cookies()
  const body = await request.json()
  
  // Process chat message
  // ...
}
```

### 2. Streaming Chat Responses with Vercel AI SDK

```typescript
// app/api/chat/route.ts

import { StreamingTextResponse } from 'ai'
import { NextRequest } from 'next/server'

export async function POST(request: NextRequest) {
  const { message, threadId, campaignCode } = await request.json()
  
  // Call Python LangGraph backend
  const response = await fetch(`${process.env.LANGGRAPH_API_URL}/chat/stream`, {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
      'Authorization': `Bearer ${process.env.LANGGRAPH_API_KEY}`,
    },
    body: JSON.stringify({
      message,
      thread_id: threadId,
      campaign_code: campaignCode,
    }),
  })
  
  // Stream the response back to client
  return new StreamingTextResponse(response.body)
}
```

### 3. Client-Side Chat Component

```typescript
// components/chat/chat-interface.tsx

'use client'

import { useChat } from 'ai/react'
import { useState } from 'react'

interface ChatInterfaceProps {
  campaignCode: string
  initialHandle?: string
}

export function ChatInterface({ campaignCode, initialHandle }: ChatInterfaceProps) {
  const [threadId, setThreadId] = useState<string | null>(null)
  
  const { messages, input, handleInputChange, handleSubmit, isLoading } = useChat({
    api: '/api/chat',
    body: {
      threadId,
      campaignCode,
    },
    onFinish: (message) => {
      // Extract thread_id from first response if not set
      if (!threadId && message.content.includes('thread_id')) {
        // Parse and set thread ID
      }
    },
  })
  
  return (
    <div className="flex flex-col h-screen">
      <MessageList messages={messages} />
      <MessageInput 
        input={input}
        handleInputChange={handleInputChange}
        handleSubmit={handleSubmit}
        isLoading={isLoading}
      />
    </div>
  )
}
```

### 4. Supabase Integration

#### Server-Side Supabase Client

```typescript
// lib/supabase/server.ts

import { createServerClient } from '@supabase/ssr'
import { cookies } from 'next/headers'

export async function createClient() {
  const cookieStore = await cookies()
  
  return createServerClient(
    process.env.NEXT_PUBLIC_SUPABASE_URL!,
    process.env.NEXT_PUBLIC_SUPABASE_ANON_KEY!,
    {
      cookies: {
        getAll() {
          return cookieStore.getAll()
        },
        setAll(cookiesToSet) {
          try {
            cookiesToSet.forEach(({ name, value, options }) =>
              cookieStore.set(name, value, options)
            )
          } catch {
            // The `setAll` method was called from a Server Component.
            // This can be ignored if you have middleware refreshing
            // user sessions.
          }
        },
      },
    }
  )
}
```

#### Client-Side Supabase Client

```typescript
// lib/supabase/client.ts

import { createBrowserClient } from '@supabase/ssr'

export function createClient() {
  return createBrowserClient(
    process.env.NEXT_PUBLIC_SUPABASE_URL!,
    process.env.NEXT_PUBLIC_SUPABASE_ANON_KEY!
  )
}
```

### 5. Stripe Webhook Handler

```typescript
// app/api/webhooks/stripe/route.ts

import { headers } from 'next/headers'
import { NextRequest, NextResponse } from 'next/server'
import Stripe from 'stripe'

const stripe = new Stripe(process.env.STRIPE_SECRET_KEY!, {
  apiVersion: '2024-10-28.acacia',
})

export async function POST(request: NextRequest) {
  const body = await request.text()
  const headersList = await headers()
  const signature = headersList.get('stripe-signature')!
  
  let event: Stripe.Event
  
  try {
    event = stripe.webhooks.constructEvent(
      body,
      signature,
      process.env.STRIPE_WEBHOOK_SECRET!
    )
  } catch (err: any) {
    return NextResponse.json(
      { error: `Webhook Error: ${err.message}` },
      { status: 400 }
    )
  }
  
  // Handle the event
  switch (event.type) {
    case 'checkout.session.completed':
      const session = event.data.object
      // Update conversation state to "complete"
      await handlePaymentSuccess(session)
      break
    default:
      console.log(`Unhandled event type ${event.type}`)
  }
  
  return NextResponse.json({ received: true })
}
```

### 6. Enhanced Routing & Navigation

Next.js 16 includes automatic optimizations:

```typescript
// components/navigation.tsx

'use client'

import Link from 'next/link'

export function Navigation() {
  return (
    <nav>
      {/* Automatic prefetching with layout deduplication */}
      <Link href="/campaigns">Campaigns</Link>
      <Link href="/analytics">Analytics</Link>
      <Link href="/documents">Documents</Link>
    </nav>
  )
}
```

---

## Environment Variables

### `.env.local`

```bash
# Supabase
NEXT_PUBLIC_SUPABASE_URL=https://your-project.supabase.co
NEXT_PUBLIC_SUPABASE_ANON_KEY=your-anon-key
SUPABASE_SERVICE_ROLE_KEY=your-service-role-key

# LangGraph Python Backend
LANGGRAPH_API_URL=https://your-cloud-run-url.run.app
LANGGRAPH_API_KEY=your-api-key

# Stripe
NEXT_PUBLIC_STRIPE_PUBLISHABLE_KEY=pk_test_...
STRIPE_SECRET_KEY=sk_test_...
STRIPE_WEBHOOK_SECRET=whsec_...

# OpenAI (for backend)
OPENAI_API_KEY=sk-...

# Node Environment
NODE_ENV=development
```

---

## TypeScript Configuration

### `tsconfig.json`

```json
{
  "compilerOptions": {
    "target": "ES2017",
    "lib": ["dom", "dom.iterable", "esnext"],
    "allowJs": true,
    "skipLibCheck": true,
    "strict": true,
    "noEmit": true,
    "esModuleInterop": true,
    "module": "esnext",
    "moduleResolution": "bundler",
    "resolveJsonModule": true,
    "isolatedModules": true,
    "jsx": "preserve",
    "incremental": true,
    "plugins": [
      {
        "name": "next"
      }
    ],
    "paths": {
      "@/*": ["./*"]
    }
  },
  "include": ["next-env.d.ts", "**/*.ts", "**/*.tsx", ".next/types/**/*.ts"],
  "exclude": ["node_modules"]
}
```

---

## Package.json Scripts

### `package.json`

```json
{
  "name": "limitless-os-frontend",
  "version": "0.1.0",
  "private": true,
  "scripts": {
    "dev": "next dev",
    "build": "next build",
    "start": "next start",
    "lint": "eslint .",
    "format": "prettier --write .",
    "type-check": "tsc --noEmit",
    "typegen": "npx next typegen"
  },
  "dependencies": {
    "next": "^16.0.0",
    "react": "^19.2.0",
    "react-dom": "^19.2.0",
    "@supabase/supabase-js": "^2.45.0",
    "@supabase/ssr": "^0.5.0",
    "ai": "^4.0.0",
    "lucide-react": "^0.460.0",
    "date-fns": "^4.1.0",
    "stripe": "^17.3.0"
  },
  "devDependencies": {
    "typescript": "^5.7.0",
    "@types/node": "^22.10.0",
    "@types/react": "^19.0.0",
    "@types/react-dom": "^19.0.0",
    "eslint": "^9.0.0",
    "eslint-config-next": "^16.0.0",
    "tailwindcss": "^3.4.0",
    "postcss": "^8",
    "autoprefixer": "^10.4.0",
    "prettier": "^3.4.0",
    "prettier-plugin-tailwindcss": "^0.6.0"
  }
}
```

---

## Development Workflow

### 1. Start Development Server

```bash
# Turbopack is default in Next.js 16
npm run dev
```

Server starts at `http://localhost:3000`

### 2. Type Generation

Generate types for async params and searchParams:

```bash
npm run typegen
```

This creates type helpers like `PageProps`, `LayoutProps`, and `RouteContext`.

### 3. Build for Production

```bash
npm run build
```

### 4. Preview Production Build

```bash
npm run start
```

---

## Deployment

### Vercel (Recommended)

1. **Connect Repository:**
   ```bash
   vercel
   ```

2. **Set Environment Variables:**
   - Go to Vercel Dashboard → Settings → Environment Variables
   - Add all variables from `.env.local`

3. **Deploy:**
   ```bash
   vercel --prod
   ```

### Environment-Specific Settings

- **Node.js Version:** 20.x (automatically detected)
- **Build Command:** `npm run build`
- **Output Directory:** `.next`
- **Install Command:** `npm install`

---

## ESLint Configuration

Next.js 16 uses **ESLint Flat Config** by default.

### `eslint.config.mjs`

```javascript
import { FlatCompat } from '@eslint/eslintrc'

const compat = new FlatCompat({
  baseDirectory: import.meta.dirname,
})

const eslintConfig = [
  ...compat.extends('next/core-web-vitals', 'next/typescript'),
  {
    rules: {
      '@typescript-eslint/no-unused-vars': 'warn',
      '@typescript-eslint/no-explicit-any': 'warn',
    },
  },
]

export default eslintConfig
```

Run linting manually:

```bash
npm run lint
```

---

## Prettier Configuration

### `.prettierrc.json`

```json
{
  "semi": false,
  "singleQuote": true,
  "trailingComma": "es5",
  "tabWidth": 2,
  "printWidth": 100,
  "plugins": ["prettier-plugin-tailwindcss"]
}
```

---

## Performance Optimizations

### 1. React Compiler

Enable in `next.config.ts`:

```typescript
const nextConfig: NextConfig = {
  reactCompiler: true,
}
```

### 2. Turbopack File System Caching (Beta)

```typescript
const nextConfig: NextConfig = {
  experimental: {
    turbopackFileSystemCacheForDev: true,
  },
}
```

### 3. Component-Level Caching

For PPR-like behavior:

```typescript
const nextConfig: NextConfig = {
  cacheComponents: true,
}
```

---

## Common Patterns

### Loading States

```typescript
// app/chat/[campaign_code]/loading.tsx

export default function Loading() {
  return (
    <div className="flex items-center justify-center h-screen">
      <div className="animate-spin rounded-full h-32 w-32 border-b-2 border-gray-900" />
    </div>
  )
}
```

### Error Boundaries

```typescript
// app/chat/[campaign_code]/error.tsx

'use client'

export default function Error({
  error,
  reset,
}: {
  error: Error & { digest?: string }
  reset: () => void
}) {
  return (
    <div className="flex flex-col items-center justify-center h-screen">
      <h2>Something went wrong!</h2>
      <button onClick={reset}>Try again</button>
    </div>
  )
}
```

### Not Found Pages

```typescript
// app/chat/[campaign_code]/not-found.tsx

export default function NotFound() {
  return (
    <div className="flex flex-col items-center justify-center h-screen">
      <h2>Campaign Not Found</h2>
      <p>The campaign code you entered does not exist.</p>
    </div>
  )
}
```

---

## Testing

### Unit Tests (Vitest)

```bash
npm install -D vitest @testing-library/react @testing-library/jest-dom
```

### E2E Tests (Playwright)

```bash
npm install -D @playwright/test
npx playwright install
```

---

## Troubleshooting

### Issue: Build fails with webpack configuration error

**Solution:** Next.js 16 uses Turbopack by default. If you have custom webpack config, either:
- Remove it and migrate to Turbopack
- Use `--webpack` flag to opt out

### Issue: TypeScript errors with async params

**Solution:** Run `npx next typegen` to generate type helpers.

### Issue: Supabase cookies not working

**Solution:** Ensure you're using `@supabase/ssr` package and awaiting `cookies()`.

---

## Next Steps

1. Review [INTEGRATION_GUIDE.md](./INTEGRATION_GUIDE.md) for connecting to the Python LangGraph backend
2. See [COMPONENT_LIBRARY.md](./COMPONENT_LIBRARY.md) for UI component examples
3. Check [API_ROUTES.md](./API_ROUTES.md) for complete API route documentation

---

## Resources

- [Next.js 16 Documentation](https://nextjs.org/docs)
- [Vercel AI SDK](https://sdk.vercel.ai/docs)
- [Supabase Next.js Guide](https://supabase.com/docs/guides/getting-started/quickstarts/nextjs)
- [shadcn/ui](https://ui.shadcn.com)
