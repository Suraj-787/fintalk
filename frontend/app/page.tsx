'use client'

import Link from 'next/link'
import Navigation from '@/components/Navigation'
import { Button } from '@/components/ui/button'
import {
  MessageSquare,
  Mic,
  Globe,
  CreditCard,
  ArrowRight,
  CheckCircle2,
  Zap,
  Lock,
} from 'lucide-react'

const features = [
  {
    icon: MessageSquare,
    title: 'AI Chat Advisor',
    desc: 'Ask questions about loans, EMIs, interest rates, and eligibility — get instant, accurate answers.',
    color: 'text-blue-400',
    bg: 'bg-blue-500/10 border-blue-500/20',
  },
  {
    icon: Mic,
    title: 'Voice Input & TTS',
    desc: 'Speak your queries and hear responses read aloud. Hands-free financial guidance.',
    color: 'text-purple-400',
    bg: 'bg-purple-500/10 border-purple-500/20',
  },
  {
    icon: Globe,
    title: 'Multilingual Support',
    desc: 'Chat in Hindi, Tamil, Bengali, Telugu and 8 more Indian languages. Auto-detects your language.',
    color: 'text-emerald-400',
    bg: 'bg-emerald-500/10 border-emerald-500/20',
  },
  {
    icon: CreditCard,
    title: 'FinCard Profile',
    desc: 'Enter your income, credit score, and expenses once. Get advice personalised to your situation.',
    color: 'text-amber-400',
    bg: 'bg-amber-500/10 border-amber-500/20',
  },
]

const steps = [
  {
    num: '01',
    title: 'Configure API Keys',
    desc: 'Add your Google Gemini key for AI and Sarvam key for voice features in Settings.',
  },
  {
    num: '02',
    title: 'Build Your FinCard',
    desc: 'Fill in your financial profile — income, credit score, EMIs — for tailored recommendations.',
  },
  {
    num: '03',
    title: 'Start the Conversation',
    desc: 'Type or speak your loan questions and get personalised guidance instantly.',
  },
]

const benefits = [
  'Loan eligibility assessment based on your real profile',
  'Step-by-step application guidance',
  'Credit score improvement tips',
  'Understand EMI, interest rates, and loan terms clearly',
  'All data stored locally — never sent to our servers',
]

