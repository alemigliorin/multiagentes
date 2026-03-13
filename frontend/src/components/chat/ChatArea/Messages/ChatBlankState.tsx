'use client'

import { motion } from 'framer-motion'
import { FileSpreadsheet, Search, ScanLine, Lightbulb } from 'lucide-react'
import React from 'react'

interface SuggestionCard {
  icon: React.ReactNode
  title: string
  description: string
  prompt: string
}

const SUGGESTIONS: SuggestionCard[] = [
  {
    icon: <FileSpreadsheet className="h-5 w-5 text-brand" />,
    title: 'Gere uma planilha',
    description: 'de planejamento financeiro',
    prompt: 'Gere uma planilha de planejamento financeiro completa'
  },
  {
    icon: <Search className="h-5 w-5 text-brand" />,
    title: 'Buscar imagens',
    description: 'de referência',
    prompt: 'Busque imagens de referência para meu projeto'
  },
  {
    icon: <ScanLine className="h-5 w-5 text-brand" />,
    title: 'Analisar a imagem',
    description: 'de uma interface minha',
    prompt: 'Analise a imagem de uma interface que estou desenvolvendo'
  },
  {
    icon: <Lightbulb className="h-5 w-5 text-brand" />,
    title: 'Ter ideias',
    description: 'sobre algo que está projetando',
    prompt: 'Me ajude a ter ideias criativas sobre meu projeto atual'
  }
]

interface ChatBlankStateProps {
  onSuggestionClick?: (prompt: string) => void
}

const ChatBlankState = ({ onSuggestionClick }: ChatBlankStateProps) => {
  return (
    <section
      className="flex flex-col items-center text-center font-sans"
      aria-label="Tela de boas-vindas"
    >
      <div className="flex max-w-2xl flex-col gap-y-10">
        {/* Greeting */}
        <motion.div
          initial={{ opacity: 0, y: 12 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.5, delay: 0.2 }}
          className="flex flex-col gap-2"
        >
          <h1 className="text-3xl font-semibold tracking-tight text-foreground">
            Olá, Alexandre!
          </h1>
          <p className="text-base text-muted-foreground">
            Estou aqui para pensar, escolher e executar da melhor forma,
            <br />
            tudo de forma autônoma.
          </p>
        </motion.div>

        {/* Suggestion Cards */}
        <motion.div
          initial={{ opacity: 0, y: 12 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.5, delay: 0.4 }}
          className="grid grid-cols-2 gap-3"
        >
          {SUGGESTIONS.map((suggestion, index) => (
            <motion.button
              key={index}
              onClick={() => onSuggestionClick?.(suggestion.prompt)}
              className="hover:border-brand/20 group flex items-start gap-3 rounded-xl border border-border bg-card p-4 text-left shadow-card transition-all hover:shadow-card-hover"
              whileHover={{ y: -2 }}
              whileTap={{ scale: 0.98 }}
            >
              <div className="mt-0.5 flex h-9 w-9 shrink-0 items-center justify-center rounded-lg bg-brand-light">
                {suggestion.icon}
              </div>
              <div className="min-w-0">
                <span className="text-sm font-semibold text-foreground">
                  {suggestion.title}
                </span>{' '}
                <span className="text-sm text-muted-foreground">
                  {suggestion.description}
                </span>
              </div>
            </motion.button>
          ))}
        </motion.div>
      </div>
    </section>
  )
}

export default ChatBlankState
