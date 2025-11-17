import React, { useContext, useState } from 'react'
import { Link } from 'react-router-dom'
import { SparklesIcon } from '@heroicons/react/24/solid'
import AdminLoginModal from './AdminLoginModal'
import AuthContext from '../utils/AuthContext'

export default function Navbar(){
  const auth = useContext(AuthContext)
  const [showLogin, setShowLogin] = useState(false)
  const isAdmin = auth?.isAdmin
  return (
    <header className="p-4 shadow" style={{background: 'linear-gradient(90deg, var(--app-card), rgba(255,255,255,0.02))'}}>
      <div className="container mx-auto flex items-center justify-between" role="navigation" aria-label="Main navigation">
        <div className="flex items-center space-x-4">
          <div style={{background:'linear-gradient(135deg, var(--app-primary), var(--app-accent-2))'}} className="p-2 rounded-lg">
            <SparklesIcon className="w-7 h-7 text-white"/>
          </div>
          <div>
            <div className="text-xl font-semibold" style={{color:'var(--app-text)'}}>Haven Control Room</div>
            <div className="text-sm muted" style={{color:'var(--app-accent-3)'}}>Web</div>
          </div>
        </div>
        <nav className="space-x-2" aria-label="Primary">
          <Link className="px-3 py-1 hover:underline" to="/">Dashboard</Link>
          <Link className="px-3 py-1 hover:underline" to="/systems">Systems</Link>
          <Link className="px-3 py-1 hover:underline" to="/wizard">Create</Link>
          {isAdmin && <Link className="px-3 py-1 hover:underline" to="/rtai">RT-AI</Link>}
          {isAdmin && <Link className="px-3 py-1 hover:underline" to="/settings">Settings</Link>}
          <Link className="px-3 py-1 hover:underline" to="/discoveries">Discoveries</Link>
          {isAdmin && <Link className="px-3 py-1 hover:underline" to="/tests">Tests</Link>}
          <Link className="px-3 py-1 hover:underline" to="/db_stats">DB Stats</Link>
          {/* Admin control */}
          {!isAdmin ? (
            <button className="px-3 py-1 bg-blue-500 text-white rounded" onClick={()=>setShowLogin(true)}>Unlock</button>
          ) : (
            <button className="px-3 py-1 bg-red-500 text-white rounded" onClick={()=>auth.logout()}>Logout</button>
          )}
        </nav>
        <AdminLoginModal open={showLogin} onClose={()=>setShowLogin(false)} />
      </div>
    </header>
  )
}
