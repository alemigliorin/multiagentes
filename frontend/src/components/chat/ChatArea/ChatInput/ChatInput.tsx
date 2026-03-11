'use client'

import { useState } from 'react'
import { toast } from 'sonner'
import { TextArea } from '@/components/ui/textarea'
import { Button } from '@/components/ui/button'
import { useStore } from '@/store'
import useAIChatStreamHandler from '@/hooks/useAIStreamHandler'
import { useQueryState } from 'nuqs'
import {
  Plus,
  Wrench,
  Bot,
  Mic,
  ArrowUp,
  ChevronDown,
} from 'lucide-react'

const ChatInput = () => {
  const { chatInputRef, folders, sessionFolders, setSessionFolder } = useStore()
  const { handleStreamResponse } = useAIChatStreamHandler()
  const [selectedAgent] = useQueryState('agent')
  const [teamId] = useQueryState('team')
  const [sessionId] = useQueryState('session')
  const [inputMessage, setInputMessage] = useState('')
  const isStreaming = useStore((state) => state.isStreaming)

  const handleSubmit = async () => {
    if (!inputMessage.trim()) return
    const currentMessage = inputMessage
    setInputMessage('')
    try {
      await handleStreamResponse(currentMessage)
    } catch (error) {
      toast.error(
        `Erro: ${error instanceof Error ? error.message : String(error)}`
      )
    }
  }

  // Identifica qual a pasta da sessão atual
  const currentFolderId = sessionId ? (sessionFolders[sessionId] || '') : ''

  return (
    <div className="mx-auto w-full max-w-2xl">
      {/* Input Card */}
      <div className="rounded-2xl border border-input-border bg-card shadow-input">
        {/* Text input area */}
        <div className="px-4 pt-3">
          <TextArea
            placeholder="O que posso fazer por você?"
            value={inputMessage}
            onChange={(e) => setInputMessage(e.target.value)}
            onKeyDown={(e) => {
              if (
                e.key === 'Enter' &&
                !e.nativeEvent.isComposing &&
                !e.shiftKey &&
                !isStreaming
              ) {
                e.preventDefault()
                handleSubmit()
              }
            }}
            className="w-full resize-none border-0 bg-transparent p-0 text-sm text-foreground placeholder:text-muted focus:ring-0 focus:outline-none"
            disabled={!(selectedAgent || teamId)}
            ref={chatInputRef}
          />
        </div>

        {/* Toolbar */}
        <div className="flex items-center justify-between px-3 pb-2.5 pt-1">
          <div className="flex items-center gap-1">
            {/* Plus button */}
            <button
              className="flex h-8 w-8 items-center justify-center rounded-lg text-muted hover:bg-sidebar-hover hover:text-foreground transition-colors"
              title="Anexar arquivo"
            >
              <Plus className="h-4 w-4" />
            </button>

            {/* Ferramentas button */}
            <button className="flex h-8 items-center gap-1.5 rounded-lg px-2.5 text-sm text-muted hover:bg-sidebar-hover hover:text-foreground transition-colors">
              <Wrench className="h-3.5 w-3.5" />
              <span className="text-xs font-medium">Ferramentas</span>
            </button>

            {/* Experts button */}
            <button className="flex h-8 items-center gap-1.5 rounded-lg px-2.5 text-sm text-muted hover:bg-sidebar-hover hover:text-foreground transition-colors">
              <Bot className="h-3.5 w-3.5" />
              <span className="text-xs font-medium">Experts</span>
              <ChevronDown className="h-3 w-3" />
            </button>
          </div>

          <div className="flex items-center gap-1.5">
            {/* Folder Selector (Only visible if there is a session) */}
            {sessionId && folders.length > 0 && (
              <select
                value={currentFolderId}
                onChange={(e) => {
                  const val = e.target.value
                  setSessionFolder(sessionId, val === '' ? null : val)
                  toast.success(val === '' ? 'Chat removido da pasta' : 'Chat movido para a pasta')
                }}
                className="h-8 max-w-[120px] rounded-lg border border-border bg-sidebar-bg px-2 text-xs text-muted-foreground outline-none focus:ring-1 focus:ring-brand"
                title="Mover para Projeto"
              >
                <option value="">Sem Projeto</option>
                {folders.map((f) => (
                  <option key={f.id} value={f.id}>
                    {f.name}
                  </option>
                ))}
              </select>
            )}

            {/* Mic button */}
            <button
              className="flex h-8 w-8 items-center justify-center rounded-lg text-muted hover:bg-sidebar-hover hover:text-foreground transition-colors"
              title="Gravar áudio"
            >
              <Mic className="h-4 w-4" />
            </button>

            {/* Send button */}
            <Button
              onClick={handleSubmit}
              disabled={
                !(selectedAgent || teamId) || !inputMessage.trim() || isStreaming
              }
              size="icon"
              className="h-8 w-8 rounded-lg bg-brand text-white hover:bg-brand/90 disabled:opacity-30 transition-all"
            >
              <ArrowUp className="h-4 w-4" />
            </Button>
          </div>
        </div>
      </div>


    </div>
  )
}

export default ChatInput
