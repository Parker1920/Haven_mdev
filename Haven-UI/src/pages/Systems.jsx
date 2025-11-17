import React, { useEffect, useState } from 'react'
import { adminStatus } from '../utils/api'
import axios from 'axios'
import Card from '../components/Card'
import Button from '../components/Button'
import { TrashIcon, PencilIcon } from '@heroicons/react/24/outline'
import { Link } from 'react-router-dom'

export default function Systems(){
  const [systems, setSystems] = useState([])
  const [q, setQ] = useState('')
  useEffect(()=>{ load() }, [])
  useEffect(()=>{ adminStatus().then(r => setIsAdmin(!!r.logged_in)).catch(()=>{}) }, [])
  const [isAdmin, setIsAdmin] = useState(false)
  function load(){ axios.get('/api/systems').then(r=>setSystems(r.data.systems || [])).catch(()=>setSystems([])) }
  async function search(){ try{const r=await axios.get(`/api/systems/search?q=${encodeURIComponent(q)}`); setSystems(r.data.results); }catch(e){ load() } }
  async function removeSystem(id){ if(!confirm('Delete system?')) return; try{ await axios.delete(`/api/systems/${encodeURIComponent(id)}`); load(); }catch(e){ alert('Delete failed: '+ (e.response?.data?.detail || e.message)) } }

  return (
    <div>
      <div className="mb-4 flex space-x-3">
        <input aria-label="Search systems" className="px-3 py-2 border rounded" value={q} onChange={e=>setQ(e.target.value)} placeholder="Search systems" />
        <button className="px-3 py-2 btn-primary rounded" onClick={search}>Search</button>
        <button className="px-3 py-2 bg-sky-200 rounded" onClick={load}>Reload</button>
      </div>

      <div className="space-y-3">
        {systems.map(s => (
          <Card key={s.id || s.name} className="flex justify-between items-start">
            <div className="flex items-start justify-between w-full">
              <div>
                <div className="text-lg font-semibold">{s.name}</div>
                <div className="muted">{s.region} • x:{s.x} y:{s.y} z:{s.z}</div>
              </div>
              <div className="flex items-center gap-2">
                <Link aria-label={`Edit ${s.name}`} className="px-3 py-1 text-indigo-700 rounded mr-2 inline-flex items-center" to={`/wizard?edit=${encodeURIComponent(s.name)}`}><PencilIcon className="w-4 h-4 mr-1"/>Edit</Link>
                {isAdmin ? (
                  <button aria-label={`Delete ${s.name}`} onClick={() => removeSystem(s.id || s.name)} className="px-3 py-1 text-red-600 rounded inline-flex items-center"><TrashIcon className="w-4 h-4 mr-1"/>Delete</button>
                ) : (
                  <div className="px-3 py-1 text-gray-400 rounded inline-flex items-center">(admin)</div>
                )}
              </div>
            </div>
            <div className="mt-2 muted w-full">{s.description}</div>
          </Card>
        ))}
      </div>
    </div>
  )
}
import React, { useEffect, useState } from 'react'
import axios from 'axios'
import Card from '../components/Card'
import Button from '../components/Button'
import { TrashIcon, PencilIcon } from '@heroicons/react/24/outline'
import { Link } from 'react-router-dom'

