"use client"

import { Card } from "@/components/ui/card"
import { Database, TrendingUp, Zap, FileText } from "lucide-react"
import { useDashboardStats } from "@/lib/api-client"

export function KPICards() {
  const { stats, loading, error } = useDashboardStats()

  if (error) {
    return (
      <Card className="p-4 border-destructive">
        <p className="text-sm text-destructive">Error loading stats: {error}</p>
      </Card>
    )
  }

  const kpis = [
    {
      title: "Tables",
      value: loading ? "..." : (stats?.tables?.toString() || "0"),
      subtitle: "Active tables",
      icon: Database,
    },
    {
      title: "Records",
      value: loading ? "..." : (stats?.records ? (stats.records / 1000).toFixed(1) + "K" : "0"),
      subtitle: "Total records",
      icon: TrendingUp,
    },
    {
      title: "AI Status",
      value: loading ? "..." : (stats?.aiStatus || "Offline"),
      subtitle: `${stats?.queriesCount || 0} queries today`,
      icon: Zap,
    },
    {
      title: "Reports",
      value: loading ? "..." : (stats?.reportsCount?.toString() || "0"),
      subtitle: "Generated reports",
      icon: FileText,
    },
  ]

  return (
    <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
      {kpis.map((kpi, i) => {
        const Icon = kpi.icon
        return (
          <Card
            key={i}
            className="p-4 border border-border hover:border-primary/70 hover:shadow-md hover:shadow-primary/10 transition-all duration-300 cursor-pointer group"
            style={{ animationDelay: `${i * 50}ms` }}
          >
            <div className="flex items-start justify-between">
              <div>
                <p className="text-xs font-medium text-muted-foreground uppercase tracking-tight mb-1">{kpi.title}</p>
                <h3 className="text-2xl font-semibold text-foreground group-hover:text-primary transition-colors duration-300">
                  {kpi.value}
                </h3>
                <p className="text-xs text-muted-foreground mt-2">{kpi.subtitle}</p>
              </div>
              <Icon className="h-5 w-5 text-primary/60 group-hover:text-primary group-hover:scale-110 transition-all duration-300" />
            </div>
          </Card>
        )
      })}
    </div>
  )
}
