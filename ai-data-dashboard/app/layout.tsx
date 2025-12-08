import type React from "react"
import { Inter } from "next/font/google"
import { Analytics } from "@vercel/analytics/next"
import "./globals.css"
import { ChatProvider } from "@/providers/chat-provider"
import { DarkModeProvider } from "@/providers/dark-mode-provider"

const inter = Inter({ subsets: ["latin"] })

export default function RootLayout({
  children,
}: Readonly<{
  children: React.ReactNode
}>) {
  return (
    <html lang="en" suppressHydrationWarning className={inter.className}>
      <body className="antialiased">
        <DarkModeProvider>
          <ChatProvider>
            {children}
            <Analytics />
          </ChatProvider>
        </DarkModeProvider>
      </body>
    </html>
  )
}

export const metadata = {
      generator: 'v0.app'
    };