export default function Systems(){
  const [systems, setSystems] = useState([])
  const [q, setQ] = useState('')
  useEffect(()=>{ load() }, [])
  function load(){ axios.get('/api/systems').then(r=>setSystems(r.data.systems || [])) }
  async function search(){ try{const r=await axios.get(`/api/systems/search?q=${encodeURIComponent(q)}`); setSystems(r.data.results); }catch(e){ load() } }
  async function removeSystem(id){ if(!confirm('Delete system?')) return; try{ await axios.delete(`/api/systems/${encodeURIComponent(id)}`); load(); }catch(e){ alert('Delete failed: '+ (e.response?.data?.detail || e.message)) } }

  return (
    <div>
      <div className="mb-4 flex space-x-3">
        <input className="px-3 py-2 border rounded" value={q} onChange={e=>setQ(e.target.value)} placeholder="Search systems" />
        <button className="px-3 py-2 btn-primary rounded" onClick={search}>Search</button>
        <button className="px-3 py-2 bg-sky-200 rounded" onClick={load}>Reload</button>
      </div>

      <div className="space-y-3">
        {systems.map(s => (
          <Card key={s.id || s.name} className="flex justify-between items-start">
            <div className="flex items-start justify-between w-full">
              <div>
                <div className="text-lg font-semibold">{s.name}</div>
                <div className="muted">{s.region} • x:{s.x} y:{s.y} z:{s.z}</div>
              </div>
              <div className="flex items-center gap-2">
                <Link aria-label={`Edit ${s.name}`} className="px-3 py-1 text-indigo-700 rounded mr-2 inline-flex items-center" to={`/wizard?edit=${encodeURIComponent(s.name)}`}><PencilIcon className="w-4 h-4 mr-1"/>Edit</Link>
                <button aria-label={`Delete ${s.name}`} onClick={() => removeSystem(s.id || s.name)} className="px-3 py-1 text-red-600 rounded inline-flex items-center"><TrashIcon className="w-4 h-4 mr-1"/>Delete</button>
              </div>
            </div>
            <div className="mt-2 muted w-full">{s.description}</div>
            <div className="mt-2">
              <button className="px-2 py-1 bg-sky-600 rounded text-white" onClick={async ()=>{
                try{
                  const r = await axios.get(`/api/systems/${encodeURIComponent(s.name)}`)
                  s._expanded = !s._expanded
                  s._details = r.data
                  setSystems([...systems])
                }catch(e){ alert('Failed to fetch system details: '+ (e.response?.data?.detail || e.message)) }
              }}>{s._expanded ? 'Hide Details' : 'Show Details'}</button>
            </div>
            {s._expanded && s._details && (
              <div className="mt-3 bg-white/5 p-3 rounded w-full">
                <h4 className="font-semibold">Planets ({(s._details.planets || []).length})</h4>
                <div className="mt-2 space-y-2">
                  {(s._details.planets || []).map((p, i) => (
                    <div key={i} className="border rounded p-2 bg-white/2">
                      <div className="font-semibold">{p.name} • {p.sentinel}</div>
                      <div className="muted text-sm">Fauna: {p.fauna || '—'} • Flora: {p.flora || '—'} • Materials: {p.materials || '—'}</div>
                      <div className="mt-1">Notes: {p.notes || '—'}</div>
                      <div className="mt-1">Moons: {(p.moons || []).map(m => m.name).join(', ') || '—'}</div>
                    </div>
                  ))}
                </div>
              </div>
            )}
          </Card>
        ))}
      </div>
    </div>
  )
}
import React, { useEffect, useState } from 'react'
import axios from 'axios'
import Card from '../components/Card'
import { TrashIcon, PencilIcon } from '@heroicons/react/24/outline'
import { Link } from 'react-router-dom'

export default function Systems(){
  const [systems, setSystems] = useState([])
  const [q, setQ] = useState('')
  useEffect(()=>{ load() }, [])
  function load(){ axios.get('/api/systems').then(r=>setSystems(r.data.systems || [])) }
  async function search(){ try{const r=await axios.get(`/api/systems/search?q=${encodeURIComponent(q)}`); setSystems(r.data.results); }catch(e){ load() } }
  async function removeSystem(id){ if(!confirm('Delete system?')) return; try{ await axios.delete(`/api/systems/${encodeURIComponent(id)}`); load(); }catch(e){ alert('Delete failed: '+ (e.response?.data?.detail || e.message)) } }

  return (
    <div>
      <div className="mb-4 flex space-x-3">
        <input aria-label="Search systems" className="px-3 py-2 border rounded" value={q} onChange={e=>setQ(e.target.value)} placeholder="Search systems" />
        <button className="px-3 py-2 btn-primary rounded" onClick={search}>Search</button>
        <button className="px-3 py-2 bg-sky-200 rounded" onClick={load}>Reload</button>
      </div>

      <div className="space-y-3">
        {systems.map(s => (
          <Card key={s.id || s.name} className="flex justify-between items-start">
            <div className="flex items-start justify-between w-full">
              <div>
                <div className="text-lg font-semibold">{s.name}</div>
                <div className="muted">{s.region} • x:{s.x} y:{s.y} z:{s.z}</div>
              </div>
              <div className="flex items-center gap-2">
                <Link aria-label={`Edit ${s.name}`} className="px-3 py-1 text-indigo-700 rounded mr-2 inline-flex items-center" to={`/wizard?edit=${encodeURIComponent(s.name)}`}><PencilIcon className="w-4 h-4 mr-1"/>Edit</Link>
                <button aria-label={`Delete ${s.name}`} onClick={() => removeSystem(s.id || s.name)} className="px-3 py-1 text-red-600 rounded inline-flex items-center"><TrashIcon className="w-4 h-4 mr-1"/>Delete</button>
              </div>
            </div>
            <div className="mt-2 muted w-full">{s.description}</div>
          </Card>
        ))}
      </div>
    </div>
  )
}
import React, { useEffect, useState } from 'react'
import axios from 'axios'
import Card from '../components/Card'
import { TrashIcon, PencilIcon } from '@heroicons/react/24/outline'
import { Link } from 'react-router-dom'

