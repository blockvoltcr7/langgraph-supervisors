# Next.js 16 Frontend Documentation

Complete documentation for building the Limitless OS frontend with **Next.js 16**.

---

## 📚 Documentation Files

### [NEXTJS_16_SETUP.md](./NEXTJS_16_SETUP.md)
**Complete Next.js 16 setup and configuration guide**

**What's covered:**
- Prerequisites (Node.js 20.9+, TypeScript 5.1+)
- Installation and project structure
- Next.js 16 configuration (`next.config.ts`)
- Key Next.js 16 features:
  - Async Request APIs (cookies, headers, params, searchParams)
  - Turbopack by default
  - React 19.2 features
  - React Compiler support
  - Enhanced routing and navigation
- Supabase integration (client and server)
- Environment variables
- Package.json scripts
- ESLint and Prettier configuration
- Development workflow

**Read this first if:** You're setting up the Next.js 16 frontend from scratch.

**Time:** 25 minutes

---

### [INTEGRATION_GUIDE.md](./INTEGRATION_GUIDE.md)
**Backend integration and API client patterns**

**What's covered:**
- API client setup for LangGraph backend
- API Routes:
  - Streaming chat route
  - State retrieval route
  - History retrieval route
- Frontend components:
  - Chat interface with streaming
  - Instagram handle prompt
  - Message list and input
- Error handling patterns
- Rate limiting with Vercel Edge Config
- WebSocket alternative (optional)
- Testing integration
- Monitoring and logging

**Read this second:** After setting up Next.js 16, this shows how to connect to the Python backend.

**Time:** 20 minutes

---

## 🚀 Quick Start

### 1. Prerequisites

Ensure you have the required versions:

```bash
# Check Node.js version (must be 20.9+)
node --version

# Check npm version
npm --version

# Check TypeScript version (optional, will be installed)
npx tsc --version
```

### 2. Create Project

```bash
# Create Next.js 16 project
npx create-next-app@latest limitless-os-frontend --typescript --tailwind --app

# Navigate to project
cd limitless-os-frontend

# Install dependencies
npm install
```

### 3. Follow Setup Guide

Open [NEXTJS_16_SETUP.md](./NEXTJS_16_SETUP.md) and follow the complete setup instructions.

### 4. Configure Integration

Open [INTEGRATION_GUIDE.md](./INTEGRATION_GUIDE.md) to connect to the Python LangGraph backend.

---

## 🎯 Key Next.js 16 Changes

### Breaking Changes from Next.js 15

1. **Async Request APIs** - All dynamic APIs now require `await`:
   ```typescript
   // Next.js 15
   const cookieStore = cookies()
   
   // Next.js 16
   const cookieStore = await cookies()
   ```

2. **Turbopack by Default** - No `--turbopack` flag needed:
   ```json
   // package.json
   {
     "scripts": {
       "dev": "next dev",        // Turbopack enabled
       "build": "next build"     // Turbopack enabled
     }
   }
   ```

3. **Node.js 20.9+ Required** - Older versions no longer supported

4. **TypeScript 5.1+ Required** - Earlier versions not compatible

---

## 📖 Implementation Overview

### Project Structure

```
limitless-os-frontend/
├── app/
│   ├── chat/[campaign_code]/     # Main chat interface
│   ├── api/
│   │   ├── chat/                 # Streaming chat endpoint
│   │   └── webhooks/stripe/      # Payment webhooks
│   ├── layout.tsx
│   └── page.tsx
├── components/
│   ├── chat/                     # Chat UI components
│   └── ui/                       # shadcn/ui components
├── lib/
│   ├── supabase/                 # Supabase clients
│   └── api/                      # LangGraph API client
└── nextjs16/                     # This documentation
```

### Core Technologies

- **Next.js 16** - App Router with async APIs
- **React 19.2** - React Server Components
- **TypeScript 5.1+** - Type safety
- **Tailwind CSS** - Styling
- **shadcn/ui** - UI components
- **Vercel AI SDK** - Streaming chat
- **Supabase** - Backend services

---

## 🔗 Related Documentation

### Backend Documentation
- [ARCHITECTURE_OVERVIEW.md](../ARCHITECTURE_OVERVIEW.md) - System architecture
- [API_ENDPOINTS.md](../API_ENDPOINTS.md) - API specifications
- [STATE_SCHEMA.md](../STATE_SCHEMA.md) - LangGraph state design

### Database Documentation
- [DATABASE_SCHEMA.md](../DATABASE_SCHEMA.md) - Supabase schema
- [CAMPAIGN_SYSTEM.md](../CAMPAIGN_SYSTEM.md) - Campaign tracking

### Business Logic
- [SALES_PLAYBOOK.md](../SALES_PLAYBOOK.md) - Sales methodology
- [AGENT_DESIGNS.yaml](../AGENT_DESIGNS.yaml) - AI agent specs

---

## 🛠️ Common Tasks

### Start Development Server

```bash
npm run dev
```

Open http://localhost:3000

### Build for Production

```bash
npm run build
```

### Run Linting

```bash
npm run lint
```

### Format Code

```bash
npm run format
```

### Generate TypeScript Types

```bash
npm run typegen
```

This generates type helpers for async `params` and `searchParams`.

---

## ⚙️ Environment Variables

Required environment variables (add to `.env.local`):

```bash
# Supabase
NEXT_PUBLIC_SUPABASE_URL=
NEXT_PUBLIC_SUPABASE_ANON_KEY=
SUPABASE_SERVICE_ROLE_KEY=

# LangGraph Backend
LANGGRAPH_API_URL=
LANGGRAPH_API_KEY=

# Stripe
NEXT_PUBLIC_STRIPE_PUBLISHABLE_KEY=
STRIPE_SECRET_KEY=
STRIPE_WEBHOOK_SECRET=
```

See [NEXTJS_16_SETUP.md](./NEXTJS_16_SETUP.md#environment-variables) for complete list.

---

## 🐛 Troubleshooting

### Issue: TypeScript errors with async params

**Solution:** Run `npx next typegen` to generate type helpers.

### Issue: "Module not found: Can't resolve 'fs'"

**Solution:** Use `turbopack.resolveAlias` to create empty module for browser:
```typescript
// next.config.ts
export default {
  turbopack: {
    resolveAlias: {
      fs: { browser: './empty.ts' }
    }
  }
}
```

### Issue: Supabase cookies not persisting

**Solution:** Ensure you're using `@supabase/ssr` package and awaiting `cookies()`.

### Issue: Streaming not working

**Solution:** Check that API route returns `new Response(stream.body, ...)` not `NextResponse`.

---

## 📚 Additional Resources

- [Next.js 16 Documentation](https://nextjs.org/docs)
- [Next.js 16 Upgrade Guide](https://nextjs.org/docs/app/guides/upgrading/version-16)
- [Vercel AI SDK Documentation](https://sdk.vercel.ai/docs)
- [Supabase Next.js Guide](https://supabase.com/docs/guides/getting-started/quickstarts/nextjs)
- [shadcn/ui Components](https://ui.shadcn.com)
- [React 19.2 Announcement](https://react.dev/blog/2025/10/01/react-19-2)

---

## ✅ Checklist

Before starting development, ensure:

- [ ] Node.js 20.9+ installed
- [ ] TypeScript 5.1+ installed
- [ ] Next.js 16 project created
- [ ] All dependencies installed
- [ ] Environment variables configured
- [ ] Supabase project set up
- [ ] Python backend running (for testing)

---

**Ready to build? Start with [NEXTJS_16_SETUP.md](./NEXTJS_16_SETUP.md)**
