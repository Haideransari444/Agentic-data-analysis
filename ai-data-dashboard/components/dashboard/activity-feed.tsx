"use client"

import { Card } from "@/components/ui/card"
import { Badge } from "@/components/ui/badge"
import { CheckCircle2, Clock } from "lucide-react"
import { useActivity } from "@/lib/api-client"

export function ActivityFeed() {
  const { activities, loading, error } = useActivity()

  if (error) {
    return (
      <Card className="mt-6 p-6 border-destructive">
        <h3 className="font-semibold mb-4">Recent Activity</h3>
        <p className="text-sm text-destructive">Error loading activity: {error}</p>
      </Card>
    )
  }

  const displayActivities = activities && activities.length > 0 ? activities : [
    { timestamp: "Just now", action: "Waiting for activity...", status: "processing", duration: "—" }
  ]
  return (
    <Card className="mt-6 p-6 animate-slide-up" style={{ animationDelay: "400ms" }}>
      <h3 className="font-semibold mb-4">Recent Activity</h3>
      {loading ? (
        <div className="text-center py-8 text-muted-foreground">Loading activity...</div>
      ) : (
        <div className="overflow-x-auto">
          <table className="w-full text-sm">
            <thead>
              <tr className="border-b">
                <th className="text-left py-2 px-2">Timestamp</th>
                <th className="text-left py-2 px-2">Action</th>
                <th className="text-left py-2 px-2">Status</th>
                <th className="text-left py-2 px-2">Duration</th>
              </tr>
            </thead>
            <tbody>
              {displayActivities.map((activity, idx) => (
                <tr key={idx} className="border-b hover:bg-primary/5 transition-all duration-200 cursor-pointer">
                  <td className="py-3 px-2 text-muted-foreground">{activity.timestamp}</td>
                  <td className="py-3 px-2">{activity.action}</td>
                  <td className="py-3 px-2">
                    <div className="flex items-center gap-2">
                      {activity.status === "success" ? (
                        <>
                          <CheckCircle2 className="h-4 w-4 text-green-500" />
                          <Badge variant="outline" className="bg-green-500/10">
                            Done
                          </Badge>
                        </>
                      ) : (
                        <>
                          <Clock className="h-4 w-4 text-yellow-500" />
                          <Badge variant="outline" className="bg-yellow-500/10">
                            Processing
                          </Badge>
                        </>
                      )}
                    </div>
                  </td>
                  <td className="py-3 px-2 font-mono text-xs">{activity.duration}</td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      )}
    </Card>
  )
}
