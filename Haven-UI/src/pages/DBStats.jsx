import React, { useEffect, useState } from 'react'

export default function DBStats(){
  const [stats, setStats] = useState(null)
  useEffect(()=>{ fetch('/api/db_stats').then(r=>r.json()).then(j=>setStats(j.stats || null)).catch(()=>setStats(null)) }, [])
  return (
    <div>
      <h2 className="text-xl font-semibold mb-2">Database Statistics</h2>
      {stats ? (
        <div className="space-y-2">
          {Object.entries(stats).map(([k,v]) => (<div key={k}><strong>{k}</strong>: {String(v)}</div>))}
        </div>
      ) : (
        <div className="muted">No DB stats available.</div>
      )}
    </div>
  )
}
