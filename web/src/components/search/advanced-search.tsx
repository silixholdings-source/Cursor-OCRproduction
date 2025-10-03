'use client'

import React, { useState, useEffect, useRef } from 'react'
import { Card, CardContent } from '@/components/ui/card'
import { Input } from '@/components/ui/input'
import { Button } from '@/components/ui/button'
import { Badge } from '@/components/ui/badge'
import { 
  Search, 
  Filter, 
  X, 
  FileText, 
  Building, 
  Calendar,
  DollarSign,
  Zap,
  Clock,
  TrendingUp
} from 'lucide-react'
import { useKeyboardShortcuts } from '@/hooks/use-keyboard-shortcuts'

interface SearchResult {
  id: string
  type: 'invoice' | 'vendor' | 'user' | 'approval'
  title: string
  subtitle: string
  amount?: number
  currency?: string
  date?: string
  status?: string
  relevance: number
}

interface AdvancedSearchProps {
  onResultSelect?: (result: SearchResult) => void
  placeholder?: string
}

export function AdvancedSearch({ onResultSelect, placeholder = "Search invoices, vendors, users..." }: AdvancedSearchProps) {
  const [query, setQuery] = useState('')
  const [results, setResults] = useState<SearchResult[]>([])
  const [isSearching, setIsSearching] = useState(false)
  const [isOpen, setIsOpen] = useState(false)
  const [selectedIndex, setSelectedIndex] = useState(-1)
  const searchRef = useRef<HTMLInputElement>(null)
  const resultsRef = useRef<HTMLDivElement>(null)

  // Register keyboard shortcuts
  useKeyboardShortcuts()

  // Mock search data
  const mockSearchData: SearchResult[] = [
    {
      id: 'INV-001',
      type: 'invoice',
      title: 'Tech Supplies Inc - INV-2024-001',
      subtitle: 'Office supplies and equipment',
      amount: 1250.00,
      currency: 'USD',
      date: '2024-01-15',
      status: 'pending_approval',
      relevance: 0.95
    },
    {
      id: 'INV-002',
      type: 'invoice',
      title: 'Cloud Services Ltd - CSL-2024-002',
      subtitle: 'Monthly cloud hosting services',
      amount: 255.99,
      currency: 'EUR',
      date: '2024-01-14',
      status: 'approved',
      relevance: 0.89
    },
    {
      id: 'V001',
      type: 'vendor',
      title: 'Tech Supplies Inc',
      subtitle: '15 invoices, $25,000 total',
      relevance: 0.92
    },
    {
      id: 'V002',
      type: 'vendor',
      title: 'Cloud Services Ltd',
      subtitle: '12 invoices, $18,000 total',
      relevance: 0.87
    },
    {
      id: 'APP-001',
      type: 'approval',
      title: 'Pending Approval - $3,800',
      subtitle: 'Marketing Solutions - High priority',
      amount: 3800,
      currency: 'GBP',
      status: 'pending',
      relevance: 0.84
    }
  ]

  const performSearch = async (searchQuery: string) => {
    if (searchQuery.length < 2) {
      setResults([])
      setIsOpen(false)
      return
    }

    setIsSearching(true)
    
    // Simulate API search with intelligent filtering
    await new Promise(resolve => setTimeout(resolve, 300))
    
    const filteredResults = mockSearchData
      .filter(item => 
        item.title.toLowerCase().includes(searchQuery.toLowerCase()) ||
        item.subtitle.toLowerCase().includes(searchQuery.toLowerCase())
      )
      .sort((a, b) => b.relevance - a.relevance)
      .slice(0, 8)

    setResults(filteredResults)
    setIsOpen(filteredResults.length > 0)
    setSelectedIndex(-1)
    setIsSearching(false)
  }

  const handleInputChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    const value = e.target.value
    setQuery(value)
    performSearch(value)
  }

  const handleKeyDown = (e: React.KeyboardEvent) => {
    if (!isOpen) return

    switch (e.key) {
      case 'ArrowDown':
        e.preventDefault()
        setSelectedIndex(prev => 
          prev < results.length - 1 ? prev + 1 : prev
        )
        break
      case 'ArrowUp':
        e.preventDefault()
        setSelectedIndex(prev => prev > 0 ? prev - 1 : -1)
        break
      case 'Enter':
        e.preventDefault()
        if (selectedIndex >= 0 && results[selectedIndex]) {
          handleResultSelect(results[selectedIndex])
        }
        break
      case 'Escape':
        setIsOpen(false)
        setSelectedIndex(-1)
        searchRef.current?.blur()
        break
    }
  }

  const handleResultSelect = (result: SearchResult) => {
    setQuery('')
    setIsOpen(false)
    setSelectedIndex(-1)
    onResultSelect?.(result)
    
    // Navigate based on result type
    switch (result.type) {
      case 'invoice':
        router.push(`/dashboard/invoices/${result.id}`)
        break
      case 'vendor':
        router.push(`/dashboard/vendors/${result.id}`)
        break
      case 'approval':
        router.push(`/dashboard/approvals/${result.id}`)
        break
    }
  }

  const getResultIcon = (type: string) => {
    switch (type) {
      case 'invoice':
        return <FileText className="h-4 w-4 text-blue-600" />
      case 'vendor':
        return <Building className="h-4 w-4 text-green-600" />
      case 'approval':
        return <Clock className="h-4 w-4 text-orange-600" />
      default:
        return <Search className="h-4 w-4 text-gray-600" />
    }
  }

  const getStatusBadge = (status?: string) => {
    if (!status) return null
    
    const statusConfig = {
      'pending_approval': { color: 'bg-yellow-100 text-yellow-800', label: 'Pending' },
      'approved': { color: 'bg-green-100 text-green-800', label: 'Approved' },
      'rejected': { color: 'bg-red-100 text-red-800', label: 'Rejected' },
      'pending': { color: 'bg-orange-100 text-orange-800', label: 'Pending' }
    }

    const config = statusConfig[status as keyof typeof statusConfig]
    if (!config) return null

    return (
      <Badge className={config.color} size="sm">
        {config.label}
      </Badge>
    )
  }

  // Close search when clicking outside
  useEffect(() => {
    const handleClickOutside = (event: MouseEvent) => {
      if (resultsRef.current && !resultsRef.current.contains(event.target as Node)) {
        setIsOpen(false)
      }
    }

    document.addEventListener('mousedown', handleClickOutside)
    return () => {
      document.removeEventListener('mousedown', handleClickOutside)
    }
  }, [])

  return (
    <div className="relative w-full max-w-2xl" ref={resultsRef}>
      <div className="relative">
        <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 h-4 w-4 text-gray-400" />
        <Input
          ref={searchRef}
          data-search-input
          type="text"
          placeholder={placeholder}
          value={query}
          onChange={handleInputChange}
          onKeyDown={handleKeyDown}
          onFocus={() => query.length >= 2 && setIsOpen(true)}
          className="pl-10 pr-10 py-3 text-lg"
        />
        {query && (
          <Button
            variant="ghost"
            size="sm"
            className="absolute right-2 top-1/2 transform -translate-y-1/2 h-6 w-6 p-0"
            onClick={() => {
              setQuery('')
              setIsOpen(false)
              searchRef.current?.focus()
            }}
          >
            <X className="h-4 w-4" />
          </Button>
        )}
      </div>

      {/* Search Results Dropdown */}
      {isOpen && (
        <Card className="absolute top-full left-0 right-0 mt-2 z-50 shadow-lg border">
          <CardContent className="p-0">
            {isSearching ? (
              <div className="p-4 text-center">
                <div className="flex items-center justify-center space-x-2">
                  <Search className="h-4 w-4 animate-pulse text-blue-600" />
                  <span className="text-gray-600">Searching...</span>
                </div>
              </div>
            ) : results.length > 0 ? (
              <div className="max-h-96 overflow-y-auto">
                {results.map((result, index) => (
                  <div
                    key={result.id}
                    className={`p-4 border-b last:border-b-0 cursor-pointer transition-colors ${
                      index === selectedIndex ? 'bg-blue-50' : 'hover:bg-gray-50'
                    }`}
                    onClick={() => handleResultSelect(result)}
                  >
                    <div className="flex items-center justify-between">
                      <div className="flex items-center space-x-3">
                        {getResultIcon(result.type)}
                        <div>
                          <div className="font-medium text-gray-900">{result.title}</div>
                          <div className="text-sm text-gray-600">{result.subtitle}</div>
                        </div>
                      </div>
                      
                      <div className="flex items-center space-x-2">
                        {result.amount && (
                          <span className="font-medium text-gray-900">
                            {new Intl.NumberFormat('en-US', {
                              style: 'currency',
                              currency: result.currency || 'USD'
                            }).format(result.amount)}
                          </span>
                        )}
                        {getStatusBadge(result.status)}
                        <Badge variant="outline" size="sm">
                          {Math.round(result.relevance * 100)}%
                        </Badge>
                      </div>
                    </div>
                  </div>
                ))}
                
                {/* Search Tips */}
                <div className="p-3 bg-gray-50 border-t">
                  <div className="text-xs text-gray-600">
                    <strong>Tips:</strong> Use Ctrl+/ to focus search • Arrow keys to navigate • Enter to select
                  </div>
                </div>
              </div>
            ) : (
              <div className="p-4 text-center text-gray-600">
                <Search className="h-8 w-8 mx-auto mb-2 text-gray-400" />
                <div>No results found for "{query}"</div>
                <div className="text-sm mt-1">Try searching for invoices, vendors, or approval items</div>
              </div>
            )}
          </CardContent>
        </Card>
      )}

      {/* Keyboard Shortcuts Help */}
      {query === '?' && (
        <Card className="absolute top-full left-0 right-0 mt-2 z-50 shadow-lg border">
          <CardContent className="p-4">
            <h4 className="font-medium mb-3">Keyboard Shortcuts</h4>
            <div className="space-y-2 text-sm">
              <div className="flex justify-between">
                <span>Dashboard</span>
                <Badge variant="outline" size="sm">Ctrl + D</Badge>
              </div>
              <div className="flex justify-between">
                <span>Invoices</span>
                <Badge variant="outline" size="sm">Ctrl + I</Badge>
              </div>
              <div className="flex justify-between">
                <span>Approvals</span>
                <Badge variant="outline" size="sm">Ctrl + A</Badge>
              </div>
              <div className="flex justify-between">
                <span>New Invoice</span>
                <Badge variant="outline" size="sm">Ctrl + N</Badge>
              </div>
              <div className="flex justify-between">
                <span>Search</span>
                <Badge variant="outline" size="sm">Ctrl + /</Badge>
              </div>
            </div>
          </CardContent>
        </Card>
      )}
    </div>
  )
}

