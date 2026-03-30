'use client'

import { motion } from 'framer-motion'
import React from 'react'

interface ChatBlankStateProps {
  onSuggestionClick?: (prompt: string) => void
}

const ChatBlankState = ({ onSuggestionClick }: ChatBlankStateProps) => {
  return (
    <section
      className="flex flex-col items-center text-center font-sans"
      aria-label="Tela de boas-vindas"
    >
      <div className="flex max-w-2xl flex-col gap-y-10 py-20">
        {/* Greeting */}
        <motion.div
            initial={{ opacity: 0, y: 12 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.5, delay: 0.2 }}
            className="flex flex-col gap-4"
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
      </div>
    </section>
  )
}

export default ChatBlankState
