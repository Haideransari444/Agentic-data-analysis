"use client"

import type React from "react"

import { createContext, useContext, useState } from "react"

export interface ChatMessage {
  id: string
  role: "user" | "ai"
  content: string
  timestamp: Date
  visualization?: {
    type: "bar" | "line" | "pie"
    data: any[]
    config?: {
      xKey?: string
      yKey?: string
      labelKey?: string
      valueKey?: string
    }
  }
}

interface ChatContextType {
  messages: ChatMessage[]
  addMessage: (message: ChatMessage) => void
  updateMessage: (id: string, patch: Partial<ChatMessage>) => void
  clearMessages: () => void
  conversationId: string | null
  setConversationId: (conversationId: string | null) => void
}

const ChatContext = createContext<ChatContextType | undefined>(undefined)

export function ChatProvider({ children }: { children: React.ReactNode }) {
  const [messages, setMessages] = useState<ChatMessage[]>([
    {
      id: "1",
      role: "ai",
      content:
        'Hello! I\'m your AI data analyst. How can I help you today? Try asking "Show me sales by country" or "Generate a report".',
      timestamp: new Date(),
    },
  ])
  const [conversationId, setConversationId] = useState<string | null>(null)

  const addMessage = (message: ChatMessage) => {
    setMessages((prev) => [...prev, message])
  }

  const updateMessage = (id: string, patch: Partial<ChatMessage>) => {
    setMessages((prev) => prev.map((msg) => (msg.id === id ? { ...msg, ...patch } : msg)))
  }

  const clearMessages = () => {
    setMessages([])
    setConversationId(null)
  }

  return (
    <ChatContext.Provider value={{ messages, addMessage, updateMessage, clearMessages, conversationId, setConversationId }}>
      {children}
    </ChatContext.Provider>
  )
}

export function useChat() {
  const context = useContext(ChatContext)
  if (!context) {
    throw new Error("useChat must be used within ChatProvider")
  }
  return context
}
