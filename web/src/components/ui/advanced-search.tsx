'use client'

import React, { useState, useCallback, useMemo } from 'react'
import { Input } from '@/components/ui/input'
import { Button } from '@/components/ui/button'
import { Badge } from '@/components/ui/badge'
import { 
  Select, 
  SelectContent, 
  SelectItem, 
  SelectTrigger, 
  SelectValue 
} from '@/components/ui/select'
import { Calendar } from '@/components/ui/calendar'
import { Popover, PopoverContent, PopoverTrigger } from '@/components/ui/popover'
import { 
  Search, 
  Filter, 
  X, 
  Calendar as CalendarIcon,
  SortAsc,
  SortDesc,
  Download,
  RefreshCw
} from 'lucide-react'
import { format } from 'date-fns'
import { cn } from '@/lib/utils'

export interface SearchFilter {
  key: string
  label: string
  type: 'text' | 'select' | 'date' | 'dateRange' | 'number'
  options?: { value: string; label: string }[]
  placeholder?: string
}

export interface SearchState {
  query: string
  filters: Record<string, any>
  sortBy: string
  sortOrder: 'asc' | 'desc'
  dateRange?: {
    from: Date
    to: Date
  }
}

interface AdvancedSearchProps {
  filters: SearchFilter[]
  onSearch: (searchState: SearchState) => void
  onExport?: () => void
  onRefresh?: () => void
  placeholder?: string
  className?: string
  showExport?: boolean
  showRefresh?: boolean
}

