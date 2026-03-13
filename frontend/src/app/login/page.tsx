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
    <div className="relative flex min-h-screen items-center justify-center overflow-hidden bg-sidebar-bg font-geist">
      {/* Dynamic Background Elements */}
      <div className="absolute left-[-10%] top-[-10%] h-96 w-96 animate-pulse rounded-full bg-brand opacity-20 blur-[120px]" />
      <div className="absolute bottom-[-10%] right-[-10%] h-96 w-96 animate-pulse rounded-full bg-purple-500 opacity-20 blur-[120px] delay-1000" />

      <div className="bg-card/60 hover:shadow-brand/10 relative z-10 w-full max-w-md rounded-2xl border border-input-border p-8 shadow-2xl backdrop-blur-xl transition-all duration-300 sm:p-10">
        <div className="mb-8 flex flex-col items-center">
          <div className="mb-4 flex h-14 w-14 items-center justify-center rounded-xl bg-brand text-2xl font-bold text-white shadow-lg">
            M
          </div>
          <h1 className="to-foreground/70 bg-gradient-to-r from-foreground bg-clip-text text-3xl font-bold tracking-tight text-foreground">
            Migliorin-Labs
          </h1>
          <p className="mt-2 text-center text-sm text-muted-foreground">
            {isLogin
              ? 'Faça login para continuar sua experiência'
              : 'Crie uma conta para começar a usar os Agentes'}
          </p>
        </div>

        <form onSubmit={handleSubmit} className="space-y-4">
          <div className="space-y-1.5">
            <label
              className="text-foreground/80 text-sm font-medium"
              htmlFor="email"
            >
              E-mail
            </label>
            <input
              id="email"
              name="email"
              type="email"
              required
              className="bg-sidebar-bg/50 focus:ring-brand/50 w-full rounded-xl border border-input-border px-4 py-3 text-foreground shadow-sm transition-all placeholder:text-muted focus:outline-none focus:ring-2"
              placeholder="seu@email.com"
            />
          </div>

          <div className="space-y-1.5">
            <label
              className="text-foreground/80 text-sm font-medium"
              htmlFor="password"
            >
              Senha
            </label>
            <input
              id="password"
              name="password"
              type="password"
              required
              className="bg-sidebar-bg/50 focus:ring-brand/50 w-full rounded-xl border border-input-border px-4 py-3 text-foreground shadow-sm transition-all placeholder:text-muted focus:outline-none focus:ring-2"
              placeholder="••••••••"
            />
          </div>

          {error && (
            <div className="rounded-xl border border-red-500/20 bg-red-500/10 p-3 text-center text-sm text-red-500 animate-in fade-in slide-in-from-top-1">
              {error}
            </div>
          )}

          <Button
            type="submit"
            className="hover:bg-brand/90 hover:shadow-brand/25 group relative mt-6 w-full overflow-hidden rounded-xl bg-brand py-6 text-lg font-medium text-white shadow-lg transition-all"
            disabled={isLoading}
          >
            <span className="relative z-10">
              {isLoading ? 'Carregando...' : isLogin ? 'Entrar' : 'Criar Conta'}
            </span>
            <div className="absolute inset-0 h-full w-full -translate-x-full bg-gradient-to-r from-transparent via-white/20 to-transparent group-hover:animate-[shimmer_1.5s_infinite]" />
          </Button>
        </form>

        <div className="mt-8 text-center">
          <button
            type="button"
            onClick={() => {
              setIsLogin(!isLogin)
              setError(null)
            }}
            className="hover:text-brand/80 text-sm font-medium text-brand transition-colors"
          >
            {isLogin
              ? 'Não possui uma conta? Crie uma aqui'
              : 'Já tem uma conta? Faça login'}
          </button>
        </div>
      </div>
    </div>
  )
}
