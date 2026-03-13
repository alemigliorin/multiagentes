'use client'

import { useState, useRef } from 'react'
import { toast } from 'sonner'
import { TextArea } from '@/components/ui/textarea'
import { Button } from '@/components/ui/button'
import { useStore } from '@/store'
import useAIChatStreamHandler from '@/hooks/useAIStreamHandler'
import { useQueryState } from 'nuqs'
import { Plus, Wrench, Bot, Mic, ArrowUp, ChevronDown, X } from 'lucide-react'
import {
  DropdownMenu,
  DropdownMenuContent,
  DropdownMenuItem,
  DropdownMenuTrigger
} from '@/components/ui/dropdown-menu'
import {
  Dialog,
  DialogContent,
  DialogDescription,
  DialogFooter,
  DialogHeader,
  DialogTitle
} from '@/components/ui/dialog'

const ChatInput = () => {
  const { chatInputRef, folders, sessionFolders, setSessionFolder } = useStore()
  const { handleStreamResponse } = useAIChatStreamHandler()
  const [selectedAgent] = useQueryState('agent')
  const [teamId] = useQueryState('team')
  const [sessionId] = useQueryState('session')
  const [inputMessage, setInputMessage] = useState('')
  const isStreaming = useStore((state) => state.isStreaming)

  // PDF Temp Upload
  const [selectedTempFile, setSelectedTempFile] = useState<File | null>(null)
  const [isUploadingTemp, setIsUploadingTemp] = useState(false)

  // Video Upload
  const [isVideoModalOpen, setIsVideoModalOpen] = useState(false)
  const [videoCreatorName, setVideoCreatorName] = useState('')
  const [selectedVideoFile, setSelectedVideoFile] = useState<File | null>(null)
  const [isUploadingVideo, setIsUploadingVideo] = useState(false)

  const tempFileInputRef = useRef<HTMLInputElement>(null)
  const ragFileInputRef = useRef<HTMLInputElement>(null)
  const videoFileInputRef = useRef<HTMLInputElement>(null)

  const handleSubmit = async () => {
    if (!inputMessage.trim() && !selectedTempFile) return
    setIsUploadingTemp(true)

    let messageToSend = inputMessage

    if (selectedTempFile) {
      const toastId = toast.loading(`Analisando ${selectedTempFile.name}...`)
      try {
        const formData = new FormData()
        formData.append('file', selectedTempFile)
        formData.append('save_to_rag', 'false')

        const { createClient } = await import('@/utils/supabase/client')
        const supabase = createClient()
        const {
          data: { session: currentSession }
        } = await supabase.auth.getSession()
        const token =
          currentSession?.access_token || useStore.getState().authToken

        const res = await fetch(
          `${process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000'}/upload-pdf`,
          {
            method: 'POST',
            headers: token ? { Authorization: `Bearer ${token}` } : {},
            body: formData
          }
        )
        const data = await res.json()
        if (data.status === 'success') {
          messageToSend = `[DOCUMENTO TEMPORÁRIO: ${selectedTempFile.name}]\n${data.extracted_text}\n[FIM DO DOCUMENTO]\n\n${messageToSend}`
          setSelectedTempFile(null)
          toast.dismiss(toastId)
        } else {
          toast.error(data.error || 'Erro ao ler PDF', { id: toastId })
          setIsUploadingTemp(false)
          return
        }
      } catch (err) {
        toast.error('Falha na requisição de upload', { id: toastId })
        setIsUploadingTemp(false)
        return
      }
    }

    setInputMessage('')
    setIsUploadingTemp(false)
    try {
      if (messageToSend.trim() !== '') {
        await handleStreamResponse(messageToSend)
      }
    } catch (error) {
      toast.error(
        `Erro: ${error instanceof Error ? error.message : String(error)}`
      )
    }
  }

  const handleRagUpload = async (e: React.ChangeEvent<HTMLInputElement>) => {
    const file = e.target.files?.[0]
    if (!file) return
    const toastId = toast.loading(
      `Enviando ${file.name} para a Base Global (RAG)...`
    )
    try {
      const formData = new FormData()
      formData.append('file', file)
      formData.append('save_to_rag', 'true')

      const { createClient } = await import('@/utils/supabase/client')
      const supabase = createClient()
      const {
        data: { session: currentSession }
      } = await supabase.auth.getSession()
      const token =
        currentSession?.access_token || useStore.getState().authToken

      const res = await fetch(
        `${process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000'}/upload-pdf`,
        {
          method: 'POST',
          headers: token ? { Authorization: `Bearer ${token}` } : {},
          body: formData
        }
      )
      const data = await res.json()
      if (data.status === 'success') {
        toast.success('Documento salvo e indexado na base de conhecimento!', {
          id: toastId
        })
      } else {
        toast.error(data.error || 'Erro ao indexar no RAG', { id: toastId })
      }
    } catch (err) {
      toast.error('Erro de conexão com o servidor', { id: toastId })
    }
    if (ragFileInputRef.current) ragFileInputRef.current.value = ''
  }

  const handleVideoSubmit = async () => {
    if (!videoCreatorName.trim() || !selectedVideoFile) {
      toast.error('Preencha o nome do criador e selecione um vídeo.')
      return
    }
    setIsUploadingVideo(true)
    const toastId = toast.loading(
      `Enviando ${selectedVideoFile.name} para a pasta de ${videoCreatorName}...`
    )
    try {
      const formData = new FormData()
      formData.append('file', selectedVideoFile)
      formData.append('creator_name', videoCreatorName)

      const { createClient } = await import('@/utils/supabase/client')
      const supabase = createClient()
      const {
        data: { session: currentSession }
      } = await supabase.auth.getSession()
      const token =
        currentSession?.access_token || useStore.getState().authToken

      const res = await fetch(
        `${process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000'}/upload-video`,
        {
          method: 'POST',
          headers: token ? { Authorization: `Bearer ${token}` } : {},
          body: formData
        }
      )
      const data = await res.json()
      if (data.status === 'success') {
        toast.success('Vídeo salvo com sucesso para transcrição futura!', {
          id: toastId
        })
        setIsVideoModalOpen(false)
        setVideoCreatorName('')
        setSelectedVideoFile(null)
      } else {
        toast.error(data.error || 'Erro ao salvar o vídeo', { id: toastId })
      }
    } catch (err) {
      toast.error('Erro de conexão ao enviar o vídeo', { id: toastId })
    }
    setIsUploadingVideo(false)
    if (videoFileInputRef.current) videoFileInputRef.current.value = ''
  }

  const currentFolderId = sessionId ? sessionFolders[sessionId] || '' : ''

  return (
    <div className="mx-auto w-full max-w-2xl pb-4">
      {/* Input Card */}
      <div className="rounded-2xl border border-input-border bg-card shadow-input">
        {/* Attachment Pill */}
        {selectedTempFile && (
          <div className="px-4 pb-1 pt-4">
            <div className="border-brand/30 flex w-max items-center gap-2 rounded-md border bg-transparent px-3 py-1.5 text-xs text-foreground shadow-sm">
              <span className="max-w-[200px] truncate">
                {selectedTempFile.name}
              </span>
              <button
                disabled={isUploadingTemp}
                onClick={() => setSelectedTempFile(null)}
                className="transition-colors hover:text-red-500"
              >
                <X className="h-3.5 w-3.5" />
              </button>
            </div>
          </div>
        )}

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
                !isStreaming &&
                !isUploadingTemp
              ) {
                e.preventDefault()
                handleSubmit()
              }
            }}
            className="w-full resize-none border-0 bg-transparent p-0 text-sm text-foreground placeholder:text-muted focus:outline-none focus:ring-0"
            disabled={!(selectedAgent || teamId) || isUploadingTemp}
            ref={chatInputRef}
          />
        </div>

        {/* Toolbar */}
        <div className="flex items-center justify-between px-3 pb-2.5 pt-1">
          <div className="flex items-center gap-1">
            {/* Plus button */}
            <input
              type="file"
              accept=".pdf"
              className="hidden"
              ref={tempFileInputRef}
              onChange={(e) => setSelectedTempFile(e.target.files?.[0] || null)}
            />
            <button
              onClick={() => tempFileInputRef.current?.click()}
              className="flex h-8 w-8 items-center justify-center rounded-lg text-muted transition-colors hover:bg-sidebar-hover hover:text-foreground"
              title="Anexar arquivo PDF temporário"
            >
              <Plus className="h-4 w-4" />
            </button>

            {/* Ferramentas button */}
            <input
              type="file"
              accept=".pdf"
              className="hidden"
              ref={ragFileInputRef}
              onChange={handleRagUpload}
            />
            <DropdownMenu>
              <DropdownMenuTrigger asChild>
                <button className="flex h-8 items-center gap-1.5 rounded-lg px-2.5 text-sm text-muted outline-none ring-0 transition-colors hover:bg-sidebar-hover hover:text-foreground">
                  <Wrench className="h-3.5 w-3.5" />
                  <span className="text-xs font-medium">Ferramentas</span>
                </button>
              </DropdownMenuTrigger>
              <DropdownMenuContent
                align="start"
                className="z-50 w-64 rounded-xl border-border bg-background p-1 shadow-md"
              >
                <DropdownMenuItem
                  className="cursor-pointer rounded-lg px-3 py-2 text-sm text-foreground hover:bg-sidebar-hover focus:bg-sidebar-hover"
                  onClick={() => ragFileInputRef.current?.click()}
                >
                  Adicionar ao RAG Global (PDF)
                </DropdownMenuItem>
                <DropdownMenuItem
                  className="cursor-pointer rounded-lg px-3 py-2 text-sm text-foreground hover:bg-sidebar-hover focus:bg-sidebar-hover"
                  onClick={() => setIsVideoModalOpen(true)}
                >
                  Upload de Vídeo (Transcrição)
                </DropdownMenuItem>
              </DropdownMenuContent>
            </DropdownMenu>

            {/* Experts button */}
            <button className="flex hidden h-8 items-center gap-1.5 rounded-lg px-2.5 text-sm text-muted transition-colors hover:bg-sidebar-hover hover:text-foreground">
              <Bot className="h-3.5 w-3.5" />
              <span className="text-xs font-medium">Experts</span>
              <ChevronDown className="h-3 w-3" />
            </button>
          </div>

          <div className="flex items-center gap-1.5">
            {/* Folder Selector */}
            {sessionId && folders.length > 0 && (
              <select
                value={currentFolderId}
                onChange={(e) => {
                  const val = e.target.value
                  setSessionFolder(sessionId, val === '' ? null : val)
                  toast.success(
                    val === ''
                      ? 'Chat removido da pasta'
                      : 'Chat movido para a pasta'
                  )
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

            {/* Send button */}
            <Button
              onClick={handleSubmit}
              disabled={
                (!(selectedAgent || teamId) ||
                  !inputMessage.trim() ||
                  isStreaming ||
                  isUploadingTemp) &&
                !selectedTempFile
              }
              size="icon"
              className="hover:bg-brand/90 h-8 w-8 rounded-lg bg-brand text-white transition-all disabled:opacity-30"
            >
              <ArrowUp className="h-4 w-4" />
            </Button>
          </div>
        </div>
      </div>

      {/* Video Upload Modal */}
      <Dialog open={isVideoModalOpen} onOpenChange={setIsVideoModalOpen}>
        <DialogContent className="z-50 rounded-xl border-border bg-card shadow-xl sm:max-w-md">
          <DialogHeader>
            <DialogTitle className="text-lg text-foreground">
              Upload de Vídeo
            </DialogTitle>
            <DialogDescription className="text-sm text-muted-foreground">
              Selecione o vídeo e especifique o nome do criador para adicioná-lo
              à pasta do repositório.
            </DialogDescription>
          </DialogHeader>
          <div className="flex flex-col gap-5 py-4">
            <div className="flex flex-col gap-2">
              <label className="text-xs font-semibold uppercase tracking-widest text-foreground">
                Nome do Criador
              </label>
              <input
                type="text"
                placeholder="Ex: jeffnippard"
                value={videoCreatorName}
                onChange={(e) => setVideoCreatorName(e.target.value)}
                className="w-full rounded-lg border border-input-border bg-input-bg px-3 py-2 text-sm text-foreground outline-none focus:ring-1 focus:ring-brand"
              />
            </div>
            <div className="flex flex-col gap-2">
              <label className="text-xs font-semibold uppercase tracking-widest text-foreground">
                Arquivo do Vídeo
              </label>
              <input
                type="file"
                accept=".mp4,.mov,.webm,.avi"
                ref={videoFileInputRef}
                onChange={(e) =>
                  setSelectedVideoFile(e.target.files?.[0] || null)
                }
                className="hover:file:bg-brand/90 w-full rounded-lg border border-input-border bg-input-bg p-2 text-sm text-foreground transition-colors file:mr-4 file:cursor-pointer file:rounded-md file:border-0 file:bg-brand file:px-4 file:py-2 file:text-xs file:font-semibold file:text-white"
              />
            </div>
          </div>
          <DialogFooter className="mt-2 gap-2 sm:justify-end">
            <Button
              variant="ghost"
              onClick={() => setIsVideoModalOpen(false)}
              className="h-9 text-sm text-muted-foreground hover:text-foreground"
            >
              Cancelar
            </Button>
            <Button
              disabled={
                isUploadingVideo || !videoCreatorName || !selectedVideoFile
              }
              onClick={handleVideoSubmit}
              className="hover:bg-brand/90 h-9 bg-brand text-sm text-white"
            >
              {isUploadingVideo ? 'Enviando...' : 'Fazer Upload'}
            </Button>
          </DialogFooter>
        </DialogContent>
      </Dialog>
    </div>
  )
}

export default ChatInput