export default function Systems(){
  const [systems, setSystems] = useState([])
  const [q, setQ] = useState('')
  useEffect(()=>{ load() }, [])
  function load(){ axios.get('/api/systems').then(r=>setSystems(r.data.systems || [])) }
  async function search(){ try{const r=await axios.get(`/api/systems/search?q=${encodeURIComponent(q)}`); setSystems(r.data.results); }catch(e){ load() } }
  async function removeSystem(id){ if(!confirm('Delete system?')) return; try{ await axios.delete(`/api/systems/${encodeURIComponent(id)}`); load(); }catch(e){ alert('Delete failed: '+ (e.response?.data?.detail || e.message)) } }

  return (
    <div>
      <div className="mb-4 flex space-x-3">
        <input aria-label="Search systems" className="px-3 py-2 border rounded" value={q} onChange={e=>setQ(e.target.value)} placeholder="Search systems" />
        <button className="px-3 py-2 btn-primary rounded" onClick={search}>Search</button>
        <button className="px-3 py-2 bg-sky-200 rounded" onClick={load}>Reload</button>
      </div>

      <div className="space-y-3">
        {systems.map(s => (
          <Card key={s.id || s.name} className="flex justify-between items-start">
            <div className="flex items-start justify-between w-full">
              <div>
                <div className="text-lg font-semibold">{s.name}</div>
                <div className="muted">{s.region} • x:{s.x} y:{s.y} z:{s.z}</div>
              </div>
              <div className="flex items-center gap-2">
                <Link aria-label={`Edit ${s.name}`} className="px-3 py-1 text-indigo-700 rounded mr-2 inline-flex items-center" to={`/wizard?edit=${encodeURIComponent(s.name)}`}><PencilIcon className="w-4 h-4 mr-1"/>Edit</Link>
                <button aria-label={`Delete ${s.name}`} onClick={() => removeSystem(s.id || s.name)} className="px-3 py-1 text-red-600 rounded inline-flex items-center"><TrashIcon className="w-4 h-4 mr-1"/>Delete</button>
              </div>
            </div>
            <div className="mt-2 muted w-full">{s.description}</div>
          </Card>
        ))}
      </div>
    </div>
  )
}
/* CLEAN: Systems.jsx updated */
// Systems page - deleted all content temporarily to clear duplicates
import React, { useEffect, useState } from 'react'
import axios from 'axios'
import Card from '../components/Card'
import Button from '../components/Button'
import { TrashIcon, PencilIcon } from '@heroicons/react/24/outline'
import { Link } from 'react-router-dom'

