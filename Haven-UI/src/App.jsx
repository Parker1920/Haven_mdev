import React, { useEffect } from 'react'
import { Routes, Route, Link } from 'react-router-dom'
import Dashboard from './pages/Dashboard'
import Systems from './pages/SystemsNew'
import Wizard from './pages/Wizard'
import RTAI from './pages/RTAI'
import Settings from './pages/Settings'
import Discoveries from './pages/Discoveries'
import Tests from './pages/Tests'
import DBStats from './pages/DBStats'
import Navbar from './components/Navbar'
import { AuthProvider, AuthContext } from './utils/AuthContext'
import { useContext } from 'react'
import { Navigate } from 'react-router-dom'

function RequireAdmin({children}){
  const auth = useContext(AuthContext)
  if (!auth || !auth.isAdmin) return <Navigate to='/' replace />
  return children
}

export default function App(){
  useEffect(() => {
    // Fetch server settings and apply server-side theme (if present)
    fetch('/api/settings')
      .then(res => res.json())
      .then(settings => {
        if (!settings) return
        const theme = settings.theme || {}
        // Apply background and text color if provided
        if (theme.bg) document.documentElement.style.setProperty('--app-bg', theme.bg)
        if (theme.text) document.documentElement.style.setProperty('--app-text', theme.text)
        if (theme.card) document.documentElement.style.setProperty('--app-card', theme.card)
        if (theme.primary) document.documentElement.style.setProperty('--app-primary', theme.primary)
      })
      .catch(() => {})
  }, [])

  return (
    <AuthProvider>
    <div className="min-h-screen" style={{backgroundColor: 'var(--app-bg, #f8fafc)', color: 'var(--app-text, #111827)'}}>
      <Navbar />
      <main className="container mx-auto p-6">
        <Routes>
          <Route path="/" element={<Dashboard />} />
          <Route path="/systems" element={<Systems />} />
          <Route path="/wizard" element={<Wizard />} />
          <Route path="/rtai" element={<RequireAdmin><RTAI /></RequireAdmin>} />
          <Route path="/settings" element={<RequireAdmin><Settings /></RequireAdmin>} />
          <Route path="/discoveries" element={<Discoveries />} />
          <Route path="/tests" element={<RequireAdmin><Tests /></RequireAdmin>} />
          <Route path="/db_stats" element={<DBStats />} />
        </Routes>
      </main>
    </div>
  )
}
