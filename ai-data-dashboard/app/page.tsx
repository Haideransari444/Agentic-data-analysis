"use client"

import { AppLayout } from "@/components/layout/app-layout"
import { ChatInterface } from "@/components/chat/chat-interface"
import { KPICards } from "@/components/dashboard/kpi-cards"
import { ChartsGrid } from "@/components/dashboard/charts-grid"
import { ActivityFeed } from "@/components/dashboard/activity-feed"
import { Card } from "@/components/ui/card"
import { Upload, Zap, FileText } from "lucide-react"
import { useRouter } from "next/navigation"

export default function DashboardPage() {
  const router = useRouter()

  return (
    <AppLayout>
      <div className="space-y-8 pb-32">
        <div className="animate-slide-up">
          <h1 className="text-5xl font-bold bg-gradient-to-r from-foreground via-primary to-accent bg-clip-text text-transparent text-balance">
            DataForge Intelligence
          </h1>
          <p className="text-lg text-muted-foreground mt-3 max-w-2xl">
            Unlock insights with AI-powered analytics. Real-time data visualization meets natural language processing.
          </p>
        </div>

        {/* KPI Cards */}
        <KPICards />

        {/* Quick Actions */}
        <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
          {[
            { icon: Upload, title: "Upload Data", desc: "Import CSV files", href: "/upload" },
            { icon: Zap, title: "Run Analysis", desc: "Ask AI anything", href: "/analysis" },
            { icon: FileText, title: "Generate Report", desc: "PDF exports", href: "/reports" },
          ].map((action, i) => {
            const Icon = action.icon
            return (
              <button
                key={action.title}
                type="button"
                onClick={() => router.push(action.href)}
                className="text-left w-full"
              >
                <Card
                  className="p-6 cursor-pointer hover:border-primary/70 hover:shadow-lg hover:shadow-primary/15 transition-all duration-300 animate-slide-up border-border/50 bg-card/50 backdrop-blur-sm group overflow-hidden active:scale-95"
                  style={{ animationDelay: `${100 + i * 50}ms` }}
                >
                  <div className="absolute inset-0 bg-gradient-to-br from-primary/5 to-transparent opacity-0 group-hover:opacity-100 transition-opacity duration-300" />
                  <div className="relative">
                    <Icon className="h-8 w-8 text-primary/70 group-hover:text-primary group-hover:scale-120 transition-all duration-300" />
                    <h3 className="font-semibold mt-3 group-hover:text-primary transition-colors duration-300">
                      {action.title}
                    </h3>
                    <p className="text-sm text-muted-foreground mt-1">{action.desc}</p>
                  </div>
                </Card>
              </button>
            )
          })}
        </div>

        {/* Charts */}
        <ChartsGrid />

        {/* Activity Feed */}
        <ActivityFeed />
      </div>

      {/* Chat Interface */}
      <ChatInterface />
    </AppLayout>
  )
}
