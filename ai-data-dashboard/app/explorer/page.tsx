"use client"

import { AppLayout } from "@/components/layout/app-layout"
import { ChatInterface } from "@/components/chat/chat-interface"
import { Card } from "@/components/ui/card"
import { Button } from "@/components/ui/button"
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from "@/components/ui/select"
import { Download, FileJson, Database } from "lucide-react"
import { useState, useEffect } from "react"

export default function ExplorerPage() {
  const [tables, setTables] = useState<any[]>([])
  const [selectedTable, setSelectedTable] = useState<string>("")
  const [tableData, setTableData] = useState<any>(null)
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState<string | null>(null)

  // Fetch tables list
  useEffect(() => {
    fetch("/api/tables")
      .then(res => res.json())
      .then(data => {
        setTables(data.tables || [])
        if (data.tables && data.tables.length > 0) {
          setSelectedTable(data.tables[0].name)
        }
        setLoading(false)
      })
      .catch(err => {
        setError(err.message)
        setLoading(false)
      })
  }, [])

  // Fetch selected table data
  useEffect(() => {
    if (!selectedTable) return

    setLoading(true)
    fetch(`/api/tables/${selectedTable}`)
      .then(res => res.json())
      .then(data => {
        setTableData(data)
        setLoading(false)
      })
      .catch(err => {
        setError(err.message)
        setLoading(false)
      })
  }, [selectedTable])

  const handleExportCSV = () => {
    if (!tableData?.sampleData) return
    
    const csvContent = [
      tableData.columns.map((c: any) => c.name).join(","),
      ...tableData.sampleData.map((row: any) =>
        tableData.columns.map((c: any) => row[c.name]).join(",")
      )
    ].join("\n")
    
    const blob = new Blob([csvContent], { type: "text/csv" })
    const url = URL.createObjectURL(blob)
    const a = document.createElement("a")
    a.href = url
    a.download = `${selectedTable}.csv`
    a.click()
  }

  const handleExportJSON = () => {
    if (!tableData?.sampleData) return
    
    const blob = new Blob([JSON.stringify(tableData.sampleData, null, 2)], { type: "application/json" })
    const url = URL.createObjectURL(blob)
    const a = document.createElement("a")
    a.href = url
    a.download = `${selectedTable}.json`
    a.click()
  }

  if (error) {
    return (
      <AppLayout>
        <div className="space-y-6 pb-32">
          <Card className="p-6 border-destructive">
            <p className="text-destructive">Error: {error}</p>
          </Card>
        </div>
        <ChatInterface />
      </AppLayout>
    )
  }

  return (
    <AppLayout>
      <div className="space-y-6 pb-32">
        <div>
          <h1 className="text-3xl font-bold">Data Explorer</h1>
          <p className="text-muted-foreground">Browse and analyze your database tables</p>
        </div>

        {/* Table Stats Overview */}
        <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
          <Card className="p-4">
            <div className="flex items-center gap-3">
              <Database className="h-8 w-8 text-primary" />
              <div>
                <p className="text-sm text-muted-foreground">Total Tables</p>
                <p className="text-2xl font-bold">{tables.length}</p>
              </div>
            </div>
          </Card>
          <Card className="p-4">
            <div>
              <p className="text-sm text-muted-foreground">Total Records</p>
              <p className="text-2xl font-bold">
                {tables.reduce((sum, t) => sum + (t.rowCount || 0), 0).toLocaleString()}
              </p>
            </div>
          </Card>
          <Card className="p-4">
            <div>
              <p className="text-sm text-muted-foreground">Selected Table</p>
              <p className="text-2xl font-bold">{selectedTable || "None"}</p>
            </div>
          </Card>
        </div>

        {/* Table Selector */}
        <Card className="p-6">
          <div className="space-y-4">
            <div>
              <label className="text-sm font-medium">Select Table</label>
              {loading && !tableData ? (
                <div className="p-3 text-muted-foreground">Loading tables...</div>
              ) : (
                <Select value={selectedTable} onValueChange={setSelectedTable}>
                  <SelectTrigger>
                    <SelectValue placeholder="Select a table" />
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

            {/* Column Info */}
            {tableData?.columns && (
              <div>
                <h3 className="font-semibold mb-3">
                  Columns ({tableData.columns.length})
                </h3>
                <div className="grid grid-cols-2 md:grid-cols-4 gap-3">
                  {tableData.columns.map((col: any) => (
                    <div key={col.name} className="p-3 bg-secondary rounded-lg text-sm">
                      <div className="font-medium truncate" title={col.name}>
                        {col.name}
                      </div>
                      <div className="text-xs text-muted-foreground">{col.type || "text"}</div>
                    </div>
                  ))}
                </div>
              </div>
            )}

            {/* Export Buttons */}
            <div className="flex gap-2 pt-4">
              <Button
                variant="outline"
                className="gap-2 bg-transparent"
                onClick={handleExportCSV}
                disabled={!tableData?.sampleData}
              >
                <Download className="h-4 w-4" />
                Export to CSV
              </Button>
              <Button
                variant="outline"
                className="gap-2 bg-transparent"
                onClick={handleExportJSON}
                disabled={!tableData?.sampleData}
              >
                <FileJson className="h-4 w-4" />
                Export to JSON
              </Button>
            </div>
          </div>
        </Card>

        {/* Data Preview */}
        <Card className="p-6">
          <h2 className="font-semibold mb-4">
            Data Preview ({tableData?.stats?.rowCount?.toLocaleString() || 0} total rows, showing first 100)
          </h2>
          {loading ? (
            <div className="text-center py-8 text-muted-foreground">Loading data...</div>
          ) : tableData?.sampleData && tableData.sampleData.length > 0 ? (
            <div className="overflow-x-auto">
              <table className="w-full text-sm">
                <thead>
                  <tr className="border-b">
                    {tableData.columns.map((col: any) => (
                      <th key={col.name} className="text-left py-2 px-3 font-semibold whitespace-nowrap">
                        {col.name}
                      </th>
                    ))}
                  </tr>
                </thead>
                <tbody>
                  {tableData.sampleData.map((row: any, idx: number) => (
                    <tr key={idx} className="border-b hover:bg-secondary/50 transition-colors">
                      {tableData.columns.map((col: any) => (
                        <td key={col.name} className="py-2 px-3 whitespace-nowrap">
                          {row[col.name]?.toString() || "—"}
                        </td>
                      ))}
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          ) : (
            <div className="text-center py-8 text-muted-foreground">No data available</div>
          )}
        </Card>
      </div>
      <ChatInterface />
    </AppLayout>
  )
}
