import type { Metadata } from 'next'
import { Inter } from 'next/font/google'
import './globals.css'
import Navigation from '@/components/layout/Navigation'
import Footer from '@/components/layout/footer'
import { Providers } from '@/components/providers'
import { Toaster } from '@/components/ui/toaster'
import { ToastContainer } from '@/components/ui/toast-container'
import { ErrorBoundary } from '@/components/error-boundary'
 

const inter = Inter({ subsets: ['latin'] })

export const metadata: Metadata = {
  title: 'AI ERP SaaS - AI-Powered Invoice Automation | Save 60% vs Competitors',
  description: 'Transform your invoice processing with AI automation. Save 80% time and 60% costs compared to Bill.com, Tipalti, and Stampli. Start free trial today.',
  keywords: 'invoice automation, AI OCR, accounts payable, ERP integration, invoice processing, AP automation',
  metadataBase: new URL('https://ai-erp-saas.com'),
  manifest: '/manifest.json',
  icons: {
    apple: '/icons/icon-192x192.png',
    icon: '/icons/icon-192x192.png'
  },
  openGraph: {
    title: 'AI ERP SaaS - AI-Powered Invoice Automation',
    description: 'Save 80% time and 60% costs with AI-powered invoice automation. Start your free trial today.',
    type: 'website',
    url: '/',
    siteName: 'AI ERP SaaS',
    images: [
      {
        url: '/images/og-image.svg',
        width: 1200,
        height: 630,
        alt: 'AI ERP SaaS Platform',
      }
    ],
  },
  twitter: {
    card: 'summary_large_image',
    title: 'AI ERP SaaS - AI-Powered Invoice Automation',
    description: 'Save 80% time and 60% costs with AI-powered invoice automation.',
    images: ['/images/twitter-image.svg'],
  },
}

export const viewport = {
  width: 'device-width',
  initialScale: 1,
  viewportFit: 'cover',
  themeColor: '#2563eb'
}

export default function RootLayout({
  children,
}: {
  children: React.ReactNode
}) {
  return (
    <html lang="en">
      <body className={inter.className}>
        <ErrorBoundary>
          <Providers>
            <Navigation />
            <main>
              {children}
            </main>
            <Footer />
            <Toaster />
            <ToastContainer />
          </Providers>
        </ErrorBoundary>
      </body>
    </html>
  )
}