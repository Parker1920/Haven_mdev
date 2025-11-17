import React, { useEffect, useRef, useState } from 'react'
import Card from '../components/Card'

export default function Logs(){
  const [lines, setLines] = useState([])
  const ref = useRef(null)
  useEffect(()=>{ fetch('/api/logs').then(r=>r.json()).then(j=>setLines(j.lines || []))
  const protocol = window.location.protocol === 'https:' ? 'wss' : 'ws'
  const ws = new WebSocket(`${protocol}://${window.location.host}/ws/logs`)
  ws.onmessage = (e) => setLines(l => [...l, e.data])
  return ()=> ws.close(); }, [])
  return (
    <div>
      <Card>
        <h2 className="text-lg font-semibold mb-2">Live Logs</h2>
        <pre className="bg-gray-900 text-white p-3 rounded h-72 overflow-auto" ref={ref}>{lines.join('\n')}</pre>
      </Card>
    </div>
  )
}
