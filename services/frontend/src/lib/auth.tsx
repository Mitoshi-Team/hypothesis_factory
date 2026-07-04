import {
  createContext,
  useCallback,
  useContext,
  useEffect,
  useMemo,
  useState,
  type ReactNode,
} from 'react'
import type { User } from '@/types'
import {
  getStoredUser,
  login as apiLogin,
  logout as apiLogout,
  onAuthExpired,
  register as apiRegister,
} from '@/lib/api'

interface AuthContextValue {
  user: User | null
  login: (username: string, password: string) => Promise<void>
  register: (username: string, password: string) => Promise<void>
  logout: () => void
}

const AuthContext = createContext<AuthContextValue | null>(null)

export function AuthProvider({ children }: { children: ReactNode }) {
  const [user, setUser] = useState<User | null>(() => getStoredUser())

  // When a refresh token dies mid-session the API client broadcasts it —
  // flip to the logged-out state without reloading the page.
  useEffect(() => onAuthExpired(() => setUser(null)), [])

  const login = useCallback(async (username: string, password: string) => {
    const u = await apiLogin(username.trim(), password)
    setUser(u)
  }, [])

  const register = useCallback(async (username: string, password: string) => {
    const u = await apiRegister(username.trim(), password)
    setUser(u)
  }, [])

  const logout = useCallback(() => {
    apiLogout()
    setUser(null)
  }, [])

  const value = useMemo(
    () => ({ user, login, register, logout }),
    [user, login, register, logout],
  )

  return <AuthContext.Provider value={value}>{children}</AuthContext.Provider>
}

export function useAuth(): AuthContextValue {
  const ctx = useContext(AuthContext)
  if (!ctx) throw new Error('useAuth must be used within AuthProvider')
  return ctx
}
