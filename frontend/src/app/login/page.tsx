'use client'

import { useState } from 'react'
import { login, signup } from './actions'
import { Button } from '@/components/ui/button'

export default function LoginPage() {
  const [isLogin, setIsLogin] = useState(true)
  const [error, setError] = useState<string | null>(null)
  const [isLoading, setIsLoading] = useState(false)

  const handleSubmit = async (e: React.FormEvent<HTMLFormElement>) => {
    e.preventDefault()
    setIsLoading(true)
    setError(null)
    
    const formData = new FormData(e.currentTarget)
    
    try {
      if (isLogin) {
        const result = await login(formData)
        if (result?.error) setError(result.error)
      } else {
        const result = await signup(formData)
        if (result?.error) setError(result.error)
      }
    } catch (err) {
      // Re-throw redirect errors, catch others
      if (err instanceof Error && err.message === 'NEXT_REDIRECT') {
        throw err
      }
      setError('An unexpected error occurred.')
    } finally {
      setIsLoading(false)
    }
  }

  return (
    <div className="flex min-h-screen items-center justify-center bg-sidebar-bg font-geist relative overflow-hidden">
      {/* Dynamic Background Elements */}
      <div className="absolute top-[-10%] left-[-10%] w-96 h-96 bg-brand blur-[120px] opacity-20 rounded-full animate-pulse" />
      <div className="absolute bottom-[-10%] right-[-10%] w-96 h-96 bg-purple-500 blur-[120px] opacity-20 rounded-full animate-pulse delay-1000" />
      
      <div className="w-full max-w-md p-8 sm:p-10 rounded-2xl border border-input-border bg-card/60 backdrop-blur-xl shadow-2xl relative z-10 transition-all duration-300 hover:shadow-brand/10">
        <div className="flex flex-col items-center mb-8">
          <div className="w-14 h-14 bg-brand rounded-xl flex items-center justify-center mb-4 text-white text-2xl font-bold shadow-lg">
            M
          </div>
          <h1 className="text-3xl font-bold tracking-tight text-foreground bg-gradient-to-r from-foreground to-foreground/70 bg-clip-text">
            Migliorin-Labs
          </h1>
          <p className="text-sm text-muted-foreground mt-2 text-center">
            {isLogin 
              ? 'Faça login para continuar sua experiência' 
              : 'Crie uma conta para começar a usar os Agentes'}
          </p>
        </div>

        <form onSubmit={handleSubmit} className="space-y-4">
          <div className="space-y-1.5">
            <label className="text-sm font-medium text-foreground/80" htmlFor="email">E-mail</label>
            <input
              id="email"
              name="email"
              type="email"
              required
              className="w-full px-4 py-3 rounded-xl border border-input-border bg-sidebar-bg/50 text-foreground placeholder:text-muted focus:outline-none focus:ring-2 focus:ring-brand/50 transition-all shadow-sm"
              placeholder="seu@email.com"
            />
          </div>
          
          <div className="space-y-1.5">
            <label className="text-sm font-medium text-foreground/80" htmlFor="password">Senha</label>
            <input
              id="password"
              name="password"
              type="password"
              required
              className="w-full px-4 py-3 rounded-xl border border-input-border bg-sidebar-bg/50 text-foreground placeholder:text-muted focus:outline-none focus:ring-2 focus:ring-brand/50 transition-all shadow-sm"
              placeholder="••••••••"
            />
          </div>

          {error && (
            <div className="p-3 bg-red-500/10 border border-red-500/20 rounded-xl text-red-500 text-sm text-center animate-in fade-in slide-in-from-top-1">
              {error}
            </div>
          )}

          <Button 
            formAction={isLogin ? login : signup} 
            className="w-full py-6 mt-6 rounded-xl bg-brand hover:bg-brand/90 text-white font-medium text-lg transition-all shadow-lg hover:shadow-brand/25 relative overflow-hidden group"
            disabled={isLoading}
          >
            <span className="relative z-10">{isLoading ? 'Carregando...' : (isLogin ? 'Entrar' : 'Criar Conta')}</span>
            <div className="absolute inset-0 h-full w-full bg-gradient-to-r from-transparent via-white/20 to-transparent -translate-x-full group-hover:animate-[shimmer_1.5s_infinite]" />
          </Button>
        </form>

        <div className="mt-8 text-center">
          <button
            type="button"
            onClick={() => {
              setIsLogin(!isLogin)
              setError(null)
            }}
            className="text-sm text-brand hover:text-brand/80 transition-colors font-medium"
          >
            {isLogin ? "Não possui uma conta? Crie uma aqui" : 'Já tem uma conta? Faça login'}
          </button>
        </div>
      </div>
    </div>
  )
}
