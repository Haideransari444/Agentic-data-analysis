"use client"

import { useState, useRef, useEffect } from "react"
import { Send, Paperclip, X, MessageCircle } from "lucide-react"
import {
  BarChart,
  Bar,
  LineChart,
  Line,
  PieChart,
  Pie,
  Cell,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  ResponsiveContainer,
} from "recharts"
import { Button } from "@/components/ui/button"
import { Input } from "@/components/ui/input"
import { Card } from "@/components/ui/card"
import { useChat } from "@/providers/chat-provider"
import type { ChatMessage } from "@/providers/chat-provider"

type VisualizationPayload = NonNullable<ChatMessage["visualization"]>

const SUGGESTED_QUERIES = ["Show sales by country", "Top 5 cities", "Generate report", "Upload data"]
const CHART_COLORS = ["#0ea5e9", "#22d3ee", "#a855f7", "#f472b6", "#fb923c", "#34d399"]

export function ChatInterface() {
  const { messages, addMessage, conversationId, setConversationId } = useChat()
  const [input, setInput] = useState("")
  const [isMinimized, setIsMinimized] = useState(false)
  const [isLoading, setIsLoading] = useState(false)
  const messagesEndRef = useRef<HTMLDivElement>(null)
  const scrollAreaRef = useRef<HTMLDivElement>(null)

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: "smooth" })
  }

  useEffect(() => {
    scrollToBottom()
  }, [messages])

  const handleSendMessage = async (text?: string) => {
    const messageText = text || input.trim()
    if (!messageText) return

    setInput("")
    setIsLoading(true)

    const userMessage: ChatMessage = {
      id: Date.now().toString(),
      role: "user",
      content: messageText,
      timestamp: new Date(),
    }
    addMessage(userMessage)

    try {
      const response = await fetch('/api/chat', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ message: messageText, conversationId })
      })
      
      if (!response.ok) throw new Error('API request failed')
      
      const data = await response.json()
      if (data.conversationId) {
        setConversationId(data.conversationId)
      }
      
      const messageId = (Date.now() + 1).toString()
      const aiMessage: ChatMessage = {
        id: messageId,
        role: "ai",
        content: data.response || 'No response from AI',
        timestamp: new Date(),
        visualization: data.visualization
      }
      addMessage(aiMessage)
    } catch (error) {
      console.error('Chat error:', error)
      const errorMessage: ChatMessage = {
        id: (Date.now() + 1).toString(),
        role: "ai",
        content: "Sorry, I'm having trouble connecting to the backend. Please check if the API server is running.",
        timestamp: new Date(),
      }
      addMessage(errorMessage)
    } finally {
      setIsLoading(false)
    }
  }

  if (isMinimized) {
    return (
      <Button
        size="icon"
        className="fixed bottom-6 right-6 z-40 rounded-full h-10 w-10 bg-primary text-primary-foreground shadow-lg hover:bg-primary/90 transition-all"
        onClick={() => setIsMinimized(false)}
        title="Open chat"
      >
        <MessageCircle className="h-4 w-4" />
      </Button>
    )
  }

  return (
    <Card className="fixed bottom-6 right-6 z-40 w-72 h-[420px] flex flex-col shadow-lg border-2 border-primary bg-card overflow-hidden rounded-lg">
      <div className="flex items-center justify-between px-4 py-3 border-b border-border bg-card">
        <h3 className="text-sm font-semibold text-foreground">Chat</h3>
        <Button
          size="icon"
          variant="ghost"
          onClick={() => setIsMinimized(true)}
          className="h-6 w-6 text-muted-foreground hover:text-foreground hover:bg-muted/50 rounded transition-colors"
        >
          <X className="h-4 w-4" />
        </Button>
      </div>

      <div ref={scrollAreaRef} className="flex-1 overflow-y-auto p-3 space-y-2">
        {messages.map((msg) => (
          <div
            key={msg.id}
            className={`flex ${msg.role === "user" ? "justify-end" : "justify-start"} animate-slide-up`}
          >
            <div
              className={`max-w-xs px-3 py-2 rounded text-sm leading-normal ${
                msg.role === "user"
                  ? "bg-primary text-primary-foreground"
                  : "bg-muted text-foreground border border-border"
              }`}
            >
              <p className="text-sm">{msg.content}</p>
              {msg.visualization && msg.role === "ai" && <VisualizationPreview visualization={msg.visualization} />}
            </div>
          </div>
        ))}
        {isLoading && (
          <div className="flex justify-start">
            <div className="bg-muted border border-border rounded px-3 py-2">
              <div className="flex gap-1">
                <div className="w-2 h-2 bg-primary rounded-full animate-bounce" />
                <div className="w-2 h-2 bg-primary rounded-full animate-bounce" style={{ animationDelay: "0.1s" }} />
                <div className="w-2 h-2 bg-primary rounded-full animate-bounce" style={{ animationDelay: "0.2s" }} />
              </div>
            </div>
          </div>
        )}
        <div ref={messagesEndRef} />
      </div>

      {messages.length === 0 && (
        <div className="px-3 py-2 border-t border-border space-y-2 bg-card">
          <p className="text-xs font-medium text-muted-foreground">Quick queries</p>
          <div className="grid grid-cols-2 gap-1.5">
            {SUGGESTED_QUERIES.map((query) => (
              <button
                key={query}
                onClick={() => handleSendMessage(query)}
                className="text-xs px-2 py-1 rounded bg-muted text-foreground hover:bg-primary/20 hover:text-primary border border-border/50 transition-all duration-200 hover:border-primary/50 active:scale-95"
              >
                {query}
              </button>
            ))}
          </div>
        </div>
      )}

      <div className="p-3 border-t border-border space-y-2 bg-card">
        <div className="flex gap-2">
          <Input
            value={input}
            onChange={(e) => setInput(e.target.value)}
            onKeyPress={(e) => {
              if (e.key === "Enter" && !e.shiftKey) {
                e.preventDefault()
                handleSendMessage()
              }
            }}
            placeholder="Ask something..."
            className="flex-1 h-8 text-sm bg-muted border-border text-foreground placeholder:text-muted-foreground focus:ring-1 focus:ring-primary"
            disabled={isLoading}
          />
          <Button
            size="icon"
            onClick={() => handleSendMessage()}
            disabled={isLoading || !input.trim()}
            className="h-8 w-8 bg-primary text-primary-foreground hover:bg-primary/90 hover:shadow-md transition-all duration-200 active:scale-95"
          >
            <Send className="h-3.5 w-3.5" />
          </Button>
        </div>
        <div className="flex gap-1.5">
          <Button
            size="sm"
            variant="outline"
            className="flex-1 h-7 text-xs border-border text-foreground hover:bg-muted/70 hover:border-primary/50 bg-transparent transition-all duration-200 active:scale-95"
          >
            <Paperclip className="h-3 w-3 mr-1" />
            Attach
          </Button>
        </div>
      </div>
    </Card>
  )
}

