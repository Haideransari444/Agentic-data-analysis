"use client"

import { useMemo, useState } from "react"
import { AppLayout } from "@/components/layout/app-layout"
import { ChatInterface } from "@/components/chat/chat-interface"
import { Card } from "@/components/ui/card"
import { Button } from "@/components/ui/button"
import { Badge } from "@/components/ui/badge"
import { Textarea } from "@/components/ui/textarea"
import { Download, Eye, Loader2, AlertCircle, FileText } from "lucide-react"
import { useReportGeneration } from "@/lib/api-client"

const reports = [
  { id: 1, title: "City Sales Analysis", date: "Nov 30, 2024", icon: "📊" },
  { id: 2, title: "Q4 Executive Summary", date: "Nov 28, 2024", icon: "📈" },
  { id: 3, title: "Product Performance Report", date: "Nov 25, 2024", icon: "🎯" },
  { id: 4, title: "Customer Segmentation", date: "Nov 20, 2024", icon: "👥" },
  { id: 5, title: "Revenue Forecast 2025", date: "Nov 15, 2024", icon: "🔮" },
  { id: 6, title: "Market Trends Analysis", date: "Nov 10, 2024", icon: "📉" },
]

const REPORT_TYPES = [
  { label: "Executive Summary", value: "executive-summary", template: "Executive summary of key performance metrics" },
  { label: "Detailed Analysis", value: "detailed-analysis", template: "Detailed breakdown of sales, customers, and products" },
  { label: "Custom Report", value: "custom", template: "Custom analysis" },
]

const TIME_PERIODS = [
  { label: "Last 30 days", value: "30d" },
  { label: "Last Quarter", value: "quarter" },
  { label: "Last Year", value: "year" },
  { label: "Custom Range", value: "custom" },
]

export default function ReportsPage() {
  const [reportType, setReportType] = useState(REPORT_TYPES[0].value)
  const [timePeriod, setTimePeriod] = useState(TIME_PERIODS[0].value)
  const [notes, setNotes] = useState("")
  const { generateReport, generating, status, error } = useReportGeneration()

  const requestSummary = useMemo(() => {
    const typeLabel = REPORT_TYPES.find((t) => t.value === reportType)?.label || "Report"
    const periodLabel = TIME_PERIODS.find((t) => t.value === timePeriod)?.label || "Recent"
    return `${typeLabel} • ${periodLabel}`
  }, [reportType, timePeriod])

  const buildQuery = () => {
    const typeTemplate = REPORT_TYPES.find((t) => t.value === reportType)?.template || ""
    const periodTemplate = TIME_PERIODS.find((t) => t.value === timePeriod)?.label || ""
    return [typeTemplate, `Time period: ${periodTemplate}`, notes.trim()].filter(Boolean).join(" | ")
  }

  const handleGenerate = async () => {
    if (generating) return
    const query = buildQuery()
    if (!query.trim()) return
    await generateReport({ query, format: "pdf" })
  }

  const handleDownload = () => {
    if (status?.fileUrl) {
      window.open(status.fileUrl, "_blank")
    }
  }

  return (
    <AppLayout>
      <div className="space-y-6 pb-32">
        <div className="flex items-center justify-between">
          <div>
            <h1 className="text-3xl font-bold">Generated Reports</h1>
            <p className="text-muted-foreground">View and download your analysis reports</p>
          </div>
          <Button className="gap-2" onClick={handleGenerate} disabled={generating}>
            {generating ? <Loader2 className="h-4 w-4 animate-spin" /> : "+"} Generate Report
          </Button>
        </div>

        {/* Report Gallery */}
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
          {reports.map((report) => (
            <Card key={report.id} className="p-6 hover:shadow-lg transition-shadow">
              <div className="text-4xl mb-3">{report.icon}</div>
              <h3 className="font-semibold mb-1">{report.title}</h3>
              <p className="text-sm text-muted-foreground mb-4">{report.date}</p>
              <div className="flex gap-2">
                <Button size="sm" variant="outline" className="flex-1 gap-1 bg-transparent">
                  <Eye className="h-3 w-3" />
                  View
                </Button>
                <Button size="sm" className="flex-1 gap-1">
                  <Download className="h-3 w-3" />
                  PDF
                </Button>
              </div>
            </Card>
          ))}
        </div>

        {/* Report Generator */}
        <Card className="p-6 space-y-5">
          <div className="flex items-center justify-between">
            <div>
              <h2 className="text-xl font-semibold">Generate New Report</h2>
              <p className="text-sm text-muted-foreground">Describe what you need and we will produce a PDF.</p>
            </div>
            <Badge variant="outline" className="text-xs uppercase tracking-wide">
              {requestSummary}
            </Badge>
          </div>
          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
            <div>
              <label className="text-sm font-medium">Report Type</label>
              <select
                className="w-full mt-2 p-2 border rounded-lg bg-background"
                value={reportType}
                onChange={(e) => setReportType(e.target.value)}
              >
                {REPORT_TYPES.map((type) => (
                  <option key={type.value} value={type.value}>
                    {type.label}
                  </option>
                ))}
              </select>
            </div>
            <div>
              <label className="text-sm font-medium">Time Period</label>
              <select
                className="w-full mt-2 p-2 border rounded-lg bg-background"
                value={timePeriod}
                onChange={(e) => setTimePeriod(e.target.value)}
              >
                {TIME_PERIODS.map((period) => (
                  <option key={period.value} value={period.value}>
                    {period.label}
                  </option>
                ))}
              </select>
            </div>
          </div>
          <div>
            <label className="text-sm font-medium">Additional Notes or Metrics</label>
            <Textarea
              className="mt-2"
              rows={4}
              placeholder="Example: Highlight top 5 cities, include YoY growth, focus on automotive category"
              value={notes}
              onChange={(e) => setNotes(e.target.value)}
            />
          </div>
          {error && (
            <div className="flex items-center gap-2 text-sm text-destructive">
              <AlertCircle className="h-4 w-4" /> {error}
            </div>
          )}
          <div className="flex flex-col gap-3">
            <Button className="w-full gap-2" onClick={handleGenerate} disabled={generating}>
              {generating ? <Loader2 className="h-4 w-4 animate-spin" /> : <FileText className="h-4 w-4" />}
              {generating ? "Generating Report..." : "Generate Report"}
            </Button>
            {status && (
              <div className="rounded-lg border border-dashed border-border/60 p-4 text-sm">
                <div className="flex items-center justify-between">
                  <div>
                    <p className="font-semibold">Status: {status.status}</p>
                    <p className="text-xs text-muted-foreground">{status.message}</p>
                  </div>
                  <p className="text-xs text-muted-foreground">Progress: {status.progress}%</p>
                </div>
                {status.fileUrl && (
                  <Button className="mt-3 w-full" variant="outline" onClick={handleDownload}>
                    <Download className="h-4 w-4 mr-2" /> Download PDF
                  </Button>
                )}
              </div>
            )}
          </div>
        </Card>
      </div>
      <ChatInterface />
    </AppLayout>
  )
}
