import { create } from 'zustand'
import { persist, createJSONStorage } from 'zustand/middleware'

import {
  AgentDetails,
  SessionEntry,
  TeamDetails,
  type ChatMessage
} from '@/types/os'

export interface ProjectFolder {
  id: string
  name: string
  color: string
}

interface Store {
  hydrated: boolean
  setHydrated: () => void
  streamingErrorMessage: string
  setStreamingErrorMessage: (streamingErrorMessage: string) => void
  endpoints: {
    endpoint: string
    id__endpoint: string
  }[]
  setEndpoints: (
    endpoints: {
      endpoint: string
      id__endpoint: string
    }[]
  ) => void
  isStreaming: boolean
  setIsStreaming: (isStreaming: boolean) => void
  isEndpointActive: boolean
  setIsEndpointActive: (isActive: boolean) => void
  isEndpointLoading: boolean
  setIsEndpointLoading: (isLoading: boolean) => void
  messages: ChatMessage[]
  setMessages: (
    messages: ChatMessage[] | ((prevMessages: ChatMessage[]) => ChatMessage[])
  ) => void
  chatInputRef: React.RefObject<HTMLTextAreaElement | null>
  selectedEndpoint: string
  setSelectedEndpoint: (selectedEndpoint: string) => void
  authToken: string
  setAuthToken: (authToken: string) => void
  agents: AgentDetails[]
  setAgents: (agents: AgentDetails[]) => void
  teams: TeamDetails[]
  setTeams: (teams: TeamDetails[]) => void
  selectedModel: string
  setSelectedModel: (model: string) => void
  mode: 'agent' | 'team'
  setMode: (mode: 'agent' | 'team') => void
  sessionsData: SessionEntry[] | null
  setSessionsData: (
    sessionsData:
      | SessionEntry[]
      | ((prevSessions: SessionEntry[] | null) => SessionEntry[] | null)
  ) => void
  isSessionsLoading: boolean
  setIsSessionsLoading: (isSessionsLoading: boolean) => void

  // Folder Management State
  folders: ProjectFolder[]
  setFolders: (folders: ProjectFolder[]) => void
  addFolder: (folder: ProjectFolder) => void
  deleteFolder: (folderId: string) => void

  sessionFolders: Record<string, string> // Mapeia session_id -> folder_id
  setSessionFolder: (sessionId: string, folderId: string | null) => void // null para remover da pasta

  activeFolderId: string | null
  setActiveFolderId: (folderId: string | null) => void

  searchQuery: string
  setSearchQuery: (query: string) => void
}

export const useStore = create<Store>()(
  persist(
    (set) => ({
      hydrated: false,
      setHydrated: () => set({ hydrated: true }),
      streamingErrorMessage: '',
      setStreamingErrorMessage: (streamingErrorMessage) =>
        set(() => ({ streamingErrorMessage })),
      endpoints: [],
      setEndpoints: (endpoints) => set(() => ({ endpoints })),
      isStreaming: false,
      setIsStreaming: (isStreaming) => set(() => ({ isStreaming })),
      isEndpointActive: false,
      setIsEndpointActive: (isActive) =>
        set(() => ({ isEndpointActive: isActive })),
      isEndpointLoading: true,
      setIsEndpointLoading: (isLoading) =>
        set(() => ({ isEndpointLoading: isLoading })),
      messages: [],
      setMessages: (messages) =>
        set((state) => ({
          messages:
            typeof messages === 'function' ? messages(state.messages) : messages
        })),
      chatInputRef: { current: null },
      selectedEndpoint:
        process.env.NEXT_PUBLIC_DEFAULT_ENDPOINT || 'http://localhost:8000',
      setSelectedEndpoint: (selectedEndpoint) =>
        set(() => ({ selectedEndpoint })),
      authToken: '',
      setAuthToken: (authToken) => set(() => ({ authToken })),
      agents: [],
      setAgents: (agents) => set({ agents }),
      teams: [],
      setTeams: (teams) => set({ teams }),
      selectedModel: '',
      setSelectedModel: (selectedModel) => set(() => ({ selectedModel })),
      mode: 'agent',
      setMode: (mode) => set(() => ({ mode })),
      sessionsData: null,
      setSessionsData: (sessionsData) =>
        set((state) => ({
          sessionsData:
            typeof sessionsData === 'function'
              ? sessionsData(state.sessionsData)
              : sessionsData
        })),
      isSessionsLoading: false,
      setIsSessionsLoading: (isSessionsLoading) =>
        set(() => ({ isSessionsLoading })),

      // Folder Management implementation
      folders: [],
      setFolders: (folders) => set(() => ({ folders })),
      addFolder: (folder) =>
        set((state) => ({ folders: [...state.folders, folder] })),
      deleteFolder: (folderId) =>
        set((state) => {
          // Remove a pasta
          const newFolders = state.folders.filter((f) => f.id !== folderId)

          // Remove vínculos das sessões com essa pasta
          const newSessionFolders = { ...state.sessionFolders }
          Object.keys(newSessionFolders).forEach((key) => {
            if (newSessionFolders[key] === folderId) {
              delete newSessionFolders[key]
            }
          })

          return {
            folders: newFolders,
            sessionFolders: newSessionFolders,
            activeFolderId:
              state.activeFolderId === folderId ? null : state.activeFolderId
          }
        }),

      sessionFolders: {},
      setSessionFolder: (sessionId, folderId) =>
        set((state) => {
          const newSessionFolders = { ...state.sessionFolders }
          if (folderId === null) {
            delete newSessionFolders[sessionId]
          } else {
            newSessionFolders[sessionId] = folderId
          }
          return { sessionFolders: newSessionFolders }
        }),

      activeFolderId: null,
      setActiveFolderId: (activeFolderId) => set(() => ({ activeFolderId })),

      searchQuery: '',
      setSearchQuery: (searchQuery) => set(() => ({ searchQuery }))
    }),
    {
      name: 'endpoint-storage',
      storage: createJSONStorage(() => localStorage),
      partialize: (state) => ({
        selectedEndpoint: state.selectedEndpoint,
        folders: state.folders,
        sessionFolders: state.sessionFolders
      }),
      onRehydrateStorage: () => (state) => {
        state?.setHydrated?.()
      }
    }
  )
)
