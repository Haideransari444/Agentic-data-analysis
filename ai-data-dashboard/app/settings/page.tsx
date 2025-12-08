"use client"

import { useEffect, useMemo, useState } from "react"
import { AppLayout } from "@/components/layout/app-layout"
import { ChatInterface } from "@/components/chat/chat-interface"
import { Card } from "@/components/ui/card"
import { Button } from "@/components/ui/button"
import { Input } from "@/components/ui/input"
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from "@/components/ui/select"
import { Switch } from "@/components/ui/switch"
import { AlertCircle, CheckCircle2, RefreshCcw } from "lucide-react"

type ThemeOption = "system" | "light" | "dark"
type LanguageOption = "en" | "es" | "fr" | "de"

interface SettingsState {
  theme: ThemeOption
  language: LanguageOption
  chatSuggestions: boolean
  autoReports: boolean
  apiKey: string
  baseUrl: string
}

const DEFAULT_SETTINGS: SettingsState = {
  theme: "system",
  language: "en",
  chatSuggestions: true,
  autoReports: false,
  apiKey: "",
  baseUrl: process.env.NEXT_PUBLIC_API_BASE_URL || "http://localhost:8000",
}

export default function SettingsPage() {
  const [settings, setSettings] = useState<SettingsState>(DEFAULT_SETTINGS)
  const [isSaving, setIsSaving] = useState(false)
  const [saveMessage, setSaveMessage] = useState<string | null>(null)
  const [testStatus, setTestStatus] = useState<"idle" | "testing" | "success" | "error">("idle")
  const [testMessage, setTestMessage] = useState<string>("")

  useEffect(() => {
    const stored = localStorage.getItem("dashboard-settings")
    if (stored) {
      try {
        const parsed = JSON.parse(stored)
        setSettings({ ...DEFAULT_SETTINGS, ...parsed })
      } catch {
        setSettings(DEFAULT_SETTINGS)
      }
    }
  }, [])

  const handleChange = <K extends keyof SettingsState>(key: K, value: SettingsState[K]) => {
    setSettings((prev) => ({ ...prev, [key]: value }))
  }

  const handleSave = async () => {
    setIsSaving(true)
    setSaveMessage(null)
    try {
      localStorage.setItem("dashboard-settings", JSON.stringify(settings))
      setSaveMessage("Settings saved locally.")
    } catch (error) {
      setSaveMessage("Failed to save settings.")
    } finally {
      setIsSaving(false)
    }
  }

  const handleReset = () => {
    setSettings(DEFAULT_SETTINGS)
    localStorage.removeItem("dashboard-settings")
    setSaveMessage("Settings reset to defaults.")
  }

  const testConnection = async () => {
    setTestStatus("testing")
    setTestMessage("Testing connection...")
    try {
      const response = await fetch(`${settings.baseUrl}/health`)
      if (!response.ok) {
        throw new Error(`HTTP ${response.status}`)
      }
      const data = await response.json()
      setTestStatus("success")
      setTestMessage(`Connected: ${data.status || "OK"}`)
    } catch (error) {
      setTestStatus("error")
      setTestMessage(error instanceof Error ? error.message : "Connection failed")
    }
  }

  const themeLabel = useMemo(() => {
    switch (settings.theme) {
      case "light":
        return "Light"
      case "dark":
        return "Dark"
      default:
        return "Auto (system preference)"
    }
  }, [settings.theme])

  const languageLabel = useMemo(() => {
    const map: Record<LanguageOption, string> = {
      en: "English",
      es: "Spanish",
      fr: "French",
      de: "German",
    }
    return map[settings.language]
  }, [settings.language])

  return (
    <AppLayout>
      <div className="space-y-6 pb-32">
        <div>
          <h1 className="text-3xl font-bold">Settings</h1>
          <p className="text-muted-foreground">Manage your dashboard preferences</p>
        </div>

        {/* General Settings */}
        <Card className="p-6">
          <h2 className="text-xl font-semibold mb-4">General</h2>
          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
            <div>
              <label className="text-sm font-medium">Theme</label>
              <Select value={settings.theme} onValueChange={(value: ThemeOption) => handleChange("theme", value)}>
                <SelectTrigger className="mt-2">
                  <SelectValue placeholder="Select theme" />
                </SelectTrigger>
                <SelectContent>
                  <SelectItem value="system">Auto (system preference)</SelectItem>
                  <SelectItem value="light">Light</SelectItem>
                  <SelectItem value="dark">Dark</SelectItem>
                </SelectContent>
              </Select>
              <p className="text-xs text-muted-foreground mt-1">Current: {themeLabel}</p>
            </div>
            <div>
              <label className="text-sm font-medium">Language</label>
              <Select value={settings.language} onValueChange={(value: LanguageOption) => handleChange("language", value)}>
                <SelectTrigger className="mt-2">
                  <SelectValue placeholder="Select language" />
                </SelectTrigger>
                <SelectContent>
                  <SelectItem value="en">English</SelectItem>
                  <SelectItem value="es">Spanish</SelectItem>
                  <SelectItem value="fr">French</SelectItem>
                  <SelectItem value="de">German</SelectItem>
                </SelectContent>
              </Select>
              <p className="text-xs text-muted-foreground mt-1">Current: {languageLabel}</p>
            </div>
          </div>
        </Card>

        {/* AI Settings */}
        <Card className="p-6">
          <h2 className="text-xl font-semibold mb-4">AI Assistant</h2>
          <div className="space-y-4">
            <div className="flex items-center justify-between">
              <div>
                <p className="font-medium">Enable Chat Suggestions</p>
                <p className="text-sm text-muted-foreground">Show suggested queries</p>
              </div>
              <Switch
                checked={settings.chatSuggestions}
                onCheckedChange={(value) => handleChange("chatSuggestions", value)}
              />
            </div>
            <div className="flex items-center justify-between">
              <div>
                <p className="font-medium">Auto-Generate Reports</p>
                <p className="text-sm text-muted-foreground">Create reports automatically</p>
              </div>
              <Switch checked={settings.autoReports} onCheckedChange={(value) => handleChange("autoReports", value)} />
            </div>
          </div>
        </Card>

        {/* API Settings */}
        <Card className="p-6">
          <h2 className="text-xl font-semibold mb-4">API Configuration</h2>
          <div className="space-y-4">
            <div>
              <label className="text-sm font-medium">API Key</label>
              <Input
                type="password"
                placeholder="••••••••••••••••"
                value={settings.apiKey}
                onChange={(e) => handleChange("apiKey", e.target.value)}
                className="mt-2"
              />
            </div>
            <div>
              <label className="text-sm font-medium">Base URL</label>
              <Input
                type="text"
                placeholder="https://api.example.com"
                value={settings.baseUrl}
                onChange={(e) => handleChange("baseUrl", e.target.value)}
                className="mt-2"
              />
            </div>
            <div className="flex gap-2">
              <Button
                variant="outline"
                onClick={testConnection}
                disabled={testStatus === "testing"}
                className="gap-2"
              >
                {testStatus === "testing" ? <RefreshCcw className="h-4 w-4 animate-spin" /> : null}
                Test Connection
              </Button>
              {testStatus === "success" && <CheckCircle2 className="h-5 w-5 text-green-500" />}
              {testStatus === "error" && <AlertCircle className="h-5 w-5 text-destructive" />}
            </div>
            {testStatus !== "idle" && (
              <p
                className={`text-sm ${
                  testStatus === "success"
                    ? "text-green-600"
                    : testStatus === "error"
                      ? "text-destructive"
                      : "text-muted-foreground"
                }`}
              >
                {testMessage}
              </p>
            )}
          </div>
        </Card>

        {/* Save Settings */}
        <div className="flex gap-2">
          <Button onClick={handleSave} disabled={isSaving} className="gap-2">
            {isSaving ? <RefreshCcw className="h-4 w-4 animate-spin" /> : null}
            Save Changes
          </Button>
          <Button variant="outline" onClick={handleReset}>
            Reset to Defaults
          </Button>
          {saveMessage && <p className="text-sm text-muted-foreground">{saveMessage}</p>}
        </div>
      </div>
      <ChatInterface />
    </AppLayout>
  )
}
