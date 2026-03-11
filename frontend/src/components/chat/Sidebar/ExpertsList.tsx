'use client'

import { useState } from 'react'
import { motion, AnimatePresence } from 'framer-motion'
import { Bot, Compass, ChevronDown } from 'lucide-react'

interface Expert {
    id: string
    name: string
    description: string
    emoji: string
}

const EXPERTS: Expert[] = [
    { id: 'pesquisador', name: 'Pesquisador', description: 'Busca na internet', emoji: '🔍' },
    { id: 'copywriter', name: 'Copywriter', description: 'Escrita persuasiva', emoji: '✍️' },
    { id: 'juridico', name: 'Jurídico', description: 'Compliance e leis', emoji: '⚖️' },
    { id: 'criador_experts', name: 'Criador de Experts', description: 'Personas e Big Ideas', emoji: '🧠' },
    { id: 'criador_midia', name: 'Criador de Mídia', description: 'Imagens e vídeos', emoji: '🎨' },
    { id: 'agente_pdf', name: 'Agente PDF', description: 'Análise de documentos', emoji: '📄' },
]

interface ExpertsListProps {
    onSelectExpert?: (expertId: string) => void
}

const ExpertsList = ({ onSelectExpert }: ExpertsListProps) => {
    const [isCollapsed, setIsCollapsed] = useState(false)

    return (
        <div className="flex flex-col gap-0.5">
            <button
                onClick={() => setIsCollapsed(!isCollapsed)}
                className="flex items-center justify-between px-1 mb-1 group cursor-pointer w-full"
            >
                <span className="text-xs font-semibold uppercase tracking-wider text-muted group-hover:text-foreground transition-colors">
                    Experts
                </span>
                <motion.div
                    animate={{ rotate: isCollapsed ? -90 : 0 }}
                    transition={{ duration: 0.2 }}
                    className="text-muted group-hover:text-foreground transition-colors"
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
                        <motion.button
                            className="flex w-full items-center gap-2.5 rounded-lg px-2 py-2 text-sm text-foreground hover:bg-sidebar-hover transition-colors"
                            whileTap={{ scale: 0.98 }}
                        >
                            <Compass className="h-4 w-4 text-muted" />
                            <span>Explorar</span>
                        </motion.button>
                        {EXPERTS.map((expert) => (
                            <motion.button
                                key={expert.id}
                                onClick={() => onSelectExpert?.(expert.id)}
                                className="flex w-full items-center gap-2.5 rounded-lg px-2 py-2 text-sm text-foreground hover:bg-sidebar-hover transition-colors group"
                                whileTap={{ scale: 0.98 }}
                            >
                                <span className="text-base shrink-0">{expert.emoji}</span>
                                <div className="flex flex-col items-start min-w-0">
                                    <span className="truncate text-sm">{expert.name}</span>
                                </div>
                            </motion.button>
                        ))}
                    </motion.div>
                )}
            </AnimatePresence>
        </div>
    )
}

export default ExpertsList
