import { useMemo, useState } from 'react'
import { Link, useLocation } from 'react-router-dom'
import {
  BarChart3,
  BookOpen,
  Cpu,
  LayoutDashboard,
  List,
  LogOut,
  Radar,
  Search,
  ServerCog,
  Sparkles,
  TrendingUp,
  Users,
  ChevronDown,
  Globe2,
} from 'lucide-react'
import { cn } from '@/shared/lib/cn'
import { Button } from '@/shared/ui/button'
import { useLogout } from '@/features/auth/hooks/auth-hooks'
import Logo from '@/assets/logo.jpg'

const groups = [
  {
    title: 'Core',
    items: [
      { name: 'Dashboard', href: '/dashboard', icon: LayoutDashboard },
      { name: 'Watchlist', href: '/watchlist', icon: List },
      { name: 'Portfolio', href: '/portfolio', icon: BarChart3 },
      { name: 'Alerts', href: '/alerts', icon: Sparkles },
      { name: 'Journal', href: '/journal', icon: BookOpen },
    ],
  },
  {
    title: 'Markets',
    items: [
      { name: 'Markets', href: '/markets', icon: Globe2 },
      { name: 'Analytics', href: '/analytics', icon: TrendingUp },
      { name: 'Scanner', href: '/scanner', icon: Search },
    ],
  },
  {
    title: 'AI & Research',
    items: [
      { name: 'AI Copilot', href: '/copilot', icon: Sparkles },
      { name: 'Signals', href: '/signals', icon: Radar },
      { name: 'AI Lab', href: '/ai-lab', icon: Cpu },
      { name: 'Strategies', href: '/strategies', icon: Users },
      { name: 'Backtesting', href: '/backtesting', icon: BarChart3 },
    ],
  },
  {
    title: 'Admin',
    items: [
      { name: 'Profile', href: '/profile', icon: Users },
      { name: 'Support', href: '/support', icon: BookOpen },
      { name: 'User access', href: '/admin/users', icon: Users },
      { name: 'ML status', href: '/admin/ml-training', icon: Cpu },
      { name: 'System status', href: '/admin/system-status', icon: ServerCog },
    ],
  },
]

export function Sidebar() {
  const location = useLocation()
  const logoutMutation = useLogout()
  const [openGroups, setOpenGroups] = useState<Record<string, boolean>>({
    Core: true,
    Markets: true,
    'AI & Research': false,
    Admin: false,
  })

  const activePath = useMemo(() => location.pathname, [location.pathname])

  return (
    <div className="flex h-full w-72 flex-col bg-slate-950 border-r border-slate-900 text-slate-100">
      <div className="flex h-16 items-center px-6 border-b border-slate-800">
        <img src={Logo} alt="SwingTrader AI" className="h-8 w-8" />
        {/* <h1 className="ml-3 text-lg font-semibold tracking-tight">SwingTrader AI</h1> */}
      </div>

      <div className="flex-1 overflow-y-auto px-3 py-4">
        {groups.map((group) => (
          <div key={group.title} className="mb-4 rounded-3xl border border-slate-800/90 bg-slate-900/70 p-3">
            <button
              type="button"
              onClick={() =>
                setOpenGroups((prev) => ({
                  ...prev,
                  [group.title]: !prev[group.title],
                }))
              }
              className="flex w-full items-center justify-between rounded-2xl px-3 py-2 text-left text-sm font-semibold text-slate-200 transition hover:bg-slate-800"
            >
              <span>{group.title}</span>
              <ChevronDown
                className={cn(
                  'h-4 w-4 transition-transform duration-200',
                  openGroups[group.title] && 'rotate-180'
                )}
              />
            </button>

            {openGroups[group.title] && (
              <div className="mt-3 space-y-2">
                {group.items.map((item) => {
                  const isActive = activePath === item.href
                  return (
                    <Link key={item.name} to={item.href}>
                      <Button
                        variant={isActive ? 'secondary' : 'ghost'}
                        className={cn(
                          'w-full justify-start rounded-2xl px-3 py-3 text-sm',
                          isActive && 'bg-slate-800 text-white'
                        )}
                      >
                        <item.icon className="mr-3 h-4 w-4" />
                        {item.name}
                      </Button>
                    </Link>
                  )
                })}
              </div>
            )}
          </div>
        ))}
      </div>

      <div className="border-t border-slate-800 p-4">
        <Button
          variant="ghost"
          className="w-full justify-start text-rose-400 hover:text-rose-300"
          onClick={() => logoutMutation.mutate()}
          disabled={logoutMutation.isPending}
        >
          <LogOut className="mr-3 h-4 w-4" />
          {logoutMutation.isPending ? 'Signing out...' : 'Sign out'}
        </Button>
      </div>
    </div>
  )
}
