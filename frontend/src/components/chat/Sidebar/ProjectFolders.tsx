'use client'

import { useState } from 'react'
import { motion, AnimatePresence } from 'framer-motion'
import { Folder, Plus, X, Tag, Trash2 } from 'lucide-react'
import { useStore } from '@/store'

// Cores predefinidas para novas pastas
const FOLDER_COLORS = [
    '#8b5cf6', '#3b82f6', '#10b981', '#f59e0b', '#ec4899', '#06b6d4', '#84cc16'
]

const ProjectFolders = () => {
    const { folders, sessionFolders, activeFolderId, setActiveFolderId, addFolder, deleteFolder } = useStore()
    const [isCreating, setIsCreating] = useState(false)
    const [newFolderName, setNewFolderName] = useState('')

    const handleCreateFolder = (e: React.FormEvent) => {
        e.preventDefault()
        if (!newFolderName.trim()) {
            setIsCreating(false)
            return
        }

        const newFolder = {
            id: Date.now().toString(),
            name: newFolderName.trim(),
            color: FOLDER_COLORS[folders.length % FOLDER_COLORS.length]
        }

        addFolder(newFolder)
        setNewFolderName('')
        setIsCreating(false)
    }

    // Calcula quantos chats tem em cada pasta
    const getFolderCount = (folderId: string) => {
        return Object.values(sessionFolders).filter((id) => id === folderId).length
    }

    return (
        <div className="flex flex-col gap-0.5">
            <div className="flex items-center justify-between px-1 mb-1">
                <span className="text-xs font-semibold uppercase tracking-wider text-muted">
                    Projetos
                </span>
                <button
                    onClick={() => setIsCreating(!isCreating)}
                    title="Novo Projeto"
                    className="text-muted hover:text-foreground transition-colors p-1 rounded-md hover:bg-sidebar-hover"
                >
                    <Plus className="h-3.5 w-3.5" />
                </button>
            </div>

            <AnimatePresence>
                {isCreating && (
                    <motion.form
                        initial={{ opacity: 0, height: 0 }}
                        animate={{ opacity: 1, height: 'auto' }}
                        exit={{ opacity: 0, height: 0 }}
                        onSubmit={handleCreateFolder}
                        className="mb-2 px-1 overflow-hidden"
                    >
                        <div className="flex items-center gap-2 bg-sidebar-hover rounded-md p-1.5 border border-border/50">
                            <Tag className="h-3.5 w-3.5 text-muted ml-1" />
                            <input
                                autoFocus
                                type="text"
                                placeholder="Nome do projeto..."
                                value={newFolderName}
                                onChange={(e) => setNewFolderName(e.target.value)}
                                onKeyDown={(e) => {
                                    if (e.key === 'Escape') setIsCreating(false)
                                }}
                                onBlur={() => {
                                    if (!newFolderName.trim()) setIsCreating(false)
                                }}
                                className="flex-1 bg-transparent text-sm text-foreground outline-none placeholder:text-muted/70"
                            />
                            <button
                                type="button"
                                onClick={() => setIsCreating(false)}
                                className="p-0.5 text-muted hover:text-foreground"
                            >
                                <X className="h-3 w-3" />
                            </button>
                        </div>
                    </motion.form>
                )}
            </AnimatePresence>

            <button
                onClick={() => setActiveFolderId(null)}
                className={`flex w-full items-center justify-between rounded-lg px-2 py-2 text-sm transition-colors group ${activeFolderId === null ? 'bg-sidebar-hover text-foreground font-medium' : 'text-foreground hover:bg-sidebar-hover'
                    }`}
            >
                <div className="flex items-center gap-2.5">
                    <span className="truncate">Todos os Chats</span>
                </div>
            </button>

            {folders.map((folder) => {
                const isActive = activeFolderId === folder.id
                return (
                    <motion.button
                        key={folder.id}
                        onClick={() => setActiveFolderId(folder.id)}
                        className={`flex w-full items-center justify-between rounded-lg px-2 py-2 text-sm transition-colors group ${isActive ? 'bg-sidebar-hover text-foreground font-medium' : 'text-foreground hover:bg-sidebar-hover'
                            }`}
                        whileTap={{ scale: 0.98 }}
                    >
                        <div className="flex items-center gap-2.5">
                            <Folder
                                className="h-4 w-4 shrink-0"
                                style={{ color: folder.color }}
                                fill={isActive ? folder.color : 'transparent'}
                                strokeWidth={1.5}
                            />
                            <span className="truncate">{folder.name}</span>
                        </div>
                        <div className="flex items-center gap-1">
                            <span className="text-xs text-muted tabular-nums">
                                {getFolderCount(folder.id)}
                            </span>
                            <div
                                role="button"
                                tabIndex={0}
                                onClick={(e) => {
                                    e.stopPropagation()
                                    if (window.confirm(`Tem certeza que deseja apagar o projeto "${folder.name}"?`)) {
                                        deleteFolder(folder.id)
                                    }
                                }}
                                onKeyDown={(e) => {
                                    if (e.key === 'Enter') {
                                        e.stopPropagation()
                                        if (window.confirm(`Tem certeza que deseja apagar o projeto "${folder.name}"?`)) {
                                            deleteFolder(folder.id)
                                        }
                                    }
                                }}
                                className="opacity-0 group-hover:opacity-100 p-1 text-muted hover:text-red-500 hover:bg-red-500/10 rounded-md transition-all flex items-center justify-center focus:opacity-100"
                                title="Excluir Projeto"
                            >
                                <Trash2 className="h-3.5 w-3.5" />
                            </div>
                        </div>
                    </motion.button>
                )
            })}
        </div>
    )
}

export default ProjectFolders
