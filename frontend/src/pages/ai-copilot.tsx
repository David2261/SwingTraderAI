import { useState } from 'react'
import { Send, Sparkles } from 'lucide-react'

import { Input } from '@/shared/ui/input'
import { Button } from '@/shared/ui/button'
import { GlassCard, SectionCard } from '@/shared/ui'

import { mockAICopilotHistory, mockAIPrompts } from '@/shared/mock/mock-data'

export function AICopilotPage() {
  const [messages, setMessages] = useState(mockAICopilotHistory)
  const [inputValue, setInputValue] = useState('')
  const [isLoading, setIsLoading] = useState(false)

  const handleSendMessage = async () => {
    if (!inputValue.trim()) return

    const userMsg = {
      id: `msg-${Date.now()}`,
      role: 'user' as const,
      message: inputValue,
    }

    setMessages((prev) => [...prev, userMsg])
    setInputValue('')
    setIsLoading(true)

    // Simulate AI response
    setTimeout(() => {
      const responses = [
        'BTC momentum is strong but approaching resistance. Consider scaling into positions instead of chasing prices.',
        'The market is showing signs of consolidation. Watch for volume confirmation on any breakout attempts.',
        'Portfolio risk ratio looks healthy. Current allocation provides good diversification without excess leverage.',
        'SBER breakout pattern is classic continuation setup. Monitor the 305 support level for potential pull-back entry.',
        'Overall market sentiment is cautiously bullish. Key levels to watch: 41200 for BTC and 305 for SBER.',
      ]

      const randomResponse = responses[Math.floor(Math.random() * responses.length)]

      setMessages((prev) => [
        ...prev,
        {
          id: `msg-${Date.now()}`,
          role: 'assistant' as const,
          message: randomResponse,
        },
      ])
      setIsLoading(false)
    }, 1400)
  }

  const handleQuickPrompt = (prompt: string) => {
    setInputValue(prompt)
  }

  return (
    <div className="space-y-6 h-[calc(100vh-200px)] flex flex-col">
      {/* Header */}
      <div className="flex items-start justify-between">
        <div>
          <h1 className="text-3xl font-bold tracking-tight flex items-center gap-3">
            <Sparkles className="h-9 w-9 text-blue-400" />
            AI Copilot Terminal
          </h1>
          <p className="text-slate-400 mt-1">
            Bloomberg Terminal × ChatGPT для трейдинга
          </p>
        </div>
      </div>

      {/* Messages Area */}
      <GlassCard className="flex-1 flex flex-col overflow-hidden">
        <div className="flex-1 overflow-y-auto p-6 space-y-6">
          {messages.length === 0 ? (
            <div className="flex flex-col items-center justify-center h-full text-center py-12">
              <Sparkles className="h-16 w-16 text-slate-600 mb-6" />
              <p className="text-slate-400 text-lg">Начните разговор с AI Copilot</p>
            </div>
          ) : (
            messages.map((msg) => (
              <div
                key={msg.id}
                className={`flex ${msg.role === 'user' ? 'justify-end' : 'justify-start'}`}
              >
                <div
                  className={`max-w-[85%] md:max-w-[70%] px-5 py-3.5 rounded-3xl ${
                    msg.role === 'user'
                      ? 'bg-blue-600/90 text-white'
                      : 'bg-slate-800/80 text-slate-100 border border-slate-700/50'
                  }`}
                >
                  <p className="text-[15px] leading-relaxed">{msg.message}</p>
                </div>
              </div>
            ))
          )}

          {isLoading && (
            <div className="flex justify-start">
              <div className="bg-slate-800/80 border border-slate-700/50 px-5 py-3.5 rounded-3xl">
                <div className="flex gap-1.5">
                  <div className="h-2 w-2 rounded-full bg-slate-400 animate-bounce" />
                  <div className="h-2 w-2 rounded-full bg-slate-400 animate-bounce delay-150" />
                  <div className="h-2 w-2 rounded-full bg-slate-400 animate-bounce delay-300" />
                </div>
              </div>
            </div>
          )}
        </div>

        {/* Input Area */}
        <div className="border-t border-slate-700/50 p-6">
          <div className="flex gap-3">
            <Input
              placeholder="Спросите о рынке, сигналах или портфеле..."
              value={inputValue}
              onChange={(e) => setInputValue(e.target.value)}
              onKeyDown={(e) => {
                if (e.key === 'Enter' && !e.shiftKey) {
                  e.preventDefault()
                  handleSendMessage()
                }
              }}
              className="flex-1 bg-slate-900/70 border-slate-700 text-white placeholder:text-slate-500"
              disabled={isLoading}
            />
            <Button
              onClick={handleSendMessage}
              disabled={isLoading || !inputValue.trim()}
              size="icon"
              className="h-11 w-11 rounded-2xl"
            >
              <Send className="h-5 w-5" />
            </Button>
          </div>
        </div>
      </GlassCard>

      {/* Quick Prompts */}
      <SectionCard
        title="Быстрые промпты"
        description="Нажмите, чтобы быстро задать вопрос"
      >
        <div className="grid gap-3 sm:grid-cols-2">
          {mockAIPrompts.slice(0, 6).map((prompt, i) => (
            <Button
              key={i}
              variant="ghost"
              className="h-auto justify-start px-5 py-3.5 text-left text-sm text-slate-200 hover:bg-slate-800/50 border border-slate-800 hover:border-slate-700"
              onClick={() => handleQuickPrompt(prompt)}
            >
              {prompt}
            </Button>
          ))}
        </div>
      </SectionCard>
    </div>
  )
}
