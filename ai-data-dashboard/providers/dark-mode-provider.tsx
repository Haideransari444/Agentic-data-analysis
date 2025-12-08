"use client"

import type React from "react"

import { useEffect, useState } from "react"

export function DarkModeProvider({ children }: { children: React.ReactNode }) {
  const [isDark, setIsDark] = useState(false)
  const [mounted, setMounted] = useState(false)

  useEffect(() => {
    setMounted(true)
    const isDarkMode =
      localStorage.getItem("dark-mode") === "true" || window.matchMedia("(prefers-color-scheme: dark)").matches
    setIsDark(isDarkMode)
    updateDarkMode(isDarkMode)
  }, [])

  const updateDarkMode = (dark: boolean) => {
    if (dark) {
      document.documentElement.classList.add("dark")
    } else {
      document.documentElement.classList.remove("dark")
    }
  }

  const toggleDarkMode = () => {
    const newState = !isDark
    setIsDark(newState)
    localStorage.setItem("dark-mode", String(newState))
    updateDarkMode(newState)
  }

  if (!mounted) return children

  return (
    <>
      {children}
      <div className="fixed top-4 right-4 z-50">
        <button
          onClick={toggleDarkMode}
          className="p-2 rounded-lg bg-card text-card-foreground hover:bg-border transition-colors"
          aria-label="Toggle dark mode"
        >
          {isDark ? "☀️" : "🌙"}
        </button>
      </div>
    </>
  )
}
