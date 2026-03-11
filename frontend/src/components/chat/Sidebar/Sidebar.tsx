'use client'

import { Button } from '@/components/ui/button'
import useChatActions from '@/hooks/useChatActions'
import { useStore } from '@/store'
import { motion, AnimatePresence } from 'framer-motion'
import { useState, useEffect } from 'react'
import { useQueryState } from 'nuqs'
import {
  Home,
  MessageSquare,
  Bell,
  HelpCircle,
  Settings,
  PanelLeftClose,
  PanelLeft,
  Plus,
  Sun,
  Moon,
  ChevronDown,
  Power,
} from 'lucide-react'
import { useTheme } from 'next-themes'
import SearchBar from './SearchBar'
import ProjectFolders from './ProjectFolders'
import ExpertsList from './ExpertsList'
import Sessions from './Sessions'

const NAV_ITEMS = [
  { icon: Home, label: 'Início', id: 'home' },
  { icon: MessageSquare, label: 'Chats', id: 'chats' },
  { icon: Bell, label: 'Notificações', id: 'notifications' },
  { icon: HelpCircle, label: 'Ajuda', id: 'help' },
  { icon: Settings, label: 'Configurações', id: 'settings' },
]

const SidebarHeader = () => (
  <div className="flex items-center gap-2.5 px-1">
    <div className="flex h-8 w-8 items-center justify-center rounded-lg bg-brand text-white text-sm font-bold">
      M
    </div>
    <span className="text-sm font-semibold text-foreground tracking-tight">
      Migliorin-Labs
    </span>
  </div>
)

const Sidebar = ({
  hasEnvToken,
  envToken
}: {
  hasEnvToken?: boolean
  envToken?: string
}) => {
  const [isCollapsed, setIsCollapsed] = useState(false)
  const [isChatsCollapsed, setIsChatsCollapsed] = useState(false)
  const { clearChat, focusChatInput, initialize } = useChatActions()
  const {
    messages,
    selectedEndpoint,
    hydrated,
    mode
  } = useStore()
  const [isMounted, setIsMounted] = useState(false)
  const { theme, setTheme } = useTheme()

  useEffect(() => {
    setIsMounted(true)
    if (hydrated) initialize()
  }, [selectedEndpoint, initialize, hydrated, mode])

  const handleNewChat = () => {
    clearChat()
    focusChatInput()
  }

  return (
    <div className="flex h-screen">
      {/* Vertical Icon Navigation */}
      <div className="flex h-full w-12 shrink-0 flex-col items-center justify-between border-r border-sidebar-border bg-sidebar-bg py-3">
        <div className="flex flex-col items-center gap-1">
          {NAV_ITEMS.map((item) => (
            <button
              key={item.id}
              className="flex h-9 w-9 items-center justify-center rounded-lg text-muted hover:bg-sidebar-hover hover:text-foreground transition-colors"
              title={item.label}
            >
              <item.icon className="h-[18px] w-[18px]" />
            </button>
          ))}
        </div>
        <div className="flex flex-col items-center gap-1">
          {isMounted && (
            <button
              onClick={() => setTheme(theme === 'dark' ? 'light' : 'dark')}
              className="flex h-9 w-9 items-center justify-center rounded-lg text-muted hover:bg-sidebar-hover hover:text-foreground transition-colors"
              title="Alternar tema"
            >
              {theme === 'dark' ? <Sun className="h-[18px] w-[18px]" /> : <Moon className="h-[18px] w-[18px]" />}
            </button>
          )}
          <button
            onClick={async () => {
              const { logout } = await import('@/app/login/actions')
              await logout()
            }}
            className="flex h-9 w-9 items-center justify-center rounded-lg text-muted hover:bg-sidebar-hover hover:text-foreground transition-colors"
            title="Sair (Logout)"
          >
            <Power className="h-[18px] w-[18px]" />
          </button>
        </div>
      </div>

      {/* Main Sidebar Panel */}
      <motion.aside
        className="relative flex h-screen shrink-0 flex-col overflow-hidden border-r border-sidebar-border bg-sidebar-bg"
        initial={{ width: '15rem' }}
        animate={{ width: isCollapsed ? '0rem' : '15rem' }}
        transition={{ type: 'spring', stiffness: 300, damping: 30 }}
      >
        <motion.div
          className="flex h-full w-60 flex-col gap-4 overflow-y-auto px-3 py-3"
          animate={{ opacity: isCollapsed ? 0 : 1 }}
          transition={{ duration: 0.2 }}
          style={{ pointerEvents: isCollapsed ? 'none' : 'auto' }}
        >
          {/* Header */}
          <div className="flex items-center justify-between">
            <SidebarHeader />
            <button
              onClick={() => setIsCollapsed(true)}
              className="flex h-7 w-7 items-center justify-center rounded-md text-muted hover:bg-sidebar-hover hover:text-foreground transition-colors"
            >
              <PanelLeftClose className="h-4 w-4" />
            </button>
          </div>

          {/* Search */}
          <SearchBar />

          {/* New Chat */}
          <Button
            onClick={handleNewChat}
            disabled={messages.length === 0}
            className="h-9 w-full rounded-lg bg-brand text-sm font-medium text-white hover:bg-brand/90 shadow-sm transition-all"
          >
            <Plus className="mr-1.5 h-4 w-4" />
            Novo Chat
          </Button>

          {/* Project Folders */}
          <ProjectFolders />

          {/* Divider */}
          <div className="h-px bg-border" />

          {/* Experts */}
          <ExpertsList />

          {/* Divider */}
          <div className="h-px bg-border" />

          {/* Chat History */}
          <div className="flex flex-col gap-0.5">
            <button
              onClick={() => setIsChatsCollapsed(!isChatsCollapsed)}
              className="flex items-center justify-between px-1 mb-1 group cursor-pointer w-full"
            >
              <span className="text-xs font-semibold uppercase tracking-wider text-muted group-hover:text-foreground transition-colors">
                Chats
              </span>
              <motion.div
                animate={{ rotate: isChatsCollapsed ? -90 : 0 }}
                transition={{ duration: 0.2 }}
                className="text-muted group-hover:text-foreground transition-colors"
              >
                <ChevronDown className="h-4 w-4" />
              </motion.div>
            </button>
            <AnimatePresence initial={false}>
              {!isChatsCollapsed && (
                <motion.div
                  initial={{ height: 0, opacity: 0 }}
                  animate={{ height: 'auto', opacity: 1 }}
                  exit={{ height: 0, opacity: 0 }}
                  transition={{ duration: 0.2 }}
                  className="flex flex-col gap-0.5 overflow-hidden"
                >
                  <Sessions />
                </motion.div>
              )}
            </AnimatePresence>
          </div>
        </motion.div>
      </motion.aside>

      {/* Collapse toggle (shown when collapsed) */}
      <AnimatePresence>
        {isCollapsed && (
          <motion.button
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            exit={{ opacity: 0 }}
            onClick={() => setIsCollapsed(false)}
            className="absolute left-14 top-3 z-10 flex h-7 w-7 items-center justify-center rounded-md text-muted hover:bg-sidebar-hover hover:text-foreground transition-colors"
          >
            <PanelLeft className="h-4 w-4" />
          </motion.button>
        )}
      </AnimatePresence>
    </div>
  )
}

export default Sidebar
