'use client'

import { useState } from 'react'
import { motion, AnimatePresence } from 'framer-motion'
import { ChevronDown } from 'lucide-react'

interface Expert {
  id: string
  name: string
  description: string
  emoji: string
}

const EXPERTS: Expert[] = [
  {
    id: 'orquestrador',
    name: 'Orquestrador',
    description: 'Líder da Equipe (Default)',
    emoji: '👑'
  },
  {
    id: 'pesquisador',
    name: 'Pesquisador',
    description: 'Busca na internet',
    emoji: '🔍'
  },
  {
    id: 'copywriter',
    name: 'Copywriter',
    description: 'Escrita persuasiva',
    emoji: '✍️'
  },
  {
    id: 'juridico',
    name: 'Jurídico',
    description: 'Compliance e leis',
    emoji: '⚖️'
  },
  {
    id: 'criador_experts',
    name: 'Criador de Experts',
    description: 'Personas e Big Ideas',
    emoji: '🧠'
  },
  {
    id: 'criador_midia',
    name: 'Criador de Mídia',
    description: 'Imagens e vídeos',
    emoji: '🎨'
  },
  {
    id: 'agente_pdf',
    name: 'Agente PDF',
    description: 'Análise de documentos',
    emoji: '📄'
  }
]

const ExpertsList = () => {
  const [isCollapsed, setIsCollapsed] = useState(false)

  return (
    <div className="flex flex-col gap-0.5">
      <button
        onClick={() => setIsCollapsed(!isCollapsed)}
        className="group mb-1 flex w-full cursor-pointer items-center justify-between px-1"
      >
        <span className="text-xs font-semibold uppercase tracking-wider text-muted transition-colors group-hover:text-foreground">
          Agentes
        </span>
        <motion.div
          animate={{ rotate: isCollapsed ? -90 : 0 }}
          transition={{ duration: 0.2 }}
          className="text-muted transition-colors group-hover:text-foreground"
        >
          <ChevronDown className="h-4 w-4" />
        </motion.div>
      </button>
      <AnimatePresence initial={false}>
        {!isCollapsed && (
          <motion.div
            initial={{ height: 0, opacity: 0 }}
            animate={{ height: 'auto', opacity: 1 }}
            exit={{ height: 0, opacity: 0 }}
            transition={{ duration: 0.2 }}
            className="flex flex-col gap-0.5 overflow-hidden"
          >
            {EXPERTS.map((expert) => (
              <div
                key={expert.id}
                className={`flex w-full items-center gap-2.5 rounded-lg px-2 py-2 text-sm transition-colors ${
                  expert.id === 'orquestrador'
                    ? 'bg-brand/10 text-brand'
                    : 'text-foreground'
                }`}
              >
                <span className="shrink-0 text-base">{expert.emoji}</span>
                <div className="flex min-w-0 flex-col items-start">
                  <span className="truncate text-sm font-medium">
                    {expert.name}
                  </span>
                  <span className="truncate text-xs text-muted-foreground">
                    {expert.description}
                  </span>
                </div>
              </div>
            ))}
          </motion.div>
        )}
      </AnimatePresence>
    </div>
  )
}

export default ExpertsList
