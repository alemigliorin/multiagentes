'use client'

import { useEffect } from 'react'
import { Settings } from 'lucide-react'
import {
  DropdownMenu,
  DropdownMenuContent,
  DropdownMenuLabel,
  DropdownMenuRadioGroup,
  DropdownMenuRadioItem,
  DropdownMenuSeparator,
  DropdownMenuTrigger
} from '@/components/ui/dropdown-menu'
import { useStore } from '@/store'

const MODEL_GROUPS = [
  {
    provider: 'OpenAI',
    models: [
      { id: 'gpt-5-mini', label: 'GPT-5 Mini' },
      { id: 'gpt-5-nano', label: 'GPT-5 Nano' },
      { id: 'gpt-4o', label: 'GPT-4o' },
      { id: 'gpt-4o-mini', label: 'GPT-4o Mini' }
    ]
  },
  {
    provider: 'Anthropic',
    models: [
      { id: 'claude-sonnet-4-6', label: 'Claude Sonnet 4.6' },
      { id: 'claude-haiku-4-5-20251001', label: 'Claude Haiku 4.5' }
    ]
  },
  {
    provider: 'Google',
    models: [{ id: 'gemini-2.5-flash', label: 'Gemini 2.5 Flash' }]
  },
  {
    provider: 'Groq',
    models: [{ id: 'llama-3.3-70b-versatile', label: 'Llama 3.3 70B' }]
  },
  {
    provider: 'DeepSeek',
    models: [{ id: 'deepseek-chat', label: 'DeepSeek Chat' }]
  }
]

const DEFAULT_MODEL = 'gpt-5-mini'

interface ModelSelectorProps {
  onOpenChange?: (open: boolean) => void
}

const ModelSelector = ({ onOpenChange }: ModelSelectorProps) => {
  const { selectedModel, setSelectedModel, selectedEndpoint } = useStore()
  const activeModel = selectedModel || DEFAULT_MODEL

  // Sincroniza com o backend ao montar — garante que o frontend reflita
  // o modelo atual do orquestrador (ex: após restart do servidor)
  useEffect(() => {
    fetch(`${selectedEndpoint}/api/config/model`)
      .then((r) => r.json())
      .then((data) => {
        if (data.model && !selectedModel) {
          setSelectedModel(data.model)
        }
      })
      .catch(() => {
        // Backend indisponível — mantém o valor do localStorage
      })
  }, [selectedEndpoint]) // eslint-disable-line react-hooks/exhaustive-deps

  const handleModelChange = async (modelId: string) => {
    setSelectedModel(modelId) // atualiza UI imediatamente

    try {
      const res = await fetch(
        `${selectedEndpoint}/api/config/model?model_id=${encodeURIComponent(modelId)}`,
        { method: 'POST' }
      )
      if (!res.ok) {
        console.error('Falha ao atualizar modelo no backend:', await res.text())
      }
    } catch (err) {
      console.error('Erro ao comunicar com o backend:', err)
    }
  }

  return (
    <DropdownMenu onOpenChange={onOpenChange}>
      <DropdownMenuTrigger asChild>
        <button
          className="flex h-9 w-9 items-center justify-center rounded-lg text-muted transition-colors hover:bg-sidebar-hover hover:text-foreground"
          title="Modelo do Orquestrador"
        >
          <Settings className="h-[18px] w-[18px]" />
        </button>
      </DropdownMenuTrigger>
      <DropdownMenuContent side="right" sideOffset={8} className="w-52">
        <DropdownMenuLabel className="text-xs text-muted">
          Modelo do Orquestrador
        </DropdownMenuLabel>
        <DropdownMenuSeparator />
        <DropdownMenuRadioGroup value={activeModel} onValueChange={handleModelChange}>
          {MODEL_GROUPS.map((group, i) => (
            <div key={group.provider}>
              {i > 0 && <DropdownMenuSeparator />}
              <DropdownMenuLabel className="text-xs text-muted">
                {group.provider}
              </DropdownMenuLabel>
              {group.models.map((model) => (
                <DropdownMenuRadioItem key={model.id} value={model.id}>
                  {model.label}
                </DropdownMenuRadioItem>
              ))}
            </div>
          ))}
        </DropdownMenuRadioGroup>
      </DropdownMenuContent>
    </DropdownMenu>
  )
}

export default ModelSelector
