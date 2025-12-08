"use client"

import {
  BarChart,
  Bar,
  LineChart,
  Line,
  PieChart,
  Pie,
  Cell,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  ResponsiveContainer,
} from "recharts"
import { Card } from "@/components/ui/card"
import { useDashboardCharts } from "@/lib/api-client"

const COLORS = ["#10b981", "#059669", "#047857", "#065f46", "#064e3b"]

export function ChartsGrid() {
  const { charts, loading, error } = useDashboardCharts()

  if (error) {
    return (
      <Card className="p-6 border-destructive">
        <p className="text-sm text-destructive">Error loading charts: {error}</p>
      </Card>
    )
  }

  const salesByCountry = charts?.salesByCountry ? 
    charts.salesByCountry.labels.map((label, i) => ({
      name: label,
      value: Math.round(charts.salesByCountry.data[i] / 1000)
    })) : []

  const salesTrend = charts?.salesTrend ?
    charts.salesTrend.labels.map((label, i) => ({
      month: label.split('-')[1] || label,
      sales: Math.round(charts.salesTrend.data[i] / 1000)
    })).slice(0, 12) : []

  const productDistribution = charts?.productDistribution ?
    charts.productDistribution.labels.map((label, i) => ({
      name: label,
      value: Math.round((charts.productDistribution.data[i] / charts.productDistribution.data.reduce((a, b) => a + b, 0)) * 100)
    })) : []

  const cityPerformance = charts?.cityPerformance ?
    charts.cityPerformance.labels.slice(0, 6).map((label, i) => ({
      city: label,
      sales: Math.round(charts.cityPerformance.data[i] / 1000)
    })) : []
  return (
    <div className="grid grid-cols-1 lg:grid-cols-2 gap-4 mt-6">
      {/* Sales by Country */}
      <Card className="p-6 animate-slide-up">
        <h3 className="font-semibold mb-4">Sales by Country</h3>
        {loading ? (
          <div className="h-[250px] flex items-center justify-center text-muted-foreground">Loading...</div>
        ) : salesByCountry.length > 0 ? (
          <ResponsiveContainer width="100%" height={250}>
            <BarChart data={salesByCountry}>
              <CartesianGrid strokeDasharray="3 3" stroke="#e5e7eb" />
              <XAxis dataKey="name" stroke="#6b7280" />
              <YAxis stroke="#6b7280" />
              <Tooltip
                contentStyle={{
                  backgroundColor: "#1f2937",
                  border: "1px solid #374151",
                }}
              />
              <Bar dataKey="value" fill="#10b981" radius={[8, 8, 0, 0]} />
            </BarChart>
          </ResponsiveContainer>
        ) : (
          <div className="h-[250px] flex items-center justify-center text-muted-foreground">No data</div>
        )}
      </Card>

      {/* Sales Trend */}
      <Card className="p-6 animate-slide-up" style={{ animationDelay: "100ms" }}>
        <h3 className="font-semibold mb-4">Sales Trend (Monthly)</h3>
        {loading ? (
          <div className="h-[250px] flex items-center justify-center text-muted-foreground">Loading...</div>
        ) : salesTrend.length > 0 ? (
          <ResponsiveContainer width="100%" height={250}>
            <LineChart data={salesTrend}>
              <CartesianGrid strokeDasharray="3 3" stroke="#e5e7eb" />
              <XAxis dataKey="month" stroke="#6b7280" />
              <YAxis stroke="#6b7280" />
              <Tooltip
                contentStyle={{
                  backgroundColor: "#1f2937",
                  border: "1px solid #374151",
                }}
              />
              <Line type="monotone" dataKey="sales" stroke="#059669" strokeWidth={2} dot={false} />
            </LineChart>
          </ResponsiveContainer>
        ) : (
          <div className="h-[250px] flex items-center justify-center text-muted-foreground">No data</div>
        )}
      </Card>

      {/* Product Distribution */}
      <Card className="p-6 animate-slide-up" style={{ animationDelay: "200ms" }}>
        <h3 className="font-semibold mb-4">Product Distribution</h3>
        {loading ? (
          <div className="h-[250px] flex items-center justify-center text-muted-foreground">Loading...</div>
        ) : productDistribution.length > 0 ? (
          <ResponsiveContainer width="100%" height={250}>
            <PieChart>
              <Pie
                data={productDistribution}
                cx="50%"
                cy="50%"
                labelLine={false}
                label={({ name, value }) => `${name}: ${value}%`}
                outerRadius={80}
                fill="#8884d8"
                dataKey="value"
              >
                {productDistribution.map((entry, index) => (
                  <Cell key={`cell-${index}`} fill={COLORS[index % COLORS.length]} />
                ))}
              </Pie>
              <Tooltip />
            </PieChart>
          </ResponsiveContainer>
        ) : (
          <div className="h-[250px] flex items-center justify-center text-muted-foreground">No data</div>
        )}
      </Card>

      {/* City Performance */}
      <Card className="p-6 animate-slide-up" style={{ animationDelay: "300ms" }}>
        <h3 className="font-semibold mb-4">City Performance</h3>
        {loading ? (
          <div className="h-[250px] flex items-center justify-center text-muted-foreground">Loading...</div>
        ) : cityPerformance.length > 0 ? (
          <ResponsiveContainer width="100%" height={250}>
            <BarChart data={cityPerformance} layout="vertical" margin={{ left: 20 }}>
              <CartesianGrid strokeDasharray="3 3" stroke="#e5e7eb" />
              <XAxis type="number" stroke="#6b7280" />
              <YAxis dataKey="city" type="category" width={100} stroke="#6b7280" tick={{ fontSize: 12 }} />
              <Tooltip
                contentStyle={{
                  backgroundColor: "#1f2937",
                  border: "1px solid #374151",
                }}
              />
              <Bar dataKey="sales" fill="#047857" radius={[0, 8, 8, 0]} />
            </BarChart>
          </ResponsiveContainer>
        ) : (
          <div className="h-[250px] flex items-center justify-center text-muted-foreground">No data</div>
        )}
      </Card>
    </div>
  )
}
