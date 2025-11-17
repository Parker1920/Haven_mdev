import React, { createContext, useState, useEffect } from 'react'

export const AuthContext = createContext({ isAdmin: false, login: async () => {}, logout: async () => {} })

export function AuthProvider({ children }){
  const [isAdmin, setIsAdmin] = useState(false)

  useEffect(() => {
    let mounted = true
    fetch('/api/admin/status', { credentials: 'include' })
      .then(r => r.json())
      .then(j => { if (mounted) setIsAdmin(Boolean(j.logged_in)) })
      .catch(() => {})
    return () => { mounted = false }
  }, [])

  async function login(password){
    const r = await fetch('/api/admin/login', { method: 'POST', credentials: 'include', headers: { 'Content-Type':'application/json'}, body: JSON.stringify({ password }) })
    if (!r.ok) {
      const t = await r.text()
      throw new Error(t || 'Login failed')
    }
    // assume cookie set
    setIsAdmin(true)
    return true
  }

  async function logout(){
    await fetch('/api/admin/logout', { method: 'POST', credentials: 'include' })
    setIsAdmin(false)
  }

  return (
    <AuthContext.Provider value={{ isAdmin, login, logout }}>
      {children}
    </AuthContext.Provider>
  )
}

export default AuthContext
