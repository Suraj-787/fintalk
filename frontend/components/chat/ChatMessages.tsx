'use client'

import { useChatStore, ChatMessage } from '@/lib/store'
import { useSettingsStore } from '@/lib/store'
import { generateTTS } from '@/lib/api'
import { Button } from '@/components/ui/button'
import { Volume2, Loader2, CreditCard, User } from 'lucide-react'
import { useState, useCallback } from 'react'
import ReactMarkdown from 'react-markdown'
import { toast } from 'sonner'

function TTSButton({ message }: { message: ChatMessage }) {
  const { sarvamApiKey } = useSettingsStore()
  const [audioUrl, setAudioUrl] = useState<string | undefined>(message.audioUrl)
  const [isLoading, setIsLoading] = useState(false)
  const [isPlaying, setIsPlaying] = useState(false)

  const handlePlay = useCallback(async () => {
    if (!sarvamApiKey) {
      toast.error('Sarvam API key required — add it in Settings')
      return
    }

    let url = audioUrl
    if (!url) {
      setIsLoading(true)
      try {
        url = await generateTTS(
          message.content,
          sarvamApiKey,
          message.detectedLanguage ?? 'en-IN'
        )
        setAudioUrl(url)
      } catch {
        return
      } finally {
        setIsLoading(false)
      }
    }

    const audio = new Audio(url)
    setIsPlaying(true)
    audio.onended = () => setIsPlaying(false)
    audio.onerror = () => setIsPlaying(false)
    audio.play().catch(() => setIsPlaying(false))
  }, [audioUrl, message, sarvamApiKey])

  return (
    <Button
      size="sm"
      variant="ghost"
      className="h-6 px-2 gap-1 text-[11px] text-muted-foreground hover:text-primary hover:bg-primary/10"
      onClick={handlePlay}
      disabled={isLoading || isPlaying}
    >
      {isLoading
        ? <Loader2 className="w-3 h-3 animate-spin" />
        : <Volume2 className="w-3 h-3" />}
      {isPlaying ? 'Playing…' : isLoading ? 'Loading…' : 'Listen'}
    </Button>
  )
}

export default function ChatMessages() {
  const { messages } = useChatStore()

  if (messages.length === 0) {
    return (
      <div className="flex-1 flex items-center justify-center p-8">
        <div className="text-center max-w-sm">
          <div className="w-14 h-14 rounded-2xl bg-primary/10 border border-primary/20 flex items-center justify-center mx-auto mb-5 shadow-[0_0_24px_-8px_var(--color-primary)]">
            <CreditCard className="w-6 h-6 text-primary" />
          </div>
          <h2 className="text-lg font-bold text-foreground mb-2">FinTalk Advisor</h2>
          <p className="text-sm text-muted-foreground mb-6">
            Ask anything about loans, EMIs, credit scores, or financial planning.
            Configure your FinCard in Settings for personalised advice.
          </p>
          <div className="text-left bg-card border border-border rounded-xl p-4 space-y-2">
            <p className="text-xs font-medium text-muted-foreground uppercase tracking-wide mb-3">
              Suggested questions
            </p>
            {[
              'What loan amount can I qualify for?',
              'How can I improve my credit score?',
              'Explain the difference between fixed and floating rates.',
              'How does EMI calculation work?',
            ].map((q) => (
              <p key={q} className="text-sm text-foreground/80 flex gap-2">
                <span className="text-primary mt-0.5">›</span>
                {q}
              </p>
            ))}
          </div>
        </div>
      </div>
    )
  }

  return (
    <div className="space-y-5 p-4 sm:p-6">
      {messages.map((message) => (
        <div
          key={message.id}
          className={`flex gap-3 ${message.role === 'user' ? 'justify-end' : 'justify-start'}`}
        >
          {/* Assistant avatar */}
          {message.role === 'assistant' && (
            <div className="w-8 h-8 rounded-xl bg-primary/10 border border-primary/20 flex items-center justify-center shrink-0 mt-0.5">
              <CreditCard className="w-3.5 h-3.5 text-primary" />
            </div>
          )}

          <div className="max-w-[80%] sm:max-w-lg lg:max-w-2xl space-y-1">
            {/* Bubble */}
            <div
              className={
                message.role === 'user'
                  ? 'bg-primary text-primary-foreground px-4 py-3 rounded-2xl rounded-tr-sm shadow-sm'
                  : 'bg-card border border-border px-4 py-3 rounded-2xl rounded-tl-sm shadow-sm'
              }
            >
              {message.role === 'assistant' ? (
                <div className="prose prose-sm dark:prose-invert max-w-none text-foreground [&>p]:mb-2 [&>p:last-child]:mb-0 [&>ul]:mb-2 [&>ul]:pl-4 [&>ol]:mb-2 [&>ol]:pl-4 [&>ul>li]:mb-0.5 [&>ol>li]:mb-0.5 [&>h1]:text-base [&>h2]:text-sm [&>h3]:text-sm [&>strong]:text-foreground [&>code]:bg-muted [&>code]:px-1 [&>code]:rounded">
                  <ReactMarkdown>{message.content}</ReactMarkdown>
                </div>
              ) : (
                <p className="text-sm sm:text-base whitespace-pre-wrap">{message.content}</p>
              )}
            </div>

            {/* Meta row */}
            <div
              className={`flex items-center gap-2 px-1 ${
                message.role === 'user' ? 'justify-end' : 'justify-start'
              }`}
            >
              <span className="text-[11px] text-muted-foreground">
                {new Date(message.timestamp).toLocaleTimeString([], {
                  hour: '2-digit',
                  minute: '2-digit',
                })}
              </span>
              {message.role === 'assistant' && <TTSButton message={message} />}
            </div>
          </div>

          {/* User avatar */}
          {message.role === 'user' && (
            <div className="w-8 h-8 rounded-xl bg-muted border border-border flex items-center justify-center shrink-0 mt-0.5">
              <User className="w-3.5 h-3.5 text-muted-foreground" />
            </div>
          )}
        </div>
      ))}
    </div>
  )
}
