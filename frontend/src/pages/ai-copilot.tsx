import { useMemo, useState } from 'react'
import { Send, Sparkles } from 'lucide-react'
import { Button } from '@/shared/ui/button'
import { Input } from '@/shared/ui/input'
import { PageHeader } from '@/shared/ui/page-header'
import { SectionCard } from '@/shared/ui/section-card'
import { useAICopilotHistory, useAIPrompts } from '@/features/ai/hooks/ai-hooks'

export function AICopilotPage() {
  const [draft, setDraft] = useState('')
  const [conversation, setConversation] = useState<Array<{ id: string; role: string; message: string }>>([])
  const historyQuery = useAICopilotHistory()
  const promptsQuery = useAIPrompts()

  const history = historyQuery.data ?? []
  const prompts = promptsQuery.data ?? []

  const mergedConversation = useMemo(() => [...history, ...conversation], [conversation, history])

  const sendMessage = () => {
    if (!draft.trim()) return
    setConversation((previous) => [
      ...previous,
      { id: `out-${Date.now()}`, role: 'user', message: draft.trim() },
      { id: `in-${Date.now()}`, role: 'assistant', message: 'Analyzing the request and preparing a model-backed insight...' },
    ])
    setDraft('')
  }

  return (
    <div className="space-y-8">
      <PageHeader
        title="AI Copilot"
        description="Interact with your trading terminal using natural prompts and get instant AI commentary."
      />

      <div className="grid gap-6 xl:grid-cols-[1.5fr_0.5fr]">
        <SectionCard
          title="AI Terminal"
          description="A chat-style workspace for trading intelligence and AI-driven recommendations."
        >
          <div className="space-y-4">
            {mergedConversation.map((entry) => (
              <div key={entry.id} className={`rounded-3xl border p-4 ${entry.role === 'assistant' ? 'border-slate-700 bg-slate-950/80' : 'border-slate-800 bg-slate-900/80'}`}>
                <p className="text-xs uppercase tracking-[0.24em] text-slate-500">{entry.role}</p>
                <p className="mt-2 text-sm text-slate-200">{entry.message}</p>
              </div>
            ))}
          </div>
        </SectionCard>

        <SectionCard title="Suggested Prompts" description="Use these prompts to accelerate insights.">
          <div className="space-y-3">
            {prompts.map((prompt) => (
              <Button key={prompt} variant="ghost" className="w-full justify-between px-4 py-3 text-left text-sm text-slate-200" onClick={() => setDraft(prompt)}>
                <span>{prompt}</span>
                <Sparkles className="h-4 w-4 text-amber-300" />
              </Button>
            ))}
          </div>
        </SectionCard>
      </div>

      <SectionCard title="Quick Actions" description="Execute AI workflows directly from the command line." actions={<Send className="h-4 w-4 text-white" />}>
        <div className="space-y-4">
          <div className="rounded-3xl border border-slate-800/90 bg-slate-950/70 p-4">
            <p className="text-sm text-slate-400">Type a prompt to generate an AI trade commentary.</p>
            <div className="mt-4 flex gap-3">
              <Input value={draft} onChange={(event) => setDraft(event.target.value)} placeholder="Ask AI about BTC, risk, or strategy" className="flex-1 border-slate-800 bg-slate-900 text-slate-100" />
              <Button variant="secondary" size="lg" onClick={sendMessage}>
                Send
              </Button>
            </div>
          </div>
          <div className="grid gap-4 sm:grid-cols-2">
            <div className="rounded-3xl border border-slate-800/90 bg-slate-950/70 p-4">
              <p className="text-sm text-slate-400">Ticker quick actions</p>
              <p className="mt-2 text-white">Launch analysis on any symbol from the watchlist.</p>
            </div>
            <div className="rounded-3xl border border-slate-800/90 bg-slate-950/70 p-4">
              <p className="text-sm text-slate-400">Context cards</p>
              <p className="mt-2 text-white">Attach positions, alerts, and strategy signals to your prompt.</p>
            </div>
          </div>
        </div>
      </SectionCard>
    </div>
  )
}
