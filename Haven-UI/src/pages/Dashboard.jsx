import React, { useEffect, useState } from 'react'
import axios from 'axios'
import StatCard from '../components/StatCard'
import QuickActions from '../components/QuickActions'
import TerminalViewer from '../components/TerminalViewer'
import Tabs from '../components/Tabs'

export default function Dashboard(){
  const [stats, setStats] = useState(null)
  const [recent, setRecent] = useState([])
  const [discoveries, setDiscoveries] = useState([])
  useEffect(()=>{ 
    axios.get('/api/stats').then(r=>setStats(r.data)).catch(()=>setStats(null))
    axios.get('/api/systems').then(r=>setRecent((r.data && r.data.systems) || [])).catch(()=>setRecent([]))
    axios.get('/api/discoveries').then(r=>setDiscoveries((r.data && r.data.results) || [])).catch(()=>setDiscoveries([]))
  }, [])

  const panels = [
    { label: 'Systems', content: (
      <div>
        <div className="space-y-2">
          {recent.slice(0, 12).map(s => (
            <div key={s.id || s.name} className="flex items-center justify-between p-3 rounded-lg" style={{background: 'linear-gradient(180deg, rgba(255,255,255,0.02), transparent)'}}>
              <div>
                <div className="font-semibold">{s.name}</div>
                <div className="text-sm muted">{s.region} • x:{s.x} y:{s.y} z:{s.z}</div>
              </div>
              <div className="text-sm muted">{s.description?.slice(0, 80)}</div>
            </div>
          ))}
        </div>
      </div>
    )},
    { label: 'Discoveries', content: (
      <div>
        <div className="space-y-2">
          {discoveries.slice(0, 12).map(d => (
            <div key={d.id} className="p-3 rounded-lg" style={{background: 'linear-gradient(180deg, rgba(255,255,255,0.02), transparent)'}}>
              <div className="font-semibold">{d.discovery_name || d.discovery_type}</div>
              <div className="text-sm muted">{d.system_id ? `System ${d.system_id}` : d.location_name} • {d.time_period || ''}</div>
            </div>
          ))}
        </div>
      </div>
    )}
  ]

  return (
    <div>
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6 mb-6">
        <div className="col-span-2">
          <div className="grid grid-cols-2 gap-4">
            <StatCard title="Total Systems" value={stats ? stats.total : '—'} subtitle={stats ? (stats.regions?.length + ' regions') : ''} trend={[1,2,3,4,3,5,7]} />
            <StatCard title="Recent Discoveries" value={discoveries ? discoveries.length : '—'} subtitle={''} trend={[0,1,0,2,1,3]} />
          </div>

          <div className="mt-4">
            <h3 className="text-lg font-semibold mb-3">Recent</h3>
            <Tabs tabs={panels} />
          </div>
        </div>

        <aside>
          <div className="mb-4">
            <h3 className="text-lg font-semibold mb-3">Quick Actions</h3>
            <QuickActions />
          </div>

          <div>
            <h3 className="text-lg font-semibold mb-3">Live Logs</h3>
            <TerminalViewer />
          </div>
        </aside>
      </div>
    </div>
  )
}
