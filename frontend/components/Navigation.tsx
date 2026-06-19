'use client'

import Link from 'next/link'
import { usePathname } from 'next/navigation'
import { Home, MessageSquare, Settings, CreditCard } from 'lucide-react'
import { cn } from '@/lib/utils'

const links = [
  { href: '/', label: 'Home', icon: Home },
  { href: '/chat', label: 'Chat', icon: MessageSquare },
  { href: '/settings', label: 'Settings', icon: Settings },
]

export default function Navigation() {
  const pathname = usePathname()

  return (
    <>
      {/* ── Desktop top nav ── */}
      <nav className="border-b border-border/60 bg-card/80 backdrop-blur-sm sticky top-0 z-40 shrink-0">
        <div className="max-w-7xl mx-auto px-4 sm:px-6">
          <div className="flex items-center justify-between h-14">
            {/* Logo */}
            <Link href="/" className="flex items-center gap-2 group">
              <div className="w-7 h-7 rounded-lg bg-primary flex items-center justify-center shadow-[0_0_12px_-2px_var(--color-primary)]">
                <CreditCard className="w-3.5 h-3.5 text-primary-foreground" />
              </div>
              <span className="font-bold text-base text-foreground group-hover:text-primary transition-colors">
                FinTalk
              </span>
            </Link>

            {/* Desktop links */}
            <div className="hidden sm:flex items-center gap-1">
              {links.map(({ href, label, icon: Icon }) => {
                const active = pathname === href
                return (
                  <Link
                    key={href}
                    href={href}
                    className={cn(
                      'relative px-3 py-2 rounded-md text-sm font-medium transition-all flex items-center gap-1.5',
                      active
                        ? 'text-primary'
                        : 'text-muted-foreground hover:text-foreground hover:bg-muted/60'
                    )}
                  >
                    <Icon className="w-4 h-4" />
                    {label}
                    {active && (
                      <span className="absolute bottom-0 left-1/2 -translate-x-1/2 w-4 h-0.5 rounded-full bg-primary" />
                    )}
                  </Link>
                )
              })}
            </div>
          </div>
        </div>
      </nav>

      {/* ── Mobile bottom nav ── */}
      <nav className="sm:hidden fixed bottom-0 inset-x-0 z-50 border-t border-border/60 bg-card/90 backdrop-blur-sm">
        <div className="flex">
          {links.map(({ href, label, icon: Icon }) => {
            const active = pathname === href
            return (
              <Link
                key={href}
                href={href}
                className={cn(
                  'flex-1 flex flex-col items-center gap-0.5 py-3 text-[10px] font-medium transition-colors',
                  active ? 'text-primary' : 'text-muted-foreground'
                )}
              >
                <Icon className={cn('w-5 h-5 transition-transform', active && 'scale-110')} />
                {label}
                {active && (
                  <span className="absolute top-0 left-1/2 -translate-x-1/2 w-6 h-0.5 rounded-full bg-primary" />
                )}
              </Link>
            )
          })}
        </div>
      </nav>
    </>
  )
}
