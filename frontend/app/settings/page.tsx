'use client'

import { useEffect } from 'react'
import Navigation from '@/components/Navigation'
import ApiKeysForm from '@/components/settings/ApiKeysForm'
import FinCardForm from '@/components/settings/FinCardForm'
import { useSettingsStore } from '@/lib/store'
import { Key, CreditCard, CheckCircle2, XCircle } from 'lucide-react'

export default function SettingsPage() {
  const { loadFromLocalStorage, googleApiKey, sarvamApiKey, finCard } = useSettingsStore()

  useEffect(() => {
    loadFromLocalStorage()
  }, [loadFromLocalStorage])

  return (
    <div className="flex flex-col min-h-screen pb-14 sm:pb-0 bg-background">
      <Navigation />

      <main className="flex-1">
        <div className="max-w-3xl mx-auto px-4 py-8 sm:px-6 space-y-8">
          {/* Page header */}
          <div>
            <h1 className="text-2xl font-bold text-foreground mb-1">Settings</h1>
            <p className="text-sm text-muted-foreground">
              Configure your API keys and financial profile for personalised loan advice.
            </p>
          </div>

          {/* Status pills */}
          <div className="flex flex-wrap gap-2">
            <StatusPill
              label="Google AI"
              ok={!!googleApiKey}
              okText="Connected"
              failText="Not configured"
            />
            <StatusPill
              label="Sarvam AI"
              ok={!!sarvamApiKey}
              okText="Connected"
              failText="Not configured"
            />
            <StatusPill
              label="FinCard"
              ok={!!finCard.fullName}
              okText={finCard.fullName || 'Saved'}
              failText="Not set up"
            />
          </div>

          {/* API Keys */}
          <section className="rounded-xl border border-border bg-card overflow-hidden">
            <div className="px-5 py-4 border-b border-border/60 flex items-center gap-3">
              <div className="w-8 h-8 rounded-lg bg-primary/10 border border-primary/20 flex items-center justify-center">
                <Key className="w-4 h-4 text-primary" />
              </div>
              <div>
                <h2 className="text-base font-semibold text-foreground">API Keys</h2>
                <p className="text-xs text-muted-foreground">Stored locally — never sent to our servers</p>
              </div>
            </div>
            <div className="p-5">
              <ApiKeysForm />
            </div>
          </section>

          {/* FinCard */}
          <section className="rounded-xl border border-border bg-card overflow-hidden">
            <div className="px-5 py-4 border-b border-border/60 flex items-center gap-3">
              <div className="w-8 h-8 rounded-lg bg-amber-500/10 border border-amber-500/20 flex items-center justify-center">
                <CreditCard className="w-4 h-4 text-amber-400" />
              </div>
              <div>
                <h2 className="text-base font-semibold text-foreground">FinCard Profile</h2>
                <p className="text-xs text-muted-foreground">Your financial snapshot for personalised advice</p>
              </div>
            </div>
            <div className="p-5">
              <FinCardForm />
            </div>
          </section>
        </div>
      </main>
    </div>
  )
}

function StatusPill({
  label,
  ok,
  okText,
  failText,
}: {
  label: string
  ok: boolean
  okText: string
  failText: string
}) {
  return (
    <div
      className={`flex items-center gap-1.5 px-3 py-1.5 rounded-full border text-xs font-medium ${
        ok
          ? 'bg-emerald-500/10 border-emerald-500/25 text-emerald-400'
          : 'bg-muted border-border text-muted-foreground'
      }`}
    >
      {ok
        ? <CheckCircle2 className="w-3.5 h-3.5" />
        : <XCircle className="w-3.5 h-3.5" />}
      <span className="text-muted-foreground">{label}:</span>
      <span className={ok ? 'text-emerald-300' : ''}>{ok ? okText : failText}</span>
    </div>
  )
}
