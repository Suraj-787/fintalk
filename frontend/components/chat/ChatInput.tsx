'use client'

import { useState, useRef, useCallback } from 'react'
import { useSettingsStore, useChatStore } from '@/lib/store'
import { sendChatMessage, transcribeAudio, generateTTS } from '@/lib/api'
import { Button } from '@/components/ui/button'
import { Textarea } from '@/components/ui/textarea'
import { Spinner } from '@/components/ui/spinner'
import { Mic, Send, Square } from 'lucide-react'
import { toast } from 'sonner'

export default function ChatInput() {
  const [input, setInput] = useState('')
  const [isRecording, setIsRecording] = useState(false)
  const [recordingTime, setRecordingTime] = useState(0)
  const mediaRecorderRef = useRef<MediaRecorder | null>(null)
  const audioChunksRef = useRef<Blob[]>([])
  const timerRef = useRef<NodeJS.Timeout | undefined>(undefined)

  const { googleApiKey, sarvamApiKey, finCard } = useSettingsStore()
  const { messages, isLoading, addMessage, setIsLoading } = useChatStore()

  const startRecording = async () => {
    if (!sarvamApiKey) {
      toast.error('Sarvam API key required for voice input — add it in Settings')
      return
    }
    try {
      const stream = await navigator.mediaDevices.getUserMedia({ audio: true })
      const mediaRecorder = new MediaRecorder(stream)
      mediaRecorderRef.current = mediaRecorder
      audioChunksRef.current = []

      mediaRecorder.ondataavailable = (e) => {
        if (e.data.size > 0) audioChunksRef.current.push(e.data)
      }

      mediaRecorder.onstop = async () => {
        stream.getTracks().forEach((t) => t.stop())
        const audioBlob = new Blob(audioChunksRef.current, { type: 'audio/wav' })
        await handleAudioSubmit(audioBlob)
      }

      mediaRecorder.start(100)
      setIsRecording(true)
      setRecordingTime(0)
      timerRef.current = setInterval(() => setRecordingTime((p) => p + 1), 1000)
    } catch {
      toast.error('Microphone access denied')
    }
  }

  const stopRecording = () => {
    if (mediaRecorderRef.current && isRecording) {
      mediaRecorderRef.current.stop()
      setIsRecording(false)
      clearInterval(timerRef.current)
    }
  }

  const handleAudioSubmit = async (audioBlob: Blob) => {
    try {
      setIsLoading(true)
      const text = await transcribeAudio(audioBlob, sarvamApiKey, 'unknown')
      if (!text.trim()) {
        toast.error('Could not transcribe audio — try again')
        return
      }
      await submitMessage(text, true)
    } catch {
      // error already toasted by api.ts
    } finally {
      setIsLoading(false)
    }
  }

  const submitMessage = useCallback(
    async (messageText: string, withTTS = false) => {
      if (!messageText.trim()) return
      if (!googleApiKey) {
        toast.error('Google API key not configured — go to Settings')
        return
      }

      setIsLoading(true)

      const userMessage = {
        id: Date.now().toString(),
        role: 'user' as const,
        content: messageText,
        timestamp: Date.now(),
      }
      addMessage(userMessage)

      const chatHistory = messages.map((m) => ({
        role: m.role,
        content: m.content,
      }))

      try {
        const response = await sendChatMessage({
          message: messageText,
          googleApiKey,
          sarvamApiKey,
          finCard: finCard.fullName ? finCard : null,
          chatHistory,
        })

        let audioUrl: string | undefined
        if (withTTS && sarvamApiKey && response.detectedLanguage) {
          try {
            audioUrl = await generateTTS(
              response.response,
              sarvamApiKey,
              response.detectedLanguage
            )
          } catch {
            // TTS failure is non-fatal
          }
        }

        addMessage({
          id: (Date.now() + 1).toString(),
          role: 'assistant',
          content: response.response,
          audioUrl,
          detectedLanguage: response.detectedLanguage,
          timestamp: Date.now(),
        })

        if (audioUrl) {
          const audio = new Audio(audioUrl)
          audio.play().catch(() => {})
        }
      } catch {
        // error already toasted by api.ts
      } finally {
        setIsLoading(false)
      }
    },
    [googleApiKey, sarvamApiKey, finCard, messages, addMessage, setIsLoading]
  )

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault()
    submitMessage(input)
    setInput('')
  }

  const handleKeyDown = (e: React.KeyboardEvent<HTMLTextAreaElement>) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault()
      submitMessage(input)
      setInput('')
    }
  }

  return (
    <div className="border-t border-border/60 bg-card/80 px-4 py-3 sm:px-6">
      {isRecording && (
        <div className="flex items-center gap-3 mb-3 bg-destructive/10 border border-destructive/30 text-destructive px-3 py-2 rounded-md">
          <div className="w-2 h-2 bg-destructive rounded-full animate-pulse flex-shrink-0" />
          <span className="text-sm font-medium flex-1">Recording… {recordingTime}s</span>
          <Button
            type="button"
            size="sm"
            variant="destructive"
            onClick={stopRecording}
            className="h-7 px-3 gap-1 shrink-0"
          >
            <Square className="w-3 h-3" />
            Stop
          </Button>
        </div>
      )}

      <form onSubmit={handleSubmit} className="flex gap-2 items-end">
        <Textarea
          value={input}
          onChange={(e) => setInput(e.target.value)}
          onKeyDown={handleKeyDown}
          placeholder="Ask about loans, EMIs, credit score… (Enter to send, Shift+Enter for newline)"
          disabled={isLoading || isRecording}
          rows={1}
          className="flex-1 min-h-10.5 max-h-40 resize-none"
        />

        <Button
          type="button"
          size="icon"
          variant={isRecording ? 'destructive' : 'outline'}
          onClick={isRecording ? stopRecording : startRecording}
          disabled={isLoading}
          title={isRecording ? 'Stop recording' : 'Voice input'}
          className="shrink-0"
        >
          <Mic className="w-4 h-4" />
        </Button>

        <Button
          type="submit"
          size="icon"
          disabled={!input.trim() || isLoading || isRecording}
          title="Send message"
          className="shrink-0"
        >
          {isLoading ? <Spinner className="w-4 h-4" /> : <Send className="w-4 h-4" />}
        </Button>
      </form>

      <p className="text-xs text-muted-foreground mt-2">
        Try: &ldquo;What loan can I get?&rdquo; · &ldquo;How do I improve my credit score?&rdquo; · &ldquo;What is EMI?&rdquo;
      </p>
    </div>
  )
}
