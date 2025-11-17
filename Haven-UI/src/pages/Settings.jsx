import React, { useEffect, useState } from 'react'
import { apiGet, apiPost, adminLogin, adminLogout, adminStatus } from '../utils/api'

export default function Settings(){
  const [settings, setSettings] = useState({})
  const [loading, setLoading] = useState(true)
  const [saving, setSaving] = useState(false)
  const [adminToken, setAdminToken] = useState('')
  const [isAdmin, setIsAdmin] = useState(false)
  const [password, setPassword] = useState('')

  useEffect(() => {
    apiGet('/api/settings')
      .then(s => { setSettings(s || {}); setLoading(false) })
      .catch(() => setLoading(false))
    adminStatus().then(r => setIsAdmin(!!r.logged_in)).catch(()=>{})
  }, [])

  const save = async () => {
    setSaving(true)
    try{
      // Attempt POST using session cookie for admin access
      await apiPost('/api/settings', settings, { adminToken: adminToken || undefined })
      alert('Settings saved')
    }catch(e){
      alert('Failed to save settings: ' + e)
    }
    setSaving(false)
  }

  const doLogin = async () => {
    try{
      await adminLogin(password)
      setIsAdmin(true)
      alert('Admin login successful')
    }catch(e){
      alert('Login failed: ' + e)
    }
  }

  const doLogout = async () => {
    try{
      await adminLogout()
      setIsAdmin(false)
      alert('Logged out')
    }catch(e){
      alert('Logout failed: ' + e)
    }
  }

  const doBackup = async () => {
    try{
      const res = await fetch('/api/backup', { method: 'POST', credentials: 'same-origin' })
      if(!res.ok) throw new Error(await res.text())
      const j = await res.json()
      alert('Backup created: ' + j.backup_path)
    }catch(e){ alert('Backup failed: '+ e) }
  }

  const onUploadDB = async (e) => {
    try{
      const file = e.target.files && e.target.files[0]
      if(!file) return
      const fd = new FormData(); fd.append('file', file)
      const res = await fetch('/api/db_upload', { method:'POST', credentials: 'same-origin', body: fd })
      if(!res.ok) throw new Error(await res.text())
      const j = await res.json()
      alert('DB uploaded: '+ j.path)
    }catch(e){ alert('DB upload failed: ' + e) }
  }

  const updateTheme = (k, v) => {
    const theme = Object.assign({}, (settings.theme || {}), { [k]: v })
    setSettings({...settings, theme})
  }

  return (
    <div>
      <div className="card">
        <h2 className="text-lg font-semibold">Settings & Admin</h2>
        <div className="mt-3">
          <p className="text-sm muted">Server-side theme controls the color palette for all users.</p>
          {loading ? (
            <p className="mt-2 muted">Loading...</p>
          ) : (
            <div className="mt-3">
              <label className="block mt-2">Background color</label>
              <input type="color" value={(settings.theme && settings.theme.bg) || '#f8fafc'} onChange={e => updateTheme('bg', e.target.value)} />
              <label className="block mt-2">Text color</label>
              <input type="color" value={(settings.theme && settings.theme.text) || '#111827'} onChange={e => updateTheme('text', e.target.value)} />
              <label className="block mt-2">Card color</label>
              <input type="color" value={(settings.theme && settings.theme.card) || '#ffffff'} onChange={e => updateTheme('card', e.target.value)} />
              <label className="block mt-2">Primary color</label>
              <input type="color" value={(settings.theme && settings.theme.primary) || '#06b6d4'} onChange={e => updateTheme('primary', e.target.value)} />
              <div className="mt-4">
                {!isAdmin ? (
                  <div className="mb-3">
                    <label className="block">Admin Password:</label>
                    <input type="password" value={password} onChange={e => setPassword(e.target.value)} className="mt-2 p-2 border rounded" placeholder="Password" />
                    <div className="mt-2">
                      <button onClick={doLogin} className="px-3 py-2 btn-primary rounded">Login</button>
                    </div>
                  </div>
                ) : (
                  <div className="mb-3">
                    <div className="text-sm muted">Admin logged in</div>
                    <button className="mt-2 px-3 py-2 bg-red-600 text-white rounded" onClick={doLogout}>Logout</button>
                  </div>
                )}
                {isAdmin && (
                  <div className="mt-3">
                    <div className="mt-4">
                      <button onClick={doBackup} className="mt-2 px-3 py-2 bg-sky-600 text-white rounded">Create Backup</button>
                    </div>
                    <div className="mt-3">
                      <label>Upload DB (.db file)</label>
                      <input type="file" onChange={onUploadDB} className="mt-2" />
                    </div>
                  </div>
                )}
                <label className="block">Admin token (optional for POST):</label>
                <input type="password" value={adminToken} onChange={e => setAdminToken(e.target.value)} className="mt-2 p-2 border rounded" placeholder="X-HAVEN-ADMIN" />
              </div>
              <button disabled={saving} onClick={save} className="mt-4 px-3 py-2 btn-primary rounded">{saving ? 'Saving...' : 'Save Settings (Admin)'}</button>
            </div>
          )}
        </div>
      </div>
    </div>
  )
}
