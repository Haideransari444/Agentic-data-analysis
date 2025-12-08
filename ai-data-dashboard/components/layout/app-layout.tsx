"use client"

import type React from "react"

import { useState } from "react"
import Link from "next/link"
import { usePathname } from "next/navigation"
import { BarChart3, Database, Brain, FileText, Upload, Settings, Menu } from "lucide-react"
import { Button } from "@/components/ui/button"
import { Sheet, SheetContent, SheetTrigger } from "@/components/ui/sheet"

const navigation = [
  { name: "Dashboard", href: "/", icon: BarChart3 },
  { name: "Explorer", href: "/explorer", icon: Database },
  { name: "Analysis", href: "/analysis", icon: Brain },
  { name: "Reports", href: "/reports", icon: FileText },
  { name: "Upload", href: "/upload", icon: Upload },
  { name: "Settings", href: "/settings", icon: Settings },
]

export function AppLayout({ children }: { children: React.ReactNode }) {
  const pathname = usePathname()
  const [open, setOpen] = useState(false)

  const NavContent = () => (
    <nav className="space-y-0.5">
      {navigation.map((item) => {
        const Icon = item.icon
        const isActive = pathname === item.href
        return (
          <Link key={item.href} href={item.href}>
            <Button
              variant={isActive ? "default" : "ghost"}
              className={`w-full justify-start text-sm font-medium transition-all duration-200 ${
                isActive
                  ? "bg-primary text-primary-foreground shadow-md shadow-primary/20"
                  : "text-foreground hover:bg-muted/60 hover:text-primary"
              }`}
              onClick={() => setOpen(false)}
            >
              <Icon className="mr-2 h-4 w-4" />
              {item.name}
            </Button>
          </Link>
        )
      })}
    </nav>
  )

  return (
    <div className="flex h-screen overflow-hidden bg-background">
      <div className="hidden md:flex w-56 flex-col border-r border-border bg-card">
        <div className="p-4 border-b border-border">
          <h1 className="text-lg font-semibold text-foreground">DataForge</h1>
          <p className="text-xs text-muted-foreground mt-1">Analytics Platform</p>
        </div>
        <div className="flex-1 overflow-y-auto px-3 py-3">
          <NavContent />
        </div>
        <div className="p-3 border-t border-border text-xs text-muted-foreground">Status: Active</div>
      </div>

      {/* Mobile Hamburger */}
      <Sheet open={open} onOpenChange={setOpen}>
        <SheetTrigger asChild className="md:hidden fixed top-4 left-4 z-50">
          <Button variant="outline" size="icon" className="bg-card border-border">
            <Menu className="h-4 w-4" />
          </Button>
        </SheetTrigger>
        <SheetContent side="left" className="bg-card border-border">
          <div className="pt-8">
            <NavContent />
          </div>
        </SheetContent>
      </Sheet>

      {/* Main Content */}
      <div className="flex-1 flex flex-col overflow-hidden">
        <main className="flex-1 overflow-y-auto">
          <div className="md:p-6 p-4">{children}</div>
        </main>
      </div>
    </div>
  )
}