function VisualizationPreview({ visualization }: { visualization: VisualizationPayload }) {
  const data = Array.isArray(visualization.data) ? visualization.data : []
  if (data.length === 0) {
    return <div className="mt-2 text-xs text-muted-foreground italic">Visualization data unavailable.</div>
  }

  const sample = data[0] ?? {}
  const keys = Object.keys(sample)
  const labelKey = visualization.config?.labelKey || visualization.config?.xKey || keys[0]
  const valueKey = visualization.config?.valueKey || visualization.config?.yKey || keys.find((key) => key !== labelKey) || keys[0]

  if (!labelKey || !valueKey) {
    return <div className="mt-2 text-xs text-muted-foreground italic">Cannot determine visualization fields.</div>
  }

  return (
    <div className="mt-2 rounded border border-dashed border-border/80 bg-background p-2">
      <div className="text-[10px] uppercase tracking-wide font-semibold text-muted-foreground mb-1">
        AI Visualization ({visualization.type})
      </div>
      <div className="h-40">
        <ResponsiveContainer width="100%" height="100%">
          {visualization.type === "bar" && <BarPreview data={data} labelKey={labelKey} valueKey={valueKey} />}
          {visualization.type === "line" && <LinePreview data={data} labelKey={labelKey} valueKey={valueKey} />}
          {visualization.type === "pie" && <PiePreview data={data} labelKey={labelKey} valueKey={valueKey} />}
        </ResponsiveContainer>
      </div>
    </div>
  )
}

function BarPreview({ data, labelKey, valueKey }: { data: any[]; labelKey: string; valueKey: string }) {
  return (
    <BarChart data={data}>
      <CartesianGrid strokeDasharray="3 3" stroke="#e5e7eb" />
      <XAxis dataKey={labelKey} stroke="#9ca3af" hide={data.length > 6} />
      <YAxis stroke="#9ca3af" width={40} />
      <Tooltip />
      <Bar dataKey={valueKey} fill="#0ea5e9" radius={[4, 4, 0, 0]} />
    </BarChart>
  )
}

function LinePreview({ data, labelKey, valueKey }: { data: any[]; labelKey: string; valueKey: string }) {
  return (
    <LineChart data={data}>
      <CartesianGrid strokeDasharray="3 3" stroke="#e5e7eb" />
      <XAxis dataKey={labelKey} stroke="#9ca3af" hide={data.length > 8} />
      <YAxis stroke="#9ca3af" width={40} />
      <Tooltip />
      <Line type="monotone" dataKey={valueKey} stroke="#a855f7" strokeWidth={2} dot={false} />
    </LineChart>
  )
}

function PiePreview({ data, labelKey, valueKey }: { data: any[]; labelKey: string; valueKey: string }) {
  return (
    <PieChart>
      <Pie data={data} dataKey={valueKey} nameKey={labelKey} outerRadius={60} label>
        {data.map((_, index) => (
          <Cell key={index} fill={CHART_COLORS[index % CHART_COLORS.length]} />
        ))}
      </Pie>
      <Tooltip />
    </PieChart>
  )
}
