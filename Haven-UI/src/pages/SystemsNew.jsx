import React, { useEffect, useState } from 'react'
import axios from 'axios'
import Card from '../components/Card'
import Button from '../components/Button'
import FormField from '../components/FormField'
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
      <div className="mb-6 grid grid-cols-3 gap-4 items-center">
        <div className="col-span-2">
          <FormField>
            <input aria-label="Search systems" className="w-full px-3 py-2 rounded" value={q} onChange={e=>setQ(e.target.value)} placeholder="Search systems by name or region" />
          </FormField>
        </div>
        <div className="flex gap-2 justify-end">
          <Button onClick={search} variant="primary">Search</Button>
          <Button onClick={load} variant="ghost">Reload</Button>
          <Link to="/wizard"><Button variant="neutral">New</Button></Link>
        </div>
      </div>

      <div className="grid grid-cols-3 gap-4">
        {systems.map(s => (
          <Card key={s.id || s.name} className="flex flex-col justify-between">
            <div>
              <div className="text-lg font-semibold">{s.name}</div>
              <div className="muted">{s.region} • x:{s.x} y:{s.y} z:{s.z}</div>
              <div className="mt-3 text-sm muted">{s.description}</div>
            </div>
            <div className="mt-4 flex justify-between items-center">
              <div className="text-sm muted">ID: {s.id}</div>
              <div className="flex items-center gap-2">
                <Link aria-label={`Edit ${s.name}`} to={`/wizard?edit=${encodeURIComponent(s.name)}`}><Button variant="ghost"><PencilIcon className="w-4 h-4"/></Button></Link>
                <Button onClick={() => removeSystem(s.id || s.name)} variant="ghost"><TrashIcon className="w-4 h-4 text-red-400"/></Button>
              </div>
            </div>
          </Card>
        ))}
      </div>
    </div>
  )
}
