'use client'

import { useState, useTransition } from 'react'
import { useLocale } from 'next-intl'
import { Button } from '@/components/ui/button'
import {
  DropdownMenu,
  DropdownMenuContent,
  DropdownMenuItem,
  DropdownMenuTrigger,
} from '@/components/ui/dropdown-menu'
import { Globe } from 'lucide-react'
import { Locale, locales, localeNames, localeFlags } from '@/i18n/config'
import { setUserLocale } from '@/i18n/locale'

export function LanguageSwitcher() {
  const currentLocale = useLocale() as Locale
  const [isPending, startTransition] = useTransition()
  const [isOpen, setIsOpen] = useState(false)

  const handleLocaleChange = (locale: Locale) => {
    startTransition(async () => {
      await setUserLocale(locale)
      // Refresh the page to apply the new locale
      window.location.reload()
    })
    setIsOpen(false)
  }

  return (
    <DropdownMenu open={isOpen} onOpenChange={setIsOpen}>
      <DropdownMenuTrigger asChild>
        <Button
          variant="ghost"
          size="sm"
          className="flex items-center gap-2"
          disabled={isPending}
        >
          <Globe className="h-4 w-4" />
          <span className="hidden sm:inline">
            {localeFlags[currentLocale]} {localeNames[currentLocale]}
          </span>
          <span className="sm:hidden">
            {localeFlags[currentLocale]}
          </span>
        </Button>
      </DropdownMenuTrigger>
      <DropdownMenuContent align="end" className="w-48">
        {locales.map((locale) => (
          <DropdownMenuItem
            key={locale}
            onClick={() => handleLocaleChange(locale)}
            className={`flex items-center gap-2 ${
              locale === currentLocale ? 'bg-accent' : ''
            }`}
          >
            <span className="text-lg">{localeFlags[locale]}</span>
            <span>{localeNames[locale]}</span>
            {locale === currentLocale && (
              <span className="ml-auto text-xs text-muted-foreground">✓</span>
            )}
          </DropdownMenuItem>
        ))}
      </DropdownMenuContent>
    </DropdownMenu>
  )
}