export default function HomePage() {
  return (
    <div className="flex flex-col min-h-screen pb-14 sm:pb-0 bg-background">
      <Navigation />

      {/* ── Hero ── */}
      <section className="gradient-hero relative px-4 py-20 sm:py-32 text-center overflow-hidden">
        {/* Subtle dot grid */}
        <div
          className="pointer-events-none absolute inset-0 -z-10 opacity-[0.03]"
          style={{
            backgroundImage:
              'radial-gradient(circle, white 1px, transparent 1px)',
            backgroundSize: '32px 32px',
          }}
        />

        <div className="max-w-3xl mx-auto space-y-6">
          {/* Badge */}
          <div className="inline-flex items-center gap-2 rounded-full border border-primary/30 bg-primary/10 px-4 py-1.5 text-sm text-primary">
            <Zap className="w-3.5 h-3.5" />
            Powered by Google Gemini &amp; Sarvam AI
          </div>

          <h1 className="text-4xl sm:text-5xl lg:text-6xl font-bold leading-tight tracking-tight">
            Your Smart{' '}
            <span className="text-gradient">Financial Advisor</span>
            <br />is Here
          </h1>

          <p className="text-lg text-muted-foreground max-w-xl mx-auto">
            FinTalk helps you navigate loans, credit, and financial decisions
            with AI-powered guidance — in your language, your way.
          </p>

          <div className="flex flex-col sm:flex-row gap-3 justify-center pt-2">
            <Link href="/chat">
              <Button size="lg" className="w-full sm:w-auto gap-2 px-8">
                Start Chatting
                <ArrowRight className="w-4 h-4" />
              </Button>
            </Link>
            <Link href="/settings">
              <Button size="lg" variant="outline" className="w-full sm:w-auto px-8">
                Set Up Keys
              </Button>
            </Link>
          </div>
        </div>

        {/* Stats strip */}
        <div className="mt-16 flex flex-wrap items-center justify-center gap-x-10 gap-y-4 text-sm text-muted-foreground">
          {['11 Languages', '24 / 7 Available', 'Voice + Text', '100% Private'].map((s) => (
            <div key={s} className="flex items-center gap-1.5">
              <div className="w-1.5 h-1.5 rounded-full bg-primary" />
              {s}
            </div>
          ))}
        </div>
      </section>

      {/* ── Features ── */}
      <section className="px-4 py-16 sm:py-24 border-t border-border/60">
        <div className="max-w-6xl mx-auto">
          <div className="text-center mb-12">
            <h2 className="text-2xl sm:text-3xl font-bold mb-3">Everything You Need</h2>
            <p className="text-muted-foreground max-w-lg mx-auto">
              A complete loan advisory toolkit, powered by the latest AI models
            </p>
          </div>

          <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4">
            {features.map(({ icon: Icon, title, desc, color, bg }) => (
              <div
                key={title}
                className="card-hover rounded-xl border border-border bg-card p-5 space-y-3"
              >
                <div className={`w-10 h-10 rounded-lg border flex items-center justify-center ${bg}`}>
                  <Icon className={`w-5 h-5 ${color}`} />
                </div>
                <h3 className="font-semibold text-foreground">{title}</h3>
                <p className="text-sm text-muted-foreground leading-relaxed">{desc}</p>
              </div>
            ))}
          </div>
        </div>
      </section>

      {/* ── How it works ── */}
      <section className="px-4 py-16 sm:py-24 bg-card/40 border-t border-border/60">
        <div className="max-w-4xl mx-auto">
          <div className="text-center mb-12">
            <h2 className="text-2xl sm:text-3xl font-bold mb-3">Get Started in 3 Steps</h2>
            <p className="text-muted-foreground">Up and running in under two minutes</p>
          </div>

          <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
            {steps.map(({ num, title, desc }) => (
              <div key={num} className="relative">
                <div className="text-5xl font-black text-primary/15 mb-3 leading-none">{num}</div>
                <h3 className="font-semibold text-foreground mb-2">{title}</h3>
                <p className="text-sm text-muted-foreground leading-relaxed">{desc}</p>
              </div>
            ))}
          </div>
        </div>
      </section>

      {/* ── Benefits ── */}
      <section className="px-4 py-16 sm:py-24 border-t border-border/60">
        <div className="max-w-4xl mx-auto grid grid-cols-1 md:grid-cols-2 gap-10 items-center">
          <div>
            <h2 className="text-2xl sm:text-3xl font-bold mb-4">Why FinTalk?</h2>
            <p className="text-muted-foreground mb-8">
              Most loan apps just give you numbers. FinTalk explains them — in plain language,
              personalised to your situation.
            </p>
            <Link href="/chat">
              <Button className="gap-2">
                Try It Now <ArrowRight className="w-4 h-4" />
              </Button>
            </Link>
          </div>

          <ul className="space-y-3">
            {benefits.map((b) => (
              <li key={b} className="flex gap-3 items-start">
                <CheckCircle2 className="w-5 h-5 text-emerald-400 shrink-0 mt-0.5" />
                <span className="text-sm text-foreground">{b}</span>
              </li>
            ))}
          </ul>
        </div>
      </section>

      {/* ── CTA ── */}
      <section className="gradient-cta px-4 py-16 sm:py-24 text-center">
        <div className="max-w-2xl mx-auto space-y-5">
          <div className="w-12 h-12 rounded-xl bg-white/10 border border-white/20 flex items-center justify-center mx-auto">
            <Lock className="w-5 h-5 text-white" />
          </div>
          <h2 className="text-2xl sm:text-3xl font-bold text-white">
            Private by Design
          </h2>
          <p className="text-white/75 text-base">
            Your API keys and financial data never leave your browser.
            No account required — start immediately.
          </p>
          <Link href="/chat">
            <Button size="lg" variant="secondary" className="gap-2 mt-2">
              Start for Free
              <ArrowRight className="w-4 h-4" />
            </Button>
          </Link>
        </div>
      </section>

      {/* ── Footer ── */}
      <footer className="border-t border-border bg-card/60 px-4 py-6">
        <div className="max-w-6xl mx-auto flex flex-col sm:flex-row items-center justify-between gap-2 text-xs text-muted-foreground">
          <span className="font-semibold text-foreground">FinTalk</span>
          <span>AI-Powered Loan Advisory · Built for TGBH</span>
          <span>Gemini 2.0 Flash · Sarvam AI</span>
        </div>
      </footer>
    </div>
  )
}