export default function Systems(){
  const [systems, setSystems] = useState([])
  const [q, setQ] = useState('')
  useEffect(()=>{ load() }, [])
  function load(){ axios.get('/api/systems').then(r=>setSystems(r.data.systems || [])) }
  async function search(){ try{const r=await axios.get(`/api/systems/search?q=${encodeURIComponent(q)}`); setSystems(r.data.results); }catch(e){ load() } }
  async function removeSystem(id){ if(!confirm('Delete system?')) return; try{ await axios.delete(`/api/systems/${encodeURIComponent(id)}`); load(); }catch(e){ alert('Delete failed: '+ (e.response?.data?.detail || e.message)) } }

  return (
    <div>
      <div className="mb-4 flex space-x-3">
        <input className="px-3 py-2 border rounded" value={q} onChange={e=>setQ(e.target.value)} placeholder="Search systems" />
        <button className="px-3 py-2 btn-primary rounded" onClick={search}>Search</button>
        <button className="px-3 py-2 bg-sky-200 rounded" onClick={load}>Reload</button>
      </div>

      <div className="space-y-3">
        {systems.map(s => (
          <Card key={s.id || s.name} className="flex justify-between items-start">
            <div className="flex items-start justify-between w-full">
              <div>
                <div className="text-lg font-semibold">{s.name}</div>
                <div className="muted">{s.region} • x:{s.x} y:{s.y} z:{s.z}</div>
              </div>
              <div className="flex items-center gap-2">
                <Link aria-label={`Edit ${s.name}`} className="px-3 py-1 text-indigo-700 rounded mr-2 inline-flex items-center" to={`/wizard?edit=${encodeURIComponent(s.name)}`}><PencilIcon className="w-4 h-4 mr-1"/>Edit</Link>
                <button aria-label={`Delete ${s.name}`} onClick={() => removeSystem(s.id || s.name)} className="px-3 py-1 text-red-600 rounded inline-flex items-center"><TrashIcon className="w-4 h-4 mr-1"/>Delete</button>
              </div>
            </div>
            <div className="mt-2 muted w-full">{s.description}</div>
          </Card>
        ))}
      </div>
    </div>
  )
}
import React, { useEffect, useState } from 'react'
import axios from 'axios'
import Card from '../components/Card'
import Button from '../components/Button'
import { TrashIcon, PencilIcon } from '@heroicons/react/24/outline'
import { Link, useNavigate } from 'react-router-dom'

export default function Systems(){
  const [systems, setSystems] = useState([])
  const [q, setQ] = useState('')
  useEffect(()=>{ load() }, [])
  function load(){ axios.get('/api/systems').then(r=>setSystems(r.data.systems || [])) }
  async function search(){ try{const r=await axios.get(`/api/systems/search?q=${encodeURIComponent(q)}`); setSystems(r.data.results); }catch(e){ load() } }
  async function removeSystem(id){ if(!confirm('Delete system?')) return; try{ await axios.delete(`/api/systems/${encodeURIComponent(id)}`); load(); }catch(e){ alert('Delete failed: '+ (e.response?.data?.detail || e.message)) } }

  return (
    <div>
      <div className="mb-4 flex space-x-3">
        <input className="px-3 py-2 border rounded" value={q} onChange={e=>setQ(e.target.value)} placeholder="Search systems" />
        <button className="px-3 py-2 btn-primary rounded" onClick={search}>Search</button>
        <button className="px-3 py-2 bg-sky-200 rounded" onClick={load}>Reload</button>
                <div>
                <Link aria-label={`Edit ${s.name}`} className="px-3 py-1 text-indigo-700 rounded mr-2 inline-flex items-center" to={`/wizard?edit=${encodeURIComponent(s.name)}`}><PencilIcon className="w-4 h-4 mr-1"/>Edit</Link>
                <button aria-label={`Delete ${s.name}`} onClick={() => removeSystem(s.id || s.name)} className="px-3 py-1 text-red-600 rounded inline-flex items-center"><TrashIcon className="w-4 h-4 mr-1"/>Delete</button>
              </div>
          <Card key={s.id || s.name} className="flex justify-between items-start">
            <div className="flex items-start justify-between">
              <div>
                <div className="text-lg font-semibold">{s.name}</div>
                <div className="muted">{s.region} • x:{s.x} y:{s.y} z:{s.z}</div>
              </div>
              <div>
                <Link className="px-3 py-1 text-indigo-700 rounded mr-2 inline-flex items-center" to={`/wizard?edit=${encodeURIComponent(s.name)}`}><PencilIcon className="w-4 h-4 mr-1"/>Edit</Link>
                <button className="px-3 py-1 text-red-600 rounded inline-flex items-center"><TrashIcon className="w-4 h-4 mr-1"/>Delete</button>
              </div>
            </div>
            <div className="mt-2 muted">{s.description}</div>
          </Card>
        ))}
      </div>
    </div>
  )
}