export function AdvancedSearch({
  filters,
  onSearch,
  onExport,
  onRefresh,
  placeholder = "Search...",
  className,
  showExport = true,
  showRefresh = true
}: AdvancedSearchProps) {
  const [searchState, setSearchState] = useState<SearchState>({
    query: '',
    filters: {},
    sortBy: '',
    sortOrder: 'desc'
  })
  const [showFilters, setShowFilters] = useState(false)
  const [dateRange, setDateRange] = useState<{ from?: Date; to?: Date }>({})

  const activeFiltersCount = useMemo(() => {
    return Object.values(searchState.filters).filter(value => 
      value !== '' && value !== null && value !== undefined
    ).length
  }, [searchState.filters])

  const handleQueryChange = useCallback((query: string) => {
    const newState = { ...searchState, query }
    setSearchState(newState)
    onSearch(newState)
  }, [searchState, onSearch])

  const handleFilterChange = useCallback((key: string, value: any) => {
    const newFilters = { ...searchState.filters, [key]: value }
    const newState = { ...searchState, filters: newFilters }
    setSearchState(newState)
    onSearch(newState)
  }, [searchState, onSearch])

  const handleSortChange = useCallback((sortBy: string) => {
    const newOrder = searchState.sortBy === sortBy && searchState.sortOrder === 'desc' ? 'asc' : 'desc'
    const newState = { ...searchState, sortBy, sortOrder: newOrder }
    setSearchState(newState)
    onSearch(newState)
  }, [searchState, onSearch])

  const clearFilters = useCallback(() => {
    const newState = {
      query: '',
      filters: {},
      sortBy: '',
      sortOrder: 'desc' as const,
      dateRange: undefined
    }
    setSearchState(newState)
    setDateRange({})
    onSearch(newState)
  }, [onSearch])

  const clearFilter = useCallback((key: string) => {
    const newFilters = { ...searchState.filters }
    delete newFilters[key]
    const newState = { ...searchState, filters: newFilters }
    setSearchState(newState)
    onSearch(newState)
  }, [searchState, onSearch])

  return (
    <div className={cn("space-y-4", className)}>
      {/* Main Search Bar */}
      <div className="flex flex-col sm:flex-row gap-2">
        <div className="relative flex-1">
          <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 h-4 w-4 text-muted-foreground" />
          <Input
            placeholder={placeholder}
            value={searchState.query}
            onChange={(e) => handleQueryChange(e.target.value)}
            className="pl-10 pr-4"
          />
        </div>
        
        <div className="flex gap-2">
          <Button
            variant="outline"
            onClick={() => setShowFilters(!showFilters)}
            className="relative"
          >
            <Filter className="h-4 w-4 mr-2" />
            Filters
            {activeFiltersCount > 0 && (
              <Badge className="ml-2 h-5 w-5 p-0 text-xs">
                {activeFiltersCount}
              </Badge>
            )}
          </Button>
          
          {showRefresh && (
            <Button variant="outline" onClick={onRefresh}>
              <RefreshCw className="h-4 w-4" />
            </Button>
          )}
          
          {showExport && (
            <Button variant="outline" onClick={onExport}>
              <Download className="h-4 w-4 mr-2" />
              Export
            </Button>
          )}
        </div>
      </div>

      {/* Active Filters */}
      {activeFiltersCount > 0 && (
        <div className="flex flex-wrap gap-2">
          {Object.entries(searchState.filters).map(([key, value]) => {
            if (!value) return null
            const filter = filters.find(f => f.key === key)
            return (
              <Badge key={key} variant="secondary" className="flex items-center gap-1">
                {filter?.label}: {value}
                <Button
                  variant="ghost"
                  size="sm"
                  className="h-4 w-4 p-0 hover:bg-transparent"
                  onClick={() => clearFilter(key)}
                >
                  <X className="h-3 w-3" />
                </Button>
              </Badge>
            )
          })}
          <Button
            variant="ghost"
            size="sm"
            onClick={clearFilters}
            className="h-6 px-2 text-xs"
          >
            Clear All
          </Button>
        </div>
      )}

      {/* Advanced Filters Panel */}
      {showFilters && (
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4 p-4 border rounded-lg bg-muted/30">
          {filters.map((filter) => (
            <div key={filter.key} className="space-y-2">
              <label className="text-sm font-medium">{filter.label}</label>
              
              {filter.type === 'text' && (
                <Input
                  placeholder={filter.placeholder}
                  value={searchState.filters[filter.key] || ''}
                  onChange={(e) => handleFilterChange(filter.key, e.target.value)}
                />
              )}
              
              {filter.type === 'select' && (
                <Select
                  value={searchState.filters[filter.key] || ''}
                  onValueChange={(value) => handleFilterChange(filter.key, value)}
                >
                  <SelectTrigger>
                    <SelectValue placeholder={filter.placeholder} />
                  </SelectTrigger>
                  <SelectContent>
                    {filter.options?.map((option) => (
                      <SelectItem key={option.value} value={option.value}>
                        {option.label}
                      </SelectItem>
                    ))}
                  </SelectContent>
                </Select>
              )}
              
              {filter.type === 'date' && (
                <Popover>
                  <PopoverTrigger asChild>
                    <Button
                      variant="outline"
                      className={cn(
                        "w-full justify-start text-left font-normal",
                        !searchState.filters[filter.key] && "text-muted-foreground"
                      )}
                    >
                      <CalendarIcon className="mr-2 h-4 w-4" />
                      {searchState.filters[filter.key] ? (
                        format(new Date(searchState.filters[filter.key]), "PPP")
                      ) : (
                        <span>{filter.placeholder}</span>
                      )}
                    </Button>
                  </PopoverTrigger>
                  <PopoverContent className="w-auto p-0">
                    <Calendar
                      mode="single"
                      selected={searchState.filters[filter.key] ? new Date(searchState.filters[filter.key]) : undefined}
                      onSelect={(date) => handleFilterChange(filter.key, date?.toISOString())}
                      initialFocus
                    />
                  </PopoverContent>
                </Popover>
              )}
              
              {filter.type === 'number' && (
                <Input
                  type="number"
                  placeholder={filter.placeholder}
                  value={searchState.filters[filter.key] || ''}
                  onChange={(e) => handleFilterChange(filter.key, e.target.value)}
                />
              )}
            </div>
          ))}
        </div>
      )}

      {/* Sort Options */}
      <div className="flex gap-2">
        <Select
          value={searchState.sortBy}
          onValueChange={handleSortChange}
        >
          <SelectTrigger className="w-48">
            <SelectValue placeholder="Sort by..." />
          </SelectTrigger>
          <SelectContent>
            <SelectItem value="date">Date</SelectItem>
            <SelectItem value="amount">Amount</SelectItem>
            <SelectItem value="vendor">Vendor</SelectItem>
            <SelectItem value="status">Status</SelectItem>
            <SelectItem value="priority">Priority</SelectItem>
          </SelectContent>
        </Select>
        
        {searchState.sortBy && (
          <Button
            variant="outline"
            size="sm"
            onClick={() => handleSortChange(searchState.sortBy)}
            className="px-3"
          >
            {searchState.sortOrder === 'asc' ? (
              <SortAsc className="h-4 w-4" />
            ) : (
              <SortDesc className="h-4 w-4" />
            )}
          </Button>
        )}
      </div>
    </div>
  )
}

export default AdvancedSearch


