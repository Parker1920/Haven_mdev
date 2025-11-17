import React, { useEffect, useState } from 'react'
import Card from '../components/Card'

export default function RTAI(){
  const [messages, setMessages] = useState([])
  useEffect(()=>{ fetch('/api/rtai/history').then(r=>r.json()).then(j=>setMessages(j.messages || []));
  const protocol = window.location.protocol === 'https:' ? 'wss' : 'ws'
  const ws = new WebSocket(`${protocol}://${window.location.host}/ws/rtai`)
  ws.onmessage = (e) => setMessages(m => [...m, e.data])
  return ()=> ws.close(); }, [])
  return (
    <div>
      <Card>
        <h2 className="text-lg font-semibold mb-2">Round Table AI Chat</h2>
        <div className="space-y-2 h-72 overflow-auto bg-white p-3 rounded">
          {messages.map((m,i) => <div key={i} className="muted">{m}</div>)}
        </div>
        <div className="mt-2">
          <button className="px-3 py-2 bg-gray-200 rounded" onClick={() => fetch('/api/rtai/clear', {method:'POST'})}>Clear</button>
        </div>
      </Card>
    </div>
  )
}
