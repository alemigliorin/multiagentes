'use client'

import { useState, useEffect } from 'react'
import { Search } from 'lucide-react'
import { useStore } from '@/store'

interface SearchBarProps {
  onSearch?: (query: string) => void
  placeholder?: string
}

const SearchBar = ({ onSearch, placeholder = 'Pesquisar' }: SearchBarProps) => {
  const { searchQuery, setSearchQuery } = useStore()
  const [localQuery, setLocalQuery] = useState(searchQuery || '')

  useEffect(() => {
    setLocalQuery(searchQuery || '')
  }, [searchQuery])

  const handleChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    const value = e.target.value
    setLocalQuery(value)
    setSearchQuery(value)
    onSearch?.(value)
  }

  return (
    <div className="relative">
      <Search className="absolute left-3 top-1/2 h-4 w-4 -translate-y-1/2 text-muted" />
      <input
        type="text"
        value={localQuery}
        onChange={handleChange}
        placeholder={placeholder}
        className="focus:ring-brand/30 h-9 w-full rounded-lg border border-border bg-background pl-9 pr-3 text-sm text-foreground transition-colors placeholder:text-muted focus:border-brand focus:outline-none focus:ring-1"
      />
    </div>
  )
}

export default SearchBar
