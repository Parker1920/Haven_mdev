import React, { useEffect, useState } from 'react'
import axios from 'axios'
import { useLocation, useNavigate } from 'react-router-dom'
import Card from '../components/Card'
import Button from '../components/Button'
import PlanetEditor from '../components/PlanetEditor'
import Modal from '../components/Modal'
import { adminStatus } from '../utils/api'

function useQuery(){ return new URLSearchParams(useLocation().search) }

export default function Wizard(){
  const query = useQuery();
  const navigate = useNavigate();
  const edit = query.get('edit')
  const [system, setSystem] = useState({ id:'', name:'', region:'', x:'', y:'', z:'', description:'', planets: [] })
  const [planetModalOpen, setPlanetModalOpen] = useState(false)
  const [editingPlanetIndex, setEditingPlanetIndex] = useState(null)
  const [editingPlanet, setEditingPlanet] = useState(null)
  useEffect(()=>{ if(edit){ axios.get(`/api/systems/${encodeURIComponent(edit)}`).then(r=>setSystem(r.data)).catch(()=>{}) } }, [edit])
  useEffect(()=>{ adminStatus().then(r => { if(!r.logged_in){ /* Not admin, will prompt in save */ } }).catch(()=>{}) }, [])

  async function submit(e){ e.preventDefault();
    // Client-side validation for nested planets & moons
    if(!system.name || !system.name.trim()) { alert('System name is required'); return; }
    if(system.planets){
      for(const p of system.planets){
        if(!p.name || !p.name.trim()){ alert('All planets must have a name'); return; }
        if(p.moons){
          for(const m of p.moons){
            if(!m.name || !m.name.trim()){ alert('All moons must have a name'); return; }
          }
        }
      }
    }
    try{ const r = await axios.post('/api/save_system', system); alert('Saved: '+ JSON.stringify(r.data)); navigate('/systems'); } catch(err){ alert('Save failed: ' + (err.response?.data?.detail || err.message || err)) } }

  function setField(k,v){ setSystem(s => ({...s, [k]: v})) }

  function addPlanet(){
    setEditingPlanetIndex(-1)
    setEditingPlanet({ name: '', sentinel: 'None', moons: [] })
    setPlanetModalOpen(true)
  }

  function editPlanet(i){
    setEditingPlanetIndex(i)
    setEditingPlanet(system.planets[i])
    setPlanetModalOpen(true)
  }

  function commitPlanet(planet){
    const planets = [...(system.planets || [])]
    if(editingPlanetIndex === -1){
      planets.push(planet)
    } else {
      planets[editingPlanetIndex] = planet
    }
    setSystem({...system, planets})
    setPlanetModalOpen(false)
  }

  function updatePlanet(idx, val){
    const planets = [...(system.planets || [])]
    planets[idx] = val
    setSystem({...system, planets})
  }

  function removePlanet(idx){
    const planets = [...(system.planets || [])]
    planets.splice(idx, 1)
    setSystem({...system, planets})
  }

  return (
    <div>
      <Card className="max-w-xl">
        <form onSubmit={submit}>
        <label className="block mb-2">Name <input placeholder="Name" aria-label="Name" className="w-full mt-1" value={system.name || ''} onChange={e=>setField('name', e.target.value)} required/></label>
        <div className="grid grid-cols-3 gap-2">
          <input className="mt-1" value={system.x || ''} onChange={e=>setField('x', e.target.value)} type="number" placeholder="X" />
          <input className="mt-1" value={system.y || ''} onChange={e=>setField('y', e.target.value)} type="number" placeholder="Y" />
          <input className="mt-1" value={system.z || ''} onChange={e=>setField('z', e.target.value)} type="number" placeholder="Z" />
        </div>
        <label className="block mt-3">Region <input placeholder="Region" className="w-full mt-1" value={system.region || ''} onChange={e=>setField('region', e.target.value)} /></label>
        <label className="block mt-3">Description <textarea aria-label="System description" className="w-full mt-1" value={system.description || ''} onChange={e=>setField('description', e.target.value)} /></label>
        <div className="mt-4">
          <h3 className="text-md font-semibold mb-2">Planets</h3>
          <div>
            {(system.planets || []).map((p, i) => (
              <div key={i} className="mb-2">
                <PlanetEditor index={i} planet={p} onChange={updatePlanet} onRemove={removePlanet} />
                <div className="mt-1 flex space-x-2">
                  <button className="px-3 py-1 bg-sky-600 text-white rounded" onClick={() => editPlanet(i)}>Edit</button>
                </div>
              </div>
            ))}
          </div>
          <div className="mt-2">
            <button type="button" onClick={addPlanet} className="px-3 py-1 bg-green-600 rounded">➕ Add Planet</button>
          </div>
        </div>
        <div className="mt-4 flex space-x-2">
          <Button className="btn-primary" type="submit">Save</Button>
          <Button className="bg-gray-200 text-gray-800" onClick={()=> navigate('/systems')}>Cancel</Button>
        </div>
        {planetModalOpen && (
        <Modal title={editingPlanetIndex === -1 ? 'Add Planet' : 'Edit Planet'} onClose={() => setPlanetModalOpen(false)}>
          <PlanetEditor planet={editingPlanet} index={editingPlanetIndex} onChange={(i,p)=>{ setEditingPlanet(p) }} onRemove={() => {}} onSave={commitPlanet} />
        </Modal>
      )}
        </form>
      </Card>
    </div>
  )
}
