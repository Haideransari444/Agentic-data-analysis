"use client"

import { useMemo, useState } from "react"
import { AppLayout } from "@/components/layout/app-layout"
import { ChatInterface } from "@/components/chat/chat-interface"
import { Card } from "@/components/ui/card"
import { Button } from "@/components/ui/button"
import { Textarea } from "@/components/ui/textarea"
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from "@/components/ui/select"
import { Badge } from "@/components/ui/badge"
import { Loader2, AlertCircle, Database, RefreshCcw } from "lucide-react"
import { apiClient, type AnalysisResponse, useTables } from "@/lib/api-client"

const SUGGESTED_QUERIES = [
  "Show sales by city",
  "Top 5 products",
  "Revenue by quarter",
  "Customer analysis",
]

export default function AnalysisPage() {
  const { tables, loading: tablesLoading, error: tablesError, refresh } = useTables()
  const [query, setQuery] = useState("")
  const [selectedTable, setSelectedTable] = useState<string>("")
  const [history, setHistory] = useState<string[]>(SUGGESTED_QUERIES)
  const [result, setResult] = useState<AnalysisResponse | null>(null)
  const [analysisError, setAnalysisError] = useState<string | null>(null)
  const [isRunning, setIsRunning] = useState(false)

  const rows = useMemo(() => (Array.isArray(result?.data) ? result.data : []), [result])

  const columnNames = useMemo(() => {
    if (rows.length === 0) return []
    const firstRow = rows[0]
    return typeof firstRow === "object" && firstRow !== null ? Object.keys(firstRow) : []
  }, [rows])

  const handleRunAnalysis = async () => {
    const trimmed = query.trim()
    if (!trimmed) return

    setIsRunning(true)
    setAnalysisError(null)

    try {
      const response = await apiClient.runAnalysis({
        query: trimmed,
        table: selectedTable || undefined,
      })
      setResult(response)
      setHistory((prev) => {
        const next = [trimmed, ...prev.filter((item) => item !== trimmed)]
        return next.slice(0, 8)
      })
    } catch (error) {
      const message = error instanceof Error ? error.message : "Failed to run analysis"
      setAnalysisError(message)
      setResult(null)
    } finally {
      setIsRunning(false)
    }
  }

  const handleClear = () => {
    setQuery("")
    setResult(null)
    setAnalysisError(null)
  }

  const handleSelectHistory = (entry: string) => {
    setQuery(entry)
  }

  return (
    <AppLayout>
      <div className="space-y-6 pb-32">
        <div>
          <h1 className="text-3xl font-bold">AI-Powered Analysis</h1>
          <p className="text-muted-foreground">Ask natural-language questions and run live SQL analysis</p>
        </div>

        <div className="grid grid-cols-1 lg:grid-cols-4 gap-6">
          {/* Query History Sidebar */}
          <Card className="lg:col-span-1 p-4 h-fit space-y-4">
            <div className="flex items-center justify-between">
              <h3 className="font-semibold">Query History</h3>
              <Button variant="ghost" size="icon" className="h-7 w-7" onClick={() => setHistory([])} title="Clear history">
                <RefreshCcw className="h-3.5 w-3.5" />
              </Button>
            </div>
            <div className="space-y-2">
              {history.length === 0 && (
                <p className="text-xs text-muted-foreground">Submit queries to build your history.</p>
              )}
              {history.map((entry) => (
                <button
                  key={entry}
                  onClick={() => handleSelectHistory(entry)}
                  className="w-full text-left text-sm p-2 rounded border border-border/60 hover:border-primary/60 hover:text-primary transition-colors"
                >
                  • {entry}
                </button>
              ))}
            </div>
          </Card>

          {/* Main Panel */}
          <div className="lg:col-span-3 space-y-4">
            {/* Query Input */}
            <Card className="p-6 space-y-4">
              <div className="flex flex-col gap-2">
                <label className="text-sm font-medium">What do you want to analyze?</label>
                <Textarea
                  value={query}
                  onChange={(e) => setQuery(e.target.value)}
                  placeholder="Example: Show total sales by country for 2023"
                  className="min-h-[120px]"
                />
              </div>

              <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                <div>
                  <label className="text-sm font-medium">Target Table (optional)</label>
                  {tablesLoading ? (
                    <div className="mt-2 flex items-center text-sm text-muted-foreground gap-2">
                      <Loader2 className="h-4 w-4 animate-spin" /> Loading tables...
                    </div>
                  ) : tablesError ? (
                    <button
                      onClick={refresh}
                      className="mt-2 flex items-center gap-2 text-sm text-destructive underline"
                    >
                      <AlertCircle className="h-4 w-4" /> Retry loading tables
                    </button>
                  ) : (
                    <Select value={selectedTable} onValueChange={setSelectedTable}>
                      <SelectTrigger className="mt-2">
                        <SelectValue placeholder="Select table (auto-detect if empty)" />
                      </SelectTrigger>
                      <SelectContent>
                        {tables.map((table) => (
                          <SelectItem key={table.name} value={table.name}>
                            {table.name} ({table.rowCount?.toLocaleString()} rows)
                          </SelectItem>
                        ))}
                      </SelectContent>
                    </Select>
                  )}
                </div>
                <div className="rounded-lg border border-dashed border-border/70 p-3 text-xs text-muted-foreground flex gap-2">
                  <Database className="h-4 w-4 text-primary" />
                  Ask for metrics, rankings, filters, or correlations—LLM will generate SQL using the live schema.
                </div>
              </div>

              {analysisError && (
                <div className="flex items-center gap-2 text-sm text-destructive">
                  <AlertCircle className="h-4 w-4" /> {analysisError}
                </div>
              )}

              <div className="flex gap-2 flex-wrap">
                <Button className="gap-2" onClick={handleRunAnalysis} disabled={isRunning || !query.trim()}>
                  {isRunning ? <Loader2 className="h-4 w-4 animate-spin" /> : "🚀"} Run Analysis
                </Button>
                <Button variant="outline" onClick={handleClear} disabled={isRunning}>
                  Clear
                </Button>
              </div>
            </Card>

            {/* Results */}
            <Card className="p-6">
              <div className="flex items-center justify-between mb-4">
                <h3 className="font-semibold">Analysis Results</h3>
                {result?.query && (
                  <Badge variant="outline" className="font-mono text-xs">
                    {result.query.replace(/\s+/g, " ").slice(0, 80)}
                    {result.query.length > 80 ? "…" : ""}
                  </Badge>
                )}
              </div>

              {isRunning ? (
                <div className="flex flex-col items-center justify-center py-16 text-muted-foreground">
                  <Loader2 className="h-10 w-10 animate-spin mb-4" />
                  Running SQL analysis...
                </div>
              ) : result ? (
                <div className="space-y-4">
                  {result.insights && <p className="text-sm text-foreground leading-relaxed">{result.insights}</p>}

                  {columnNames.length > 0 ? (
                    <div className="overflow-x-auto">
                      <table className="w-full text-sm">
                        <thead>
                          <tr className="border-b">
                            {columnNames.map((col) => (
                              <th key={col} className="text-left py-2 px-2 font-semibold whitespace-nowrap">
                                {col}
                              </th>
                            ))}
                          </tr>
                        </thead>
                        <tbody>
                          {rows.slice(0, 50).map((row, idx) => (
                            <tr key={idx} className="border-b hover:bg-muted/40">
                              {columnNames.map((col) => (
                                <td key={col} className="py-2 px-2 whitespace-nowrap">
                                  {(row as Record<string, unknown>)[col]?.toString() || "—"}
                                </td>
                              ))}
                            </tr>
                          ))}
                        </tbody>
                      </table>
                      {rows.length > 50 && (
                        <p className="text-xs text-muted-foreground mt-2">Showing first 50 rows</p>
                      )}
                    </div>
                  ) : (
                    <p className="text-sm text-muted-foreground">No tabular results returned.</p>
                  )}
                </div>
              ) : (
                <div className="py-10 text-center text-muted-foreground text-sm">
                  Ask a question above to view live results.
                </div>
              )}
            </Card>
          </div>
        </div>
      </div>
      <ChatInterface />
    </AppLayout>
  )
}
