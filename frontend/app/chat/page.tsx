'use client'

import { useEffect, useRef } from 'react'
import Link from 'next/link'
import { useSettingsStore, useChatStore } from '@/lib/store'
import ChatMessages from '@/components/chat/ChatMessages'
import ChatInput from '@/components/chat/ChatInput'
import Navigation from '@/components/Navigation'
import { Button } from '@/components/ui/button'
import { AlertTriangle, Settings, Trash2 } from 'lucide-react'

export default function ChatPage() {
  const { loadFromLocalStorage, googleApiKey, sarvamApiKey, finCard } = useSettingsStore()
  const { messages, clearMessages } = useChatStore()
  const messagesEndRef = useRef<HTMLDivElement>(null)

  useEffect(() => {
    loadFromLocalStorage()
  }, [loadFromLocalStorage])

  useEffect(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' })
  }, [messages])

  return (
    <div className="flex flex-col h-dvh pb-14 sm:pb-0 bg-background">
      <Navigation />

      <div className="flex-1 flex flex-col overflow-hidden">
        {/* ── Header ── */}
        <div className="border-b border-border/60 bg-card/60 px-4 py-3 sm:px-6 shrink-0">
          <div className="flex items-center justify-between">
            <div className="flex items-center gap-3">
              {/* Status dot */}
              <div className="relative">
                <div className="w-2 h-2 rounded-full bg-emerald-400" />
                <div className="w-2 h-2 rounded-full bg-emerald-400 absolute inset-0 animate-ping opacity-60" />
              </div>
              <div>
                <h1 className="text-base font-semibold text-foreground leading-tight">
                  Loan Advisor AI
                </h1>
                <p className="text-xs text-muted-foreground leading-tight">
                  {finCard.fullName
                    ? `Advising ${finCard.fullName} · Score ${finCard.creditScore}`
                    : 'Add FinCard in Settings for personalised advice'}
                </p>
              </div>
            </div>

            <Button
              variant="ghost"
              size="sm"
              onClick={clearMessages}
              disabled={messages.length === 0}
              className="gap-1.5 text-xs text-muted-foreground hover:text-destructive hover:bg-destructive/10"
            >
              <Trash2 className="w-3.5 h-3.5" />
              Clear
            </Button>
          </div>
        </div>

        {/* ── Banners ── */}
        {!googleApiKey && (
          <div className="bg-amber-500/10 border-b border-amber-500/25 px-4 py-2.5 flex items-center gap-3 shrink-0">
            <AlertTriangle className="w-4 h-4 text-amber-400 shrink-0" />
            <p className="text-sm text-amber-300 flex-1">
              Google API key not set — chat won&apos;t work.
            </p>
            <Link href="/settings">
              <Button size="sm" variant="outline" className="h-7 text-xs gap-1 border-amber-500/30 text-amber-300 hover:bg-amber-500/10">
                <Settings className="w-3 h-3" />
                Settings
              </Button>
            </Link>
          </div>
        )}

        {googleApiKey && !sarvamApiKey && (
          <div className="bg-primary/5 border-b border-primary/15 px-4 py-2 flex items-center gap-3 shrink-0">
            <p className="text-xs text-muted-foreground flex-1">
              Voice input and text-to-speech are disabled — add your Sarvam API key to enable them.
            </p>
            <Link href="/settings">
              <Button size="sm" variant="ghost" className="h-6 text-xs text-primary hover:bg-primary/10">
                Add key
              </Button>
            </Link>
          </div>
        )}

        {/* ── Messages ── */}
        <div className="flex-1 overflow-y-auto">
          <ChatMessages />
          <div ref={messagesEndRef} />
        </div>

        {/* ── Input ── */}
        <ChatInput />
      </div>
    </div>
  )
}
