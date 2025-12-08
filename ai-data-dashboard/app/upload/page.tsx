"use client"

import { useCallback, useRef, useState } from "react"
import { AppLayout } from "@/components/layout/app-layout"
import { ChatInterface } from "@/components/chat/chat-interface"
import { Card } from "@/components/ui/card"
import { Button } from "@/components/ui/button"
import { Progress } from "@/components/ui/progress"
import { UploadIcon, FileUp, CheckCircle2, AlertCircle, Loader2 } from "lucide-react"
import { useFileUpload } from "@/lib/api-client"

interface UploadedFile {
  id: string
  name: string
  size: string
  rows: number
  tableName: string
  status: "processing" | "success" | "error"
  error?: string
}

const formatBytes = (bytes: number) => {
  if (!bytes) return "0 B"
  const units = ["B", "KB", "MB", "GB"]
  const i = Math.floor(Math.log(bytes) / Math.log(1024))
  return `${(bytes / Math.pow(1024, i)).toFixed(1)} ${units[i]}`
}

export default function UploadPage() {
  const { upload, uploading, error, progress } = useFileUpload()
  const [uploads, setUploads] = useState<UploadedFile[]>([])
  const [dragActive, setDragActive] = useState(false)
  const fileInputRef = useRef<HTMLInputElement>(null)

  const handleFiles = useCallback(
    async (fileList: FileList | null) => {
      if (!fileList || fileList.length === 0) return
      const file = fileList[0]
      const uploadId = `${Date.now()}-${file.name}`

      const tempUpload: UploadedFile = {
        id: uploadId,
        name: file.name,
        size: formatBytes(file.size),
        rows: 0,
        tableName: "Pending",
        status: "processing",
      }
      setUploads((prev) => [tempUpload, ...prev])

      const response = await upload(file)
      setUploads((prev) =>
        prev.map((entry) => {
          if (entry.id === uploadId) {
            if (response) {
              return {
                ...entry,
                tableName: response.tableName,
                rows: response.rowsUploaded,
                status: "success",
              }
            }
            return { ...entry, status: "error", error: error || "Upload failed" }
          }
          return entry
        })
      )
    },
    [upload, error]
  )

  const onDrop = async (event: React.DragEvent<HTMLDivElement>) => {
    event.preventDefault()
    setDragActive(false)
    await handleFiles(event.dataTransfer.files)
  }

  const onDragOver = (event: React.DragEvent<HTMLDivElement>) => {
    event.preventDefault()
    setDragActive(true)
  }

  const onDragLeave = () => setDragActive(false)

  const onBrowseClick = () => {
    fileInputRef.current?.click()
  }

  const handleFileInput = async (event: React.ChangeEvent<HTMLInputElement>) => {
    await handleFiles(event.target.files)
    if (event.target) event.target.value = ""
  }

  return (
    <AppLayout>
      <div className="space-y-6 pb-32">
        <div>
          <h1 className="text-3xl font-bold">Upload Data</h1>
          <p className="text-muted-foreground">Import CSV files to analyze</p>
        </div>

        {/* Upload Zone */}
        <Card
          className={`p-12 border-2 border-dashed transition-colors cursor-pointer text-center ${
            dragActive ? "border-primary bg-primary/5" : "hover:border-primary"
          }`}
          onDragOver={onDragOver}
          onDragLeave={onDragLeave}
          onDrop={onDrop}
          onClick={onBrowseClick}
        >
          <input
            type="file"
            accept=".csv,.xls,.xlsx"
            className="hidden"
            ref={fileInputRef}
            onChange={handleFileInput}
          />
          <UploadIcon className="h-12 w-12 mx-auto text-muted-foreground mb-4" />
          <h3 className="font-semibold text-lg mb-2">Drag & Drop CSV/XLS File Here</h3>
          <p className="text-muted-foreground mb-4">or</p>
          <Button variant="outline" className="gap-2 bg-transparent" disabled={uploading}>
            {uploading ? <Loader2 className="h-4 w-4 animate-spin" /> : <FileUp className="h-4 w-4" />}
            {uploading ? "Uploading..." : "Browse Files"}
          </Button>
          {uploading && (
            <div className="mt-6 space-y-2">
              <Progress value={progress} />
              <p className="text-xs text-muted-foreground">Uploading... {progress}%</p>
            </div>
          )}
          {error && !uploading && (
            <p className="text-sm text-destructive mt-4 flex items-center justify-center gap-2">
              <AlertCircle className="h-4 w-4" /> {error}
            </p>
          )}
        </Card>

        {/* Upload Info */}
        <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
          <Card className="p-4">
            <h4 className="font-semibold mb-2">Supported Formats</h4>
            <p className="text-sm text-muted-foreground">CSV, XLS, XLSX</p>
          </Card>
          <Card className="p-4">
            <h4 className="font-semibold mb-2">Max File Size</h4>
            <p className="text-sm text-muted-foreground">100 MB</p>
          </Card>
          <Card className="p-4">
            <h4 className="font-semibold mb-2">Preview</h4>
            <p className="text-sm text-muted-foreground">Auto-detect columns</p>
          </Card>
        </div>

        {/* Recent Uploads */}
        <Card className="p-6">
          <h2 className="font-semibold mb-4">Recent Uploads</h2>
          <div className="space-y-3">
            {uploads.length === 0 && <p className="text-sm text-muted-foreground">No uploads yet.</p>}
            {uploads.map((file) => (
              <div key={file.id} className="flex items-center justify-between p-3 bg-secondary rounded-lg">
                <div>
                  <p className="font-medium">{file.name}</p>
                  <p className="text-xs text-muted-foreground">
                    {file.size} • {file.rows ? `${file.rows.toLocaleString()} rows` : "Processing"} • Table: {file.tableName}
                  </p>
                  {file.error && <p className="text-xs text-destructive mt-1">{file.error}</p>}
                </div>
                <div className="flex items-center gap-2">
                  {file.status === "success" && <CheckCircle2 className="h-5 w-5 text-green-500" />}
                  {file.status === "error" && <AlertCircle className="h-5 w-5 text-destructive" />}
                  {file.status === "processing" && <Loader2 className="h-5 w-5 animate-spin text-primary" />}
                  <Button size="sm" variant="ghost" disabled={file.status !== "success"}>
                    View
                  </Button>
                </div>
              </div>
            ))}
          </div>
        </Card>
      </div>
      <ChatInterface />
    </AppLayout>
  )
}
