import type { Metadata } from 'next'
import { Inter } from 'next/font/google'
import './globals.css'
// import { Providers } from '@/components/providers'

const inter = Inter({ subsets: ['latin'] })

export const metadata: Metadata = {
  title: 'AI ERP SaaS',
  description: 'AI-powered ERP solution with OCR and automation',
}

export default function RootLayout({
  children,
}: {
  children: React.ReactNode
}) {
  return (
    <html lang="en">
      <body className={inter.className}>
        {children}
      </body>
    </html>
  )
}

